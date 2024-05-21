import streamlit as st
import base64
from models_api.yandex_gpt.yandex_gpt_api import UseCase
from models_api.yandex_ocr.yandex_ocr_api import file_base64_to_text
from streamlit import session_state as session
from docx import Document


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

# Проверка существования списка сообщений для данного user_id в текщей сессии
if "messages" not in session:
    # Если нет, создаем новую запись с пустым списком сообщений
    session.messages = []

# Проверка существования расшифровки текста документа
if 'doc_text' not in session:
    # Если нет, создаем новую запись со значением None
    session.doc_text = None

# Панель загрузки файла форматов "png", "jpeg", "jpg", "pdf", "docx"
uploaded_file = st.file_uploader(label="Загрузите документ",
                                 type=["png", "jpeg", "jpg", "pdf", "docx"])

# Если файл загружен
if not uploaded_file:
    st.warning("Пожалуйста, загрузите документ!")
    st.stop()

else:
    try:
        if uploaded_file.type == "application/vnd.openxmlformats-" \
                                 "officedocument.wordprocessingml.document":
            session.doc_text = read_docx(uploaded_file)

        elif uploaded_file.type == "text/plain":
            session.doc_text = read_txt(uploaded_file)

        elif uploaded_file.type == "application/pdf":
            document = read_pdf(uploaded_file)
            session.doc_text = file_base64_to_text(document, 'pdf')

        elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            document = read_image(uploaded_file)
            session.doc_text = file_base64_to_text(
                document, uploaded_file.type.split('/')[-1]
                )

            image_as_bytes = uploaded_file.read()
            st.image(image_as_bytes, use_column_width=True)

        else:
            st.write('Некорректный формат документа!')
            uploaded_file = None

        if len(session.messages) == 0 and uploaded_file:
            session.messages.append(
                {'role': 'user', 'content': 'Отправка файла...'}
                )
            session.model = UseCase()
            response_doc = session.model.operate(session.doc_text)
            session.messages.append({'role': 'ai', 'content': response_doc})

    except Exception:
        st.write('Ошибка формата документа!')
        uploaded_file = None

if session.doc_text:
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
        response = session.model.operate(user_input)

        # Показывает ответ модели
        with st.chat_message('ai'):
            st.markdown(response)

        # Добавляет ответ модели в историю сообщений
        session.messages.append({'role': 'ai', 'content': response})
