import streamlit as st
import socket
import hashlib
import base64
import PIL
from streamlit import session_state as session


# Функция хэширования ip-адреса пользователя
def generate_unique_user_id(ip_address):
    return hashlib.sha256(ip_address.encode()).hexdigest()


# Главная информация страницы
st.title("Проверка договора на наличие подозрительных пунктов")
st.header("Загрузка документа")

# Проверяка наличия уникального идентификатора пользователя в session_state
if "user_id" not in session:
    # Если нет, то создаем новый уникальный идентификатор для пользователя
    session.user_id = generate_unique_user_id(socket.gethostbyname(socket.gethostname()))

# Проверка существования сообщений для данного user_id в текщей сессии
if "messages" not in session:
    # Если нет, создаем новую запись с пустым словарем сообщений
    session.messages = {}

uploaded_file = st.file_uploader(label="Загрузите документ",
                                 type=["png", "jpeg", "pdf"])

if not uploaded_file:
    st.warning("Пожалуйста, загрузите документ!")
    st.stop()
else:
    if uploaded_file.type != "application/pdf":
        image_as_bytes = uploaded_file.read()
        st.image(image_as_bytes, use_column_width=True)
    try:
        file_contents = uploaded_file.getvalue()
        file_base64 = base64.b64encode(file_contents).decode('utf-8')
    except PIL.UnidentifiedImageError as e:
        print('Ошибка при конвертации файла! Отправьте другой файл.')

    doc_button = st.button("Отправить документ")

if doc_button:
    # TODO: отправка фотографии на модель и получение текста
    # TODO: отправка текста документа на модель и получение результата качесства
    st.write(f"Ответ от модели: OK!")

# После ответа от модели появлется возможность общения
st.subheader("Обращение к модели")
user_input = st.text_area("Введите сообщение:", "", max_chars=200)
text_button = st.button("Отправить сообщение")

if text_button and user_input:
    # TODO: в response ответ модели на user_input
    response = f'Ответ модели на {user_input}'

    # Если запись для данного user_id уже существует, добавляем сообщение в список
    if session.user_id in session.messages:
        session.messages[session.user_id]['message'].append(user_input)
        session.messages[session.user_id]['response'].append(response)
    # Если запись для данного user_id еще не существует, создаем новую запись
    else:
        session.messages[session.user_id] = {'message': [user_input], 'response': [response]}

    # Отображаем все сообщения для данного пользователя
    for i in range(len(session.messages[session.user_id]['message'])):
        st.write(f"Вы: {session.messages[session.user_id]['message'][i]}")
        st.write(f"Ответ: {session.messages[session.user_id]['response'][i]}")
