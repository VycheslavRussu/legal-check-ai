import requests
import json
import os


current_dir = os.path.dirname(__file__)
absolute_path = os.path.join(current_dir, '../../secrets.json')

try:
    with open(absolute_path, 'r') as secrets_file:
        secrets = json.load(secrets_file)

    GPT_API_KEY = secrets.get("GPT_API_KEY")
    FOLDER_ID = secrets.get("FOLDER_ID")

except Exception as e:
    GPT_API_KEY = os.environ.get("GPT_API_KEY")
    FOLDER_ID = os.environ.get("FOLDER_ID")


class YandexGPT:
    """
    Класс YandexGPT конфигурирует параметры модели,
    Метод send_response, отправляет запрос к модели.
    На вход передаем контекст из сообщений, на выходе получаем dict
    с ответом модели
    """

    def __init__(self):
        self.__FOLDER_ID = FOLDER_ID
        self.__API_KEY = GPT_API_KEY

    # Model Params
    stream = False
    temperature = 0.3
    max_tokens = "500"

    def send_response(self, context_messages: list[dict]):
        prompt = {
            "modelUri": "gpt://" + self.__FOLDER_ID + "/yandexgpt-lite",
            "completionOptions": {
                "stream": self.stream,
                "temperature": self.temperature,
                "maxTokens": self.max_tokens
            },
            "messages": context_messages
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key " + self.__API_KEY
        }

        response = requests.post(url, headers=headers, json=prompt)
        result = response.text

        return result


class ContextStorage:
    """
    Должен содержать лист диктов со всем контекстом общения
    На вход должен получать dict с сообщением
    На выходе должен отдавать список со всеми сообщениями (контекст)
    """

    def __init__(self):
        self.__context_storage = []
        self.__tokens_count = 0
        pass

    def set_default_context(self, default_context: list):
        """
        Принимает на вход список из сообщений с базовым контекстом,
        который мы задаем.
        Добавляет каждое сообщение в context_storage
        :param default_context:  список из словарей,
        в котором храним первичные настройки модели
        """
        for message in default_context:
            self.__context_storage.append(message)
            self.__tokens_count += len(message["text"]) // 5
        pass

    def get_context(self):
        return self.__context_storage

    def add_context(self, message):
        self.__context_storage.append(message)
        self.__tokens_count += len(message["text"]) // 5
        pass

    def get_approximate_tokens_count(self):
        return self.__tokens_count

    def delete_message_from_context(self):
        self.__tokens_count -= len(self.__context_storage[3]["text"]) // 5
        self.__context_storage.pop(3)
        pass


def normalize(user_message: str):
    normalized_message = {
        "role": "user",
        "text": user_message
    }
    return normalized_message


class UseCase:
    """
    1. Создать экземпляр класс, передать в него секреты
    2. Вызвать метод setup_context и задать дефолтный контекст для модели
    3. Вызывать метод execute и отправить в нем текст документа
    4. Вызывать метод execute для общения с моделью
    """

    def __init__(self):
        self.context_storage = ContextStorage()
        self.yandex_gpt = YandexGPT()
        # Задаем дефолтный контекст для модели
        self.context_storage.set_default_context(self.setup_messages)
        pass

    # Начальный контекст, передаем сюда промт и первое сообщение пользователя
    setup_messages = [
        {
            "role": "system",
            "text": """Ты — опытный юрист,
                       который разбирается в гражданском праве
                       и сделках с недвижимостью.
                       Твоя роль — внимательно и полностью
                       прочитать текст договора,
                       который отправит пользователь,
                       а также найти и показать пользователю
                       все ошибки и подозрительные пункты,
                       которые будут в этом договоре."""
        },
        {
            "role": "user",
            "text": """Привет, дорогая модель!
                       Следующим сообщением я отправлю тебе текст
                       гражданского договора купли продажи.
                       Пожалуйста, прочитай его внимательно и укажи
                       на подозрительные пункты в нем, которые могут
                       потенциально наведить мне."""
        }
    ]

    def execute(self, message: str):
        """
        Функция, которая отвечает за отправку и прием сообщений от пользователя
        :param message: на вход прининимает строку с вопросом к модели
        :return: возращает строку, в которой содержется ответ модели на вопрос
        Попутно добавляет сообщения в контекст
        """

        # Нормализуем сообщение от пользователя
        # (превращаем строку в словарь и добавляем параметр с ролью)
        # Сохраняем сообщение от пользователя в context storage
        self.context_storage.add_context(normalize(message))

        # Отправляем запрос на модель.
        # В запросе передаем контекст, который содержится в context_storage
        # В ответ получаем словарь с ответом модели,
        # из которого достаем message
        reply = json.loads(self.yandex_gpt.send_response(
            self.context_storage.get_context()
            ))
        reply_message = reply["result"]["alternatives"][0]["message"]

        # Сохраняем ответ модели в context_storage
        self.context_storage.add_context(reply_message)

        # Возращаем строку с ответом модели
        return reply_message["text"]

    def operate(self, message: str):
        if self.context_storage.get_approximate_tokens_count() < 6000:
            return self.execute(message)
        else:
            while self.context_storage.get_approximate_tokens_count() > 6000:
                self.context_storage.delete_message_from_context()
            return self.execute(message)
