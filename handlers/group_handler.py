from __future__ import annotations

from typing import TYPE_CHECKING, Any

from astrbot.api import logger

if TYPE_CHECKING:
    pass

DEFAULT_MUTE_DURATION = 60


class GroupHandler:
    """Handles QQ group management operations via OneBot API."""

    @staticmethod
    async def _call_api(bot: Any, action: str, **params) -> dict | None:
        """Call a OneBot API action and return the response.

        Returns the response dict on success, or None on failure.
        Use this for read operations where you need the return value.
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

        Use this for write/mutation operations (mute, ban, promote, etc.)
        where the API may return None on success.
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

        Returns (result, "") on success, or (None, error_message) on failure.
        Use this for read operations where you need the return value.
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

        Returns (True, "") on success, or (False, error_message) on failure.
        Use this for write/mutation operations where the API may return None on success.
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

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The target user ID.
            duration: Mute duration in seconds. 0 to unmute.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(
            bot, "set_group_ban", group_id=group_id, user_id=user_id, duration=duration
        )

    async def unmute(self, bot: Any, group_id: int, user_id: int) -> bool:
        """Unmute a user in the group (duration=0)."""
        return await self.mute(bot, group_id, user_id, duration=0)

    async def global_mute(self, bot: Any, group_id: int, enable: bool) -> bool:
        """Enable or disable whole-group mute.

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            enable: True to enable, False to disable.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(
            bot, "set_group_whole_ban", group_id=group_id, enable=enable
        )

    async def ban(self, bot: Any, group_id: int, user_id: int) -> bool:
        """Kick and ban a user from the group (reject future join requests).

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The target user ID.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(
            bot,
            "set_group_kick",
            group_id=group_id,
            user_id=user_id,
            reject_add_request=True,
        )

    async def recall(self, bot: Any, message_id: int) -> bool:
        """Recall (delete) a message.

        Args:
            bot: The CQHttp bot instance.
            message_id: The message ID to recall.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(bot, "delete_msg", message_id=message_id)

    async def rename(
        self, bot: Any, group_id: int, user_id: int, new_name: str
    ) -> bool:
        """Change a user's group card (nickname).

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The target user ID.
            new_name: The new nickname.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(
            bot, "set_group_card", group_id=group_id, user_id=user_id, card=new_name
        )

    async def set_title(
        self, bot: Any, group_id: int, user_id: int, title: str
    ) -> tuple[bool, str]:
        """Set a user's special title (requires bot to be group owner).

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The target user ID.
            title: The title text.

        Returns:
            (True, "") on success, (False, error_message) on failure.
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

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The target user ID.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(
            bot, "set_group_admin", group_id=group_id, user_id=user_id, enable=True
        )

    async def demote(self, bot: Any, group_id: int, user_id: int) -> bool:
        """Remove a user from group admin.

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The target user ID.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(
            bot, "set_group_admin", group_id=group_id, user_id=user_id, enable=False
        )

    async def set_group_name(self, bot: Any, group_id: int, name: str) -> bool:
        """Change the group name.

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            name: The new group name.

        Returns:
            True if successful, False otherwise.
        """
        return await self._execute_api(
            bot, "set_group_name", group_id=group_id, group_name=name
        )

    async def get_member_info(
        self, bot: Any, group_id: int, user_id: int
    ) -> dict | None:
        """Get group member information.

        Args:
            bot: The CQHttp bot instance.
            group_id: The group ID.
            user_id: The target user ID.

        Returns:
            Member info dict, or None on failure.
        """
        return await self._call_api(
            bot,
            "get_group_member_info",
            group_id=group_id,
            user_id=user_id,
            no_cache=True,
        )
