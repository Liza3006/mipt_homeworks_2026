Message = dict[str, str]

class ChatSession:
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def clear(self) -> None:
        self.messages.clear()

    def _trim(self, content: str, limit_chars: int | None) -> str:
        if limit_chars is not None and len(content) > limit_chars:
            return content[-limit_chars:]
        return content

    def _add(
        self,
        role: str,
        content: str,
        limit_message: int | None,
        limit_chars: int | None,
    ) -> str:
        content = self._trim(content, limit_chars)
        self.messages.append({'role': role, 'content': content})

        while self.messages:
            if limit_message is not None and len(self.messages) > limit_message:
                self.messages.pop(0)
            elif (
                limit_chars
                and sum(len(m['content']) for m in self.messages) > limit_chars
            ):
                self.messages.pop(0)
            else:
                break

        return content

    def add_user_message(
        self,
        content: str,
        limit_message: int | None,
        limit_chars: int | None,
    ) -> str:
        return self._add('user', content, limit_message, limit_chars)

    def add_assistant_message(
        self,
        content: str,
        limit_message: int | None,
        limit_chars: int | None,
    ) -> str:
        return self._add('assistant', content, limit_message, limit_chars)

    def api_messages(self, system_prompt: str | None = None) -> list[Message]:
        if system_prompt:
            return [{'role': 'system', 'content': system_prompt}] + self.messages
        return self.messages.copy()