# ИИ-ассистент

## Переменные окружения:

- API_KEY
- API_HOST
- LIMIT_MESSAGE
- LIMIT_CHARS
- TEMPERATURE

config.yaml:

api_key: ollama
api_host: http://localhost:11434/v1/
limit_message: 20
limit_chars: 2000
temperature: 0.7
model: gemma3:4b
system_prompt: You are a helpful AI assistant.



## Команды:
- \q — выход
- /reset — очистить историю и экран
- /file_chunk, /filechunk — режим обработки файла


## Установка:
- brew install ollama
- ollama pull gemma3:4b

## Запуск:
- ollama serve
- python main.py

## Файлы проекта
- cli.py — консольный интерфейс, обработка команд (/reset, /file_chunk и т.д.)
- config.py — загрузка настроек 
- files.py — чтение текстовых файлов
- llm.py — взаимодействие с Ollama
- session.py — хранение истории сообщений