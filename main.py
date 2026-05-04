from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from astrbot.api import logger, star
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.message_components import At, Plain

from .handlers import GroupHandler, JoinHandler, NoticeHandler
from .i18n import I18nManager

PLUGIN_BASE_DIR = Path(__file__).parent
WELCOME_MESSAGE_MAX_LEN = 200

CST = timezone(timedelta(hours=8))


@star.register(
    name="astrbot_plugin_group_keeper",
    author="SSJ-ZYJ",
    desc="A QQ group management plugin for AstrBot, designed for HTS Team.",
    version="1.0.5",
    repo="https://github.com/SSJ-ZYJ/astrbot_plugin_group_keeper",
)
class GroupKeeperPlugin(star.Star):
    """QQ Group Keeper - comprehensive group management plugin."""

    def __init__(self, context: star.Context, config: dict | None = None):
        super().__init__(context)
        self.config = config or {}
        self.data_path = star.StarTools.get_data_dir("astrbot_plugin_group_keeper")
        self.groups_path = self.data_path / "groups"
        self.groups_path.mkdir(parents=True, exist_ok=True)

        self.locale = self.config.get("locale", "zh_CN")
        self.default_mute_duration = self.config.get("default_mute_duration", 60)
        self.default_welcome_enabled = self.config.get("default_welcome_enabled", True)
        self.default_welcome_message = self.config.get("default_welcome_message", "")
        self.max_recall_count = max(1, self.config.get("max_recall_count", 10))
        self.default_admin_list = self.config.get("default_admin_list", [])
        self.default_announce_confirm_required = self.config.get(
            "default_announce_confirm_required", False
        )
        self.default_announce_pinned = self.config.get("default_announce_pinned", False)

        self.i18n = I18nManager(PLUGIN_BASE_DIR / "locales")
        self.group_handler = GroupHandler()
        self.notice_handler = NoticeHandler()
        self.join_handler = JoinHandler()

        self._group_configs: dict[str, dict] = {}

    async def initialize(self):
        """Load per-group data on plugin activation."""
        logger.info("Group Keeper plugin initialized.")

    async def terminate(self):
        """Save all per-group data on plugin deactivation."""
        for group_id, cfg in self._group_configs.items():
            self._save_group_config(group_id, cfg)
        logger.info("Group Keeper plugin terminated.")

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
        cfg.setdefault("welcome_enabled", self.default_welcome_enabled)
        cfg.setdefault("welcome_message", "")
        cfg.setdefault("admin_list", list(self.default_admin_list))
        cfg.setdefault("announcements", [])
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

    def _t(self, key: str, event: AstrMessageEvent | None = None, **kwargs) -> str:
        return self.i18n.get(key, self.locale, **kwargs)

    def _reply(self, event: AstrMessageEvent, text: str):
        event.set_result(MessageEventResult().message(text))

    def _reply_key(self, event: AstrMessageEvent, key: str, **kwargs):
        self._reply(event, self._t(key, event, **kwargs))

    def _reply_error_with_detail(
        self, event: AstrMessageEvent, key: str, detail: str, **kwargs
    ):
        base = self._t(key, event, **kwargs)
        if detail:
            self._reply(
                event, f"{base}\n{self._t('msg_error_detail', event, error=detail)}"
            )
        else:
            self._reply(event, base)

    @staticmethod
    def _get_bot(event: AstrMessageEvent):
        return getattr(event, "bot", None)

    @staticmethod
    def _is_group_chat(event: AstrMessageEvent) -> bool:
        return bool(event.get_group_id())

    async def _is_plugin_admin(self, event: AstrMessageEvent, group_id: str) -> bool:
        cfg = self._get_group_config(group_id)
        admin_list = cfg.get("admin_list", [])
        sender_id = event.get_sender_id()
        if admin_list and sender_id in admin_list:
            return True
        if admin_list:
            return await self._check_group_role(event, group_id, "admin")
        return True

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
        except Exception:
            return False

    def _extract_target_user(self, event: AstrMessageEvent) -> str | None:
        """Extract the target user ID from an At component or message text."""
        for comp in event.get_messages():
            if isinstance(comp, At):
                return str(comp.qq)
        msg_str = event.get_message_str().strip()
        numbers = re.findall(r"\b(\d{5,15})\b", msg_str)
        if numbers:
            return numbers[0]
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

    # ------------------------------------------------------------------ #
    #  Command group: /bot
    # ------------------------------------------------------------------ #

    @filter.command_group("bot")
    async def bot_group(self):
        pass

    # ---- /bot help ----

    @bot_group.command("help")
    async def cmd_help(self, event: AstrMessageEvent):
        t = self._t
        lines = [
            t("help_title", event),
            "",
            t("help_header", event),
            t("cmd_welcome", event),
            t("cmd_add_admin", event),
            t("cmd_remove_admin", event),
            t("cmd_list_admins", event),
            t("cmd_mute", event),
            t("cmd_unmute", event),
            t("cmd_global_mute", event),
            t("cmd_ban", event),
            t("cmd_recall", event),
            t("cmd_rename", event),
            t("cmd_title", event),
            t("cmd_promote", event),
            t("cmd_demote", event),
            t("cmd_set_group_name", event),
            t("cmd_announce", event),
            t("cmd_list_announcements", event),
        ]
        self._reply(event, "\n".join(lines))

    # ---- /bot welcome [on|off|message <text>] ----

    @bot_group.command("welcome")
    async def cmd_welcome(
        self, event: AstrMessageEvent, arg1: str = "", arg2: str = ""
    ):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        cfg = self._get_group_config(group_id)

        if not arg1:
            status = (
                self._t("msg_status_on", event)
                if cfg["welcome_enabled"]
                else self._t("msg_status_off", event)
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
            new_msg = arg2.strip()
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

    # ---- /bot add_admin <QQå? ----

    @bot_group.command("add_admin")
    async def cmd_add_admin(self, event: AstrMessageEvent, qq: str = ""):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return
        if not qq or not qq.isdigit():
            qq = self._extract_target_user(event) or ""
        if not qq or not qq.isdigit():
            self._reply_key(event, "msg_parameter_error")
            return

        cfg = self._get_group_config(group_id)
        if qq in cfg["admin_list"]:
            self._reply_key(event, "msg_admin_already_exists", qq=qq)
            return
        cfg["admin_list"].append(qq)
        self._save_group_config(group_id, cfg)
        self._reply_key(event, "msg_admin_added", qq=qq)

    # ---- /bot remove_admin <QQå? ----

    @bot_group.command("remove_admin")
    async def cmd_remove_admin(self, event: AstrMessageEvent, qq: str = ""):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return
        if not qq or not qq.isdigit():
            qq = self._extract_target_user(event) or ""
        if not qq or not qq.isdigit():
            self._reply_key(event, "msg_parameter_error")
            return

        cfg = self._get_group_config(group_id)
        if qq not in cfg["admin_list"]:
            self._reply_key(event, "msg_admin_not_exists", qq=qq)
            return
        cfg["admin_list"].remove(qq)
        self._save_group_config(group_id, cfg)
        self._reply_key(event, "msg_admin_removed", qq=qq)

    # ---- /bot list_admins ----

    @bot_group.command("list_admins")
    async def cmd_list_admins(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        cfg = self._get_group_config(group_id)
        admin_list = cfg.get("admin_list", [])
        if not admin_list:
            self._reply_key(event, "msg_no_admins")
            return
        admin_str = "\n".join(f"- {a}" for a in admin_list)
        self._reply_key(event, "msg_admins_list", list=admin_str)

    # ---- /bot mute <QQå? [seconds] ----

    @bot_group.command("mute")
    async def cmd_mute(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
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
            event, exclude=target, default=self.default_mute_duration
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

    # ---- /bot unmute <QQå? ----

    @bot_group.command("unmute")
    async def cmd_unmute(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
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

    @bot_group.command("global_mute")
    async def cmd_global_mute(self, event: AstrMessageEvent, status: str = ""):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
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

    # ---- /bot ban <QQå? ----

    @bot_group.command("ban")
    async def cmd_ban(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
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

        success = await self.group_handler.ban(bot, int(group_id), int(target))
        if success:
            self._reply_key(event, "msg_ban_success", user=target)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot recall <QQå? [count] ----

    @bot_group.command("recall")
    async def cmd_recall(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
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
        count = max(1, min(count, self.max_recall_count))

        recalled = 0
        try:
            history = await bot.call_action(
                "get_group_msg_history", group_id=int(group_id), count=count * 3
            )
            messages = history.get("messages", []) if history else []
            for msg in messages:
                sender = msg.get("sender", {})
                if str(sender.get("user_id", "")) == target:
                    ok = await self.group_handler.recall(bot, msg["message_id"])
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

    # ---- /bot rename <QQå? <name> ----

    @bot_group.command("rename")
    async def cmd_rename(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
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

    # ---- /bot title <QQå? <title> ----

    @bot_group.command("title")
    async def cmd_title(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()

        is_owner = await self._check_group_role(event, group_id, "owner")
        if not is_owner:
            self._reply_key(event, "msg_owner_required")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
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

    # ---- /bot promote <QQå? ----

    @bot_group.command("promote")
    async def cmd_promote(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()

        is_owner = await self._check_group_role(event, group_id, "owner")
        if not is_owner:
            self._reply_key(event, "msg_owner_required")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
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

    # ---- /bot demote <QQå? ----

    @bot_group.command("demote")
    async def cmd_demote(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()

        is_owner = await self._check_group_role(event, group_id, "owner")
        if not is_owner:
            self._reply_key(event, "msg_owner_required")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
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

    @bot_group.command("set_group_name")
    async def cmd_set_group_name(self, event: AstrMessageEvent, *, name: str = ""):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        if not name:
            msg_str = event.get_message_str().strip()
            rest = re.sub(
                r"^/?bot\s+set_group_name\s*", "", msg_str, flags=re.IGNORECASE
            ).strip()
            quote_match = re.match(r'^"(.*)"$', rest) or re.match(r"^'(.*)'$", rest)
            if quote_match:
                name = quote_match.group(1)
            else:
                name = rest

        name = name.strip()
        if not name:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.set_group_name(bot, int(group_id), name)
        if success:
            self._reply_key(event, "msg_group_name_success", name=name)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot announce <content> ----

    @bot_group.command("announce")
    async def cmd_announce(self, event: AstrMessageEvent, *, content: str = ""):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()
        if not await self._is_plugin_admin(event, group_id):
            self._reply_key(event, "msg_no_permission")
            return

        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
            return

        if not content:
            msg_str = event.get_message_str().strip()
            content = re.sub(
                r"^/?bot\s+announce\s*", "", msg_str, flags=re.IGNORECASE
            ).strip()

        content = content.strip()
        if not content:
            self._reply_key(event, "msg_parameter_error")
            return

        confirm_required = self.default_announce_confirm_required
        pinned = self.default_announce_pinned
        success = await self.notice_handler.publish(
            bot, int(group_id), content, confirm_required, pinned
        )
        if success:
            cfg = self._get_group_config(group_id)
            sender_name = event.get_sender_name() or event.get_sender_id()
            cfg["announcements"] = self.notice_handler.add_to_local(
                cfg.get("announcements", []), content, sender_name
            )
            self._save_group_config(group_id, cfg)
            self._reply_key(event, "msg_announce_success")
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot list_announcements ----

    @bot_group.command("list_announcements")
    async def cmd_list_announcements(self, event: AstrMessageEvent):
        if not self._is_group_chat(event):
            self._reply_key(event, "msg_not_in_group")
            return
        group_id = event.get_group_id()

        bot = self._get_bot(event)
        remote_announcements = []
        if bot is not None:
            remote_announcements = await self.notice_handler.get_from_group(
                bot, int(group_id)
            )

        if remote_announcements:
            lines = [self._t("msg_announcement_list_header", event)]
            for i, ann in enumerate(remote_announcements[:10], 1):
                ts = ann.get("time", ann.get("timestamp", 0))
                dt = (
                    datetime.fromtimestamp(ts, tz=CST).strftime("%Y-%m-%d %H:%M")
                    if ts
                    else "N/A"
                )
                content = ann.get("content", "")
                pinned_flag = ann.get("pinned", False)
                confirm_flag = ann.get("confirm_required", False)
                tags = []
                if pinned_flag:
                    tags.append(self._t("msg_tag_pinned", event))
                if confirm_flag:
                    tags.append(self._t("msg_tag_confirm", event))
                tag_str = f" [{', '.join(tags)}]" if tags else ""
                lines.append(f"{i}. [{dt}]{tag_str} {content}")
            self._reply(event, "\n".join(lines))
            return

        cfg = self._get_group_config(group_id)
        announcements = cfg.get("announcements", [])
        if not announcements:
            self._reply_key(event, "msg_no_announcements")
            return

        lines = [self._t("msg_announcement_list_header", event)]
        for i, ann in enumerate(announcements[-10:], 1):
            ts = ann.get("timestamp", 0)
            dt = (
                datetime.fromtimestamp(ts, tz=CST).strftime("%Y-%m-%d %H:%M")
                if ts
                else "N/A"
            )
            sender = ann.get("sender", "Unknown")
            content = ann.get("content", "")
            lines.append(f"{i}. [{dt}] {sender}: {content}")
        self._reply(event, "\n".join(lines))

    # ------------------------------------------------------------------ #
    #  Event listener for member join / leave
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
        if not group_id:
            return

        cfg = self._get_group_config(group_id)

        if notice_type == "group_increase" and cfg.get("welcome_enabled", False):
            user_id = str(raw.get("user_id", ""))
            if not user_id:
                return
            custom_msg = cfg.get("welcome_message", "")
            if not custom_msg:
                custom_msg = self.default_welcome_message
            if not custom_msg:
                custom_msg = self._t("welcome_message", event)
            await self.join_handler.send_welcome(
                bot, int(group_id), int(user_id), custom_msg
            )

    # ------------------------------------------------------------------ #
    #  Text extraction helpers
    # ------------------------------------------------------------------ #

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
