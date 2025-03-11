from dagster import job, op, repository, Field, String, Out, In
from minio import Minio
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document  # Updated import for Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os

# Default values aligned with Docker Compose
DEFAULT_MINIO_ENDPOINT = "minio:9000"
DEFAULT_MINIO_ACCESS_KEY = "aqyn"
DEFAULT_MINIO_SECRET_KEY = "aqynpassword"
DEFAULT_MINIO_BUCKET = "aqyn-bucket"
DEFAULT_QDRANT_HOST = "rag.aqyn.tech"
DEFAULT_QDRANT_PORT = 6333
DEFAULT_QDRANT_API_KEY = "e47ac10b-58c0-4372-a567-0e02b2c3d422"
DEFAULT_QDRANT_COLLECTION = "aqyn"

# Resolve actual values from environment or defaults
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", DEFAULT_MINIO_ENDPOINT)
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", DEFAULT_MINIO_ACCESS_KEY)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", DEFAULT_MINIO_SECRET_KEY)
MINIO_BUCKET = os.getenv("MINIO_BUCKET", DEFAULT_MINIO_BUCKET)
QDRANT_HOST = os.getenv("QDRANT_HOST", DEFAULT_QDRANT_HOST)
QDRANT_PORT = int(os.getenv("QDRANT_PORT", DEFAULT_QDRANT_PORT))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", DEFAULT_QDRANT_API_KEY)
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", DEFAULT_QDRANT_COLLECTION)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    context.log.info("Fetching and chunking files from MinIO...")

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

    # List all objects in the bucket
    objects = minio_client.list_objects(bucket_name, recursive=True)
    if not objects:
        context.log.warning("No files found in the bucket!")
        return []

    # Text splitter for chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Process each file
    documents = []
    for obj in objects:
        context.log.info(f"Processing file: {obj.object_name}")
        
        # Get the file content from MinIO
        response = minio_client.get_object(bucket_name, obj.object_name)
        file_content = response.read()
        response.close()

        # Assume HTML content
        try:
            html_content = file_content.decode("utf-8")
            # Create a Document object directly from the string
            doc = Document(page_content=html_content, metadata={"source": obj.object_name})
            chunks = text_splitter.split_documents([doc])
            documents.extend(chunks)
        except Exception as e:
            context.log.warning(f"Failed to process {obj.object_name} as HTML: {e}")
            continue

    context.log.info(f"Chunked {len(documents)} document chunks")
    return documents

# Op 2: Generate embeddings and store in Qdrant
@op(
    ins={"documents": In(list, description="List of chunked documents")},
    config_schema={
        "qdrant_host": Field(String, default_value=QDRANT_HOST),
        "qdrant_port": Field(int, default_value=QDRANT_PORT),
        "qdrant_api_key": Field(String, default_value=QDRANT_API_KEY),
        "qdrant_collection": Field(String, default_value=QDRANT_COLLECTION),
    }
)
def embed_and_store(context, documents):
    context.log.info("Generating embeddings and storing in Qdrant...")

    if not documents:
        context.log.warning("No documents to embed!")
        return

    # Initialize OpenAI embeddings with text-embedding-3-small
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Qdrant client setup
    qdrant_client = QdrantClient(
        host=context.op_config["qdrant_host"],
        port=context.op_config["qdrant_port"],
        api_key=context.op_config["qdrant_api_key"],
        https=False
    )

    # Generate embeddings
    texts = [doc.page_content for doc in documents]
    embedding_vectors = embeddings.embed_documents(texts)

    # Prepare points for Qdrant with updated payload schema
    points = [
        models.PointStruct(
            id=idx,
            vector=vector,
            payload={"raw_text": doc.page_content}
        )
        for idx, (vector, doc) in enumerate(zip(embedding_vectors, documents))
    ]

    # Upsert points into Qdrant
    collection_name = context.op_config["qdrant_collection"]
    qdrant_client.upsert(
        collection_name=collection_name,
        points=points
    )

    context.log.info(f"Stored {len(points)} embeddings in Qdrant collection: {collection_name}")

# Define the job
@job
def html_embedding_job():
    documents = fetch_and_chunk_html()
    embed_and_store(documents=documents)

# Define the repository
@repository
def aqyn():
    return [html_embedding_job]

# Execute the job in-process (for testing)
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
                "embed_and_store": {
                    "config": {
                        "qdrant_host": QDRANT_HOST,
                        "qdrant_port": QDRANT_PORT,
                        "qdrant_api_key": QDRANT_API_KEY,
                        "qdrant_collection": QDRANT_COLLECTION
                    }
                }
            }
        }
    )