from __future__ import annotations

import time
from typing import Any

from astrbot.api import logger


class NoticeHandler:
    """Handles group announcement operations.

    处理群公告操作。
    """

    @staticmethod
    async def publish(
        bot: Any,
        group_id: int,
        content: str,
        confirm_required: bool = False,
        pinned: bool = False,
    ) -> bool:
        """Publish a group announcement (notice).

        发布群公告。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            content: The announcement content.
                     公告内容。
            confirm_required: Whether group members need to confirm.
                             是否需要群成员确认。
            pinned: Whether the announcement is pinned.
                    是否置顶。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        try:
            params: dict[str, Any] = {
                "group_id": group_id,
                "content": content,
                "confirm_required": confirm_required,
                "pinned": pinned,
            }
            await bot.call_action("_send_group_notice", **params)
            return True
        except Exception as e:
            logger.error(f"Failed to publish announcement to group {group_id}: {e}")
            return False

    @staticmethod
    def add_to_local(
        announcements: list[dict], content: str, sender_name: str
    ) -> list[dict]:
        """Add an announcement to the local storage list.

        将公告添加到本地存储列表。

        Args:
            announcements: The existing announcements list.
                           现有的公告列表。
            content: The announcement content.
                     公告内容。
            sender_name: The name of the sender.
                         发送者名称。

        Returns:
            Updated announcements list.
            更新后的公告列表。
        """
        announcements.append(
            {
                "content": content,
                "sender": sender_name,
                "timestamp": int(time.time()),
            }
        )
        return announcements
