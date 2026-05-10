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
#
# This file contains code derived from astrbot_plugin_sentinel
# (https://github.com/Foolllll-J/astrbot_plugin_sentinel),
# originally licensed under AGPL-3.0 by Foolllll-J.

from __future__ import annotations

import asyncio
import json
import random
import re
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

INSPECTION_DIR = "inspection"
LEGACY_INSPECTION_DIR = "sentinel"
VIOLATION_FILE = "violation_counts.json"


class InspectionHandler:
    """Handles inspection logic: rule matching, violation tracking, and actions.

    处理巡检监控逻辑，包括规则匹配、违规记录跟踪和操作执行。
    """

    def __init__(self, data_path: Path):
        self.inspection_path = data_path / INSPECTION_DIR
        self.legacy_inspection_path = data_path / LEGACY_INSPECTION_DIR
        self.inspection_path.mkdir(parents=True, exist_ok=True)
        self._violation_data: dict[str, dict[str, dict[str, int]]] = {}
        self._load_violations()

    @staticmethod
    def _get_with_legacy(
        data: dict, current_key: str, legacy_key: str, default: Any
    ) -> Any:
        """Read the current inspection key with legacy config fallback.

        读取当前巡检配置键，并兼容旧版配置键。
        """
        if current_key in data:
            return data.get(current_key, default)
        return data.get(legacy_key, default)

    def _load_violations(self):
        """Load violation counters from plugin data storage.

        从插件数据目录加载违规计数。
        """
        vf = self.inspection_path / VIOLATION_FILE
        if not vf.exists():
            legacy_vf = self.legacy_inspection_path / VIOLATION_FILE
            if legacy_vf.exists():
                vf = legacy_vf
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
        vf = self.inspection_path / VIOLATION_FILE
        try:
            with vf.open("w", encoding="utf-8") as f:
                json.dump(self._violation_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save violation counts: {e}")

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
        """Find all configured inspection rules hit by a message.

        查找当前消息命中的配置巡检规则。
        """
        matched: list[dict] = []

        inspection_settings = config.get("inspection_settings") or config.get(
            "sentinel_settings", {}
        )
        group_blacklist = [
            str(g)
            for g in self._get_with_legacy(
                inspection_settings,
                "inspection_group_blacklist",
                "sentinel_group_blacklist",
                [],
            )
        ]
        if group_id in group_blacklist:
            return matched

        user_whitelist = [
            str(u)
            for u in self._get_with_legacy(
                inspection_settings,
                "inspection_user_whitelist",
                "sentinel_user_whitelist",
                [],
            )
        ]
        if sender_id in user_whitelist:
            return matched

        sender_role = await self._get_sender_role(event, group_id, sender_id)

        rules_group = self._get_with_legacy(
            inspection_settings,
            "inspection_rules_group",
            "sentinel_rules_group",
            {},
        )
        rules = self._get_with_legacy(
            rules_group,
            "inspection_rules",
            "sentinel_rules",
            [],
        )
        for idx, rule in enumerate(rules):
            if self._match_rule(
                rule, group_id, sender_id, sender_role, message_str, message_types
            ):
                matched.append({"type": "config", "index": idx, "rule": rule})

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
        """Evaluate one WebUI-configured inspection rule.

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
        """Execute recall, mute, reply, and kick actions for a hit.

        对命中规则执行撤回、禁言、回复和踢出动作。
        """
        rule = match_info["rule"]

        mute_str = rule.get("mute_duration", "0")
        recall_delay = rule.get("recall_delay", 0)
        reply_list = rule.get("reply_message", [])
        kick_threshold = rule.get("kick_threshold", 0)
        kick_list = rule.get("kick_message", [])
        rule_id = f"cfg_{match_info['index']}"

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
                logger.warning(f"Inspection recall failed: {e}")

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
                logger.warning(f"Inspection mute failed: {e}")

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
                logger.warning(f"Inspection reply failed: {e}")

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
                    logger.warning(f"Inspection kick failed: {e}")
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
                            logger.warning(f"Inspection kick message failed: {e2}")

        return rule_id

    @staticmethod
    def _render_template(text: str, user_id: str, user_name: str) -> str:
        """Render runtime placeholders in inspection reply/kick templates.

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
