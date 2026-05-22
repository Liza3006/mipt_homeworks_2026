import os
from .config import load_config
from .files import expand_file_markers, read_text_file, chunk_text
from .llm import LLM
from .session import ChatSession

def clear_screen():
    os.system('clear')

def run():
    try:
        config = load_config()
    except ValueError as e:
        print(e)
        return 1
    if not config:
        print('Не найдены настройки')
        return 1

    client = LLM(config)
    session = ChatSession()

    while True:
        user_input = input('>>> ').strip()
        if not user_input:
            continue

        if user_input == '\\q':
            return 0

        if user_input == '/reset':
            session.clear()
            clear_screen()
            continue

        if user_input.startswith('/file_chunk') or user_input.startswith('/filechunk'):
            parts = user_input.split()
            auto = '-y' in parts
            mode = 'paragraph'
            paragraph_size = 1
            chunk_len = 0
            for p in parts:
                if p.startswith('paragraph='):
                    mode = 'paragraph'
                    paragraph_size = int(p.split('=')[1])
                elif p.startswith('len='):
                    mode = 'length'
                    chunk_len = int(p.split('=')[1])

            file_path = input('>>> Введите путь до файла\n').strip()
            user_prompt = input('>>> Что нужно сделать для каждого фрагмента?\n').strip()

            try:
                text = read_text_file(file_path)
                chunks = chunk_text(text, mode=mode, paragraph_size=paragraph_size, chunk_length=chunk_len)
            except (FileNotFoundError, IsADirectoryError, ValueError) as e:
                print(e)
                continue

            if not chunks:
                print('Файл пуст.')
                continue

            print('Принято. Начинаю обработку:')
            for i, chunk in enumerate(chunks):
                messages = [{'role': 'user', 'content': f'{user_prompt}\n\n{chunk}'}]
                try:
                    answer = client.generate(messages)
                except KeyboardInterrupt:
                    print()
                    break
                except Exception as e:
                    print(e)
                    break
                print(answer)
                if not auto and i < len(chunks) - 1:
                    if input('>>> ').strip() != '':
                        break
            else:
                print('Обработка файла завершена.')
            continue

        try:
            user_text = expand_file_markers(user_input)
            session.add_user_message(user_text, config.limit_message, config.limit_chars)
            messages = session.api_messages(config.system_prompt)
            answer = client.generate(messages)
        except (FileNotFoundError, IsADirectoryError, ValueError) as e:
            print(e)
            continue
        except KeyboardInterrupt:
            print()
            continue
        except Exception as e:
            print(e)
            continue

        print(answer)
        session.add_assistant_message(answer, config.limit_message, config.limit_chars)
