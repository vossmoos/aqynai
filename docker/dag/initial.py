from dagster import job, op, repository

@op
def initial(context):
    context.log.info("Hello, World!")

@job
def initial_job():
    initial()

# This repository definition is crucial for Dagster to discover your jobs
@repository
def aqyn():
    return [initial_job]

if __name__ == "__main__":
    result = initial_job.execute_in_process()