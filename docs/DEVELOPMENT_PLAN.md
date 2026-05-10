# AstrBot QQ 群管理插件开发说明

> 本文档记录当前插件的实际结构、数据约定和开发规范，避免与代码实现脱节。

---

## 1. 当前结构

```text
astrbot_plugin_group_keeper/
├── main.py
├── metadata.yaml
├── README.md
├── CHANGELOG.md
├── _conf_schema.json
├── i18n.py
├── .astrbot-plugin/
│   └── i18n/
│       ├── zh-CN.json
│       └── en-US.json
├── handlers/
│   ├── __init__.py
│   ├── group_handler.py
│   ├── join_handler.py
│   ├── message_handler.py
│   ├── sentinel_handler.py
│   └── time_parser.py
└── docs/
    └── DEVELOPMENT_PLAN.md
```

---

## 2. 核心模块

| 模块 | 职责 |
|------|------|
| `main.py` | 插件入口、命令处理、事件拦截、欢迎消息、巡检调度 |
| `handlers/group_handler.py` | 群管理 API 封装（禁言、撤回、改名、头衔、精华等） |
| `handlers/join_handler.py` | 入群欢迎消息处理 |
| `handlers/message_handler.py` | 长消息完整封装与合并消息构造 |
| `handlers/sentinel_handler.py` | 巡检规则匹配、违规计数、动作执行、通知发送 |
| `handlers/time_parser.py` | 巡检时间范围解析 |
| `i18n.py` | 插件级中英双语翻译加载 |

---

## 3. 数据约定

- 插件持久化数据应存放在 `StarTools.get_data_dir("astrbot_plugin_group_keeper")` 返回的目录中。
- 群级欢迎配置存放在 `groups/group_<群号>.json`。
- 巡检指令规则存放在 `sentinel/command_rules_<群号>.json`。
- 违规计数存放在 `sentinel/violation_counts.json`。

---

## 4. 国际化约定

- 插件消息和 WebUI 文案统一使用 `.astrbot-plugin/i18n/zh-CN.json` 与 `.astrbot-plugin/i18n/en-US.json`。
- 配置文件中的文本说明应走 i18n 结构，不新增硬编码用户可见文案。
- 新增消息 key 时，需同时补齐中英两份翻译。

---

## 5. 代码规范

1. 仅在插件目录内修改。
2. 新增逻辑优先复用现有 helper，避免重复权限判断和重复文本处理。
3. 用户可见文本必须来自 i18n。
4. 持久化数据必须落在 AstrBot 数据目录。
5. 修改后执行 `ruff format` 与 `ruff check`。

---

## 6. 现有命令

| 指令 | 权限 |
|------|------|
| `/bot help` | 所有人 |
| `/bot welcome` | 群管理员/群主 |
| `/bot mute`、`/bot unmute`、`/bot global_mute`、`/bot recall` | 群管理员/群主 |
| `/bot rename`、`/bot set_group_name` | 群管理员/群主 |
| `/bot title`、`/bot promote`、`/bot demote` | 群管理员/群主，且机器人本身需具备群主权限 |
| `/bot set_essence`、`/bot remove_essence` | 所有人（仅要求群聊与平台支持） |
| `/bot monitor`、`/bot unmonitor`、`/bot monitorlist` | 群管理员/群主或指令白名单用户 |

---

## 7. 版本记录

| 版本 | 说明 |
|------|------|
| v1.2.7 | 长消息超过阈值时仅进行单节点合并发送，不再拆分消息内容 |
| v1.2.6 | 重构版本，统一前置检查、长消息处理、巡检通知 i18n 和文档 |
