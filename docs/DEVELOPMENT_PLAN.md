# AstrBot QQ群管理插件开发计划

> 本文档描述了 QQ群管理插件（Group Keeper）的完整开发计划和技术设计。

---

## 1. 项目概述

### 1.1 项目简介

本插件旨在为 **HTS Team** 提供专业的 QQ 群管理功能，参考成熟插件 `astrbot_plugin_qqadmin` 的设计思路，实现核心管理功能。

### 1.2 设计目标

| 目标 | 描述 |
|------|------|
| 🎯 功能完善 | 提供全面的群管理功能 |
| 🔒 权限控制 | 实现灵活的权限层级机制 |
| 💾 数据持久化 | 支持配置数据持久化存储 |
| ⚠️ 错误处理 | 提供友好的错误处理和用户提示 |
| 🌍 国际化 | 支持中英文双语版本 |

---

## 2. 插件架构设计

### 2.1 目录结构

```
astrbot_plugin_group_keeper/
├── main.py                 # 主插件入口
├── metadata.yaml           # 插件元数据
├── requirements.txt        # 依赖声明
├── README.md               # 使用说明
├── LICENSE                 # 许可证
├── docs/                   # 文档目录
│   └── DEVELOPMENT_PLAN.md # 开发计划文档
├── handlers/               # 功能处理器目录
│   ├── __init__.py
│   ├── group_handler.py    # 群管理功能
│   ├── notice_handler.py   # 公告管理功能
│   └── join_handler.py     # 进群管理功能
└── locales/                # 国际化资源文件
    ├── zh_CN.json          # 中文语言包
    └── en_US.json          # 英文语言包
```

### 2.2 核心类设计

| 类名 | 职责 | 关键方法 |
|------|------|----------|
| `GroupKeeperPlugin` | 插件主类 | `initialize()`, `terminate()` |
| `GroupHandler` | 群管理处理器 | `mute()`, `ban()`, `recall()` |
| `NoticeHandler` | 公告处理器 | `publish()`, `list()` |
| `JoinHandler` | 进群处理器 | `welcome()`, `audit()` |
| `I18nManager` | 国际化管理器 | `get()` |

---

## 3. 功能开发计划

### Phase 1: 基础框架搭建

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| 1.1 | 创建插件目录结构 | 高 | ⏳ |
| 1.2 | 编写 `metadata.yaml` 元数据 | 高 | ⏳ |
| 1.3 | 实现插件主类框架 | 高 | ⏳ |
| 1.4 | 配置数据持久化（使用 `data` 目录） | 高 | ⏳ |
| 1.5 | 实现国际化管理器 | 高 | ⏳ |

### Phase 2: 核心群管理功能

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| 2.1 | 禁言/解禁功能 | 高 | ⏳ |
| 2.2 | 全体禁言控制 | 高 | ⏳ |
| 2.3 | 拉黑功能 | 高 | ⏳ |
| 2.4 | 撤回消息功能 | 中 | ⏳ |

### Phase 3: 进阶管理功能

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| 3.1 | 修改群昵称 | 中 | ⏳ |
| 3.2 | 设置头衔 | 中 | ⏳ |
| 3.3 | 设管理员/取消管理员 | 高 | ⏳ |
| 3.4 | 修改群名称 | 中 | ⏳ |

### Phase 4: 公告与进群管理

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| 4.1 | 发布群公告 | 中 | ⏳ |
| 4.2 | 查看群公告 | 中 | ⏳ |
| 4.3 | 进群欢迎消息 | 高 | ⏳ |
| 4.4 | 进群审核功能 | 低 | ⏳ |

### Phase 5: 权限控制与测试

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| 5.1 | 实现权限层级控制 | 高 | ⏳ |
| 5.2 | 添加错误处理机制 | 高 | ⏳ |
| 5.3 | 完善中英文翻译 | 中 | ⏳ |
| 5.4 | 测试所有功能 | 高 | ⏳ |
| 5.5 | 更新 README 文档 | 中 | ⏳ |

---

## 4. API 使用规范

### 4.1 导入方式

```python
from astrbot.api import star
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api import logger
```

### 4.2 消息发送方式

```python
# 发送文本消息
event.set_result(MessageEventResult().message("消息内容"))

# 发送复杂消息（如图片、@用户等）
from astrbot.api.message_components import Plain, At, Image
event.set_result(MessageEventResult().message([Plain("Hello"), At(qq="123456")]))
```

### 4.3 权限控制

```python
def _check_permission(self, event: AstrMessageEvent, required_level: int) -> bool:
    """检查用户权限等级"""
    # 1: 成员, 2: 管理员, 3: 群主, 4: 超级管理员
    pass
```

---

## 5. 国际化（i18n）支持

### 5.1 设计目标

插件应支持中文和英文两个版本，所有用户可见的文本均不应硬编码，需通过国际化资源文件管理。

### 5.2 语言包结构

