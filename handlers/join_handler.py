from __future__ import annotations

from typing import Any

from astrbot.api import logger


class JoinHandler:
    """Handles group join events such as welcome messages.

    处理群加入事件，如欢迎消息。
    """

    @staticmethod
    async def send_welcome(
        bot: Any,
        group_id: int,
        user_id: int,
        message: str,
        member_name: str = "",
    ) -> bool:
        """Send a welcome message to the group mentioning the new member.

        Supports ``{membername}`` placeholder which will be replaced with the
        member's display name (card / nickname / user_id fallback).

        发送欢迎消息到群，提及新成员。
        支持 ``{membername}`` 占位符，将被替换为成员的显示名称（卡片名、昵称或用户ID）。
        """
        display_name = member_name or str(user_id)
        message = message.replace("{membername}", display_name)
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
