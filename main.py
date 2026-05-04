from __future__ import annotations

import json
import re

from astrbot.api import AstrBotConfig, logger, star
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.message_components import At, Plain

from .handlers import GroupHandler, JoinHandler
from .i18n import I18nManager

WELCOME_MESSAGE_MAX_LEN = 200


@star.register(
    name="astrbot_plugin_group_keeper",
    author="SSJ-ZYJ",
    desc="BotKeeper - A QQ group management plugin for AstrBot, designed for HTS Team.",
    version="1.0.16",
    repo="https://github.com/SSJ-ZYJ/astrbot_plugin_group_keeper",
)
class GroupKeeperPlugin(star.Star):
    """BotKeeper - Group Control Assistant - comprehensive group management plugin.

    群控助手 - 综合群管理插件。
    """

    def __init__(self, context: star.Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.data_path = star.StarTools.get_data_dir("astrbot_plugin_group_keeper")
        self.groups_path = self.data_path / "groups"
        self.groups_path.mkdir(parents=True, exist_ok=True)

        self.i18n = I18nManager()
        self.group_handler = GroupHandler()
        self.join_handler = JoinHandler()

        self._group_configs: dict[str, dict] = {}

    async def initialize(self):
        """Load per-group data on plugin activation."""
        logger.info("BotKeeper plugin initialized.")

    async def terminate(self):
        """Save all per-group data on plugin deactivation."""
        for group_id, cfg in self._group_configs.items():
            self._save_group_config(group_id, cfg)
        logger.info("BotKeeper plugin terminated.")

    # ------------------------------------------------------------------ #
    #  Metadata helpers for i18n display name switching
    # ------------------------------------------------------------------ #

    @property
    def display_name(self) -> str:
        """Return the plugin display name based on current locale."""
        return self.i18n.get_metadata("display_name", self._locale) or "BotKeeper"

    @property
    def short_desc(self) -> str:
        """Return the plugin short description based on current locale."""
        return (
            self.i18n.get_metadata("short_desc", self._locale)
            or "A QQ group management plugin for HTS Team."
        )

    @property
    def desc(self) -> str:
        """Return the plugin description based on current locale."""
        return (
            self.i18n.get_metadata("desc", self._locale)
            or "A QQ group management plugin for AstrBot, designed for HTS Team."
        )

    # ------------------------------------------------------------------ #
    #  Data persistence
    # ------------------------------------------------------------------ #

    def _get_group_config(self, group_id: str) -> dict:
        if group_id in self._group_configs:
            return self._group_configs[group_id]
        group_file = self.groups_path / f"group_{group_id}.json"
        if group_file.exists():
            try:
                with open(group_file, encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load group config for {group_id}: {e}")
                cfg = {}
        else:
            cfg = {}
        cfg.setdefault(
            "welcome_enabled", self.config.get("default_welcome_enabled", True)
        )
        cfg.setdefault("welcome_message", "")
        cfg.setdefault("announcements", [])
        cfg.pop("admin_list", None)
        self._group_configs[group_id] = cfg
        return cfg

    def _save_group_config(self, group_id: str, cfg: dict):
        group_file = self.groups_path / f"group_{group_id}.json"
        try:
            with open(group_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save group config for {group_id}: {e}")

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    @property
    def _locale(self) -> str:
        return self.config.get("locale", "zh_CN")

    def _t(self, key: str, **kwargs) -> str:
        return self.i18n.get(key, self._locale, **kwargs)

    def _reply(self, event: AstrMessageEvent, text: str):
        event.set_result(MessageEventResult().message(text))

    def _reply_key(self, event: AstrMessageEvent, key: str, **kwargs):
        self._reply(event, self._t(key, **kwargs))

    def _reply_error_with_detail(
        self, event: AstrMessageEvent, key: str, detail: str, **kwargs
    ):
        base = self._t(key, **kwargs)
        if detail:
            self._reply(event, f"{base}\n{self._t('msg_error_detail', error=detail)}")
        else:
            self._reply(event, base)

    @staticmethod
    def _extract_text_after_target(event: AstrMessageEvent, target: str) -> str:
        """Extract the text portion after the target user identifier.

        Handles both At-based and plain-text-based target references.
        """
        messages = event.get_messages()
        found_target = False
        text_parts = []
        for comp in messages:
            if isinstance(comp, At) and str(comp.qq) == target:
                found_target = True
                continue
            if found_target and isinstance(comp, Plain):
                text_parts.append(comp.text)
        if text_parts:
            return " ".join(text_parts).strip()

        msg_str = event.get_message_str().strip()
        parts = msg_str.split(None, 2)
        if len(parts) >= 3:
            remainder = parts[2]
            remainder = re.sub(r"^\d{5,15}\s*", "", remainder, count=1).strip()
            return remainder
        return ""

    @staticmethod
    def _get_bot(event: AstrMessageEvent):
        return getattr(event, "bot", None)

    @staticmethod
    def _is_group_chat(event: AstrMessageEvent) -> bool:
        return bool(event.get_group_id())

    def _is_group_allowed(self, group_id: str) -> bool:
        """Check if the group is in the whitelist (if whitelist is enabled).

        Returns:
            True if the group is allowed to use plugin features.
        """
        whitelist_enabled = self.config.get("whitelist_enabled", False)
        if not whitelist_enabled:
            return True
        whitelist = self.config.get("group_whitelist", [])
        return str(group_id) in [str(g) for g in whitelist]

    async def _is_plugin_admin(self, event: AstrMessageEvent, group_id: str) -> bool:
        """Check if the sender is a real group owner or admin."""
        return await self._check_group_role(event, group_id, "admin")

    @staticmethod
    async def _check_group_role(
        event: AstrMessageEvent, group_id: str, required_role: str
    ) -> bool:
        """Check if the sender has the required role in the QQ group.

        Args:
            required_role: "owner" or "admin".

        Returns:
            True if the sender meets the requirement.
        """
        bot = getattr(event, "bot", None)
        if bot is None:
            return False
        try:
            info = await bot.call_action(
                "get_group_member_info",
                group_id=int(group_id),
                user_id=int(event.get_sender_id()),
                no_cache=True,
            )
            role = info.get("role", "member")
            if required_role == "owner":
                return role == "owner"
            if required_role == "admin":
                return role in ("owner", "admin")
            return True
        except Exception as e:
            logger.warning(
                f"Failed to check group role for {event.get_sender_id()}: {e}"
            )
            return False

    @staticmethod
    async def _check_bot_role(
        event: AstrMessageEvent, group_id: str, required_role: str
    ) -> bool:
        """Check if the bot itself has the required role in the QQ group.

        Args:
            required_role: "owner" or "admin".

        Returns:
            True if the bot meets the requirement.
        """
        bot = getattr(event, "bot", None)
        if bot is None:
            return False
        try:
            info = await bot.call_action(
                "get_group_member_info",
                group_id=int(group_id),
                user_id=int(event.get_self_id()),
                no_cache=True,
            )
            role = info.get("role", "member")
            if required_role == "owner":
                return role == "owner"
            if required_role == "admin":
                return role in ("owner", "admin")
            return True
        except Exception as e:
            logger.warning(f"Failed to check bot role in group {group_id}: {e}")
            return False

    def _extract_target_user(self, event: AstrMessageEvent) -> str | None:
        """Extract the target user ID from an At component or message text."""
        self_id = str(event.get_self_id())
        for comp in event.get_messages():
            if isinstance(comp, At):
                qq = str(comp.qq)
                if qq != self_id and qq != "all":
                    return qq
        msg_str = event.get_message_str().strip()
        numbers = re.findall(r"\b(\d{5,15})\b", msg_str)
        for num in numbers:
            if num != self_id:
                return num
        return None

    def _parse_int_from_text(
        self, event: AstrMessageEvent, exclude: str = "", default: int = 0
    ) -> int:
        """Parse the first integer from message text that is not excluded."""
        msg_str = event.get_message_str().strip()
        for match in re.finditer(r"\b(\d+)\b", msg_str):
            val = match.group(1)
            if val != exclude:
                return int(val)
        return default

    def _strip_command_prefix(self, event: AstrMessageEvent, *cmd_names: str) -> str:
        """Strip command prefix from message text, supporting multiple command name variants."""
        msg_str = event.get_message_str().strip()
        names_pattern = "|".join(re.escape(n) for n in cmd_names)
        pattern = rf"^/?bot\s+({names_pattern})\s*"
        return re.sub(pattern, "", msg_str, flags=re.IGNORECASE).strip()

    @staticmethod
    def _strip_quotes(text: str) -> str:
        """Strip matching surrounding quotes (double or single) from text and trim whitespace.

        ``"hello world"`` -> ``hello world``
        ``'hello world'`` -> ``hello world``
        ``hello``         -> ``hello``
        """
        text = text.strip()
        if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
            return text[1:-1].strip()
        if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
            return text[1:-1].strip()
        return text

    # ------------------------------------------------------------------ #
    #  Command group: /bot
    # ------------------------------------------------------------------ #

    @filter.command_group("bot")
    async def bot_group(self):
        pass

    # ---- /bot help ----

    @bot_group.command("help", alias={"帮助"})
    async def cmd_help(self, event: AstrMessageEvent):
        lines = [
            self._t("help_title"),
            "",
            self._t("help_header"),
            self._t("cmd_welcome"),
            self._t("cmd_mute"),
            self._t("cmd_unmute"),
            self._t("cmd_global_mute"),
            self._t("cmd_recall"),
            self._t("cmd_rename"),
            self._t("cmd_title"),
            self._t("cmd_promote"),
            self._t("cmd_demote"),
            self._t("cmd_set_group_name"),
        ]
        self._reply(event, "\n".join(lines))

    # ---- /bot welcome [on|off|message <text>] ----

    @bot_group.command("welcome", alias={"欢迎"})
    async def cmd_welcome(
        self, event: AstrMessageEvent, arg1: str = "", arg2: str = ""
    ):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        cfg = self._get_group_config(group_id)

        if not arg1:
            status = (
                self._t("msg_status_on")
                if cfg["welcome_enabled"]
                else self._t("msg_status_off")
            )
            self._reply_key(event, "msg_welcome_status", status=status)
            return

        if arg1.lower() == "on":
            cfg["welcome_enabled"] = True
            self._save_group_config(group_id, cfg)
            self._reply_key(event, "msg_welcome_enabled")
        elif arg1.lower() == "off":
            cfg["welcome_enabled"] = False
            self._save_group_config(group_id, cfg)
            self._reply_key(event, "msg_welcome_disabled")
        elif arg1.lower() == "message":
            new_msg = self._strip_command_prefix(event, "welcome", "欢迎")
            new_msg = re.sub(r"^(message)\s*", "", new_msg, flags=re.IGNORECASE).strip()
            if not new_msg:
                self._reply_key(event, "msg_parameter_error")
                return
            if len(new_msg) > WELCOME_MESSAGE_MAX_LEN:
                self._reply_key(event, "msg_welcome_message_too_long")
                return
            cfg["welcome_message"] = new_msg
            self._save_group_config(group_id, cfg)
            self._reply_key(event, "msg_welcome_message_set")
        else:
            self._reply_key(event, "msg_parameter_error")

    # ---- /bot mute <QQ> [seconds] ----

    @bot_group.command("mute", alias={"禁言"})
    async def cmd_mute(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return

        duration = self._parse_int_from_text(
            event,
            exclude=target,
            default=self.config.get("default_mute_duration", 60),
        )
        success = await self.group_handler.mute(
            bot, int(group_id), int(target), duration
        )
        if success:
            self._reply_key(
                event, "msg_mute_success", user=target, duration=f"{duration}s"
            )
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot unmute <QQ> ----

    @bot_group.command("unmute", alias={"解禁"})
    async def cmd_unmute(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.unmute(bot, int(group_id), int(target))
        if success:
            self._reply_key(event, "msg_unmute_success", user=target)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot global_mute on|off ----

    @bot_group.command("global_mute", alias={"全员禁言"})
    async def cmd_global_mute(self, event: AstrMessageEvent, status: str = ""):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        if not status:
            self._reply_key(event, "msg_parameter_error")
            return
        if status.lower() == "on":
            enable = True
        elif status.lower() == "off":
            enable = False
        else:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.global_mute(bot, int(group_id), enable)
        if success:
            key = "msg_global_mute_enabled" if enable else "msg_global_mute_disabled"
            self._reply_key(event, key)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot recall <QQ> [count] ----

    @bot_group.command("recall", alias={"撤回"})
    async def cmd_recall(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return

        count = self._parse_int_from_text(event, exclude=target, default=1)
        count = max(1, min(count, self.config.get("max_recall_count", 10)))

        recalled = 0
        try:
            history = await bot.call_action(
                "get_group_msg_history", group_id=int(group_id), count=count * 3
            )
            messages = history.get("messages", []) if history else []
            for msg in messages:
                sender = msg.get("sender", {})
                if str(sender.get("user_id", "")) == target:
                    ok = await self.group_handler.recall(bot, int(msg["message_id"]))
                    if ok:
                        recalled += 1
                    if recalled >= count:
                        break
        except Exception as e:
            logger.error(f"Failed to recall messages: {e}")

        if recalled > 0:
            self._reply_key(event, "msg_recall_success", count=str(recalled))
        else:
            self._reply_key(event, "msg_recall_no_messages")

    # ---- /bot rename <QQ> <name> ----

    @bot_group.command("rename", alias={"改名"})
    async def cmd_rename(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return

        new_name = self._extract_text_after_target(event, target)
        if not new_name:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.rename(
            bot, int(group_id), int(target), new_name
        )
        if success:
            self._reply_key(event, "msg_rename_success", user=target, new_name=new_name)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot title <QQ> <title> ----

    @bot_group.command("title", alias={"头衔"})
    async def cmd_title(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        is_bot_owner = await self._check_bot_role(event, group_id, "owner")
        if not is_bot_owner:
            self._reply_key(event, "msg_owner_required")
            return

        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return

        title = self._extract_text_after_target(event, target)
        if not title:
            self._reply_key(event, "msg_parameter_error")
            return

        success, error_msg = await self.group_handler.set_title(
            bot, int(group_id), int(target), title
        )
        if success:
            self._reply_key(event, "msg_title_success", user=target, title=title)
        else:
            self._reply_error_with_detail(event, "msg_operation_failed", error_msg)

    # ---- /bot promote <QQ> ----

    @bot_group.command("promote", alias={"提升"})
    async def cmd_promote(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        is_bot_owner = await self._check_bot_role(event, group_id, "owner")
        if not is_bot_owner:
            self._reply_key(event, "msg_owner_required")
            return

        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.promote(bot, int(group_id), int(target))
        if success:
            self._reply_key(event, "msg_promote_success", user=target)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot demote <QQ> ----

    @bot_group.command("demote", alias={"降级"})
    async def cmd_demote(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        is_bot_owner = await self._check_bot_role(event, group_id, "owner")
        if not is_bot_owner:
            self._reply_key(event, "msg_owner_required")
            return

        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.demote(bot, int(group_id), int(target))
        if success:
            self._reply_key(event, "msg_demote_success", user=target)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot set_group_name <name> ----

    @bot_group.command("set_group_name", alias={"设置群名"})
    async def cmd_set_group_name(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        rest = self._strip_command_prefix(event, "set_group_name", "设置群名")
        name = self._strip_quotes(rest)

        if not name:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.set_group_name(bot, int(group_id), name)
        if success:
            self._reply_key(event, "msg_group_name_success", name=name)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ------------------------------------------------------------------ #
    #  Event listener for member join / leave and unknown commands
    # ------------------------------------------------------------------ #

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_event(self, event: AstrMessageEvent):
        """Listen for all events and handle group notice events."""
        bot = self._get_bot(event)
        if bot is None:
            return

        raw = getattr(event.message_obj, "raw_message", None)
        if raw is None:
            return

        if not isinstance(raw, dict):
            if hasattr(raw, "get"):
                try:
                    raw = dict(raw)
                except (TypeError, ValueError):
                    return
            else:
                return

        post_type = raw.get("post_type", "")
        if post_type != "notice":
            return

        notice_type = raw.get("notice_type", "")
        group_id = str(raw.get("group_id", ""))
        if not group_id or group_id == "0":
            return

        if not self._is_group_allowed(group_id):
            return

        cfg = self._get_group_config(group_id)

        if notice_type == "group_increase" and cfg.get("welcome_enabled", False):
            user_id = str(raw.get("user_id", ""))
            if not user_id:
                return
            custom_msg = cfg.get("welcome_message", "")
            if not custom_msg:
                custom_msg = self.config.get("default_welcome_message", "")
            if not custom_msg:
                custom_msg = self._t("msg_welcome_message")

            member_name = ""
            try:
                info = await bot.call_action(
                    "get_group_member_info",
                    group_id=int(group_id),
                    user_id=int(user_id),
                    no_cache=True,
                )
                member_name = info.get("card", "") or info.get("nickname", "") or ""
            except Exception as e:
                logger.debug(f"Failed to get member info for {user_id}: {e}")

            await self.join_handler.send_welcome(
                bot, int(group_id), int(user_id), custom_msg, member_name
            )

    # ------------------------------------------------------------------ #
    #  Fallback handler for unknown /bot commands
    # ------------------------------------------------------------------ #

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_unknown_command(self, event: AstrMessageEvent):
        """Handle unknown /bot commands by checking if the message starts with /bot
        but doesn't match any registered sub-command.
        """
        msg_str = event.get_message_str().strip()
        if not msg_str.startswith("/bot"):
            return

        group_id = event.get_group_id()
        if group_id and not self._is_group_allowed(group_id):
            self._reply_key(event, "msg_whitelist_not_allowed")
            return

        parts = msg_str.split(None, 1)
        if len(parts) < 2:
            # Just "/bot" with no sub-command
            self._reply_key(event, "msg_command_not_found")
            return

        sub_cmd = parts[1].split(None, 1)[0].lower()

        # List of valid sub-commands
        valid_commands = {
            "help",
            "帮助",
            "welcome",
            "欢迎",
            "mute",
            "禁言",
            "unmute",
            "解禁",
            "global_mute",
            "全员禁言",
            "recall",
            "撤回",
            "rename",
            "改名",
            "title",
            "头衔",
            "promote",
            "提升",
            "demote",
            "降级",
            "set_group_name",
            "设置群名",
        }

        if sub_cmd not in valid_commands:
            self._reply_key(event, "msg_command_not_found")
