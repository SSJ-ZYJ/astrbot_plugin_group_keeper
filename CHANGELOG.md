# 更新日志

---

## [1.1.6] - 2026-05-05

### 修复
- 🐛 修复非白名单群聊中 `@机器人 /bot xxx` 格式命令未被正确拦截的问题
- 🐛 修复 `stop_event()` 后缺少 `yield` 导致事件未被正确阻止的问题

---

## [1.1.6] - 2026-05-05

### Fixed
- 🐛 Fix `@bot /bot xxx` format commands not being correctly intercepted in non-whitelist groups
- 🐛 Fix missing `yield` after `stop_event()` causing events not being properly blocked

---

## [1.1.5] - 2026-05-05

### 新增
- ✨ 支持 `@机器人 /bot xxx` 格式的命令接管，与直接 `/bot xxx` 使用相同的拦截逻辑

---

## [1.1.5] - 2026-05-05

### Added
- ✨ Support `@bot /bot xxx` format command interception, using the same logic as direct `/bot xxx`

---

## [1.1.4] - 2026-05-05

### 修复
- 🐛 重构消息判断逻辑：通过原始消息判断是否为 `/bot` 命令，不再干扰其他对话
- 🐛 修复白名单和无效命令截断功能失效的问题

### 修改
- ♻️ 优化拦截逻辑：
  1. 接管所有以 `/bot` 开头的指令，无论群聊是否在白名单内
  2. 白名单内的群聊：有效命令正常回复，无效命令提示"命令不存在"
  3. 非白名单群聊：所有 `/bot` 命令静默处理，不回复

---

## [1.1.4] - 2026-05-05

### Fixed
- 🐛 Refactor message judgment logic: determine if it's a `/bot` command by raw message, no longer interferes with other conversations
- 🐛 Fix whitelist and unknown command interception not working

### Changed
- ♻️ Optimize interception logic:
  1. Take over all commands starting with `/bot`, regardless of whether the group is in the whitelist
  2. Groups in whitelist: valid commands get normal reply, invalid commands show "Command not found"
  3. Groups not in whitelist: all `/bot` commands are silently ignored

---

## [1.1.3] - 2026-05-05

### 修复
- 🐛 修复白名单和无效命令截断功能失效的问题
- 🐛 改进拦截逻辑：区分无效命令和正常 LLM 对话，只有当没有其他 handler 被激活时才拦截

---

## [1.1.2] - 2026-05-05

### 修复
- 🐛 修复无效指令截断影响正常 LLM 对话的问题：现在只截断以 `/bot` 开头的消息，不再干扰其他对话

---

## [1.1.1] - 2026-05-05

### 修改
- ♻️ 非白名单群聊中输入指令时改为静默处理，不再回复提示消息

---

## [1.1.0] - 2026-05-05

### 新增
- ✨ 添加群白名单功能：可配置白名单群号，启用后只有白名单内的群才能使用插件功能
- ✨ 新增配置项 `whitelist_enabled`：启用/禁用群白名单
- ✨ 新增配置项 `group_whitelist`：群白名单列表，支持多个群号
- ✨ 新增配置项 `welcome_global_enabled`：新人欢迎全局总开关，可一键关闭所有群的新人欢迎功能，默认开启
- ✨ 新增国际化翻译 `msg_whitelist_not_allowed`：白名单限制提示消息

### 修复
- 🐛 修复未知命令（如 `/bot list`）不提示"指令不存在"的问题
- 🐛 修复白名单拦截不生效的问题：`WakingCheckStage` 会去掉唤醒前缀，导致消息不包含 `/bot`
- 🐛 修复 `whitelist_guard` 未正确使用 `yield` 返回结果，导致事件拦截不生效的问题
- 🐛 修复命令 handler 检测逻辑：改为检查是否有命令 handler（以 `cmd_` 开头）被激活

### 修改
- ♻️ 重构命令拦截机制：使用高优先级事件监听器 `whitelist_guard` 统一处理白名单检查和未知命令拦截
- ♻️ 规范配置项命名：`welcome_enabled` → `welcome_global_enabled`（全局总开关），`default_welcome_enabled` → `welcome_default_enabled`（新群默认值）
- 📝 更新 README.md，新增配置优先级说明和群级别配置说明

