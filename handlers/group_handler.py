from __future__ import annotations

from typing import TYPE_CHECKING, Any

from astrbot.api import logger

if TYPE_CHECKING:
    pass

DEFAULT_MUTE_DURATION = 60


class GroupHandler:
    """Handles QQ group management operations via OneBot API.

    通过 OneBot API 处理QQ群管理操作。
    """

    @staticmethod
    async def _call_api(bot: Any, action: str, **params) -> dict | None:
        """Call a OneBot API action and return the response.

        调用 OneBot API 并返回响应。

        Returns:
            The response dict on success, or None on failure.
            成功返回响应字典，失败返回 None。

        Note:
            Use this for read operations where you need the return value.
            用于需要返回值的读取操作。
        """
        try:
            result = await bot.call_action(action, **params)
            return result
        except Exception as e:
            logger.error(f"OneBot API call '{action}' failed: {e}")
            return None

    @staticmethod
    async def _execute_api(bot: Any, action: str, **params) -> bool:
        """Execute a OneBot API action. Returns True if no exception was raised.

        执行 OneBot API 操作，无异常返回 True。

        Note:
            Use this for write/mutation operations (mute, ban, promote, etc.)
            where the API may return None on success.
            用于写入/修改操作（禁言、封禁、提升管理员等），此类API成功时可能返回 None。
        """
        try:
            await bot.call_action(action, **params)
            return True
        except Exception as e:
            logger.error(f"OneBot API call '{action}' failed: {e}")
            return False

    @staticmethod
    async def _call_api_with_error(
        bot: Any, action: str, **params
    ) -> tuple[dict | None, str]:
        """Call a OneBot API action and return (result, error_msg).

        调用 OneBot API 并返回 (结果, 错误信息)。

        Returns:
            (result, "") on success, or (None, error_message) on failure.
            成功返回 (结果, "")，失败返回 (None, 错误信息)。

        Note:
            Use this for read operations where you need the return value.
            用于需要返回值的读取操作。
        """
        try:
            result = await bot.call_action(action, **params)
            return result, ""
        except Exception as e:
            error_msg = str(e)
            logger.error(f"OneBot API call '{action}' failed: {error_msg}")
            return None, error_msg

    @staticmethod
    async def _execute_api_with_error(
        bot: Any, action: str, **params
    ) -> tuple[bool, str]:
        """Execute a OneBot API action and return (success, error_msg).

        执行 OneBot API 操作并返回 (成功, 错误信息)。

        Returns:
            (True, "") on success, or (False, error_message) on failure.
            成功返回 (True, "")，失败返回 (False, 错误信息)。

        Note:
            Use this for write/mutation operations where the API may return None on success.
            用于写入/修改操作，此类API成功时可能返回 None。
        """
        try:
            await bot.call_action(action, **params)
            return True, ""
        except Exception as e:
            error_msg = str(e)
            logger.error(f"OneBot API call '{action}' failed: {error_msg}")
            return False, error_msg

    async def mute(
        self,
        bot: Any,
        group_id: int,
        user_id: int,
        duration: int = DEFAULT_MUTE_DURATION,
    ) -> bool:
        """Mute a user in the group.

        禁言群成员。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            user_id: The target user ID.
                     目标用户ID。
            duration: Mute duration in seconds. 0 to unmute.
                      禁言时长（秒），0表示解除禁言。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        return await self._execute_api(
            bot, "set_group_ban", group_id=group_id, user_id=user_id, duration=duration
        )

    async def unmute(self, bot: Any, group_id: int, user_id: int) -> bool:
        """Unmute a user in the group (duration=0).

        解除群成员禁言（时长=0）。
        """
        return await self.mute(bot, group_id, user_id, duration=0)

    async def global_mute(self, bot: Any, group_id: int, enable: bool) -> bool:
        """Enable or disable whole-group mute.

        开启或关闭全员禁言。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            enable: True to enable, False to disable.
                    True开启，False关闭。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        return await self._execute_api(
            bot, "set_group_whole_ban", group_id=group_id, enable=enable
        )

    async def recall(self, bot: Any, message_id: int) -> bool:
        """Recall (delete) a message.

        撤回消息。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            message_id: The message ID to recall.
                        要撤回的消息ID。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        return await self._execute_api(bot, "delete_msg", message_id=message_id)

    async def rename(
        self, bot: Any, group_id: int, user_id: int, new_name: str
    ) -> bool:
        """Change a user's group card (nickname).

        修改群成员昵称（群名片）。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            user_id: The target user ID.
                     目标用户ID。
            new_name: The new nickname.
                      新昵称。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        return await self._execute_api(
            bot, "set_group_card", group_id=group_id, user_id=user_id, card=new_name
        )

    async def set_title(
        self, bot: Any, group_id: int, user_id: int, title: str
    ) -> tuple[bool, str]:
        """Set a user's special title (requires bot to be group owner).

        设置群成员专属头衔（需要机器人是群主）。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            user_id: The target user ID.
                     目标用户ID。
            title: The title text.
                   头衔文本。

        Returns:
            (True, "") on success, (False, error_message) on failure.
            成功返回 (True, "")，失败返回 (False, 错误信息)。
        """
        return await self._execute_api_with_error(
            bot,
            "set_group_special_title",
            group_id=group_id,
            user_id=user_id,
            special_title=title,
            duration=-1,
        )

    async def promote(self, bot: Any, group_id: int, user_id: int) -> bool:
        """Set a user as group admin.

        设置群成员为管理员。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            user_id: The target user ID.
                     目标用户ID。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        return await self._execute_api(
            bot, "set_group_admin", group_id=group_id, user_id=user_id, enable=True
        )

    async def demote(self, bot: Any, group_id: int, user_id: int) -> bool:
        """Remove a user from group admin.

        移除群成员的管理员权限。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            user_id: The target user ID.
                     目标用户ID。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        return await self._execute_api(
            bot, "set_group_admin", group_id=group_id, user_id=user_id, enable=False
        )

    async def set_group_name(self, bot: Any, group_id: int, name: str) -> bool:
        """Change the group name.

        修改群名称。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            name: The new group name.
                  新群名称。

        Returns:
            True if successful, False otherwise.
            成功返回 True，失败返回 False。
        """
        return await self._execute_api(
            bot, "set_group_name", group_id=group_id, group_name=name
        )

    async def get_member_info(
        self, bot: Any, group_id: int, user_id: int
    ) -> dict | None:
        """Get group member information.

        获取群成员信息。

        Args:
            bot: The CQHttp bot instance.
                 CQHttp 机器人实例。
            group_id: The group ID.
                      群ID。
            user_id: The target user ID.
                     目标用户ID。

        Returns:
            Member info dict, or None on failure.
            成员信息字典，失败返回 None。
        """
        return await self._call_api(
            bot,
            "get_group_member_info",
            group_id=group_id,
            user_id=user_id,
            no_cache=True,
        )
