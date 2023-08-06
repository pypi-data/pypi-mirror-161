# Import testing modules:
import pytest
import os
import io
import json

from igwn_alert import client as test_client
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout


hop_auth_toml = """[[auth]]
username = "user-asdf"
password = "pw123"
"""

auth_netrc = """machine kafka://kafka.test/ login user-asdf password pw123
"""


def callback_function(topic=None, payload=None):
    """An example callback function """
    response = "Callback message: {payload} from {topic}".\
               format(payload=payload, topic=topic)
    print(response)
    return response


# Test the version number
def test_version():
    from igwn_alert import __version__
    assert __version__ == '0.2.2'


# Test an unauthorized session
def test_no_auth():
    tc = test_client(noauth=True)
    assert tc.auth is None


USER_PASS_TEST_DATA = [
    {'username': 'user-asdf', 'password': 'pw123'},
    {'username': 'user-asdf'},
    {'password': 'pw123'},
]


# Test that username/password inputs work:
@pytest.mark.parametrize("username_and_or_password", USER_PASS_TEST_DATA)
def test_username_and_or_password_provided(username_and_or_password):

    # When there is not a username and a password, then the code should
    # produce an error. Define the error string and the error raised.

    if not len(username_and_or_password) == 2:
        err_str = 'You must provide both a username and a password for '\
                  'basic authentication.'
        with pytest.raises(RuntimeError, match=err_str):
            tc = test_client(**username_and_or_password)
    else:
        tc = test_client(**username_and_or_password)
        creds = tc.auth_obj

        assert creds.username == username_and_or_password.get('username')
        assert creds.password == username_and_or_password.get('password')


# Test for response when toml does not exist:
def test_hop_toml_not_exist():

    hop_toml = '/tmp/auth.toml'

    if os.path.exists(hop_toml):
        os.remove(hop_toml)

    with pytest.raises(FileNotFoundError):
        test_client(authfile=hop_toml)


# Test for response when toml exists but has bad permissions:
def test_hop_toml_bad_permissions():

    hop_toml = '/tmp/auth.toml'

    if os.path.exists(hop_toml):
        os.remove(hop_toml)

    with os.fdopen(os.open(hop_toml,
                   os.O_WRONLY | os.O_CREAT, 0o755), 'w') as h:
        h.write(hop_auth_toml)

    with pytest.raises(RuntimeError):
        test_client(authfile=hop_toml)


# Test for response when toml exists and has correct permissions:
def test_hop_toml_correct_permissions():

    hop_toml = '/tmp/auth.toml'

    if os.path.exists(hop_toml):
        os.remove(hop_toml)

    with os.fdopen(os.open(hop_toml,
                   os.O_WRONLY | os.O_CREAT, 0o600), 'w') as h:
        h.write(hop_auth_toml)

    tc = test_client(authfile=hop_toml)
    creds = tc.auth_obj[0]

    assert creds.username == 'user-asdf'
    assert creds.password == 'pw123'


# Test the case where there's no toml and no netrc
def test_no_toml_no_netrc_auth():

    homedir = os.getenv("HOME")
    netrc_file = os.path.join(homedir, '.netrc')

    # CAREFULLY move the netrc file, if it exists:
    if os.path.exists(netrc_file):
        os.rename(netrc_file, netrc_file + '.testsave')

    mock_topics = MagicMock()
    mock_topics.load_auth = MagicMock(side_effect=Exception)

    with patch('hop.auth', mock_topics):
        with pytest.warns(Warning):
            tc = test_client(server='kafka://test.server',
                             port=1234,
                             group='test')

    assert tc.auth_obj is False

    if os.path.exists(netrc_file + '.testsave'):
        os.rename(netrc_file + '.testsave', netrc_file)


# Test netrc auth:
def test_netrc_auth():

    homedir = os.getenv("HOME")
    netrc_file = os.path.join(homedir, '.netrc')

    # CAREFULLY move the netrc file, if it exists:
    if os.path.exists(netrc_file):
        os.rename(netrc_file, netrc_file + '.testsave')

    # Create a new .netrc, with the correct permissions:
    with os.fdopen(os.open(netrc_file,
                   os.O_WRONLY | os.O_CREAT, 0o600), 'w') as h:
        h.write(auth_netrc)

    mock_topics = MagicMock()
    mock_topics.load_auth = MagicMock(side_effect=Exception)

    with patch('hop.auth', mock_topics):
        tc = test_client(server='kafka://kafka.test/',
                         port=1234,
                         group='test')
        creds = tc.auth_obj

    if os.path.exists(netrc_file + '.testsave'):
        os.rename(netrc_file + '.testsave', netrc_file)
    else:
        os.remove(netrc_file)

    assert creds.username == 'user-asdf'
    assert creds.password == 'pw123'