---

## [1.0.16] - 2026-05-04

### 新增
- ✨ 添加群白名单功能：可配置白名单群号，启用后只有白名单内的群才能使用插件功能
- ✨ 新增配置项 `whitelist_enabled`：启用/禁用群白名单
- ✨ 新增配置项 `group_whitelist`：群白名单列表，支持多个群号
- ✨ 新增国际化翻译 `msg_whitelist_not_allowed`：白名单限制提示消息

---

## [1.0.15] - 2026-05-04

### 修复
- 🐛 修复兜底处理机制无效的问题
- 🐛 移除无效的 `@bot_group.command("")` 方式，改用 `@filter.event_message_type` 事件监听器
- 🐛 新增 `on_unknown_command` 方法，监听所有消息事件，检查 `/bot` 前缀但子指令不在有效列表中时提示"指令不存在"

---

## [1.0.14] - 2026-05-04

### 修改
- ♻️ 全面更新 README.md，反映最新功能状态
- ♻️ 更新插件名称、指令列表、配置说明、权限说明等内容
- ♻️ 添加欢迎消息变量说明和未知指令处理说明

---

## [1.0.13] - 2026-05-04

### 修复
- 🐛 修复外显名称（display_name、short_desc、desc）中英文切换无效的问题
- 🐛 `I18nManager` 现在正确加载 `metadata` 部分，并新增 `get_metadata()` 方法
- 🐛 `main.py` 新增 `display_name`、`short_desc`、`desc` 属性，根据当前 locale 动态返回对应语言的元数据
- 🐛 `metadata.yaml` 恢复标准格式（name 使用英文标识符，display_name 使用英文）

---

## [1.0.12] - 2026-05-04

### 修改
- ♻️ 插件更名为 **群控助手 - BotKeeper**
- ♻️ 更新所有相关文件中的插件名称引用（metadata.yaml、i18n 文件、main.py 类注释和日志）

---

## [1.0.11] - 2026-05-04

### 新增
- ✨ 添加兜底处理机制：当用户输入的 `/bot` 指令不存在或格式错误时，自动提示"指令不存在，请使用 /bot help 查看可用指令"
- ✨ 新增 `msg_command_not_found` 国际化翻译 key（中英文）

---

## [1.0.10] - 2026-05-04

### 修改
- ♻️ 更新中文 i18n 文件，将所有指令示例中的 `/机器人` 改为 `/bot`

---

## [1.0.9] - 2026-05-04

### 修改
- ♻️ 移除指令组中文别名 `/机器人`，统一使用 `/bot` 作为唯一指令前缀
- ♻️ 更新 `_strip_command_prefix()` 方法，仅支持 `/bot` 前缀解析

---

## [1.0.8] - 2026-05-04

### 修改
- ♻️ 统一指令前缀：中英文消息均需以 `/bot` 开头，确保指令唤醒的一致性和明确性

---

## [1.0.7] - 2026-05-04

### 修复
- 🐛 修复语言切换无效问题：`locale` 改为每次调用 `_t()` 时动态读取配置，不再缓存
- 🐛 修复配置页始终显示英文问题：`_conf_schema.json` 改为中文描述，i18n 文件提供英文覆盖
- 🐛 修复设置群名带空格失败问题：移除框架自动参数解析，改为从原始消息提取，新增 `_strip_quotes` 引号处理

### 新增
- ✨ 所有指令新增中文别名：帮助、欢迎、禁言、解禁、全员禁言、撤回、改名、头衔、提升、降级、设置群名
- ✨ 指令组新增中文别名：`/机器人` 可替代 `/bot`
- ✨ 新增 `_strip_command_prefix()` 辅助方法，支持中英文指令前缀解析
- ✨ 新增 `_strip_quotes()` 辅助方法，支持双引号/单引号包裹参数
- ✨ 欢迎消息支持 `{membername}` 变量，自动替换为新成员的群昵称

