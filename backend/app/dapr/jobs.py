"""
Dapr Jobs API Client
Schedules and manages jobs using Dapr Jobs API for exact-time reminders
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class DaprJobsClient:
    """Client for Dapr Jobs API"""

    def __init__(self, dapr_http_port: int = 3500):
        self.dapr_http_port = dapr_http_port
        self.base_url = f"http://localhost:{dapr_http_port}"

    async def schedule_job(
        self, job_name: str, due_time: datetime, data: Dict[str, Any], period: Optional[str] = None
    ) -> bool:
        """
        Schedule a job using Dapr Jobs API

        Args:
            job_name: Unique job identifier
            due_time: When to trigger the job
            data: Payload to send to callback
            period: Optional repeat period (e.g., "R5/PT1H" for 5 repeats every hour)

        Returns:
            True if successful
        """
        url = f"{self.base_url}/v1.0-alpha1/jobs/{job_name}"

        payload = {"dueTime": due_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "data": data}

        if period:
            payload["period"] = period

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                logger.info(f"Scheduled job {job_name} for {due_time}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to schedule job {job_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error scheduling job {job_name}: {e}")
            return False

    async def cancel_job(self, job_name: str) -> bool:
        """
        Cancel a scheduled job

        Args:
            job_name: Job identifier to cancel

        Returns:
            True if successful
        """
        url = f"{self.base_url}/v1.0-alpha1/jobs/{job_name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, timeout=10.0)
                response.raise_for_status()
                logger.info(f"Cancelled job {job_name}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to cancel job {job_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error cancelling job {job_name}: {e}")
            return False

    async def get_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Get job details

        Args:
            job_name: Job identifier

        Returns:
            Job details or None if not found
        """
        url = f"{self.base_url}/v1.0-alpha1/jobs/{job_name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get job {job_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting job {job_name}: {e}")
            return None


# Global instance
_jobs_client: Optional[DaprJobsClient] = None


def get_jobs_client() -> DaprJobsClient:
    """Get or create the global Dapr Jobs client instance"""
    global _jobs_client
    if _jobs_client is None:
        _jobs_client = DaprJobsClient()
    return _jobs_client
