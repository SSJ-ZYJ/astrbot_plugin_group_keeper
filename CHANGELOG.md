# 更新日志

---

## [1.0.7] - 2026-05-04

### 修复
- 🐛 修复语言切换无效问题：`locale` 改为每次调用 `_t()` 时动态读取配置，不再缓存
- 🐛 修复公告置顶配置不生效问题：`notice_handler.publish()` 始终传递 `pinned` 和 `confirm_required` 参数
- 🐛 修复配置页始终显示英文问题：`_conf_schema.json` 改为中文描述，i18n 文件提供英文覆盖
- 🐛 修复设置群名带空格失败问题：移除框架自动参数解析，改为从原始消息提取，新增 `_strip_quotes` 引号处理
- 🐛 修复发布公告带空格内容被截断的问题

### 新增
- ✨ 所有指令新增中文别名：帮助、欢迎、禁言、解禁、全员禁言、撤回、改名、头衔、提升、降级、设置群名、公告
- ✨ 指令组新增中文别名：`/机器人` 可替代 `/bot`
- ✨ 新增 `_strip_command_prefix()` 辅助方法，支持中英文指令前缀解析
- ✨ 新增 `_strip_quotes()` 辅助方法，支持双引号/单引号包裹参数
- ✨ 欢迎消息支持 `{membername}` 变量，自动替换为新成员的群昵称

### 修改
- ♻️ 移除 `add_admin`、`remove_admin`、`list_admins` 冗余指令，权限自动同步群内管理员角色
- ♻️ 移除 `list_announcements` 查看公告指令及相关功能
- ♻️ 移除 `admin_list` 本地管理员列表，所有权限检测直接查询 QQ 群内真实角色
- ♻️ `title`、`promote`、`demote` 指令新增 `_is_plugin_admin` 权限检查
- ♻️ 移除 `NoticeHandler.get_from_group()` 未使用的方法
- ♻️ 配置值（禁言时长、最大撤回条数等）改为动态读取，不再缓存
- ♻️ 移除 `ban`（封禁）指令及相关功能
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

## [1.0.7] - 2026-05-04

### Fixed
- 🐛 Fix locale switching not working: `locale` is now read dynamically from config on each `_t()` call instead of being cached
- 🐛 Fix announcement pinned config not taking effect: `notice_handler.publish()` now always passes `pinned` and `confirm_required` parameters
- 🐛 Fix config page always showing English: `_conf_schema.json` now uses Chinese descriptions, i18n files provide English overrides
- 🐛 Fix set_group_name failing with quoted names containing spaces: remove framework auto param parsing, extract from raw message, add `_strip_quotes` helper
- 🐛 Fix announce command content being truncated when containing spaces

### Added
- ✨ Add Chinese aliases for all commands: 帮助、欢迎、禁言、解禁、全员禁言、撤回、改名、头衔、提升、降级、设置群名、公告
- ✨ Add Chinese alias for command group: `/机器人` as alternative to `/bot`
- ✨ Add `_strip_command_prefix()` helper method supporting both Chinese and English command prefix parsing
- ✨ Add `_strip_quotes()` helper method supporting double/single quoted parameters
- ✨ Welcome message supports `{membername}` variable, auto-replaced with new member's group nickname

### Changed
- ♻️ Remove redundant commands: `add_admin`, `remove_admin`, `list_admins`; permissions auto-sync with real group admin roles
- ♻️ Remove `list_announcements` command and related functionality
- ♻️ Remove local `admin_list`; all permission checks query real QQ group roles directly
- ♻️ Add `_is_plugin_admin` permission check to `title`, `promote`, `demote` commands
- ♻️ Remove unused `NoticeHandler.get_from_group()` method
- ♻️ Config values (mute duration, max recall count, etc.) are now read dynamically instead of cached
- ♻️ Remove `ban` (kick and ban) command and related functionality
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
