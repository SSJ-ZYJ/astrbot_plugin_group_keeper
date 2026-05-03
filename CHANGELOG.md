# Changelog / 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] / [未发布]

## [1.0.1] - 2026-05-03

### Added / 新增

- ✨ Add WebUI configuration panel support / 添加 WebUI 配置面板支持
- ✨ Add locale setting (Chinese/English) / 新增配置项：语言设置（中文/英文）
- ✨ Add default mute duration setting / 新增配置项：默认禁言时长
- ✨ Add default welcome enabled setting / 新增配置项：默认开启欢迎消息
- ✨ Add default welcome message setting / 新增配置项：默认欢迎消息内容
- ✨ Add max recall count setting / 新增配置项：最大撤回条数

### Changed / 修改

- ♻️ Refactor config management using AstrBot standard config system / 重构配置管理，使用 AstrBot 标准配置系统
- ♻️ Remove manual global_config file storage / 移除手动文件存储的 global_config
- ♻️ Use StarTools.get_data_dir() for data directory / 使用 StarTools.get_data_dir() 获取数据目录
- 📝 Update license description in README (AGPL-3.0) / 更新 README 许可证说明（AGPL-3.0）

### Fixed / 修复

- 🐛 Fix register_star() parameter name error (description → desc) / 修复 register_star() 参数名错误
- 🐛 Fix Context object has no data_dir attribute error / 修复 Context 对象无 data_dir 属性错误

## [1.0.0] - 2026-05-03

### Added / 新增

- ✨ Initial release / 初始版本发布
- ✨ Welcome message for new members / 新人欢迎功能（自动发送欢迎消息）
- ✨ Admin management (add/remove/list) / 管理员管理（添加/移除/列出管理员）
- ✨ Mute management (single mute, unmute, global mute) / 禁言管理（单个禁言、解禁、全体禁言）
- ✨ Ban function / 拉黑功能（封禁用户）
- ✨ Message recall function / 消息撤回功能
- ✨ Group card management (nickname, title) / 群名片管理（修改昵称、设置头衔）
- ✨ Admin permission management (promote/demote) / 管理员权限管理（设为管理员/取消管理员）
- ✨ Group name modification / 群名称修改
- ✨ Group announcement management (publish/list) / 群公告管理（发布/查看公告）
- ✨ Chinese/English bilingual support / 中英文双语支持
