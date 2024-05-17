import requests
import json

secrets_file = open("../../secrets.json")
secrets = json.load(secrets_file)

API_KEY = secrets["API_KEY"]
FOLDER_ID = secrets["FOLDER_ID"]


class YandexGPT:
    """
    Класс YandexGPT конфигурирует параметры модели,
    Метод send_response, отправляет запрос к модели. На вход передаем контекст из сообщений, на выходе получаем dict
    с ответом модели
    """

    def __init__(self):
        self.__FOLDER_ID = FOLDER_ID
        self.__API_KEY = API_KEY

    # Model Params
    stream = False
    temperature = 0.3
    max_tokens = "100"

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
        pass

    def set_default_context(self, default_context: list):
        """
        Принимает на вход список из сообщений с базовым контекстом, который мы задаем.
        Добавляет каждое сообщение в context_storage
        :param default_context:  список из словарей, в котором храним первичные настройки модели
        """
        for message in default_context:
            self.__context_storage.append(message)
        pass

    def get_context(self):
        return self.__context_storage

    def add_context(self, message):
        self.__context_storage.append(message)
        pass

    # UseCasesAPI
    # 1. Получаем сообщение от пользователя
    # 2. Вызываем функцию сохранения в классе Storage и сохраняем сообщение от пользователя
    # 3. Вызываем функцию из класса Storage, забираем весь контекст который в ней хранится
    # 4. Вызываем класс YandexAPI, передаем в него весь контекст, получаем json с ответом
    # 5. Достаем message из json'a, отправляем его в Storage
    # 6. Показываем пользователю ответ


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
        self.context_storage.set_default_context(self.setup_messages)  # Задаем дефолтный контекст для модели
        pass

    # Начальный контекст, передаем сюда промт и первое сообщение пользователя
    setup_messages = [
        {
            "role": "system",
            "text": """Ты — опытный юрист, который разбирается в гражданском праве и сделках с недвижимостью.
                           Твоя роль — внимательно и полностью прочитать текст договора, который отправит пользователь, 
                           а также найти и показать пользователю все ошибки и подозрительные пункты, которые будут в этом договоре."""
        },
        {
            "role": "user",
            "text": """Привет, дорогая модель! Следующим сообщением я отправлю тебе текст гражданского договора купли продажи. 
                           Пожалуйста, прочитай его внимательно и укажи на подозрительные пункты в нем, которые могут 
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

        # Нормализуем сообщение от пользователя (превращаем строку в словарь и добавляем параметр с ролью)
        # Сохраняем сообщение от пользователя в context storage
        self.context_storage.add_context(normalize(message))

        # Отправляем запрос на модель. В запросе передаем контекст, который содержится в context_storage
        # В ответ получаем словарь с ответом модели, из которого достаем message
        reply = json.loads(self.yandex_gpt.send_response(self.context_storage.get_context()))
        reply_message = reply["result"]["alternatives"][0]["message"]

        # Сохраняем ответ модели в context_storage
        self.context_storage.add_context(reply_message)

        # Возращаем строку с ответом модели
        return reply_message["text"]


# # Создали экземпляр класса
# test_use_case = UseCase()
#
# # Пример текста, который мы получаем из OCR
# legal_document_text = """
# договор купли-продажи квартиры
# Санкт-Петербург,
# года.
# Мы, гр. рождения: года рождения, место гор. Ленинград, гражданство: Российская Федерация, пол: мужской, выданный ТП паспорт отдела УФМС России по Санкт-Петербургу и Ленинградской обл. в Невском р-не гор. Санкт-Петербурга года, код подразделения зарегистрированная по адресу: Санкт-Петербург, гр.
# Санкт-Петербург, гражданство: Российская Федерация, пол: мужской, паспорт года, код
# выданный подразделения
# милиции Невского района Санкт-Петербурга зарегистрированный по адресу: Санкт-Петербург,
# квартира года рождения, место рождения: гор.
# действующий за себя и как законный представитель своей несовершеннолетней дочери года рождения, место рождения: г. Санкт-Петербург, Россия, гражданство: Российская Федерация, пол: женский, свидетельство рождении Василеостровского района Санкт-Петербурга дата записи акта о рождении проспект
# выданное Отделом ЗАГС администрации года, запись акта о рождении № года, зарегистрированной по адресу: Санкт-Петербург, несовершеннолетний гр. года рождения, место рождения: гор. Санкт-Петербург, выданный ТП
# гражданство: Российская Федерация, пол: мужской, паспорт отдела УФМС России по Санкт-Петербургу и Ленинградской обл. в Невском р-не г. Санкт-Петербурга года. код подразделения зарегистрированный по адресу: Санкт-Петербург, действующий с согласия своего отца,
# года рождения, место рождения: гор.
# Санкт-Петербург, гражданство: Российская Федерация, пол: мужской, паспорт выданный милиции Невского района Санкт-Петербурга 06 марта 2003 года, код подразделения зарегистрированного по адресу: Санкт-Петербург, именуемые в дальнейшем ПРОДАВЕЦ, с одной стороны,
# и гр.
# года рождения, место рождения: гор.
# гражданство: Российская Федерация, пол: женский, паспорт выданный ТП № Отдела УФМС России по Санкт-Петербургу и Ленинградской обл. в Невском р-не г. Санкт-Петербурга года, код подразделения зарегистрированная по адресу: Санкт-Петербург, действующая от имени
# гр.
# года рождения, место рождения: гражданство: пол: женский, паспорт выданный Министерством иностранных дел года. зарегистрированной по адресу: город по доверенности бланк удостоверенной года нотариусом города зарегистрированного в именуемая в дальнейшем ПОКУПАТЕЛЬ, с другой стороны,
# реестре за заключили настоящий договор о нижеследующем:
# 1. ПРОДАВЕЦ продал, а ПОКУПАТЕЛЬ купил принадлежащую ПРОДАВЦУ по праву общей долевой собственности квартиру, находящуюся по адресу: Санкт-Петербург, проспект Квартира расположена на 3 этаже, имеет общую плошадь 59,7 кв.м, назначение объекта недвижимости -
# жилое. Кадастровый номер
# 2. Указанная квартира принадлежит ПРОДАВЦУ по праву общей долевой собственности на
# основании договора № передачи доли коммунальной квартиры в собственность граждан, заключенного года c Жилищным комитетом Правительства Санкт-Петербурга. Свидетельство о государственной регистрации права выдано Управлением Федеральной службы государственной регистрации, кадастра и картографии по Санкт-Петербургу года, о чем в Едином государственном реестре прав на недвижимое имущество и сделок с ним года сделана запись регистрации Свидетельство о государственной регистрации права выдано Управлением Федеральной службы государственной регистрации, кадастра и картографии по Санкт-Петербургу года, о чем в Едином государственном реестре прав на нелвижимое имушество и сделок с ним года сделана запись регистрации Свидетельство о государственной регистрации права выдано
# """
#
# # Отправляем текст договора legal_document_text в модель и получаем от нее ответ
# reply = test_use_case.execute(legal_document_text)
#
#
# print(reply)