# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-05-03

### Added

- ✨ 添加 WebUI 配置面板支持
- ✨ 新增配置项：语言设置（中文/英文）
- ✨ 新增配置项：默认禁言时长
- ✨ 新增配置项：默认开启欢迎消息
- ✨ 新增配置项：默认欢迎消息内容
- ✨ 新增配置项：最大撤回条数

### Changed

- ♻️ 重构配置管理，使用 AstrBot 标准配置系统
- ♻️ 移除手动文件存储的 global_config
- ♻️ 使用 `StarTools.get_data_dir()` 获取数据目录
- 📝 更新 README 许可证说明（AGPL-3.0）

### Fixed

- 🐛 修复 `register_star()` 参数名错误（`description` → `desc`）
- 🐛 修复 `Context` 对象无 `data_dir` 属性错误

## [1.0.0] - 2026-05-03

### Added

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