### 修改
- ♻️ 移除 `add_admin`、`remove_admin`、`list_admins` 冗余指令，权限自动同步群内管理员角色
- ♻️ 移除 `admin_list` 本地管理员列表，所有权限检测直接查询 QQ 群内真实角色
- ♻️ `title`、`promote`、`demote` 指令新增 `_is_plugin_admin` 权限检查
- ♻️ 配置值（禁言时长、最大撤回条数等）改为动态读取，不再缓存
- ♻️ 移除 `ban`（封禁）指令及相关功能
- ♻️ 移除公告相关功能（`cmd_announce`、`NoticeHandler`、公告配置项）
- ♻️ 帮助菜单根据语言设置只显示对应语言的指令，不再中英混杂
- ♻️ 更新 README.md 反映当前功能状态

---

## [1.0.6] - 2026-05-04

### 修复
- 🐛 修复 `cmd_help` 传递多余 `event` 参数给 `_t()` 导致 basedpyright 报错
- 🐛 修复 `cmd_global_mute` 空参数时 `status.lower()` 崩溃
- 🐛 修复 `_check_group_role` 异常静默无日志
- 🐛 修复 `on_event` 中 `group_id=0` 被当作有效群号
- 🐛 修复 main.py 中 9 处注释乱码（`<QQå?>`）

### 修改
- ♻️ 移除 `default_admin_list` 配置项，权限检测改为直接查询 QQ 群内真实角色
- ♻️ 统一国际化文件至 `.astrbot-plugin/i18n/` 目录，移除旧的 `locales/` 和 `i18n.py` 硬编码翻译
- ♻️ 重构 `__init__` 签名，使用 `AstrBotConfig` 类型
- ♻️ 重构 `_t()` 方法，移除未使用的 `event` 参数
- ♻️ 将 `_extract_text_after_target` 移至 Helpers 区
- ♻️ 所有方法添加中英文双语 docstrings
- ♻️ 补全缺失的 i18n 翻译 key（help/cmd/mute_success 等 20+ 个）
- ♻️ 严格按照 AstrBot 插件文档规范重构项目结构

---

## [1.0.5] - 2026-05-03

### 新增
- ✨ 新增配置项 `default_admin_list`：在 WebUI 中设置全局默认管理员 QQ 号列表

---

## [1.0.4] - 2026-05-03

### 修复
- 🐛 修复插件无法识别群主和群管理员权限的问题，`_is_plugin_admin` 现在会同时检查本地管理员列表和 QQ 群内真实角色

---

## [1.0.3] - 2026-05-03

### 修复
- 🐛 修复设置头衔（`set_group_special_title`）和提升管理员（`set_group_admin`）功能无效的问题
- 🐛 修复所有写操作（禁言、踢人、改名等）成功后仍提示"操作失败"的根因：OneBot API 成功时返回 `None` 被误判为失败
- 🐛 修复获取公告列表无法获取群内公告的问题，新增 `_get_group_notice` API 调用
- 🐛 修复添加管理员（`add_admin`）和移除管理员（`remove_admin`）功能不可用，增加手动参数提取回退逻辑
- 🐛 修复 `_extract_text_after_target` 在 At 组件后无法正确提取文本的问题

### 新增
- ✨ 发布公告支持配置项：是否需要群成员确认（`default_announce_confirm_required`）
- ✨ 发布公告支持配置项：是否置顶（`default_announce_pinned`）
- ✨ 公告列表显示置顶和需确认标签
- ✨ 设置群名（`set_group_name`）支持双引号包裹带空格的群名，如 `/bot set_group_name "群名称"`

### 修改
- ♻️ 重构 `GroupHandler`，新增 `_execute_api` 和 `_execute_api_with_error` 方法，区分读操作和写操作的返回值判断逻辑
- ♻️ 重构 `NoticeHandler`，新增 `get_from_group` 方法获取群内公告

---

## [1.0.2] - 2026-05-03

### 修复
- 🐛 修复 `set_group_special_title` API 缺少 `duration` 参数导致设置头衔失败
- 🐛 改进错误处理，操作失败时显示具体错误信息

