import requests
import fitz  # PyMuPDF
import base64
import io
import json
import os

current_dir = os.path.dirname(__file__)
absolute_path = os.path.join(current_dir, '../../secrets.json')

try:
    with open(absolute_path, 'r') as secrets_file:
        secrets = json.load(secrets_file)

    IAM_TOKEN = secrets.get("IAM_TOKEN")
    FOLDER_ID = secrets.get("FOLDER_ID")

except Exception as e:
    IAM_TOKEN = os.environ.get("IAM_TOKEN")
    FOLDER_ID = os.environ.get("FOLDER_ID")


def pdf_base64_to_images(base64_pdf):
    """ Конвертирует base64 PDF в список изображений. """
    pdf_data = base64.b64decode(base64_pdf)
    pdf_stream = io.BytesIO(pdf_data)
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_data = pix.pil_tobytes(format="png")
        images.append(img_data)
    return images

def image_base64_to_bytes(base64_image):
    """ Конвертирует base64 изображение в байты. """
    return base64.b64decode(base64_image)

def ocr_image(image_data):
    """ Распознает текст на изображении с помощью Yandex OCR. """
    ocr_url = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}"
    }
    data = {
        "folderId": FOLDER_ID,
        "analyze_specs": [{
            "content": base64.b64encode(image_data).decode('utf-8'),  # Конвертируем байты в base64 строку
            "features": [{
                "type": "TEXT_DETECTION",
                "text_detection_config": {
                    "language_codes": ["*"]
                }
            }]
        }]
    }
    response = requests.post(ocr_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def extract_text_from_response(response):
    """ Извлекает текст из ответа Yandex OCR. """
    pages_text = []
    for result in response['results']:
        text = ""
        for page in result['results'][0]['textDetection']['pages']:
            for block in page['blocks']:
                for line in block['lines']:
                    text += " ".join([word['text'] for word in line['words']]) + "\n"
        pages_text.append(text)
    return "\n".join(pages_text)

def file_base64_to_text(base64_file, file_type):
    """ Основная функция для получения текста из файла в формате base64. """
    if file_type == 'pdf':
        images = pdf_base64_to_images(base64_file)
    elif file_type in ['png', 'jpg', 'jpeg']:
        images = [image_base64_to_bytes(base64_file)]
    else:
        raise ValueError("Unsupported file type")

    all_text = []
    for img_data in images:
        ocr_result = ocr_image(img_data)
        text = extract_text_from_response(ocr_result)
        all_text.append(text)
    return "\n".join(all_text)

# Пример использования
# base64_file = "..."  # base64 строка файла
# file_type = "pdf"  # тип файла: pdf, png, jpg, jpeg
# recognized_text = file_base64_to_text(base64_file, file_type)
# print(recognized_text)