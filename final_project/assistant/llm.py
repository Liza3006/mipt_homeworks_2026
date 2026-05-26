import json
from http.client import HTTPConnection
from urllib.parse import urlparse

from .config import AppConfig
from .session import Message


class LLM:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def _split_host(self) -> tuple[str, int | None, str]:
        url = urlparse(self._config.api_host)
        hostname = url.hostname or 'localhost'
        port = url.port
        prefix = url.path.rstrip('/')
        return hostname, port, prefix

    def generate(self, messages: list[Message], timeout: float | None = None) -> str:
        payload = {
            'model': 'gemma3:4b',
            'messages': messages,
            'temperature': self._config.temperature,
        }
        host, port, prefix = self._split_host()

        body = json.dumps(payload)
        connection = HTTPConnection(host, port, timeout=timeout)

        try:
            connection.request(
                'POST',
                f'{prefix}/chat/completions',
                body=body,
                headers={
                    'Authorization': f'Bearer {self._config.api_key}',
                    'Content-Type': 'application/json',
                },
            )
            response = connection.getresponse()
            data = json.loads(response.read().decode('utf-8'))

            if response.status >= 400:
                raise RuntimeError(f'HTTP {response.status}: {data}')

            choices = data.get('choices', [])
            if not choices:
                raise RuntimeError('Empty response from model')

            content = choices[0].get('message', {}).get('content', '')
            if not content:
                raise RuntimeError('Empty assistant content')

            return str(content)
        finally:
            connection.close()
