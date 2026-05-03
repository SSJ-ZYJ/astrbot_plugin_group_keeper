# QQ群管理插件 (Group Keeper)

一个用于管理 QQ 群聊的 AstrBot 插件，专为 HTS Team 设计。

## 功能特性

- 🎉 **新人欢迎** - 自动欢迎新成员加入群聊
- 👑 **管理员管理** - 支持添加、移除和查看管理员列表
- 🔧 **权限控制** - 只有管理员可以执行管理操作

## 安装方式

1. 通过 AstrBot 插件市场搜索安装
2. 或手动克隆到 `data/plugins/` 目录：
   ```bash
   git clone https://github.com/SSJ-ZYJ/astrbot_plugin_group_keeper.git data/plugins/astrbot_plugin_group_keeper
   ```

## 使用说明

### 指令列表

| 指令 | 说明 | 参数 |
|------|------|------|
| `/group welcome [on/off]` | 设置新人欢迎功能 | `on` 开启 / `off` 关闭 |
| `/group add_admin <qq>` | 添加管理员 | QQ号 |
| `/group remove_admin <qq>` | 移除管理员 | QQ号 |
| `/group list_admins` | 列出所有管理员 | 无 |
| `/group help` | 显示帮助信息 | 无 |

### 使用示例

```
/group welcome on              # 开启新人欢迎
/group welcome off             # 关闭新人欢迎
/group add_admin 123456789     # 添加管理员
/group remove_admin 123456789  # 移除管理员
/group list_admins             # 查看管理员列表
```

## 配置说明

插件配置文件位于 `data/group_keeper/config.json`：

```json
{
  "welcome_enabled": true,
  "admin_list": ["123456789", "987654321"]
}
```

## 开发原则

本插件遵循 AstrBot 插件开发规范：

1. ✅ 功能经过测试
2. ✅ 包含良好的注释
3. ✅ 持久化数据存储于 `data` 目录
4. ✅ 完善的错误处理机制
5. ✅ 使用 `ruff` 格式化代码
6. ✅ 使用异步网络请求库

## 支持平台

- QQ (aiocqhttp)

## 版本要求

- AstrBot >= v4.5.0

## 许可证

MIT License