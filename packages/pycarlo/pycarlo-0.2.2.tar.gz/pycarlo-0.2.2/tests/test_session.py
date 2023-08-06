from configparser import NoSectionError
from unittest import TestCase
from unittest.mock import patch, call

from pycarlo.common.errors import InvalidSessionError
from pycarlo.core import Session


class SessionTest(TestCase):

    @patch.object(Session, '_read_config')
    def test_session_with_params(self, mock_read):
        mcd_id, mcd_token = 'foo', 'bar'
        session = Session(mcd_id=mcd_id, mcd_token=mcd_token)

        self.assertEqual(session.id, mcd_id)
        self.assertEqual(session.token, mcd_token)
        mock_read.assert_not_called()

    @patch('pycarlo.core.session.MCD_DEFAULT_API_ID', 'foo')
    @patch('pycarlo.core.session.MCD_DEFAULT_API_TOKEN', 'bar')
    @patch.object(Session, '_read_config')
    def test_session_with_env(self, mock_read):
        session = Session()

        self.assertEqual(session.id, 'foo')
        self.assertEqual(session.token, 'bar')
        mock_read.assert_not_called()

    @patch('pycarlo.core.session.MCD_DEFAULT_API_TOKEN', 'bar')
    @patch.object(Session, '_read_config')
    def test_session_with_mixed(self, mock_read):
        mcd_id = 'foo'
        session = Session(mcd_id=mcd_id)

        self.assertEqual(session.id, mcd_id)
        self.assertEqual(session.token, 'bar')
        mock_read.assert_not_called()

    @patch('pycarlo.core.session.MCD_DEFAULT_API_TOKEN', 'qux')
    @patch.object(Session, '_read_config')
    def test_session_with_precedence(self, mock_read):
        mcd_id, mcd_token = 'foo', 'bar'
        session = Session(mcd_id=mcd_id, mcd_token=mcd_token)

        self.assertEqual(session.id, mcd_id)
        self.assertEqual(session.token, mcd_token)
        mock_read.assert_not_called()

    @patch.object(Session, '_read_config')
    def test_session_with_partial(self, mock_read):
        with self.assertRaises(InvalidSessionError):
            Session(mcd_id='foo')
        mock_read.assert_not_called()

    @patch('pycarlo.core.session.configparser')
    def test_read_config(self, mock_parser):
        mcd_id, mcd_token, mcd_api_endpoint, mcd_config_path = 'foo', 'bar', 'endpoint', 'path/'
        mock_parser.ConfigParser().get.side_effect = [mcd_id, mcd_token, mcd_api_endpoint]

        session = Session(mcd_config_path=mcd_config_path)
        mock_parser.assert_has_calls = [
            call.ConfigParser(),
            call.ConfigParser().read('path/profiles.ini'),
            call.ConfigParser().get('default', 'mcd_id'),
            call.ConfigParser().get('default', 'mcd_token'),
            call.ConfigParser().get('default', 'mcd_api_endpoint'),
        ]
        self.assertEqual(session.id, mcd_id)
        self.assertEqual(session.token, mcd_token)
        self.assertEqual(session.endpoint, mcd_api_endpoint)

    @patch.object(Session, '_get_config_parser')
    def test_read_config_with_bad_section(self, mock_parser):
        class InvalidParser:
            def read(self, *args, **kwargs):
                pass

            def get(self, *args, **kwargs):
                raise NoSectionError('')

        mock_parser.return_value = InvalidParser()

        with self.assertRaises(InvalidSessionError):
            Session()

    @patch('pycarlo.core.session.pkg_resources')
    @patch('pycarlo.core.session.uuid')
    def test_set_session_name(self, mock_uuid, mock_pkg):
        mcd_id, mcd_token = 'foo', 'bar'
        mock_uuid_val, mock_pkg_val = '42', '99'

        mock_uuid.uuid4.return_value = mock_uuid_val
        mock_pkg.get_distribution().version = mock_pkg_val
        session = Session(mcd_id=mcd_id, mcd_token=mcd_token)

        self.assertEqual(session.id, mcd_id)
        self.assertEqual(session.token, mcd_token)
        self.assertEqual(session.session_name, f'python-sdk-{mock_pkg_val}-{mock_uuid_val}')

    def test_set_session_endpoint(self):
        mcd_id, mcd_token, endpoint = 'foo', 'bar', 'test.com'
        self.assertEqual(Session(mcd_id=mcd_id, mcd_token=mcd_token, endpoint=endpoint).endpoint, endpoint)
        self.assertEqual(Session(mcd_id=mcd_id, mcd_token=mcd_token).endpoint, 'https://api.getmontecarlo.com/graphql')
