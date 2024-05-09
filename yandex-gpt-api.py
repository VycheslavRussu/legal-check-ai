import requests
import json

secrets_file = open("secrets.json")
secrets = json.load(secrets_file)

API_KEY = secrets["API_KEY"]
ENV = secrets["ENV"]


messages = [{
                "role": "system",
                "text": "Ты опытный юрист, который разберается в гражданском праве и сделках с недвижимостью."
            },
            {
                "role": "user",
                "text": "Привет! Прочитай пожалуйста договор о купле-продаже квартиры и найди в нем ошибки или подозрительные пункты."
            }]

# print(text["result"]["alternatives"][0]["message"]["text"])


# ——————————————————————————————————————————————————————————————————————————————

class YandexGPT:
    """
    Класс YandexGPT конфигурирует параметры модели,
    Метод send_response, отправляет запрос к модели. На вход передаем контекст из сообщений, на выходе получаем dict
    с ответом модели
    """
    def __init__(self, folder_id, api_key):
        self.__FOLDER_ID = folder_id
        self.__API_KEY = api_key

    # Параметры модели
    stream = False
    temperature = 0.3
    max_tokens = "100"

    def send_response(self, context_messages: list[dict]) -> dict:
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


# yandex_api = YandexGPT(ENV, API_KEY)
# response = yandex_api.send_response(messages)

# print(response)




class ContextStorage:
    # Должен содержать лист диктов со всем контекстом общения
    # На вход должен получать dict с сообщением
    # На выходе должен отдавать список со всеми сообщениями (контекст)

    def __init__(self):


# class UseCases:

    # API Yandex
    # 0. Конфигурируем среду, передаем секреты
    # 1. Подключиться к серверу
    # 2. Запросить контекст и Storage
    # 3. Передать весь контекст в модель
    # 4. Получить json в ответ и сохранить его

    # Storage API
    # 1. Передаем в него сообщения от пользователя, сохраняем его
    # 2. Передаем в него ответы от модели, сохраняем их
    # 3. По запросу отдаем сообщения из хранилища

    # UseCasesAPI
    # 1. Получаем сообщение от пользователя
    # 2. Вызываем функцию сохранения в классе Storage и сохраняем сообщение от пользователя
    # 3. Вызываем функцию из класса Storage, забираем весь контекст который в ней хранится
    # 4. Вызываем класс YandexAPI, передаем в него весь контекст, получаем json с ответом
    # 5. Достаем message из json'a, отправляем его в Storage
    # 6. Показываем пользователю ответ

