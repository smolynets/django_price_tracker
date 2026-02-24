from celery import shared_task
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def run_daily_logic():
    # This is the function executed by Celery Worker
    logger.info("Task execution started...")
    
    # Place your business logic here
    result = "Daily data synchronized"
    
    logger.info(f"Task status: {result}")
    return result
