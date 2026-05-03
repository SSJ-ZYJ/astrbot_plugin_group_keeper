from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from pathlib import Path
import json
import asyncio

@register(
    name="qq_group_keeper",
    author="SSJ-ZYJ",
    description="一个用来管理 QQ群聊 的 Astrbot 插件，用于管理 HTS Team，满足 HTS 管理需求",
    version="1.0.0",
    repo="https://github.com/SSJ-ZYJ/astrbot_plugin_group_keeper"
)
class GroupKeeperPlugin(Star):
    """QQ群管理插件主类
    
    提供群成员管理、公告管理等功能
    """
    
    def __init__(self, context: Context):
        super().__init__(context)
        self.data_path = Path(context.data_dir) / "group_keeper"
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.welcome_enabled = True
        self.admin_list = []
        asyncio.create_task(self._load_config())

    async def _load_config(self):
        """异步加载配置文件"""
        config_file = self.data_path / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.welcome_enabled = config.get('welcome_enabled', True)
                    self.admin_list = config.get('admin_list', [])
                logger.info("群管理插件配置加载成功")
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
        else:
            await self._save_config()

    async def _save_config(self):
        """异步保存配置文件"""
        config_file = self.data_path / "config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'welcome_enabled': self.welcome_enabled,
                    'admin_list': self.admin_list
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

    async def initialize(self):
        """插件初始化方法"""
        logger.info("QQ群管理插件初始化完成")

    @filter.command_group("group")
    async def group_command_group(self):
        """群管理指令组"""
        pass

    @group_command_group.command("welcome")
    async def group_welcome(self, event: AstrMessageEvent, status: str = None):
        """设置新人欢迎功能
        
        参数:
            status: on/off，开启或关闭欢迎功能
        """
        try:
            if not self._is_admin(event):
                yield event.plain_result("❌ 权限不足，只有管理员可以执行此操作")
                return
            
            if status is None:
                current_status = "开启" if self.welcome_enabled else "关闭"
                yield event.plain_result(f"当前新人欢迎功能状态: {current_status}")
            elif status.lower() == "on":
                self.welcome_enabled = True
                await self._save_config()
                yield event.plain_result("✅ 新人欢迎功能已开启")
            elif status.lower() == "off":
                self.welcome_enabled = False
                await self._save_config()
                yield event.plain_result("✅ 新人欢迎功能已关闭")
            else:
                yield event.plain_result("❌ 参数错误，请使用 on 或 off")
        except Exception as e:
            logger.error(f"执行欢迎设置命令失败: {str(e)}")
            yield event.plain_result("❌ 操作失败，请稍后重试")

    @group_command_group.command("add_admin")
    async def group_add_admin(self, event: AstrMessageEvent, qq: str):
        """添加管理员
        
        参数:
            qq: 要添加的管理员QQ号
        """
        try:
            if not self._is_admin(event):
                yield event.plain_result("❌ 权限不足，只有管理员可以执行此操作")
                return
            
            if qq in self.admin_list:
                yield event.plain_result(f"❌ QQ {qq} 已经是管理员")
                return
            
            self.admin_list.append(qq)
            await self._save_config()
            yield event.plain_result(f"✅ 已添加管理员: {qq}")
        except Exception as e:
            logger.error(f"添加管理员失败: {str(e)}")
            yield event.plain_result("❌ 添加失败，请稍后重试")

    @group_command_group.command("remove_admin")
    async def group_remove_admin(self, event: AstrMessageEvent, qq: str):
        """移除管理员
        
        参数:
            qq: 要移除的管理员QQ号
        """
        try:
            if not self._is_admin(event):
                yield event.plain_result("❌ 权限不足，只有管理员可以执行此操作")
                return
            
            if qq not in self.admin_list:
                yield event.plain_result(f"❌ QQ {qq} 不是管理员")
                return
            
            self.admin_list.remove(qq)
            await self._save_config()
            yield event.plain_result(f"✅ 已移除管理员: {qq}")
        except Exception as e:
            logger.error(f"移除管理员失败: {str(e)}")
            yield event.plain_result("❌ 移除失败，请稍后重试")

    @group_command_group.command("list_admins")
    async def group_list_admins(self, event: AstrMessageEvent):
        """列出所有管理员"""
        try:
            if not self.admin_list:
                yield event.plain_result("当前没有管理员")
            else:
                admins = "\n".join([f"- {admin}" for admin in self.admin_list])
                yield event.plain_result(f"📋 管理员列表:\n{admins}")
        except Exception as e:
            logger.error(f"获取管理员列表失败: {str(e)}")
            yield event.plain_result("❌ 获取失败，请稍后重试")

    @group_command_group.command("help")
    async def group_help(self, event: AstrMessageEvent):
        """显示群管理插件帮助信息"""
        help_text = """
📖 群管理插件帮助

/group welcome [on/off] - 设置新人欢迎功能
/group add_admin <qq> - 添加管理员
/group remove_admin <qq> - 移除管理员
/group list_admins - 列出所有管理员
/group help - 显示此帮助信息

示例:
/group welcome on
/group add_admin 123456789
        """.strip()
        yield event.plain_result(help_text)

    def _is_admin(self, event: AstrMessageEvent) -> bool:
        """检查用户是否为管理员
        
        优先检查消息发送者是否在管理员列表中，
        如果列表为空则默认所有群成员都有管理权限
        """
        sender_id = event.get_sender_id()
        if not self.admin_list:
            return True
        return sender_id in self.admin_list

    async def terminate(self):
        """插件终止方法"""
        await self._save_config()
        logger.info("QQ群管理插件已终止")