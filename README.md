# QQ群管理插件 (Group Keeper)

一个用于管理 QQ 群聊的 AstrBot 插件，专为 HTS Team 设计。支持中英文双语。

---

## ✨ 功能特性

| 功能分类 | 功能描述 |
|----------|----------|
| 🎉 新人欢迎 | 自动欢迎新成员加入群聊，支持 `{membername}` 变量显示昵称 |
| 🔇 禁言管理 | 支持单个禁言、解禁、全员禁言 |
| 📝 消息管理 | 撤回指定用户消息 |
| 🏷️ 群名片管理 | 修改群昵称、设置专属头衔 |
| 📢 公告管理 | 发布群公告，支持置顶 |
| 🔧 权限控制 | 自动同步群内管理员角色，群主和管理员可操作 |

---

## 📦 安装方式

### 方式一：插件市场安装
在 AstrBot WebUI 的插件市场中搜索 **Group Keeper** 或 **群管理插件**，点击安装即可。

### 方式二：手动安装
```bash
cd /path/to/AstrBot/data/plugins
git clone https://github.com/SSJ-ZYJ/astrbot_plugin_group_keeper.git
```

---

## 📖 使用说明

### 指令前缀

所有指令使用 `/bot` 或 `/机器人` 作为前缀。每个指令都支持中英文别名。

### 指令列表

| 指令 | 中文别名 | 功能描述 | 权限要求 |
|------|----------|----------|----------|
| `/bot help` | `/bot 帮助` | 显示帮助信息 | 全体 |
| `/bot welcome [on\|off\|message <文本>]` | `/bot 欢迎` | 新人欢迎设置（支持 `{membername}` 变量） | 管理员 |
| `/bot mute <QQ> [秒数]` | `/bot 禁言` | 禁言指定用户 | 管理员 |
| `/bot unmute <QQ>` | `/bot 解禁` | 解除禁言 | 管理员 |
| `/bot global_mute on\|off` | `/bot 全员禁言` | 全员禁言控制 | 管理员 |
| `/bot recall <QQ> [数量]` | `/bot 撤回` | 撤回指定用户消息 | 管理员 |
| `/bot rename <QQ> <昵称>` | `/bot 改名` | 修改群昵称 | 管理员 |
| `/bot title <QQ> <头衔>` | `/bot 头衔` | 设置专属头衔 | 管理员 |
| `/bot promote <QQ>` | `/bot 提升` | 提升为管理员 | 管理员 |
| `/bot demote <QQ>` | `/bot 降级` | 移除管理员 | 管理员 |
| `/bot set_group_name <名称>` | `/bot 设置群名` | 修改群名称 | 管理员 |
| `/bot announce <内容>` | `/bot 公告` | 发布群公告 | 管理员 |

> **注意**: `<QQ>` 参数支持 @提及 或直接输入 QQ 号。

### 使用示例

```bash
# 开启新人欢迎
/bot welcome on
/机器人 欢迎 on

# 禁言用户 5 分钟
/bot mute @张三 300
/机器人 禁言 @张三 300

# 发布群公告
/bot announce 请注意，明天下午有重要会议！
/机器人 公告 请注意，明天下午有重要会议！

# 设置专属头衔
/bot title @张三 优秀成员
/机器人 头衔 @张三 优秀成员
```

### 欢迎消息变量

欢迎消息支持以下变量，发送时会自动替换为实际值：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{membername}` | 新成员的群昵称/昵称 | 欢迎 张三 加入群聊！ |

示例：设置自定义欢迎消息
```
/bot welcome message 欢迎 {membername} 加入群聊，请阅读群公告！
/机器人 欢迎 message 欢迎 {membername} 加入群聊，请阅读群公告！
```

---

## ⚙️ 配置说明

插件配置通过 AstrBot WebUI 管理，包含以下选项：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `locale` | 选择 | zh_CN | 插件显示语言（简体中文 / English） |
| `default_mute_duration` | 整数 | 60 | 默认禁言时长（秒） |
| `default_welcome_enabled` | 布尔 | true | 新人欢迎默认开启 |
| `default_welcome_message` | 文本 | (空) | 默认欢迎消息，留空使用语言包。支持 `{membername}` 变量 |
| `max_recall_count` | 整数 | 10 | 单次最多撤回消息条数 |
| `default_announce_confirm_required` | 布尔 | false | 公告是否需要群成员确认 |
| `default_announce_pinned` | 布尔 | false | 公告是否默认置顶 |

### 群组数据

每个群的独立配置（欢迎开关、欢迎消息、公告记录）自动存储在 `data/astrbot_plugin_group_keeper/groups/` 目录下。

---

## 🌍 国际化支持

插件支持中文和英文两种语言：

- **机器人消息语言**：通过配置文件中的 `locale` 选项切换（`zh_CN` / `en_US`），控制机器人在群聊中的回复语言。
- **WebUI 配置页语言**：通过 AstrBot WebUI 右上角的语言切换器切换，自动显示对应语言的配置描述。

---

## 🛡️ 权限说明

| 权限等级 | 说明 | 可执行操作 |
|----------|------|------------|
| 成员 | 普通群成员 | 查看帮助 |
| 管理员 | 群内真实管理员 | 禁言、解禁、撤回、改名、发公告、设置头衔、提升/降级管理员 |
| 群主 | 群创建者 | 所有管理员操作 |

> **重要**: 权限自动同步群内真实的管理员角色，无需手动添加。

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
