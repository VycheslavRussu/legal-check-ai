import streamlit as st
import base64
# from models_api.yandex_gpt.yandex_gpt_api.py import UseCase
from models_api.yandex_gpt.yandex_gpt_api import UseCase
from streamlit import session_state as session
from docx import Document
import json


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
    file_contents = file.getvalue()
    file_base64 = base64.b64encode(file_contents).decode('utf-8')
    return file_base64


# Главная информация страницы
st.title("Проверка договора на наличие подозрительных пунктов")
st.header("Загрузка документа")

# Проверка существования словаря сообщений для данного user_id в текщей сессии
if "messages" not in session:
    # Если нет, создаем новую запись с пустым словарем сообщений
    session.messages = []

uploaded_file = st.file_uploader(label="Загрузите документ",
                                 type=["png", "jpeg", "jpg", "pdf", "docx"])
if not uploaded_file:
    st.warning("Пожалуйста, загрузите документ!")
    st.stop()

else:
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        session.doc_text = read_docx(uploaded_file)

    elif uploaded_file.type == "text/plain":
        session.doc_text = read_txt(uploaded_file)

    elif uploaded_file.type == "application/pdf":
        session.doc_text = None
        session.document = read_pdf(uploaded_file)
    elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:

        session.doc_text = None
        session.document = read_image(uploaded_file)
        image_as_bytes = uploaded_file.read()
        st.image(image_as_bytes, use_column_width=True)

    if session.doc_text is None:
        # TODO: отправка документа на модель и получение текста
        # text_doc = model.to_text()
        session.doc_text = 'Как твои дела?'

    if len(session.messages) == 0:
        session.messages.append({'role': 'user', 'content': 'Отправка файла...'})
        session.model = UseCase()
        response_doc = session.model.execute(session.doc_text)
        # response_doc = 'Ответ модели на документ'
        session.messages.append({'role': 'ai', 'content': response_doc})

# После ответа от модели появлется возможность общения
st.subheader("Обращение к модели")
user_input = st.chat_input("Введите сообщение:", max_chars=200)

for message in session.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# После сообщения пользователя
if user_input:
    # Показывает сообщение пользователя
    with st.chat_message('user'):
        st.markdown(user_input)

    # Добавляет сообщение в историю сообщений
    session.messages.append({'role': 'user', 'content': user_input})

    # Ответ модели на запрос
    response = session.model.execute(user_input)
    # response = f'Ответ модели на {user_input}'

    # Показывает ответ модели
    with st.chat_message('ai'):
        st.markdown(response)

    # Добавляет ответ модели в историю сообщений
    session.messages.append({'role': 'ai', 'content': response})
