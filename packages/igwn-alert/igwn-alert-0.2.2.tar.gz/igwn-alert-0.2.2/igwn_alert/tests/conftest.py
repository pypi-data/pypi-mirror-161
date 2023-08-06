import pytest
from unittest import mock
from igwn_alert import client


@pytest.fixture
def mock_alert_client():
    """A client class which mocks away the client.open() method """
    alert_client = client
    alert_client.open = mock.MagicMock()
    alert_client.open.write = mock.MagicMock()
    alert_client.auth = [mock.MagicMock()]
    return alert_client


@pytest.fixture
def no_callback_message():
    """Templated output when a user doesn't specify a callback """
    response = "New message from topic {topic}: {msg}"
    return response


@pytest.fixture
def callback_function(payload=None, topic=None):
    """An example callback function """
    response = "Callback message: {msg} from {topic}"
    return response