#### 中文语言包 (`locales/zh_CN.json`)
```json
{
  "help_title": "📖 群管理插件帮助",
  "msg_no_permission": "❌ 权限不足，只有管理员可以执行此操作",
  "msg_welcome_enabled": "✅ 新人欢迎功能已开启"
}
```

#### 英文语言包 (`locales/en_US.json`)
```json
{
  "help_title": "📖 Group Manager Plugin Help",
  "msg_no_permission": "❌ Insufficient permissions. Only admins can perform this action.",
  "msg_welcome_enabled": "✅ Welcome message enabled"
}
```

### 5.3 国际化工具类设计

```python
class I18nManager:
    """国际化管理器"""
    
    def __init__(self, plugin_path: Path):
        self.locales_dir = plugin_path / "locales"
        self.translations = {}
        self._load_locales()
    
    def _load_locales(self):
        """加载所有语言包"""
        for locale_file in self.locales_dir.glob("*.json"):
            locale_code = locale_file.stem
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations[locale_code] = json.load(f)
    
    def get(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """获取翻译文本"""
        locale = locale if locale in self.translations else "zh_CN"
        text = self.translations[locale].get(key, key)
        return text.format(**kwargs)
```

### 5.4 语言检测策略

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 用户配置 | 用户在插件设置中指定的语言 |
| 2 | 消息上下文 | 从消息事件中获取的用户语言偏好 |
| 3 | 系统默认 | AstrBot 全局语言设置 |
| 4 | 回退语言 | 默认使用中文 (zh_CN) |

---

## 6. 数据持久化方案

配置文件存储于 `data/group_keeper/` 目录：

```
data/group_keeper/
├── config.json          # 全局配置
└── groups/              # 各群配置目录
    ├── group_123456.json
    └── group_654321.json
```

---

## 7. 指令设计

### 7.1 指令前缀

所有指令使用 `/bot` 作为前缀。

### 7.2 指令列表（中英文对照）

| 中文指令 | 英文指令 | 功能 | 权限要求 |
|----------|----------|------|----------|
| `/bot help` | `/bot help` | 显示帮助 | 全体 |
| `/bot welcome on/off` | `/bot welcome on/off` | 欢迎消息控制 | 管理员 |
| `/bot add_admin <qq>` | `/bot add_admin <qq>` | 添加管理员 | 管理员 |
| `/bot remove_admin <qq>` | `/bot remove_admin <qq>` | 移除管理员 | 管理员 |
| `/bot list_admins` | `/bot list_admins` | 列出管理员 | 全体 |
| `/bot mute @用户 [秒数]` | `/bot mute @user [seconds]` | 禁言用户 | 管理员 |
| `/bot unmute @用户` | `/bot unmute @user` | 解除禁言 | 管理员 |
| `/bot global_mute on/off` | `/bot global_mute on/off` | 全体禁言 | 管理员 |
| `/bot ban @用户` | `/bot ban @user` | 拉黑用户 | 管理员 |
| `/bot recall @用户 [数量]` | `/bot recall @user [count]` | 撤回消息 | 管理员 |
| `/bot rename @用户 昵称` | `/bot rename @user name` | 修改群名片 | 管理员 |
| `/bot title @用户 头衔` | `/bot title @user title` | 设置头衔 | 群主 |
| `/bot promote @用户` | `/bot promote @user` | 设置管理员 | 群主 |
| `/bot demote @用户` | `/bot demote @user` | 取消管理员 | 群主 |
| `/bot set_group_name 名称` | `/bot set_group_name name` | 修改群名称 | 管理员 |
| `/bot announce 内容` | `/bot announce content` | 发布公告 | 管理员 |
| `/bot list_announcements` | `/bot list_announcements` | 查看公告 | 全体 |

---

## 8. 实施建议

1. **权限优先**：先实现权限控制机制，确保只有授权用户才能执行管理操作
2. **核心功能优先**：先实现禁言、拉黑等核心功能
3. **渐进式开发**：每完成一个功能模块就进行测试验证
4. **错误处理**：为每个功能添加完善的异常处理和错误提示
5. **国际化优先**：在实现功能时同步添加中英文翻译

---

## 9. 开发原则

遵循 AstrBot 插件开发规范：

| 原则 | 说明 |
|------|------|
| ✅ 功能测试 | 所有功能需经过测试验证 |
| ✅ 良好注释 | 代码需要清晰的注释说明 |
| ✅ 数据持久化 | 存储于 `data` 目录，而非插件目录 |
| ✅ 错误处理 | 完善的异常处理机制 |
| ✅ 代码格式化 | 使用 `ruff` 格式化代码 |
| ✅ 异步请求 | 使用 `aiohttp`/`httpx` 异步库 |
| ✅ 国际化支持 | 所有用户可见文本不应硬编码 |

---

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | - | 初始版本 |

---

*Last updated: 2026-05-03*