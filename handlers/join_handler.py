from __future__ import annotations

from typing import Any

from astrbot.api import logger


class JoinHandler:
    """Handles group join events such as welcome messages.

    处理群加入事件，如欢迎消息。
    """

    @staticmethod
    async def send_welcome(bot: Any, group_id: int, user_id: int, message: str) -> bool:
        """Send a welcome message to the group mentioning the new member.

        发送欢迎消息到群，@新成员。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            user_id: The new member's user ID.
                     新成员的用户ID。
            message: The welcome message text (plain text, At is prepended).
                     欢迎消息文本（纯文本，会自动添加@）。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
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
