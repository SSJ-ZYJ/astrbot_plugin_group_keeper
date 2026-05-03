from __future__ import annotations

import time
from typing import Any

from astrbot.api import logger


class NoticeHandler:
    """Handles group announcement operations."""

    @staticmethod
    async def publish(
        bot: Any,
        group_id: int,
        content: str,
        confirm_required: bool = False,
        pinned: bool = False,
    ) -> bool:
        """Publish a group announcement (notice).

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            content: The announcement content.
            confirm_required: Whether group members need to confirm.
            pinned: Whether the announcement is pinned.

        Returns:
            True if successful, False otherwise.
        """
        try:
            params: dict[str, Any] = {
                "group_id": group_id,
                "content": content,
            }
            if confirm_required:
                params["confirm_required"] = True
            if pinned:
                params["pinned"] = True
            await bot.call_action("_send_group_notice", **params)
            return True
        except Exception as e:
            logger.error(f"Failed to publish announcement to group {group_id}: {e}")
            return False

    @staticmethod
    async def get_from_group(bot: Any, group_id: int) -> list[dict]:
        """Fetch announcements from the QQ group via API.

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.

        Returns:
            List of announcement dicts, or empty list on failure.
        """
        try:
            result = await bot.call_action("_get_group_notice", group_id=group_id)
            if result is None:
                return []
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return result.get("data", result.get("notices", []))
            return []
        except Exception as e:
            logger.error(f"Failed to get announcements from group {group_id}: {e}")
            return []

    @staticmethod
    def add_to_local(
        announcements: list[dict], content: str, sender_name: str
    ) -> list[dict]:
        """Add an announcement to the local storage list.

        Args:
            announcements: The existing announcements list.
            content: The announcement content.
            sender_name: The name of the sender.

        Returns:
            Updated announcements list.
        """
        announcements.append(
            {
                "content": content,
                "sender": sender_name,
                "timestamp": int(time.time()),
            }
        )
        return announcements