### 修改
- ♻️ 将指令参数从 `@用户` 格式改为 `<QQ号>` 格式
- ♻️ 规范本地化文件格式，统一使用 `<QQ号>` / `<QQ>` 格式

## [1.0.1] - 2026-05-03

### 新增
- ✨ 添加 WebUI 配置面板支持
- ✨ 新增配置项：语言设置（中文/英文）
- ✨ 新增配置项：默认禁言时长
- ✨ 新增配置项：默认开启欢迎消息
- ✨ 新增配置项：默认欢迎消息内容
- ✨ 新增配置项：最大撤回条数

### 修改
- ♻️ 重构配置管理，使用 AstrBot 标准配置系统
- ♻️ 移除手动文件存储的 global_config
- ♻️ 使用 StarTools.get_data_dir() 获取数据目录
- 📝 更新 README 许可证说明（AGPL-3.0）

### 修复
- 🐛 修复 register_star() 参数名错误
- 🐛 修复 Context 对象无 data_dir 属性错误

## [1.0.0] - 2026-05-03

### 新增
- ✨ 初始版本发布
- ✨ 新人欢迎功能（自动发送欢迎消息）
- ✨ 管理员管理（添加/移除/列出管理员）
- ✨ 禁言管理（单个禁言、解禁、全体禁言）
- ✨ 拉黑功能（封禁用户）
- ✨ 消息撤回功能
- ✨ 群名片管理（修改昵称、设置头衔）
- ✨ 管理员权限管理（设为管理员/取消管理员）
- ✨ 群名称修改
- ✨ 群公告管理（发布/查看公告）
- ✨ 中英文双语支持

---

# Changelog

---

## [1.1.3] - 2026-05-05

### Fixed
- 🐛 Fix whitelist and unknown command interception not working
- 🐛 Improve interception logic: distinguish between invalid commands and normal LLM conversations, only intercept when no other handlers are activated

---

## [1.1.2] - 2026-05-05

### Fixed
- 🐛 Fix unknown command interception affecting normal LLM conversations: now only intercepts messages starting with `/bot`, no longer interferes with other conversations

---

## [1.1.1] - 2026-05-05

### Changed
- ♻️ Non-whitelist groups now silently ignore commands instead of replying with a message

---

## [1.1.0] - 2026-05-05

### Added
- ✨ Add group whitelist feature: configure whitelist group IDs, when enabled only whitelisted groups can use plugin features
- ✨ Add config option `whitelist_enabled`: enable/disable group whitelist
- ✨ Add config option `group_whitelist`: group whitelist list, supports multiple group IDs
- ✨ Add config option `welcome_global_enabled`: global master switch for welcome messages, can disable welcome messages for all groups with one click, enabled by default
- ✨ Add i18n translation `msg_whitelist_not_allowed`: whitelist restriction prompt message

### Fixed
- 🐛 Fix unknown commands (e.g. `/bot list`) not showing "Command not found" message
- 🐛 Fix whitelist interception not working: `WakingCheckStage` removes wake prefix, causing message to not contain `/bot`
- 🐛 Fix `whitelist_guard` not using `yield` to return results, causing event interception to not work
- 🐛 Fix command handler detection logic: check if any command handler (starting with `cmd_`) is activated

### Changed
- ♻️ Refactor command interception mechanism: use high-priority event listener `whitelist_guard` to handle whitelist check and unknown command interception
- ♻️ Standardize config option naming: `welcome_enabled` → `welcome_global_enabled` (global master switch), `default_welcome_enabled` → `welcome_default_enabled` (default value for new groups)
- 📝 Update README.md, add configuration priority explanation and group-level configuration description

---

## [1.0.16] - 2026-05-04

### Added
- ✨ Add group whitelist feature: configure whitelist group IDs, when enabled only whitelisted groups can use plugin features
- ✨ Add config option `whitelist_enabled`: enable/disable group whitelist
- ✨ Add config option `group_whitelist`: group whitelist list, supports multiple group IDs
- ✨ Add i18n translation `msg_whitelist_not_allowed`: whitelist restriction prompt message

