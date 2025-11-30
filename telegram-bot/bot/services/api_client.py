"""API client for communicating with backend."""
import os
import httpx
from typing import Optional, Dict, Any


class APIClient:
    """Client for backend API requests."""

    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def get_participant_by_telegram_id(
        self, telegram_user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get participant by Telegram user ID."""
        try:
            response = await self.client.get(
                f"/api/v1/participants",
                params={"telegram_user_id": telegram_user_id}
            )
            if response.status_code == 200:
                participants = response.json()
                return participants[0] if participants else None
            return None
        except Exception as e:
            print(f"Error fetching participant: {e}")
            return None

    async def create_participant(
        self,
        ton_wallet_address: str,
        telegram_user_id: int,
        username: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new participant."""
        try:
            response = await self.client.post(
                "/api/v1/participants",
                json={
                    "ton_wallet_address": ton_wallet_address,
                    "telegram_user_id": telegram_user_id,
                    "username": username,
                }
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error creating participant: {e}")
            return None

    async def get_participant_stats(
        self, participant_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get participant statistics."""
        try:
            response = await self.client.get(
                f"/api/v1/participants/{participant_id}"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
