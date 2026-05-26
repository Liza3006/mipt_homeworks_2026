from pathlib import Path
import re

MAX_FILE_SIZE = 5 * 1024 * 1024
FILE_MARKER_RE = re.compile(r'@::(.+?)::')


def read_text_file(path: str | Path) -> str:
    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(str(file_path))
    if not file_path.is_file():
        raise IsADirectoryError(str(file_path))
    return file_path.read_text(encoding='utf-8')

def expand_file_markers(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        path = match.group(1).strip()
        content = read_text_file(path)
        return f'\n{content}'

    return FILE_MARKER_RE.sub(replace, text)


def chunk_text(
    text: str,
    mode: str = 'paragraph',
    paragraph_size: int = 1,
    chunk_length: int = 0,
) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    if mode == 'paragraph':
        if paragraph_size < 1:
            raise ValueError('paragraph_size must be positive')
        paragraphs = [part.strip() for part in stripped.split('\n\n') if part.strip()]
        return [
            '\n\n'.join(paragraphs[index:index + paragraph_size])
            for index in range(0, len(paragraphs), paragraph_size)
        ]
    if mode == 'length':
        if chunk_length < 1:
            raise ValueError('chunk_length must be positive')
        return [
            stripped[index:index + chunk_length]
            for index in range(0, len(stripped), chunk_length)
        ]
    raise ValueError(f'unknown mode: {mode}')