---

## [1.0.15] - 2026-05-04

### Fixed
- 🐛 Fix fallback handler not working for unknown commands
- 🐛 Remove invalid `@bot_group.command("")` approach, use `@filter.event_message_type` event listener instead
- 🐛 Add `on_unknown_command` method to listen all message events, check if `/bot` prefix is present but sub-command is not in valid list, then prompt "Command not found"

---

## [1.0.14] - 2026-05-04

### Changed
- ♻️ Fully updated README.md to reflect latest feature status
- ♻️ Updated plugin name, command list, configuration description, permission description
- ♻️ Added welcome message variable description and unknown command handling description

---

## [1.0.13] - 2026-05-04

### Fixed
- 🐛 Fix display_name, short_desc, desc i18n switching not working
- 🐛 `I18nManager` now correctly loads `metadata` section, added `get_metadata()` method
- 🐛 `main.py` added `display_name`, `short_desc`, `desc` properties that return locale-specific metadata
- 🐛 `metadata.yaml` restored to standard format (name uses English identifier, display_name uses English)

---

## [1.0.12] - 2026-05-04

### Changed
- ♻️ Plugin renamed to **BotKeeper - Group Manager**
- ♻️ Updated all plugin name references in metadata.yaml, i18n files, main.py class docstrings and logs

---

## [1.0.11] - 2026-05-04

### Added
- ✨ Add fallback handler: When user inputs an unknown or invalid `/bot` command, automatically prompt "Command not found, use /bot help to see available commands"
- ✨ Add `msg_command_not_found` i18n translation key (Chinese and English)

---

## [1.0.10] - 2026-05-04

### Changed
- ♻️ Updated Chinese i18n file, changed all command examples from `/机器人` to `/bot`

---

## [1.0.9] - 2026-05-04

### Changed
- ♻️ Removed command group Chinese alias `/机器人`, unified to use `/bot` as the only command prefix
- ♻️ Updated `_strip_command_prefix()` method to only support `/bot` prefix parsing

---

## [1.0.8] - 2026-05-04

### Changed
- ♻️ Unified command prefix: Both Chinese and English messages must start with `/bot` to ensure consistent and clear command wake-up

---

## [1.0.7] - 2026-05-04

### Fixed
- 🐛 Fix locale switching not working: `locale` is now read dynamically from config on each `_t()` call instead of being cached
- 🐛 Fix config page always showing English: `_conf_schema.json` now uses Chinese descriptions, i18n files provide English overrides
- 🐛 Fix set_group_name failing with quoted names containing spaces: remove framework auto param parsing, extract from raw message, add `_strip_quotes` helper

### Added
- ✨ Add Chinese aliases for all commands: 帮助、欢迎、禁言、解禁、全员禁言、撤回、改名、头衔、提升、降级、设置群名
- ✨ Add Chinese alias for command group: `/机器人` as alternative to `/bot`
- ✨ Add `_strip_command_prefix()` helper method supporting both Chinese and English command prefix parsing
- ✨ Add `_strip_quotes()` helper method supporting double/single quoted parameters
- ✨ Welcome message supports `{membername}` variable, auto-replaced with new member's group nickname

### Changed
- ♻️ Remove redundant commands: `add_admin`, `remove_admin`, `list_admins`; permissions auto-sync with real group admin roles
- ♻️ Remove local `admin_list`; all permission checks query real QQ group roles directly
- ♻️ Add `_is_plugin_admin` permission check to `title`, `promote`, `demote` commands
- ♻️ Config values (mute duration, max recall count, etc.) are now read dynamically instead of cached
- ♻️ Remove `ban` (kick and ban) command and related functionality
- ♻️ Remove announcement-related functionality (`cmd_announce`, `NoticeHandler`, announcement config options)
- ♻️ Help menu now shows only commands in the current locale language, no more mixed Chinese/English
- ♻️ Update README.md to reflect current feature state

---

## [1.0.6] - 2026-05-04

