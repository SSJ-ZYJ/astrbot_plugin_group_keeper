from __future__ import annotations

import asyncio
import json
import random
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from astrbot.api import logger

from .time_parser import TimeParser

MSG_TYPE_MAP = {
    "text": "Plain",
    "image": "Image",
    "voice": "Record",
    "video": "Video",
    "file": "File",
    "face": "Face",
    "forward": "Forward",
    "json": "Json",
}

VIOLATION_FILE = "violation_counts.json"
Translator = Callable[..., str]


class SentinelHandler:
    """Handles sentinel monitoring logic: rule matching, violation tracking, and actions.

    处理巡检监控逻辑，包括规则匹配、违规记录跟踪和操作执行。
    """

    def __init__(self, data_path: Path, translator: Translator | None = None):
        self.sentinel_path = data_path / "sentinel"
        self.sentinel_path.mkdir(parents=True, exist_ok=True)
        self._translator = translator
        self._violation_data: dict[str, dict[str, dict[str, int]]] = {}
        self._load_violations()

    def _t(self, key: str, **kwargs) -> str:
        """Translate sentinel notification text through the plugin i18n manager.

        通过插件 i18n 管理器翻译巡检通知文本。
        """
        if self._translator is None:
            return key
        return self._translator(key, **kwargs)

    def _load_violations(self):
        """Load violation counters from plugin data storage.

        从插件数据目录加载违规计数。
        """
        vf = self.sentinel_path / VIOLATION_FILE
        if vf.exists():
            try:
                with vf.open(encoding="utf-8") as f:
                    self._violation_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load violation counts: {e}")
                self._violation_data = {}

    def _save_violations(self):
        """Persist violation counters to plugin data storage.

        将违规计数保存到插件数据目录。
        """
        vf = self.sentinel_path / VIOLATION_FILE
        try:
            with vf.open("w", encoding="utf-8") as f:
                json.dump(self._violation_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save violation counts: {e}")

    def load_command_rules(self, group_id: str) -> dict:
        """Load command-created sentinel rules for one group.

        加载单群通过指令创建的巡检规则。
        """
        rf = self.sentinel_path / f"command_rules_{group_id}.json"
        if rf.exists():
            try:
                with rf.open(encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load command rules for {group_id}: {e}")
        return {"rules": [], "next_id": 1}

    def save_command_rules(self, group_id: str, data: dict):
        """Persist command-created sentinel rules for one group.

        保存单群通过指令创建的巡检规则。
        """
        rf = self.sentinel_path / f"command_rules_{group_id}.json"
        try:
            with rf.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save command rules for {group_id}: {e}")

    def add_command_rule(
        self,
        group_id: str,
        keyword: str,
        monitor_users: list[str],
        creator_id: str,
    ) -> int:
        """Add a command-created monitor rule and return its numeric id.

        添加指令创建的监控规则，并返回数字编号。
        """
        data = self.load_command_rules(group_id)
        rule_id = data["next_id"]
        data["rules"].append(
            {
                "rule_id": f"cmd_{rule_id}",
                "keyword": keyword,
                "monitor_users": monitor_users,
                "creator_id": creator_id,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        data["next_id"] = rule_id + 1
        self.save_command_rules(group_id, data)
        return rule_id

    def remove_command_rules(
        self,
        group_id: str,
        keyword: str | None = None,
        target_users: list[str] | None = None,
        rule_id: str | None = None,
    ) -> list[str]:
        """Remove command-created rules by id, keyword, or target users.

        按规则 ID、关键词或目标用户删除指令创建的规则。
        """
        data = self.load_command_rules(group_id)
        removed: list[str] = []

        if rule_id is not None:
            data["rules"] = [
                r
                for r in data["rules"]
                if r["rule_id"] != rule_id or not removed.append(r["rule_id"])
            ]
        elif target_users and not keyword:
            remaining = []
            for r in data["rules"]:
                if r["monitor_users"]:
                    for u in target_users:
                        if u in r["monitor_users"]:
                            r["monitor_users"].remove(u)
                    if not r["monitor_users"]:
                        removed.append(r["rule_id"])
                    else:
                        remaining.append(r)
                else:
                    remaining.append(r)
            data["rules"] = remaining
        elif keyword and target_users:
            remaining = []
            for r in data["rules"]:
                if r["keyword"] == keyword and r["monitor_users"]:
                    for u in target_users:
                        if u in r["monitor_users"]:
                            r["monitor_users"].remove(u)
                    if not r["monitor_users"]:
                        removed.append(r["rule_id"])
                    else:
                        remaining.append(r)
                else:
                    remaining.append(r)
            data["rules"] = remaining
        elif keyword and not target_users:
            matched = [r for r in data["rules"] if r["keyword"] == keyword]
            data["rules"] = [r for r in data["rules"] if r["keyword"] != keyword]
            if matched:
                removed = [f"keyword:{keyword}"]

        self.save_command_rules(group_id, data)
        return removed

    def get_violation_count(self, group_id: str, user_id: str, rule_id: str) -> int:
        """Return the current violation count for a user/rule pair.

        返回指定用户和规则的当前违规计数。
        """
        return self._violation_data.get(group_id, {}).get(user_id, {}).get(rule_id, 0)

    def increment_violation(self, group_id: str, user_id: str, rule_id: str) -> int:
        """Increment and persist a user/rule violation counter.

        增加并保存指定用户和规则的违规计数。
        """
        if group_id not in self._violation_data:
            self._violation_data[group_id] = {}
        if user_id not in self._violation_data[group_id]:
            self._violation_data[group_id][user_id] = {}
        self._violation_data[group_id][user_id][rule_id] = (
            self._violation_data[group_id][user_id].get(rule_id, 0) + 1
        )
        self._save_violations()
        return self._violation_data[group_id][user_id][rule_id]

    def reset_violation(self, group_id: str, user_id: str, rule_id: str):
        """Reset one user/rule violation counter and prune empty containers.

        重置指定用户和规则的违规计数，并清理空容器。
        """
        if (
            group_id in self._violation_data
            and user_id in self._violation_data[group_id]
        ):
            self._violation_data[group_id][user_id].pop(rule_id, None)
            if not self._violation_data[group_id][user_id]:
                del self._violation_data[group_id][user_id]
            if not self._violation_data[group_id]:
                del self._violation_data[group_id]
            self._save_violations()

    async def check_message(
        self,
        event: Any,
        config: dict,
        group_id: str,
        sender_id: str,
        message_str: str,
        message_types: set[str],
    ) -> list[dict]:
        """Find all configured and command-created sentinel rules hit by a message.

        查找当前消息命中的配置规则和指令规则。
        """
        matched: list[dict] = []

        sentinel_settings = config.get("sentinel_settings", {})
        group_blacklist = [
            str(g) for g in sentinel_settings.get("sentinel_group_blacklist", [])
        ]
        if group_id in group_blacklist:
            return matched

        user_whitelist = [
            str(u) for u in sentinel_settings.get("sentinel_user_whitelist", [])
        ]
        if sender_id in user_whitelist:
            return matched

        sender_role = await self._get_sender_role(event, group_id, sender_id)

        rules_group = sentinel_settings.get("sentinel_rules_group", {})
        rules = rules_group.get("sentinel_rules", [])
        for idx, rule in enumerate(rules):
            if self._match_rule(
                rule, group_id, sender_id, sender_role, message_str, message_types
            ):
                matched.append({"type": "config", "index": idx, "rule": rule})

        cmd_rules_data = self.load_command_rules(group_id)
        cmd_group = sentinel_settings.get("sentinel_command_group", {})
        cmd_config = {
            "mute_duration": cmd_group.get("sentinel_command_mute_duration", "60"),
            "reply_message": cmd_group.get("sentinel_command_reply_message", []),
            "ignore_admin": cmd_group.get("sentinel_command_ignore_admin", True),
            "kick_threshold": cmd_group.get("sentinel_command_kick_threshold", 0),
            "kick_message": cmd_group.get("sentinel_command_kick_message", []),
            "notify_creator": cmd_group.get("sentinel_command_notify_creator", True),
            "command_user_whitelist": [
                str(u) for u in cmd_group.get("sentinel_command_user_whitelist", [])
            ],
        }

        for cmd_rule in cmd_rules_data.get("rules", []):
            if self._match_command_rule(
                cmd_rule, group_id, sender_id, sender_role, message_str, cmd_config
            ):
                matched.append(
                    {
                        "type": "command",
                        "rule": cmd_rule,
                        "cmd_config": cmd_config,
                    }
                )

        return matched

    def _match_rule(
        self,
        rule: dict,
        group_id: str,
        sender_id: str,
        sender_role: str,
        message_str: str,
        message_types: set[str],
    ) -> bool:
        """Evaluate one WebUI-configured sentinel rule.

        评估一条 WebUI 配置的巡检规则。
        """
        groups = rule.get("groups", [])
        if groups and str(group_id) not in [str(g) for g in groups]:
            return False

        time_range = rule.get("time_range", "")
        if not TimeParser.is_in_range(time_range):
            return False

        rule_whitelist = [str(u) for u in rule.get("rule_user_whitelist", [])]
        if sender_id in rule_whitelist:
            return False

        monitor_list = [str(u) for u in rule.get("rule_user_monitor_list", [])]
        if monitor_list and sender_id not in monitor_list:
            return False

        if rule.get("ignore_admin", True) and sender_role in ("admin", "owner"):
            return False
        if rule.get("ignore_owner", True) and sender_role == "owner":
            return False

        keywords = rule.get("keywords", [])
        msg_types = rule.get("msg_types", [])

        if keywords:
            for kw in keywords:
                try:
                    if re.search(kw, message_str):
                        break
                except re.error:
                    if kw in message_str:
                        break
            else:
                if keywords:
                    return False

        if msg_types:
            rule_types = set()
            for mt in msg_types:
                mapped = MSG_TYPE_MAP.get(mt)
                if mapped:
                    rule_types.add(mapped)
            if rule_types and not rule_types.intersection(message_types):
                return False

        return True

    def _match_command_rule(
        self,
        rule: dict,
        group_id: str,
        sender_id: str,
        sender_role: str,
        message_str: str,
        cmd_config: dict,
    ) -> bool:
        """Evaluate one command-created monitor rule.

        评估一条通过指令创建的监控规则。
        """
        cmd_whitelist = cmd_config.get("command_user_whitelist", [])
        if sender_id in cmd_whitelist:
            return False

        if cmd_config.get("ignore_admin", True) and sender_role in ("admin", "owner"):
            return False

        monitor_users = rule.get("monitor_users", [])
        if monitor_users and sender_id not in [str(u) for u in monitor_users]:
            return False

        keyword = rule.get("keyword", "")
        if not keyword:
            return False

        if keyword in message_str:
            return True

        return False

    async def execute_action(
        self,
        event: Any,
        bot: Any,
        group_id: str,
        user_id: str,
        user_name: str,
        message_id: int | None,
        match_info: dict,
    ) -> str | None:
        """Execute recall, mute, reply, kick, and notification actions for a hit.

        对命中规则执行撤回、禁言、回复、踢出和通知动作。
        """
        rule = match_info["rule"]
        match_type = match_info["type"]

        if match_type == "config":
            mute_str = rule.get("mute_duration", "0")
            recall_delay = rule.get("recall_delay", 0)
            reply_list = rule.get("reply_message", [])
            kick_threshold = rule.get("kick_threshold", 0)
            kick_list = rule.get("kick_message", [])
            notify_group_admin = rule.get("notify_group_admin", False)
            notify_bot_admin = rule.get("notify_bot_admin", False)
            show_keyword = rule.get("show_rule_in_notification", False)
            rule_id = f"cfg_{match_info['index']}"
        else:
            cmd_config = match_info.get("cmd_config", {})
            mute_str = cmd_config.get("mute_duration", "0")
            recall_delay = 0
            reply_list = cmd_config.get("reply_message", [])
            kick_threshold = cmd_config.get("kick_threshold", 0)
            kick_list = cmd_config.get("kick_message", [])
            notify_group_admin = False
            notify_bot_admin = False
            show_keyword = False
            rule_id = rule.get("rule_id", "cmd_unknown")

        should_recall = True
        should_mute = True
        if mute_str == "-1":
            should_recall = False
            should_mute = False

        if should_recall and message_id is not None:
            if recall_delay > 0:
                await asyncio.sleep(recall_delay)
            try:
                await bot.call_action("delete_msg", message_id=message_id)
            except Exception as e:
                logger.warning(f"Sentinel recall failed: {e}")

        if should_mute and mute_str != "0":
            try:
                duration = self._parse_mute_duration(mute_str)
                if duration > 0:
                    await bot.call_action(
                        "set_group_ban",
                        group_id=int(group_id),
                        user_id=int(user_id),
                        duration=duration,
                    )
            except Exception as e:
                logger.warning(f"Sentinel mute failed: {e}")

        if reply_list:
            reply_text = random.choice(reply_list)
            reply_text = self._render_template(reply_text, user_id, user_name)
            try:
                await bot.call_action(
                    "send_group_msg",
                    group_id=int(group_id),
                    message=[
                        {"type": "at", "data": {"qq": str(user_id)}},
                        {"type": "text", "data": {"text": f" {reply_text}"}},
                    ],
                )
            except Exception as e:
                logger.warning(f"Sentinel reply failed: {e}")

        if kick_threshold > 0:
            count = self.increment_violation(group_id, user_id, rule_id)
            if count >= kick_threshold:
                kick_text = ""
                if kick_list:
                    kick_text = random.choice(kick_list)
                    kick_text = self._render_template(kick_text, user_id, user_name)
                try:
                    await bot.call_action(
                        "set_group_kick",
                        group_id=int(group_id),
                        user_id=int(user_id),
                        reject_add_request=False,
                    )
                except Exception as e:
                    logger.warning(f"Sentinel kick failed: {e}")
                else:
                    self.reset_violation(group_id, user_id, rule_id)
                    if kick_text:
                        try:
                            await bot.call_action(
                                "send_group_msg",
                                group_id=int(group_id),
                                message={"type": "text", "data": {"text": kick_text}},
                            )
                        except Exception as e2:
                            logger.warning(f"Sentinel kick message failed: {e2}")

        if notify_group_admin:
            await self._notify_group_admins(
                bot, group_id, rule, show_keyword, user_id, user_name
            )

        if notify_bot_admin:
            await self._notify_bot_admin(
                bot, group_id, rule, show_keyword, user_id, user_name
            )

        if match_type == "command" and match_info.get("cmd_config", {}).get(
            "notify_creator", True
        ):
            creator_id = rule.get("creator_id", "")
            if creator_id:
                await self._notify_creator(
                    bot, group_id, rule, creator_id, user_id, user_name
                )

        return rule_id

    @staticmethod
    def _render_template(text: str, user_id: str, user_name: str) -> str:
        """Render runtime placeholders in sentinel reply/kick templates.

        渲染巡检回复和踢出提示中的运行时占位符。
        """
        now = datetime.now()
        text = text.replace("{id}", str(user_id))
        text = text.replace("{name}", user_name or str(user_id))
        text = text.replace("{date}", now.strftime("%Y-%m-%d"))
        text = text.replace("{time}", now.strftime("%H:%M:%S"))
        return text

    @staticmethod
    def _parse_mute_duration(mute_str: str) -> int:
        """Parse a fixed or ranged mute duration string.

        解析固定值或区间格式的禁言秒数。
        """
        try:
            if "~" in mute_str:
                parts = mute_str.split("~")
                lo = int(parts[0].strip())
                hi = int(parts[1].strip())
                return random.randint(lo, hi) if lo <= hi else random.randint(hi, lo)
            return int(mute_str)
        except (ValueError, IndexError):
            return 0

    @staticmethod
    async def _get_sender_role(event: Any, group_id: str, sender_id: str) -> str:
        """Fetch the sender's real group role, falling back to member.

        获取发送者真实群角色，失败时按普通成员处理。
        """
        bot = getattr(event, "bot", None)
        if bot is None:
            return "member"
        try:
            info = await bot.call_action(
                "get_group_member_info",
                group_id=int(group_id),
                user_id=int(sender_id),
                no_cache=True,
            )
            return info.get("role", "member")
        except Exception:
            return "member"

    async def _notify_group_admins(
        self,
        bot: Any,
        group_id: str,
        rule: dict,
        show_keyword: bool,
        user_id: str,
        user_name: str,
    ):
        """Notify group admins by private message when a config rule is hit.

        配置规则命中时，通过私聊通知群管理员。
        """
        try:
            info = await bot.call_action(
                "get_group_member_list", group_id=int(group_id)
            )
            admins = [
                m
                for m in (info or [])
                if m.get("role") in ("owner", "admin")
                and str(m.get("user_id", "")) != str(bot.self_id)
            ]
            keyword_info = ""
            if show_keyword:
                keywords = rule.get("keywords", [])
                if keywords:
                    keyword_info = self._t(
                        "msg_sentinel_keyword_info", keywords=",".join(keywords)
                    )
            text = self._t(
                "msg_sentinel_hit_notification",
                group_id=group_id,
                user_name=user_name,
                user_id=user_id,
                keyword_info=keyword_info,
            )
            for admin in admins:
                try:
                    await bot.call_action(
                        "send_private_msg",
                        user_id=int(admin["user_id"]),
                        message=text,
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Sentinel notify group admins failed: {e}")

    async def _notify_bot_admin(
        self,
        bot: Any,
        group_id: str,
        rule: dict,
        show_keyword: bool,
        user_id: str,
        user_name: str,
    ):
        """Notify the group owner as the bot-admin fallback recipient.

        将群主作为 Bot 管理员回退接收者进行通知。
        """
        try:
            await bot.call_action("get_login_info")
            keyword_info = ""
            if show_keyword:
                keywords = rule.get("keywords", [])
                if keywords:
                    keyword_info = self._t(
                        "msg_sentinel_keyword_info", keywords=",".join(keywords)
                    )
            text = self._t(
                "msg_sentinel_hit_notification",
                group_id=group_id,
                user_name=user_name,
                user_id=user_id,
                keyword_info=keyword_info,
            )
            admins = await bot.call_action(
                "get_group_member_list", group_id=int(group_id)
            )
            owner = next((m for m in (admins or []) if m.get("role") == "owner"), None)
            if owner:
                try:
                    await bot.call_action(
                        "send_private_msg",
                        user_id=int(owner["user_id"]),
                        message=text,
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Sentinel notify bot admin failed: {e}")

    async def _notify_creator(
        self,
        bot: Any,
        group_id: str,
        rule: dict,
        creator_id: str,
        user_id: str,
        user_name: str,
    ):
        """Notify the creator of a command-created monitor rule.

        通知通过指令创建监控规则的创建者。
        """
        try:
            keyword = rule.get("keyword", "")
            text = self._t(
                "msg_sentinel_creator_notification",
                group_id=group_id,
                keyword=keyword,
                user_name=user_name,
                user_id=user_id,
            )
            await bot.call_action(
                "send_private_msg",
                user_id=int(creator_id),
                message=text,
            )
        except Exception as e:
            logger.warning(f"Sentinel notify creator failed: {e}")

    @staticmethod
    def extract_message_types(event: Any) -> set[str]:
        """Extract AstrBot component types plus raw OneBot segment types.

        提取 AstrBot 消息组件类型以及原始 OneBot 片段类型。
        """
        types: set[str] = set()
        messages = event.get_messages() if hasattr(event, "get_messages") else []
        for comp in messages:
            comp_type = type(comp).__name__
            types.add(comp_type)
        raw = (
            getattr(event.message_obj, "raw_message", None)
            if hasattr(event, "message_obj")
            else None
        )
        if raw:
            if isinstance(raw, dict):
                msg_content = raw.get("message", [])
                if isinstance(msg_content, list):
                    for seg in msg_content:
                        if isinstance(seg, dict):
                            seg_type = seg.get("type", "")
                            if seg_type == "json":
                                types.add("Json")
            elif hasattr(raw, "message"):
                msg_list = raw.message if isinstance(raw.message, list) else []
                for seg in msg_list:
                    if isinstance(seg, dict) and seg.get("type") == "json":
                        types.add("Json")
        return types

    @staticmethod
    def extract_message_id(event: Any) -> int | None:
        """Extract OneBot message_id from raw event payload.

        从原始事件载荷中提取 OneBot message_id。
        """
        raw = (
            getattr(event.message_obj, "raw_message", None)
            if hasattr(event, "message_obj")
            else None
        )
        if raw:
            if isinstance(raw, dict):
                return raw.get("message_id")
            if hasattr(raw, "message_id"):
                return raw.message_id
        return None
