# This file is part of astrbot_plugin_group_keeper.
# Copyright (C) 2024-2026 SSJ-ZYJ and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from astrbot.api import AstrBotConfig, logger, star
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import At, Plain, Reply
from astrbot.core.platform import MessageType

from .handlers import GroupHandler, InspectionHandler, JoinHandler, MessageHandler
from .i18n import I18nManager

PLUGIN_NAME = "astrbot_plugin_group_keeper"
PLUGIN_VERSION = "1.2.9"
PLUGIN_REPO = "https://github.com/SSJ-ZYJ/astrbot_plugin_group_keeper"
BOT_COMMAND_PREFIX = "/bot"
WELCOME_MESSAGE_MAX_LEN = 200


@dataclass(slots=True)
class GroupCommandContext:
    """Runtime context for a group command.

    群聊命令运行上下文，用于集中传递群号和 OneBot bot 对象。
    """

    group_id: str
    bot: Any


@star.register(
    name=PLUGIN_NAME,
    author="SSJ-ZYJ",
    desc="BotKeeper - A QQ group management plugin for AstrBot, designed for HTS Team.",
    version=PLUGIN_VERSION,
    repo=PLUGIN_REPO,
)
class GroupKeeperPlugin(star.Star):
    """
    BotKeeper - Group Control Assistant - comprehensive group management plugin.
    群控助手 - 综合群管理插件。
    """

    def __init__(self, context: star.Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.data_path = star.StarTools.get_data_dir(PLUGIN_NAME)
        self.groups_path = self.data_path / "groups"
        self.groups_path.mkdir(parents=True, exist_ok=True)

        self.i18n = I18nManager()
        self.group_handler = GroupHandler()
        self.join_handler = JoinHandler()
        self.inspection_handler = InspectionHandler(self.data_path)

        self._group_configs: dict[str, dict] = {}

    async def initialize(self):
        """Load plugin resources when AstrBot activates this plugin.

        当 AstrBot 激活插件时加载插件资源。
        """
        logger.info("BotKeeper plugin initialized.")

    async def terminate(self):
        """Persist cached group data when AstrBot deactivates this plugin.

        当 AstrBot 停用插件时持久化已缓存的群配置。
        """
        for group_id, cfg in self._group_configs.items():
            self._save_group_config(group_id, cfg)
        logger.info("BotKeeper plugin terminated.")

    # ------------------------------------------------------------------ #
    #  Metadata helpers for i18n display name switching
    # ------------------------------------------------------------------ #

    @property
    def display_name(self) -> str:
        """Return the plugin display name based on current locale.

        根据当前语言返回插件显示名称。
        """
        return self.i18n.get_metadata("display_name", self._locale) or "BotKeeper"

    @property
    def short_desc(self) -> str:
        """Return the plugin short description based on current locale.

        根据当前语言返回插件短描述。
        """
        return (
            self.i18n.get_metadata("short_desc", self._locale)
            or "A QQ group management plugin for HTS Team."
        )

    @property
    def desc(self) -> str:
        """Return the plugin description based on current locale.

        根据当前语言返回插件完整描述。
        """
        return (
            self.i18n.get_metadata("desc", self._locale)
            or "A QQ group management plugin for AstrBot, designed for HTS Team."
        )

    # ------------------------------------------------------------------ #
    #  Data persistence
    # ------------------------------------------------------------------ #

    def _get_group_config(self, group_id: str) -> dict:
        """Load or initialize per-group configuration.

        加载或初始化单群配置。
        """
        if group_id in self._group_configs:
            return self._group_configs[group_id]
        group_file = self.groups_path / f"group_{group_id}.json"
        if group_file.exists():
            try:
                with group_file.open(encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load group config for {group_id}: {e}")
                cfg = {}
        else:
            cfg = {}
        cfg.setdefault(
            "welcome_enabled", self.config.get("welcome_default_enabled", True)
        )
        cfg.setdefault("welcome_message", "")
        cfg.setdefault("announcements", [])
        cfg.pop("admin_list", None)
        self._group_configs[group_id] = cfg
        return cfg

    def _save_group_config(self, group_id: str, cfg: dict):
        """Persist per-group configuration under AstrBot plugin data directory.

        将单群配置保存到 AstrBot 插件数据目录，避免插件更新时覆盖数据。
        """
        group_file = self.groups_path / f"group_{group_id}.json"
        try:
            with group_file.open("w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save group config for {group_id}: {e}")

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    @property
    def _locale(self) -> str:
        """Return the configured reply locale.

        返回当前配置的回复语言。
        """
        return self.config.get("locale", "zh_CN")

    def _t(self, key: str, **kwargs) -> str:
        """Translate a bot-facing message key with runtime placeholders.

        翻译机器人可见消息，并填充运行时占位符。
        """
        return self.i18n.get(key, self._locale, **kwargs)

    def _reply(self, event: AstrMessageEvent, text: str):
        """Set a plain text reply for the current event.

        为当前事件设置纯文本回复。
        """
        event.set_result(self._prepare_long_message(event, text))

    def _reply_key(self, event: AstrMessageEvent, key: str, **kwargs):
        """Translate and set a plain text reply for the current event.

        翻译指定 key，并为当前事件设置纯文本回复。
        """
        self._reply(event, self._t(key, **kwargs))

    def _reply_error_with_detail(
        self, event: AstrMessageEvent, key: str, detail: str, **kwargs
    ):
        """Reply with a localized error message and optional detail.

        回复本地化错误消息，并在存在时附加错误详情。
        """
        base = self._t(key, **kwargs)
        if detail:
            self._reply(event, f"{base}\n{self._t('msg_error_detail', error=detail)}")
        else:
            self._reply(event, base)

    @staticmethod
    def _extract_text_after_target(event: AstrMessageEvent, target: str) -> str:
        """Extract the text portion after the target user identifier.

        Handles both At-based and plain-text-based target references.
        支持 @ 组件和纯文本 QQ 号两种目标写法。
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
        """Return the underlying OneBot client if the adapter exposes one.

        如果当前适配器暴露 OneBot 客户端，则返回该对象。
        """
        return getattr(event, "bot", None)

    @staticmethod
    def _is_group_chat(event: AstrMessageEvent) -> bool:
        """Return whether the event belongs to a group chat.

        判断当前事件是否来自群聊。
        """
        return bool(event.get_group_id())

    def _extract_raw_message_text(self, event: AstrMessageEvent) -> str:
        """Extract raw platform text used before AstrBot wake-prefix trimming.

        提取平台原始消息文本，用于避开 AstrBot 唤醒前缀裁剪后的影响。
        """
        raw_msg_obj = getattr(event.message_obj, "raw_message", None)
        if raw_msg_obj is None:
            return ""
        if hasattr(raw_msg_obj, "raw_message"):
            return str(raw_msg_obj.raw_message or "").strip()
        if isinstance(raw_msg_obj, dict):
            return str(raw_msg_obj.get("raw_message", "")).strip()
        return ""

    @staticmethod
    def _extract_plain_after_bot_at(event: AstrMessageEvent) -> str:
        """Extract plain text after an @bot component.

        提取 @机器人 组件之后的纯文本内容。
        """
        self_id = str(event.get_self_id())
        for i, msg in enumerate(event.get_messages()):
            if isinstance(msg, At) and str(msg.qq) == self_id:
                return "".join(
                    comp.text or ""
                    for comp in event.get_messages()[i + 1 :]
                    if isinstance(comp, Plain)
                ).strip()
        return ""

    def _is_bot_command_event(self, event: AstrMessageEvent) -> bool:
        """Detect direct ``/bot`` and ``@bot /bot`` commands.

        识别直接 ``/bot`` 和 ``@机器人 /bot`` 两种命令格式。
        """
        raw_text = self._extract_raw_message_text(event)
        if raw_text.startswith(BOT_COMMAND_PREFIX):
            return True
        if event.get_message_str().strip().startswith(BOT_COMMAND_PREFIX):
            return True
        return self._extract_plain_after_bot_at(event).startswith(BOT_COMMAND_PREFIX)

    def _has_activated_plugin_command(self, event: AstrMessageEvent) -> bool:
        """Return whether AstrBot matched one of this plugin's command handlers.

        判断 AstrBot 是否已匹配到本插件的某个命令处理器。
        """
        activated_handlers = event.get_extra("activated_handlers", [])
        logger.debug(
            f"[GroupKeeper] activated_handlers: {[h.handler_name for h in activated_handlers]}"
        )
        plugin_cmd_handlers = [
            h
            for h in activated_handlers
            if h.handler_module_path == self.__module__
            and h.handler_name.startswith("cmd_")
        ]
        logger.debug(
            f"[GroupKeeper] plugin_cmd_handlers: {[h.handler_name for h in plugin_cmd_handlers]}"
        )
        return bool(plugin_cmd_handlers)

    def _require_group_chat(self, event: AstrMessageEvent) -> str | None:
        """Return group_id or reply with a localized group-only error.

        返回群号；如果当前不是群聊，则回复本地化错误。
        """
        group_id = event.get_group_id()
        if not group_id:
            self._reply_key(event, "msg_not_in_group")
            return None
        return group_id

    async def _require_group_admin(
        self, event: AstrMessageEvent, group_id: str
    ) -> bool:
        """Require sender to be a real group owner/admin.

        要求发送者是当前群真实群主或管理员。
        """
        if await self._is_plugin_admin(event, group_id):
            return True
        self._reply_key(event, "msg_no_permission")
        return False

    def _require_bot(self, event: AstrMessageEvent):
        """Return OneBot client or reply with platform-not-supported.

        返回 OneBot 客户端；如果不可用，则回复平台不支持。
        """
        bot = self._get_bot(event)
        if bot is None:
            self._reply_key(event, "msg_platform_not_supported")
        return bot

    async def _require_admin_context(
        self, event: AstrMessageEvent
    ) -> GroupCommandContext | None:
        """Validate group/admin/bot preconditions for admin commands.

        校验管理员命令需要的群聊、权限和 bot 对象前置条件。
        """
        group_id = self._require_group_chat(event)
        if group_id is None:
            return None
        if not await self._require_group_admin(event, group_id):
            return None
        bot = self._require_bot(event)
        if bot is None:
            return None
        return GroupCommandContext(group_id=group_id, bot=bot)

    def _require_group_bot_context(
        self, event: AstrMessageEvent
    ) -> GroupCommandContext | None:
        """Validate group/bot preconditions without requiring sender admin.

        校验群聊和 bot 对象前置条件，但不要求发送者是管理员。
        """
        group_id = self._require_group_chat(event)
        if group_id is None:
            return None
        bot = self._require_bot(event)
        if bot is None:
            return None
        return GroupCommandContext(group_id=group_id, bot=bot)

    async def _require_bot_owner(self, event: AstrMessageEvent, group_id: str) -> bool:
        """Require the bot itself to be group owner for owner-only APIs.

        要求机器人本身是群主，用于 OneBot 仅群主可调用的接口。
        """
        if await self._check_bot_role(event, group_id, "owner"):
            return True
        self._reply_key(event, "msg_owner_required")
        return False

    def _extract_required_target_user(self, event: AstrMessageEvent) -> str | None:
        """Extract target QQ id or reply with parameter error.

        提取目标 QQ 号；如果缺失，则回复参数错误。
        """
        target = self._extract_target_user(event)
        if not target:
            self._reply_key(event, "msg_parameter_error")
            return None
        return target

    def _is_group_allowed(self, group_id: str) -> bool:
        """Check if the group is in the whitelist (if whitelist is enabled).

        检查群是否被白名单允许；未启用白名单时默认允许。

        Returns:
            True if the group is allowed to use plugin features.
            群允许使用插件功能时返回 True。
        """
        whitelist_enabled = self.config.get("whitelist_enabled", False)
        whitelist = self.config.get("group_whitelist", [])
        logger.debug(
            f"[GroupKeeper] Config: whitelist_enabled={whitelist_enabled}, group_whitelist={whitelist}"
        )
        if not whitelist_enabled:
            return True
        whitelist_str = [str(g) for g in whitelist]
        is_allowed = str(group_id) in whitelist_str
        logger.debug(
            f"[GroupKeeper] Whitelist check: group_id={group_id}, whitelist={whitelist_str}, allowed={is_allowed}"
        )
        return is_allowed

    async def _is_plugin_admin(self, event: AstrMessageEvent, group_id: str) -> bool:
        """Check if the sender is a real group owner or admin.

        检查发送者是否为真实群主或管理员。
        """
        return await self._check_group_role(event, group_id, "admin")

    @staticmethod
    async def _check_group_role(
        event: AstrMessageEvent, group_id: str, required_role: str
    ) -> bool:
        """Check if the sender has the required role in the QQ group.

        检查发送者是否满足指定群角色要求。

        Args:
            required_role: "owner" or "admin".

        Returns:
            True if the sender meets the requirement.
            发送者满足要求时返回 True。
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

        检查机器人自身是否满足指定群角色要求。

        Args:
            required_role: "owner" or "admin".

        Returns:
            True if the bot meets the requirement.
            机器人满足要求时返回 True。
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
        """Extract the target user ID from an At component or message text.

        从 @ 组件或消息文本中提取目标用户 QQ 号。
        """
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

    @staticmethod
    def _extract_replied_message_id(event: AstrMessageEvent) -> int | None:
        """Extract the message_id of the replied/quoting message.

        Returns the id of the Reply component if present, None otherwise.
        存在 Reply 组件时返回其消息 ID，否则返回 None。
        """
        for comp in event.get_messages():
            if isinstance(comp, Reply):
                try:
                    return int(comp.id)
                except (ValueError, TypeError):
                    return None
        return None

    def _parse_int_from_text(
        self, event: AstrMessageEvent, exclude: str = "", default: int = 0
    ) -> int:
        """Parse the first integer from message text that is not excluded.

        从消息文本中解析第一个未被排除的整数。
        """
        msg_str = event.get_message_str().strip()
        for match in re.finditer(r"\b(\d+)\b", msg_str):
            val = match.group(1)
            if val != exclude:
                return int(val)
        return default

    def _strip_command_prefix(self, event: AstrMessageEvent, *cmd_names: str) -> str:
        """Strip command prefix from message text, supporting command aliases.

        从消息文本中移除命令前缀，并支持多个命令别名。
        """
        msg_str = event.get_message_str().strip()
        names_pattern = "|".join(re.escape(n) for n in cmd_names)
        pattern = rf"^/?bot\s+({names_pattern})\s*"
        return re.sub(pattern, "", msg_str, flags=re.IGNORECASE).strip()

    @staticmethod
    def _strip_quotes(text: str) -> str:
        """Strip matching surrounding quotes (double or single) from text and trim whitespace.

        移除文本首尾匹配的英文单引号或双引号，并清理空白。

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

    @staticmethod
    def _join_non_empty_text(*parts: str) -> str:
        """Join non-empty text fragments with one space.

        使用单个空格拼接非空文本片段。
        """
        return " ".join(part for part in parts if part)

    @staticmethod
    def _extract_json_component_text(event: AstrMessageEvent) -> str:
        """Extract raw text embedded in Json message components.

        提取 Json 消息组件中可用于巡检匹配的文本。
        """
        json_content = ""
        for comp in event.get_messages():
            comp_type = type(comp).__name__
            if comp_type == "Json" and hasattr(comp, "data"):
                comp_data = getattr(comp, "data", {})
                if isinstance(comp_data, dict):
                    json_content += str(comp_data.get("data", ""))
                elif comp_data:
                    json_content += str(comp_data)
        return json_content

    def _get_long_message_settings(self) -> tuple[bool, int]:
        """Get long message merge settings from config.

        获取长消息合并设置。

        Returns:
            Tuple of (enabled: bool, threshold: int)
            返回 (是否启用, 字符阈值)。
        """
        enabled = self.config.get("enable_long_message_merge", True)
        threshold = self.config.get("long_message_threshold", 350)
        return enabled, threshold

    def _prepare_long_message(
        self,
        event: AstrMessageEvent,
        message: str,
    ):
        """Prepare a message for sending with automatic long message wrapping.

        If long message merge is enabled and message exceeds threshold, the
        complete text will be wrapped in a single merged-forward node.

        根据配置准备回复消息：超过阈值时将完整文本封装为单节点合并转发消息。

        Args:
            event: The message event
            message: The message text

        Returns:
            Message result object for yielding in command handlers.
            命令处理器可直接返回的消息结果对象。
        """
        enabled, threshold = self._get_long_message_settings()

        if not enabled or len(message) <= threshold:
            return event.plain_result(message)

        self_id = str(event.get_self_id())
        nodes = MessageHandler.build_merged_message(self_id, message, self.display_name)
        return event.chain_result(nodes)

    # ------------------------------------------------------------------ #
    #  Command group: /bot
    # ------------------------------------------------------------------ #

    VALID_COMMANDS = {
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
        "set_essence",
        "设精",
        "remove_essence",
        "移精",
    }

    @filter.regex(r"^.*$", priority=1)
    async def whitelist_guard(self, event: AstrMessageEvent):
        """Intercept group ``/bot`` commands before normal command handlers run.

        在普通命令处理器执行前拦截群聊 ``/bot`` 命令，用于白名单和未知命令处理。
        """
        if event.get_message_type() != MessageType.GROUP_MESSAGE:
            return

        is_bot_command = self._is_bot_command_event(event)
        logger.debug(
            f"[GroupKeeper] raw_message_str={self._extract_raw_message_text(event)}, "
            f"is_bot_command={is_bot_command}"
        )

        if not is_bot_command:
            return

        group_id = event.get_group_id()
        logger.debug(f"[GroupKeeper] whitelist_guard triggered: group_id={group_id}")

        if not self._is_group_allowed(group_id):
            logger.debug(
                f"[GroupKeeper] Group {group_id} not in whitelist, blocking silently"
            )
            event.stop_event()
            yield
            return

        if not self._has_activated_plugin_command(event):
            logger.debug("[GroupKeeper] No valid command handler found")
            yield event.plain_result(self._t("msg_command_not_found"))
            event.stop_event()

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
            self._t("cmd_set_essence"),
            self._t("cmd_remove_essence"),
        ]
        self._reply(event, "\n".join(lines))

    # ---- /bot welcome [on|off|message <text>] ----

    @bot_group.command("welcome", alias={"欢迎"})
    async def cmd_welcome(
        self, event: AstrMessageEvent, arg1: str = "", arg2: str = ""
    ):
        group_id = self._require_group_chat(event)
        if group_id is None:
            return
        if not await self._require_group_admin(event, group_id):
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
            new_msg = self._strip_quotes(new_msg)
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
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return

        target = self._extract_required_target_user(event)
        if target is None:
            return

        duration = self._parse_int_from_text(
            event,
            exclude=target,
            default=self.config.get("default_mute_duration", 30),
        )
        success = await self.group_handler.mute(
            ctx.bot, int(ctx.group_id), int(target), duration
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
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return

        target = self._extract_required_target_user(event)
        if target is None:
            return

        success = await self.group_handler.unmute(
            ctx.bot, int(ctx.group_id), int(target)
        )
        if success:
            self._reply_key(event, "msg_unmute_success", user=target)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot global_mute on|off ----

    @bot_group.command("global_mute", alias={"全员禁言"})
    async def cmd_global_mute(self, event: AstrMessageEvent, status: str = ""):
        ctx = await self._require_admin_context(event)
        if ctx is None:
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

        success = await self.group_handler.global_mute(
            ctx.bot, int(ctx.group_id), enable
        )
        if success:
            key = "msg_global_mute_enabled" if enable else "msg_global_mute_disabled"
            self._reply_key(event, key)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot recall <QQ> [count] ----

    @bot_group.command("recall", alias={"撤回"})
    async def cmd_recall(self, event: AstrMessageEvent):
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return

        target = self._extract_required_target_user(event)
        if target is None:
            return

        count = self._parse_int_from_text(event, exclude=target, default=1)
        count = max(1, min(count, self.config.get("max_recall_count", 10)))

        recalled = 0
        try:
            history = await ctx.bot.call_action(
                "get_group_msg_history", group_id=int(ctx.group_id), count=count * 3
            )
            messages = history.get("messages", []) if history else []
            for msg in messages:
                sender = msg.get("sender", {})
                if str(sender.get("user_id", "")) == target:
                    ok = await self.group_handler.recall(
                        ctx.bot, int(msg["message_id"])
                    )
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
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return

        target = self._extract_required_target_user(event)
        if target is None:
            return

        new_name = self._extract_text_after_target(event, target)
        if not new_name:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.rename(
            ctx.bot, int(ctx.group_id), int(target), new_name
        )
        if success:
            self._reply_key(event, "msg_rename_success", user=target, new_name=new_name)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot title <QQ> <title> ----

    @bot_group.command("title", alias={"头衔"})
    async def cmd_title(self, event: AstrMessageEvent):
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return

        if not await self._require_bot_owner(event, ctx.group_id):
            return

        target = self._extract_required_target_user(event)
        if target is None:
            return

        title = self._extract_text_after_target(event, target)
        if not title:
            self._reply_key(event, "msg_parameter_error")
            return

        success, error_msg = await self.group_handler.set_title(
            ctx.bot, int(ctx.group_id), int(target), title
        )
        if success:
            self._reply_key(event, "msg_title_success", user=target, title=title)
        else:
            self._reply_error_with_detail(event, "msg_operation_failed", error_msg)

    # ---- /bot promote <QQ> ----

    @bot_group.command("promote", alias={"提升"})
    async def cmd_promote(self, event: AstrMessageEvent):
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return
        if not await self._require_bot_owner(event, ctx.group_id):
            return

        target = self._extract_required_target_user(event)
        if target is None:
            return

        success = await self.group_handler.promote(
            ctx.bot, int(ctx.group_id), int(target)
        )
        if success:
            self._reply_key(event, "msg_promote_success", user=target)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot demote <QQ> ----

    @bot_group.command("demote", alias={"降级"})
    async def cmd_demote(self, event: AstrMessageEvent):
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return
        if not await self._require_bot_owner(event, ctx.group_id):
            return

        target = self._extract_required_target_user(event)
        if target is None:
            return

        success = await self.group_handler.demote(
            ctx.bot, int(ctx.group_id), int(target)
        )
        if success:
            self._reply_key(event, "msg_demote_success", user=target)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot set_group_name <name> ----

    @bot_group.command("set_group_name", alias={"设置群名"})
    async def cmd_set_group_name(self, event: AstrMessageEvent):
        ctx = await self._require_admin_context(event)
        if ctx is None:
            return

        rest = self._strip_command_prefix(event, "set_group_name", "设置群名")
        name = self._strip_quotes(rest)

        if not name:
            self._reply_key(event, "msg_parameter_error")
            return

        success = await self.group_handler.set_group_name(
            ctx.bot, int(ctx.group_id), name
        )
        if success:
            self._reply_key(event, "msg_group_name_success", name=name)
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot set_essence (reply to a message) ----

    @bot_group.command("set_essence", alias={"设精"})
    async def cmd_set_essence(self, event: AstrMessageEvent):
        ctx = self._require_group_bot_context(event)
        if ctx is None:
            return

        message_id = self._extract_replied_message_id(event)
        if message_id is None:
            self._reply_key(event, "msg_essence_no_reply")
            return

        success = await self.group_handler.set_essence_msg(ctx.bot, message_id)
        if success:
            self._reply_key(event, "msg_set_essence_success")
        else:
            self._reply_key(event, "msg_operation_failed")

    # ---- /bot remove_essence (reply to a message) ----

    @bot_group.command("remove_essence", alias={"移精"})
    async def cmd_remove_essence(self, event: AstrMessageEvent):
        ctx = self._require_group_bot_context(event)
        if ctx is None:
            return

        message_id = self._extract_replied_message_id(event)
        if message_id is None:
            self._reply_key(event, "msg_essence_no_reply")
            return

        success = await self.group_handler.delete_essence_msg(ctx.bot, message_id)
        if success:
            self._reply_key(event, "msg_remove_essence_success")
        else:
            self._reply_key(event, "msg_operation_failed")

    # ------------------------------------------------------------------ #
    #  Inspection watchdog
    # ------------------------------------------------------------------ #

    def _get_inspection_settings(self) -> dict:
        """Return the inspection settings object from plugin config.

        从插件配置中读取巡检模块设置。
        """
        return self.config.get("inspection_settings") or self.config.get(
            "sentinel_settings", {}
        )

    @filter.regex(r"^.*$", priority=2)
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def inspection_watchdog(self, event: AstrMessageEvent):
        """Intercept group messages and check inspection rules.

        拦截群聊消息并执行巡检规则检测。
        """
        inspection_settings = self._get_inspection_settings()
        inspection_enabled = inspection_settings.get(
            "inspection_enabled", inspection_settings.get("sentinel_enabled", False)
        )
        if not inspection_enabled:
            return

        group_id = event.get_group_id()
        if not group_id:
            return

        sender_id = event.get_sender_id()

        if self._is_bot_command_event(event):
            return

        msg_str = event.get_message_str().strip()
        message_types = self.inspection_handler.extract_message_types(event)

        json_content = (
            self._extract_json_component_text(event) if "Json" in message_types else ""
        )
        full_text = self._join_non_empty_text(msg_str, json_content)

        try:
            matched = await self.inspection_handler.check_message(
                event, self.config, group_id, sender_id, full_text, message_types
            )
        except Exception as e:
            logger.error(f"Inspection check_message error: {e}")
            return

        if not matched:
            return

        bot = self._get_bot(event)
        if bot is None:
            return

        sender_name = event.get_sender_name() or sender_id
        message_id = self.inspection_handler.extract_message_id(event)

        for match_info in matched:
            try:
                await self.inspection_handler.execute_action(
                    event,
                    bot,
                    group_id,
                    sender_id,
                    sender_name,
                    message_id,
                    match_info,
                )
            except Exception as e:
                logger.error(f"Inspection execute_action error: {e}")

        event.stop_event()
        yield

    # ------------------------------------------------------------------ #
    #  Event listener for member join / leave and unknown commands
    # ------------------------------------------------------------------ #

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_event(self, event: AstrMessageEvent):
        """Listen for all events and handle group notice events.

        监听全部事件，并处理群通知事件。
        """
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
        logger.debug(f"on_event: notice_type={notice_type}, group_id={group_id}")

        if not group_id or group_id == "0":
            return

        if not self._is_group_allowed(group_id):
            logger.debug(f"Group {group_id} not in whitelist, skipping welcome")
            return

        welcome_global = self.config.get("welcome_global_enabled", True)
        logger.debug(f"welcome_global_enabled={welcome_global}")
        if not welcome_global:
            return

        cfg = self._get_group_config(group_id)
        welcome_enabled = cfg.get("welcome_enabled", False)
        logger.debug(f"Group {group_id} welcome_enabled={welcome_enabled}")

        if notice_type == "group_increase" and welcome_enabled:
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