### Fixed
- 🐛 Fix `cmd_help` passing unused `event` parameter to `_t()` causing basedpyright errors
- 🐛 Fix `cmd_global_mute` crash when status argument is empty
- 🐛 Fix `_check_group_role` silent exception handling (added logging)
- 🐛 Fix `on_event` accepting `group_id=0` as valid
- 🐛 Fix 9 garbled comments in main.py (`<QQå?>`)

### Changed
- ♻️ Remove `default_admin_list` config, use real QQ group role detection instead
- ♻️ Unify i18n to `.astrbot-plugin/i18n/` directory, remove old `locales/` and `i18n.py` hardcoded translations
- ♻️ Refactor `__init__` signature to use `AstrBotConfig` type
- ♻️ Refactor `_t()` method, remove unused `event` parameter
- ♻️ Move `_extract_text_after_target` to Helpers section
- ♻️ Add bilingual (Chinese/English) docstrings to all methods
- ♻️ Add missing i18n translation keys (help/cmd/mute_success etc. 20+ keys)
- ♻️ Refactor project structure to comply with AstrBot plugin documentation standards

---

## [1.0.5] - 2026-05-03

### Added
- ✨ Add `default_admin_list` config: set global default admin QQ numbers via WebUI

---

## [1.0.4] - 2026-05-03

### Fixed
- 🐛 Fix plugin unable to recognize group owner and admin roles; `_is_plugin_admin` now checks both local admin list and QQ group roles

---

## [1.0.3] - 2026-05-03

### Fixed
- 🐛 Fix `set_group_special_title` (set title) and `set_group_admin` (promote to admin) not working
- 🐛 Fix root cause of all write operations showing "Operation failed" on success: OneBot API returns `None` on success which was incorrectly judged as failure
- 🐛 Fix list announcements not fetching from QQ group, added `_get_group_notice` API call
- 🐛 Fix `add_admin` and `remove_admin` not working, added manual parameter extraction fallback
- 🐛 Fix `_extract_text_after_target` failing to extract text after At components

### Added
- ✨ Announcement supports `default_announce_confirm_required` config: require group members to confirm
- ✨ Announcement supports `default_announce_pinned` config: pin announcement
- ✨ Announcement list shows pinned and confirm-required tags
- ✨ Set group name (`set_group_name`) supports quoted names with spaces, e.g. `/bot set_group_name "Group Name"`

### Changed
- ♻️ Refactor `GroupHandler`: add `_execute_api` and `_execute_api_with_error` to distinguish read/write operation return value logic
- ♻️ Refactor `NoticeHandler`: add `get_from_group` method to fetch announcements from QQ group

---

## [1.0.2] - 2026-05-03

### Fixed
- 🐛 Fix `set_group_special_title` API missing `duration` parameter causing title setting failure
- 🐛 Improve error handling, show detailed error message when operation fails

### Changed
- ♻️ Change command parameter format from `@用户` to `<QQ号>` / `<QQ>`
- ♻️ Standardize locale file format, use consistent `<QQ号>` / `<QQ>` format

## [1.0.1] - 2026-05-03

### Added
- ✨ Add WebUI configuration panel support
- ✨ Add locale setting (Chinese/English)
- ✨ Add default mute duration setting
- ✨ Add default welcome enabled setting
- ✨ Add default welcome message setting
- ✨ Add max recall count setting

### Changed
- ♻️ Refactor config management using AstrBot standard config system
- ♻️ Remove manual global_config file storage
- ♻️ Use StarTools.get_data_dir() for data directory
- 📝 Update license description in README (AGPL-3.0)

### Fixed
- 🐛 Fix register_star() parameter name error (description → desc)
- 🐛 Fix Context object has no data_dir attribute error

## [1.0.0] - 2026-05-03

### Added
- ✨ Initial release
- ✨ Welcome message for new members
- ✨ Admin management (add/remove/list)
- ✨ Mute management (single mute, unmute, global mute)
- ✨ Ban function
- ✨ Message recall function
- ✨ Group card management (nickname, title)
- ✨ Admin permission management (promote/demote)
- ✨ Group name modification
- ✨ Group announcement management (publish/list)
- ✨ Chinese/English bilingual support
