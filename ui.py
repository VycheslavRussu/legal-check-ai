import streamlit as st
import socket
import hashlib
import base64
import io
# from models_api.yandex_gpt.yandex-gpt-api.py import UseCase
from PIL import Image
from streamlit import session_state as session
from docx import Document


# Функция хэширования ip-адреса пользователя
def generate_unique_user_id(ip_address):
    return hashlib.sha256(ip_address.encode()).hexdigest()


# Функция для чтения содержимого файла формата .txt в текст
def read_txt(file):
    text = file.getvalue().decode("utf-8")
    return text


# Функция для чтения содержимого файла формата .docx в текст
def read_docx(file):
    doc = Document(file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


# Функция для чтения содержимого файла формата .pdf в кодировку base64
def read_pdf(file):
    binary_content = file.getvalue()
    file_base64 = base64.b64encode(binary_content).decode('utf-8')
    return file_base64


# Функция для чтения изображения в кодировку base64
def read_image(file):
    image = Image.open(file)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


# Главная информация страницы
st.title("Проверка договора на наличие подозрительных пунктов")
st.header("Загрузка документа")


# Проверяка наличия уникального идентификатора пользователя в session_state
if "user_id" not in session:
    # Если нет, то создаем новый уникальный идентификатор для пользователя
    session.user_id = generate_unique_user_id(socket.gethostbyname(socket.gethostname()))

# Проверка существования словаря сообщений для данного user_id в текщей сессии
if "messages" not in session:
    # Если нет, создаем новую запись с пустым словарем сообщений
    session.messages = {}

uploaded_file = st.file_uploader(label="Загрузите документ",
                                 type=["png", "jpeg", "jpg", "pdf", "docx"])

if not uploaded_file:
    st.warning("Пожалуйста, загрузите документ!")
    st.stop()
else:
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        session.text = read_docx(uploaded_file)
    elif uploaded_file.type == "text/plain":
        session.text = read_txt(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        session.text = None
        session.document = read_pdf(uploaded_file)
    elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        session.text = None
        session.document = read_image(uploaded_file)
        image_as_bytes = uploaded_file.read()
        st.image(image_as_bytes, use_column_width=True)

    doc_button = st.button("Отправить документ")

if doc_button:
    if session.text is None:
        # TODO: отправка документа на модель и получение текста
        # text_doc = model.to_text()
        session.text = ''

    # TODO: отправка текста документа на модель и получение результата
    # session.model = UseCase()
    # response_doc = session.model.get_response(session.text)
    response_doc = ''
    session.messages[session.user_id] = {'message': ['Отправлен файл...'], 'response': [response_doc]}

    st.write(f"Ответ от модели: {response_doc}")

# После ответа от модели появлется возможность общения
st.subheader("Обращение к модели")
user_input = st.text_area("Введите сообщение:", "", max_chars=200)
text_button = st.button("Отправить сообщение")

if text_button and user_input:
    # TODO: в response ответ модели на user_input
    # response = session.model.get_response(user_input)
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
