from dagster import job, op

@op
def hello_world(context):
    context.log.info("Hello, World!")

@job
def hello_world_job():
    hello_world()

if __name__ == "__main__":
    result = hello_world_job.execute_in_process()