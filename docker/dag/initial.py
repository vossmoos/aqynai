from dagster import job, op, repository

@op
def hello_world(context):
    context.log.info("Hello, World!")

@job
def hello_world_job():
    hello_world()

# This repository definition is crucial for Dagster to discover your jobs
@repository
def my_repository():
    return [hello_world_job]

if __name__ == "__main__":
    result = hello_world_job.execute_in_process()