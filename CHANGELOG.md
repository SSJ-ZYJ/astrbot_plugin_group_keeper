# 更新日志

本项目的所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本控制](https://semver.org/lang/zh-CN/)。

---

## [未发布]

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

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