# Test base URL formation:
def test_base_url():

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')

    assert tc._construct_base_url() == 'kafka://test.server:1234/test'


TOPICS_LIST = ['topic1',
               ['topic1'],
               ['topic1', 'topic2'],
               ]


# Test "topics" url with one or multiple topics:
@pytest.mark.parametrize("topics_item", TOPICS_LIST)
def test_topics_url(topics_item):

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')

    if (type(topics_item) == str):
        assert tc._construct_topic_url(topics_item) == \
            'kafka://test.server:1234/test.topic1'
    elif (type(topics_item) == list):
        if (len(topics_item) == 1):
            assert tc._construct_topic_url(topics_item) == \
                'kafka://test.server:1234/test.topic1'
        elif (len(topics_item) == 2):
            assert tc._construct_topic_url(topics_item) == \
                'kafka://test.server:1234/test.topic1,test.topic2'


# Test listening with no callback
def test_listen_no_callback(no_callback_message):

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')
    topic = 'test.topic1'
    metadata = MagicMock()
    metadata.topic = topic
    alert_contents = {"test_key": "test_value"}
    message = json.dumps(alert_contents).encode('utf-8')

    alert_received = [(message, metadata)]
    with patch('igwn_alert.client.open') as client_open:

        with client_open() as stream:
            stream.read.side_effect = [alert_received]

        f = io.StringIO()
        with redirect_stdout(f):
            tc.listen(topic=topic)
        out = f.getvalue().rstrip()

    assert out == no_callback_message.format(topic=topic,
                                             msg=alert_contents)


# Test listening to all topics (blank inputs)
def test_listen_all_topics(no_callback_message):
    server_topics = {'test.topic1': '=='}
    mock_topics = MagicMock(return_value=server_topics)

    with patch('igwn_alert.client.get_topics', mock_topics):

        tc = test_client(noauth=True,
                         server='kafka://test.server',
                         port=1234,
                         group='test')
        metadata = MagicMock()
        metadata.topic = 'topic1'
        alert_contents = {"test_key": "test_value"}
        message = json.dumps(alert_contents).encode('utf-8')

        alert_received = [(message, metadata)]
        with patch('igwn_alert.client.open') as client_open:

            with client_open() as stream:
                stream.read.side_effect = [alert_received]

            f = io.StringIO()
            with redirect_stdout(f):
                tc.listen()
            out = f.getvalue().rstrip()

    assert out == no_callback_message.format(topic='topic1',
                                             msg=alert_contents)


# Test listening with a callback function
def test_listen_callback():

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')
    topic = 'test.topic1'
    metadata = MagicMock()
    metadata.topic = topic
    alert_contents = {"test_key": "test_value"}
    message = json.dumps(alert_contents).encode('utf-8')

    alert_received = [(message, metadata)]
    with patch('igwn_alert.client.open') as client_open:

        with client_open() as stream:
            stream.read.side_effect = [alert_received]

        f = io.StringIO()
        with redirect_stdout(f):
            tc.listen(callback=callback_function, topic=topic)
        out = f.getvalue().rstrip()

    assert out == callback_function(topic=topic.split('.')[1],
                                    payload=alert_contents)


# Test listening and receiving a invalid json response
def test_listen_not_json(no_callback_message):

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')
    topic = 'test.topic1'
    metadata = MagicMock()
    metadata.topic = topic
    alert_contents = "test message"

    alert_received = [(alert_contents, metadata)]
    with patch('igwn_alert.client.open') as client_open:

        with client_open() as stream:
            stream.read.side_effect = [alert_received]

        f = io.StringIO()
        with redirect_stdout(f):
            with pytest.warns(UserWarning):
                tc.listen(topic=topic)
        out = f.getvalue().rstrip()

    assert out == no_callback_message.format(topic=topic,
                                             msg=alert_contents)


# Test connecting to a single topic for writing:
@pytest.mark.parametrize("topics_item", TOPICS_LIST)
def test_connect_topic_string(mock_alert_client, topics_item):

    tc = mock_alert_client(noauth=True,
                           server='kafka://test.server',
                           port=1234,
                           group='test')

    tc.connect(topics_item)

    if (type(topics_item) == str):
        assert len(tc.sessions) == 1
    elif (type(topics_item) == list):
        assert len(tc.sessions) == len(topics_item)


# Test publishing to topics without connecting
def test_publish_to_topic_no_connect(mock_alert_client):

    err_str = "No active sessions. Please " \
              "connect before publishing to a topic."

    tc = mock_alert_client(noauth=True,
                           server='kafka://test.server',
                           port=1234,
                           group='test')

    with pytest.raises(RuntimeError, match=err_str):
        tc.publish_to_topic(topic='test', msg='test message')


