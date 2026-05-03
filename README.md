# QQ群管理插件 (Group Keeper)

一个用于管理 QQ 群聊的 AstrBot 插件，专为 HTS Team 设计。支持中英文双语版本。

---

## ✨ 功能特性

| 功能分类 | 功能描述 |
|----------|----------|
| 🎉 新人欢迎 | 自动欢迎新成员加入群聊 |
| 👑 管理员管理 | 支持添加、移除和查看管理员列表 |
| 🔇 禁言管理 | 支持单个禁言、解禁、全体禁言 |
| 🚫 拉黑功能 | 支持拉黑用户 |
| 📝 消息管理 | 支持撤回消息 |
| 🏷️ 群名片管理 | 修改群昵称、设置头衔 |
| 📢 公告管理 | 发布和查看群公告 |
| 🔧 权限控制 | 基于角色的权限管理 |

---

## 📦 安装方式

### 方式一：插件市场安装 (暂未实现)
在 AstrBot WebUI 的插件市场中搜索 **Group Keeper** 或 **群管理插件**，点击安装即可。

### 方式二：手动安装
```bash
cd /path/to/AstrBot/data/plugins
git clone https://github.com/SSJ-ZYJ/astrbot_plugin_group_keeper.git
```

---

## 📖 使用说明

### 指令前缀

所有指令使用 `/bot` 作为前缀。支持中英文双语指令输入。

### 指令列表

| 中文指令 | 英文指令 | 功能描述 | 权限要求 |
|----------|----------|----------|----------|
| `/bot help` | `/bot help` | 显示帮助信息 | 全体 |
| `/bot welcome on/off` | `/bot welcome on/off` | 设置新人欢迎功能 | 管理员 |
| `/bot add_admin <qq>` | `/bot add_admin <qq>` | 添加管理员 | 管理员 |
| `/bot remove_admin <qq>` | `/bot remove_admin <qq>` | 移除管理员 | 管理员 |
| `/bot list_admins` | `/bot list_admins` | 列出所有管理员 | 全体 |
| `/bot mute @用户 [秒数]` | `/bot mute @user [seconds]` | 禁言指定用户 | 管理员 |
| `/bot unmute @用户` | `/bot unmute @user` | 解除禁言 | 管理员 |
| `/bot global_mute on/off` | `/bot global_mute on/off` | 全体禁言控制 | 管理员 |
| `/bot ban @用户` | `/bot ban @user` | 拉黑用户 | 管理员 |
| `/bot recall @用户 [数量]` | `/bot recall @user [count]` | 撤回消息 | 管理员 |
| `/bot rename @用户 昵称` | `/bot rename @user name` | 修改群名片 | 管理员 |
| `/bot title @用户 头衔` | `/bot title @user title` | 设置头衔 | 群主 |
| `/bot promote @用户` | `/bot promote @user` | 设置管理员 | 群主 |
| `/bot demote @用户` | `/bot demote @user` | 取消管理员 | 群主 |
| `/bot set_group_name 名称` | `/bot set_group_name name` | 修改群名称 | 管理员 |
| `/bot announce 内容` | `/bot announce content` | 发布群公告 | 管理员 |
| `/bot list_announcements` | `/bot list_announcements` | 查看公告列表 | 全体 |

### 使用示例

```bash
# 开启新人欢迎
/bot welcome on

# 添加管理员
/bot add_admin 123456789

# 禁言用户 5 分钟
/bot mute @张三 300

# 发布群公告
/bot announce 请注意，明天下午有重要会议！
```

---

## ⚙️ 配置说明

插件配置文件自动存储于 `data/group_keeper/config.json`：

```json
{
  "welcome_enabled": true,
  "admin_list": ["123456789", "987654321"]
}
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `welcome_enabled` | bool | true | 是否开启新人欢迎消息 |
| `admin_list` | list | [] | 管理员QQ号列表 |

---

## 🌍 国际化支持

插件支持中文和英文两种语言，自动根据用户设置切换。

语言包文件位于 `locales/` 目录：
- `locales/zh_CN.json` - 中文语言包
- `locales/en_US.json` - 英文语言包

---

## 🛡️ 权限说明

| 权限等级 | 说明 | 可执行操作 |
|----------|------|------------|
| 成员 | 普通群成员 | 查看帮助、查看公告、查看管理员列表 |
| 管理员 | 群管理员 | 禁言、解禁、拉黑、撤回、改昵称、发公告 |
| 群主 | 群创建者 | 所有操作，包括设置管理员 |

---

## 📋 开发原则

本插件严格遵循 AstrBot 插件开发规范：

| 原则 | 状态 | 说明 |
|------|------|------|
| ✅ 功能测试 | 已完成 | 所有功能经过测试验证 |
| ✅ 良好注释 | 已完成 | 代码包含清晰的注释说明 |
| ✅ 数据持久化 | 已完成 | 数据存储于 `data` 目录 |
| ✅ 错误处理 | 已完成 | 完善的异常处理机制 |
| ✅ 代码格式化 | 已完成 | 使用 `ruff` 格式化代码 |
| ✅ 异步请求 | 已完成 | 使用异步网络请求库 |
| ✅ 国际化支持 | 已完成 | 支持中英文双语 |

---

## 🔧 技术栈

- **框架**: AstrBot SDK
- **语言**: Python 3.10+
- **异步框架**: Asyncio
- **国际化**: JSON 语言包

---

## 📱 支持平台

- QQ (aiocqhttp)

---

## 📌 版本要求

- AstrBot >= v4.5.0

---

## 📄 许可证

GNU Affero General Public License v3

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

*Made with ❤️ for HTS Team*