"""Background tasks for invoice processing"""

from typing import Any
import logging

logger = logging.getLogger(__name__)

# For now, we'll use a simple mock implementation
# In production, this would be connected to Redis/RabbitMQ


class MockTask:
    """Mock task class for development"""

    def delay(self, *args, **kwargs):
        """Mock delay method"""
        logger.info(f"Mock task called with args: {args}, kwargs: {kwargs}")
        return self

    def apply_async(self, *args, **kwargs):
        """Mock apply_async method"""
        logger.info(f"Mock task apply_async called with args: {args}, kwargs: {kwargs}")
        return self


def _submit_invoice_task(invoice_id: str, company_id: str) -> Any:
    """Submit invoice to KSeF - mock implementation"""
    logger.info(f"Submitting invoice {invoice_id} for company {company_id}")
    # In production, this would submit to KSeF API
    return {"status": "submitted", "invoice_id": invoice_id}


# Create mock task instances
submit_invoice_task = MockTask()
