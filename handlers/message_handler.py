from __future__ import annotations

from astrbot.api.message_components import Node, Plain


class MessageHandler:
    """Handles message sending with support for long message merging.

    处理消息发送，支持长消息自动合并发送。
    """

    DEFAULT_MAX_LENGTH = 350

    @staticmethod
    def split_message(text: str, max_length: int = DEFAULT_MAX_LENGTH) -> list[str]:
        """Split a long message into chunks with specified max length.

        将长消息按指定长度拆分为多个片段。

        Args:
            text: The message text to split.
            max_length: Maximum length per chunk (default: 350).

        Returns:
            List of message chunks.
        """
        chunks = []
        text = text.strip()

        while len(text) > max_length:
            # Find a good split point. / 寻找合适的拆分位置。
            split_at = max_length

            # Try to split at newline first. / 优先按换行拆分。
            newline_pos = text.rfind("\n", 0, max_length)
            if newline_pos > max_length // 2:
                split_at = newline_pos + 1
            else:
                # Try to split at sentence ending. / 再尝试按句末拆分。
                for char in ["。", "！", "？", "；", ":", ";", ".", "!", "?"]:
                    pos = text.rfind(char, 0, max_length)
                    if pos > max_length // 2:
                        split_at = pos + 1
                        break

            chunks.append(text[:split_at].strip())
            text = text[split_at:].strip()

        if text:
            chunks.append(text)

        return chunks

    @staticmethod
    def build_merged_message(
        self_id: str,
        messages: list[str],
        node_name: str,
    ) -> list[Node]:
        """Build a merged message chain from message chunks.

        由多个消息片段构造合并转发消息链。

        Args:
            self_id: The bot's own ID.
            messages: List of message chunks to merge.
            node_name: Display name shown on each merged node.

        Returns:
            List of Node components for merged message.
        """
        nodes = []
        for msg in messages:
            nodes.append(Node(uin=self_id, name=node_name, content=[Plain(msg)]))
        return nodes

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
