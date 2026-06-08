"""Data Refresh Scheduler - Update data every N minutes"""

from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime
import logging


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler = None
_last_update = None


def start_refresh_scheduler(refresh_interval: int = 5):
    """
    Start background scheduler to refresh data periodically.

    Args:
        refresh_interval: Minutes between refreshes (default 5)
    """
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        return

    _scheduler = BackgroundScheduler()

    # Add job to refresh data
    _scheduler.add_job(
        func=_refresh_data,
        trigger="interval",
        minutes=refresh_interval,
        id="data_refresh",
        name="Data refresh job",
        replace_existing=True
    )

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: _scheduler.shutdown())

    _scheduler.start()

    logger.info(f"Scheduler started - refreshing every {refresh_interval} minutes")


def _refresh_data():
    """Refresh data from sources"""
    global _last_update

    try:
        _last_update = datetime.now()
        logger.info(f"Data refresh at {_last_update}")

        # Import modules for refresh
        from kiotviet_client import KiotvietClient
        from rfm_calculator import calculate_rfm_for_customers
        from apriori_miner import analyze_market_basket
        from data_loader import DataLoader
        import os
        from datetime import datetime as dt

        # 1. Pull from Kiotviet API
        retail_id = os.getenv("KIOTVIET_RETAIL_ID")
        api_key = os.getenv("KIOTVIET_API_KEY")

        if retail_id and api_key:
            try:
                client = KiotvietClient(retail_id, api_key)
                sync_result = client.sync_to_sqlite(full_sync=False)
                logger.info(f"Kiotviet sync: {sync_result}")
                client.close()
            except Exception as e:
                logger.error(f"Kiotviet sync error: {e}")

        # 2. Update SQLite database (done by client.sync_to_sqlite)

        # 3. Recalculate RFM scores
        try:
            loader = DataLoader("retail.db")
            customers = loader.load_customers()
            invoices = loader.load_invoices()

            if not customers.empty and not invoices.empty:
                rfm_data = calculate_rfm_for_customers(customers, invoices, dt.now().date())
                logger.info(f"RFM recalculated for {len(rfm_data)} customers")
        except Exception as e:
            logger.error(f"RFM calculation error: {e}")

        # 4. Regenerate Apriori rules (for bundle recommendations)
        try:
            invoice_items = loader.load_invoice_items()

            if not invoice_items.empty:
                transactions = []
                for order_id in invoice_items['ma_hoa_don'].unique():
                    items = invoice_items[invoice_items['ma_hoa_don'] == order_id]['ma_hang'].tolist()
                    if items:
                        transactions.append({'items': items})

                result = analyze_market_basket(transactions, min_confidence=0.50)
                logger.info(f"Apriori regenerated: {len(result['bundles'])} bundles found")
        except Exception as e:
            logger.error(f"Apriori generation error: {e}")

        logger.info("Data refresh completed successfully")

    except Exception as e:
        logger.error(f"Error refreshing data: {e}")


def get_last_update():
    """Get timestamp of last update"""
    return _last_update


def stop_scheduler():
    """Stop the scheduler"""
    global _scheduler

    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        logger.info("Scheduler stopped")
