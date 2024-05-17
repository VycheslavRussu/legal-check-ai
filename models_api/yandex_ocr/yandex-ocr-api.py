# !pip install requests
# !pip install pymupdf

import requests
import fitz  # PyMuPDF
import base64
import io

IAM_TOKEN = secrets["IAM_TOKEN"]
ENV = secrets["ENV"]

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

def ocr_image(image_data, iam_token, folder_id):
    """ Распознает текст на изображении с помощью Yandex OCR. """
    ocr_url = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"
    headers = {
        "Authorization": f"Bearer {iam_token}"
    }
    data = {
        "folderId": folder_id,
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

def pdf_base64_to_text(base64_pdf, iam_token, folder_id):
    """ Основная функция для получения текста из PDF в формате base64. """
    images = pdf_base64_to_images(base64_pdf)
    all_text = []
    for img_data in images:
        ocr_result = ocr_image(img_data, iam_token, folder_id)
        text = extract_text_from_response(ocr_result)
        all_text.append(text)
    return "\n".join(all_text)

# Пример использования

# recognized_text = pdf_base64_to_text(base64_pdf, IAM_TOKEN, ENV)
# print(recognized_text)
