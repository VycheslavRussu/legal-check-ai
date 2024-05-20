import pytest
from models_api.yandex_ocr.yandex_ocr_api import file_base64_to_text
import base64


@pytest.fixture
def png_base64():
    with open("docs_example/doc1.png", "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')


@pytest.fixture
def pdf_base64():
    with open("docs_example/doc2.pdf", "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')


def test_png_base64_to_text(png_base64):
    text = file_base64_to_text(png_base64, 'png')
    assert 'АКТ ПРИЕМА-ПЕРЕДАЧИ' in text


def test_pdf_base64_to_text(pdf_base64):
    text = file_base64_to_text(pdf_base64, 'pdf')
    assert 'Договор купли-продажи автомобиля' in text
