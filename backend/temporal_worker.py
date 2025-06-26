import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow_config import get_settings
from workflows.error_processing import (
    ErrorProcessingWorkflow,
    process_error_activity,
    deduplicate_errors_activity,
    update_group_statistics_activity
)

async def run_worker():
    settings = get_settings()
    client = await Client.connect(settings["temporal_host_port"])
    
    worker = Worker(
        client,
        task_queue=settings["temporal_task_queue"],
        workflows=[ErrorProcessingWorkflow],
        activities=[
            process_error_activity,
            deduplicate_errors_activity,
            update_group_statistics_activity
        ]
    )
    
    await worker.run()

def main():
    asyncio.run(run_worker())

if __name__ == "__main__":
    main() 