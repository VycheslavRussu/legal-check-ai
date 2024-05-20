import pytest
import json
from unittest.mock import patch
from models_api.yandex_gpt.yandex_gpt_api import YandexGPT, ContextStorage


@pytest.fixture
def mock_response():
    return {
        "result": {
            "alternatives": [
                {"message": {"role": "system", "text": "This is a test response"}}
            ]
        }
    }


@patch('requests.post')
def test_send_response(mock_post, mock_response):
    mock_post.return_value.status_code = 200
    mock_post.return_value.text = json.dumps(mock_response)

    yandex_gpt = YandexGPT()
    context_messages = [
        {"role": "user", "text": "Hello, this is a test."}
    ]
    response = yandex_gpt.send_response(context_messages)
    response_data = json.loads(response)

    assert response_data == mock_response
    mock_post.assert_called_once()


def test_add_context():
    storage = ContextStorage()
    message = {"role": "user", "text": "Hello"}
    storage.add_context(message)
    assert storage.get_context() == [message]
    assert storage.get_approximate_tokens_count() == len("Hello") // 5


def test_set_default_context():
    storage = ContextStorage()
    default_context = [
        {"role": "system", "text": "System message"},
        {"role": "user", "text": "User message"}
    ]
    storage.set_default_context(default_context)
    assert storage.get_context() == default_context
    assert storage.get_approximate_tokens_count() == len("System message") // 5 + len("User message") // 5


def test_delete_message_from_context():
    storage = ContextStorage()
    default_context = [
        {"role": "system", "text": "System message"},
        {"role": "user", "text": "User message"},
        {"role": "user", "text": "Another message"},
        {"role": "user", "text": "Message to delete"}
    ]
    storage.set_default_context(default_context)
    storage.delete_message_from_context()
    assert len(storage.get_context()) == 3
    assert storage.get_approximate_tokens_count() == len("System message") // 5 + len("User message") // 5 + len("Another message") // 5
