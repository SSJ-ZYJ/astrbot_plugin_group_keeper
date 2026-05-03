from __future__ import annotations

from typing import Any

from astrbot.api import logger


class JoinHandler:
    """Handles group join events such as welcome messages."""

    @staticmethod
    async def send_welcome(bot: Any, group_id: int, user_id: int, message: str) -> bool:
        """Send a welcome message to the group mentioning the new member.

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The new member's user ID.
            message: The welcome message text (plain text, At is prepended).

        Returns:
            True if successful, False otherwise.
        """
        try:
            msg_segments = [
                {"type": "at", "data": {"qq": str(user_id)}},
                {"type": "text", "data": {"text": f" {message}"}},
            ]
            await bot.call_action(
                "send_group_msg", group_id=int(group_id), message=msg_segments
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send welcome message to group {group_id}: {e}")
            return False
