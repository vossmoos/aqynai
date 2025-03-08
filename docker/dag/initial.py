from dagster import job, op, repository, Field, String, Out, In
from minio import Minio
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import BSHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default values for environment variables (change these as needed)
DEFAULT_MINIO_ENDPOINT = "localhost:9000"
DEFAULT_MINIO_ACCESS_KEY = "minioadmin"
DEFAULT_MINIO_SECRET_KEY = "minioadmin"
DEFAULT_MINIO_BUCKET = "html-bucket"
DEFAULT_QDRANT_HOST = "localhost"
DEFAULT_QDRANT_PORT = 6333
DEFAULT_QDRANT_COLLECTION = "html_embeddings"
DEFAULT_OPENAI_API_KEY = "your-openai-api-key-here"  # Replace with a real key or leave as placeholder

# Resolve actual values from environment or defaults
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", DEFAULT_MINIO_ENDPOINT)
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", DEFAULT_MINIO_ACCESS_KEY)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", DEFAULT_MINIO_SECRET_KEY)
MINIO_BUCKET = os.getenv("MINIO_BUCKET", DEFAULT_MINIO_BUCKET)
QDRANT_HOST = os.getenv("QDRANT_HOST", DEFAULT_QDRANT_HOST)
QDRANT_PORT = int(os.getenv("QDRANT_PORT", DEFAULT_QDRANT_PORT))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", DEFAULT_QDRANT_COLLECTION)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", DEFAULT_OPENAI_API_KEY)

# Op 1: Fetch HTML files from MinIO and chunk them
@op(
    config_schema={
        "minio_endpoint": Field(String, default_value=MINIO_ENDPOINT),
        "minio_access_key": Field(String, default_value=MINIO_ACCESS_KEY),
        "minio_secret_key": Field(String, default_value=MINIO_SECRET_KEY),
        "minio_bucket": Field(String, default_value=MINIO_BUCKET),
    },
    out=Out(list, description="List of chunked documents")
)
def fetch_and_chunk_html(context):
    context.log.info("Fetching and chunking HTML files from MinIO...")

    # MinIO client setup
    minio_client = Minio(
        context.op_config["minio_endpoint"],
        access_key=context.op_config["minio_access_key"],
        secret_key=context.op_config["minio_secret_key"],
        secure=False
    )

    # Ensure bucket exists
    bucket_name = context.op_config["minio_bucket"]
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        context.log.info(f"Created bucket: {bucket_name}")
    else:
        context.log.info(f"Using existing bucket: {bucket_name}")

    # List all HTML files in the bucket
    objects = minio_client.list_objects(bucket_name, recursive=True)
    html_files = [obj for obj in objects if obj.object_name.endswith(".html")]

    if not html_files:
        context.log.warning("No HTML files found in the bucket!")
        return []

    # Text splitter for chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Process each HTML file
    documents = []
    for obj in html_files:
        context.log.info(f"Processing file: {obj.object_name}")
        
        # Get the HTML content from MinIO
        response = minio_client.get_object(bucket_name, obj.object_name)
        html_content = response.read().decode("utf-8")
        response.close()

        # Parse HTML content with BeautifulSoup via LangChain loader
        buffer = BytesIO(html_content.encode("utf-8"))
        loader = BSHTMLLoader(buffer)
        doc = loader.load()[0]  # Get the first document

        # Split the document into chunks
        chunks = text_splitter.split_documents([doc])
        documents.extend(chunks)

    context.log.info(f"Chunked {len(documents)} document chunks")
    return documents

# Op 2: Set up Qdrant collection if it doesn't exist
@op(
    config_schema={
        "qdrant_host": Field(String, default_value=QDRANT_HOST),
        "qdrant_port": Field(int, default_value=QDRANT_PORT),
        "qdrant_collection": Field(String, default_value=QDRANT_COLLECTION),
    }
)
def setup_qdrant_collection(context):
    context.log.info("Setting up Qdrant collection...")

    # Qdrant client setup
    qdrant_client = QdrantClient(
        host=context.op_config["qdrant_host"],
        port=context.op_config["qdrant_port"]
    )

    # Embedding size for text-embedding-3-large is 3072
    embedding_size = 3072
    collection_name = context.op_config["qdrant_collection"]

    # Check if collection exists
    collections = qdrant_client.get_collections().collections
    collection_exists = any(col.name == collection_name for col in collections)

    if not collection_exists:
        context.log.info(f"Creating new collection: {collection_name}")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=models.Distance.COSINE
            )
        )
    else:
        context.log.info(f"Collection {collection_name} already exists")

    return collection_name

# Op 3: Generate embeddings and store in Qdrant
@op(
    ins={"documents": In(list, description="List of chunked documents"), "collection_name": In(str, description="Qdrant collection name")},
    config_schema={
        "qdrant_host": Field(String, default_value=QDRANT_HOST),
        "qdrant_port": Field(int, default_value=QDRANT_PORT),
    }
)
def embed_and_store(context, documents, collection_name):
    context.log.info("Generating embeddings and storing in Qdrant...")

    if not documents:
        context.log.warning("No documents to embed!")
        return

    # Initialize OpenAI embeddings (API key from resolved variable)
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  # Ensure LangChain picks it up
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # Qdrant client setup
    qdrant_client = QdrantClient(
        host=context.op_config["qdrant_host"],
        port=context.op_config["qdrant_port"]
    )

    # Generate embeddings
    texts = [doc.page_content for doc in documents]
    embedding_vectors = embeddings.embed_documents(texts)

    # Prepare points for Qdrant
    points = [
        models.PointStruct(
            id=idx,
            vector=vector,
            payload={"text": doc.page_content, "metadata": doc.metadata}
        )
        for idx, (vector, doc) in enumerate(zip(embedding_vectors, documents))
    ]

    # Upsert points into Qdrant
    qdrant_client.upsert(
        collection_name=collection_name,
        points=points
    )

    context.log.info(f"Stored {len(points)} embeddings in Qdrant collection: {collection_name}")

@job
def html_embedding_job():
    documents = fetch_and_chunk_html()
    collection_name = setup_qdrant_collection()
    embed_and_store(documents=documents, collection_name=collection_name)

@repository
def aqyn():
    return [html_embedding_job]

if __name__ == "__main__":
    result = html_embedding_job.execute_in_process(
        run_config={
            "ops": {
                "fetch_and_chunk_html": {
                    "config": {
                        "minio_endpoint": MINIO_ENDPOINT,
                        "minio_access_key": MINIO_ACCESS_KEY,
                        "minio_secret_key": MINIO_SECRET_KEY,
                        "minio_bucket": MINIO_BUCKET,
                    }
                },
                "setup_qdrant_collection": {
                    "config": {
                        "qdrant_host": QDRANT_HOST,
                        "qdrant_port": QDRANT_PORT,
                        "qdrant_collection": QDRANT_COLLECTION
                    }
                },
                "embed_and_store": {
                    "config": {
                        "qdrant_host": QDRANT_HOST,
                        "qdrant_port": QDRANT_PORT
                    }
                }
            }
        }
    )