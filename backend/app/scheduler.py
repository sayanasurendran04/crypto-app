from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import AsyncSessionLocal
from app.services.ingestion import fetch_and_store
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def ingest_job():
    async with AsyncSessionLocal() as db:
        try:
            count = await fetch_and_store(db)
            logger.info(f"Scheduler: stored {count} price records")
        except Exception as e:
            logger.error(f"Scheduler ingestion failed: {e}")


async def start_scheduler():
    # Run immediately on startup, then every 15 minutes
    await ingest_job()
    scheduler.add_job(ingest_job, "interval", minutes=15, id="ingest")
    scheduler.start()
    logger.info("Scheduler started — fetching prices every 15 minutes")


async def stop_scheduler():
    scheduler.shutdown(wait=False)