# Test publishing to topics after connecting
def test_publish_to_topic_after_connecting(mock_alert_client):

    tc = mock_alert_client(noauth=True,
                           server='kafka://test.server',
                           port=1234,
                           group='test')

    topic = 'test.topic1'
    msg = 'test message'

    tc.connect(topic)

    message_count = 0
    while (message_count < 1):
        message_count += 1
        tc.publish_to_topic(topic=topic, msg=msg)

    assert message_count == 1


# Test disconnecting when not connected
def test_disconnect_not_connect(mock_alert_client):

    tc = mock_alert_client(noauth=True,
                           server='kafka://test.server',
                           port=1234,
                           group='test')

    topic = 'test.topic1'

    with pytest.warns(UserWarning):
        tc.disconnect(topics=topic)


# Test disconnecting from a topic not in the session
def test_disconnect_wrong_topic(mock_alert_client):

    tc = mock_alert_client(noauth=True,
                           server='kafka://test.server',
                           port=1234,
                           group='test')

    right_topic = 'test.topic1'
    wrong_topic = 'test.topic2'

    tc.connect(topics=right_topic)

    with pytest.warns(UserWarning):
        tc.disconnect(topics=wrong_topic)


DISCONNECT_LIST = [None, 'test.topic1']


# Test connecting and disconnecting from multiple topics:
@pytest.mark.parametrize("topics_item", DISCONNECT_LIST)
def test_disconnect_topic_string(mock_alert_client, topics_item):

    tc = mock_alert_client(noauth=True,
                           server='kafka://test.server',
                           port=1234,
                           group='test')

    tc.connect(['test.topic1', 'test.topic2'])

    tc.disconnect(topics_item)

    if topics_item:
        assert len(tc.sessions) == 1
    else:
        assert len(tc.sessions) == 2


# Test listing topics from different groups
GROUP_LIST = ['test1', 'test2', 'test3']


@pytest.mark.parametrize("test_group", GROUP_LIST)
def test_list_topics_default(test_group):

    server_topics = {'test1.topic1': '==',
                     'test1.topic2': '==',
                     'test1.topic3': '==',
                     'test2.topic4': '==',
                     'test2.topic5': '==',
                     'test2.topic6': '==',
                     }
    mock_topics = MagicMock()
    mock_topics.list_topics = MagicMock(return_value=server_topics)

    with patch('hop.list_topics', mock_topics):

        tc = test_client(noauth=True,
                         server='kafka://test.server',
                         port=1234,
                         group=test_group)

        topic_list = tc.get_topics()

    if (test_group == 'test1'):
        assert topic_list == ['topic1', 'topic2', 'topic3']
    elif (test_group == 'test2'):
        assert topic_list == ['topic4', 'topic5', 'topic6']
    else:
        assert topic_list == []


# Test publishing to topic, without a session
def test_publish_to_topic_without_session(mock_alert_client):

    tc = mock_alert_client(noauth=True,
                           server='kafka://test.server',
                           port=1234,
                           group='test')

    topic = 'test.topic1'
    msg = 'test message'

    sent_messages = 0

    while (sent_messages < 1):
        sent_messages += 1
        tc.publish(topic=topic, msg=msg)


# Test for deprecation warning in get_subscriptions.
def test_get_subscription_deprecated():

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')

    with pytest.warns(DeprecationWarning):
        tc.get_subscriptions()


# Test for deprecation warning in subscribe
def test_subscribe_deprecated():

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')

    with pytest.warns(DeprecationWarning):
        tc.subscribe()


# Test for deprecation warning in unsubscribe
def test_unsubscribe_deprecated():

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')

    with pytest.warns(DeprecationWarning):
        tc.unsubscribe()


# Test for deprecation warning in delete
def test_delete_deprecated():

    tc = test_client(noauth=True,
                     server='kafka://test.server',
                     port=1234,
                     group='test')

    with pytest.warns(DeprecationWarning):
        tc.delete()


INPUT_DICT = [{'username': 'test',
               'password': 'test',
               'auth': 'test',
               'authfile': 'test',
               'noauth': False,
               'group': 'test',
               'server': 'test',
               'port': 1234,
               'batch_size': 123,
               'batch_timeout': 123},
              {'bad_input': 'is_bad'}]


# Test for client input checking:
@pytest.mark.parametrize("input_item", INPUT_DICT)
def test_inputs(input_item):

    if ('bad_input' in input_item):
        with pytest.raises(TypeError):
            tc = test_client(**input_item)
    else:
        tc = test_client(**input_item)
        assert tc.auth_obj.username == input_item['username']
