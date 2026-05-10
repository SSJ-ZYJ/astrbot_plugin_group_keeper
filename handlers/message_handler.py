from __future__ import annotations

from astrbot.api.message_components import Node, Plain


class MessageHandler:
    """Handles long-message wrapping for merged forwarding.

    处理长消息合并转发封装，不再拆分消息内容。
    """

    DEFAULT_MAX_LENGTH = 350

    @staticmethod
    def build_merged_message(
        self_id: str,
        message: str,
        node_name: str,
    ) -> list[Node]:
        """Build a single-node merged message from the full text.

        使用完整文本构造单节点合并转发消息。

        Args:
            self_id: The bot's own ID.
            message: Full message text, kept intact.
            node_name: Display name shown on each merged node.

        Returns:
            A one-node merged message component list.
        """
        return [Node(uin=self_id, name=node_name, content=[Plain(message)])]

    @staticmethod
    def needs_merge(message: str, max_length: int = DEFAULT_MAX_LENGTH) -> bool:
        """Check if a message needs to be sent as merged message.

        判断消息是否需要以合并消息形式发送。

        Args:
            message: The message text.
            max_length: Maximum length before merging (default: 350).

        Returns:
            True if message exceeds max_length, False otherwise.
        """
        return len(message.strip()) > max_length
