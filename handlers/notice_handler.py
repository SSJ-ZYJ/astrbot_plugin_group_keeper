from __future__ import annotations

import time
from typing import Any

from astrbot.api import logger


class NoticeHandler:
    """Handles group announcement operations."""

    @staticmethod
    async def publish(bot: Any, group_id: int, content: str) -> bool:
        """Publish a group announcement (notice).

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            content: The announcement content.

        Returns:
            True if successful, False otherwise.
        """
        try:
            await bot.call_action(
                "_send_group_notice", group_id=group_id, content=content
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish announcement to group {group_id}: {e}")
            return False

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
