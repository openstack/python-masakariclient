# Copyright(c) 2016 Nippon Telegraph and Telephone Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_shell
----------------------------------

Tests for `masakariclient` module.
"""
import logging
import mock
import six
import sys
import testtools

from masakariclient import shell
from masakariclient.tests import base


class FakeClient(object):

    def __init__(self):
        super(FakeClient, self).__init__()
        self.service = FakeService()


class FakeService(object):

    def __init__(self):
        super(FakeService, self).__init__()

    def do_notification_list(self):
        pass


class HelpFormatterTest(testtools.TestCase):

    def test_start_section(self):
        formatter = shell.HelpFormatter('masakari')
        res = formatter.start_section(('dummyheading', 'dummy', 'dummy'))
        self.assertIsNone(res)
        heading = formatter._current_section.heading
        self.assertEqual("DUMMYHEADING('dummy', 'dummy')", heading)


class TestMasakariShell(base.TestCase):
    def setUp(self):
        super(TestMasakariShell, self).setUp()

    def _shell(self, func, *args, **kwargs):
        orig_out = sys.stdout
        sys.stdout = six.StringIO()
        func(*args, **kwargs)
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = orig_out

        return output

    def test_do_bash_completion(self):
        sh = shell.MasakariShell()
        sc1 = mock.Mock()
        sc2 = mock.Mock()
        sc1._optionals._option_string_actions = ('A1', 'A2', 'C')
        sc2._optionals._option_string_actions = ('B1', 'B2', 'C')
        sh.subcommands = {
            'command-foo': sc1,
            'command-bar': sc2,
            'bash-completion': None,
            'bash_completion': None,
        }

        output = self._shell(sh.do_bash_completion, None)

        output = output.split('\n')[0]
        output_list = output.split(' ')
        for option in ('A1', 'A2', 'C', 'B1', 'B2',
                       'command-foo', 'command-bar'):
            self.assertIn(option, output_list)

    @mock.patch.object(logging, 'basicConfig')
    @mock.patch.object(logging, 'getLogger')
    def test_setup_logging_debug_true(self, moc_getLogger,
                                      moc_basicConfig):
        sh = shell.MasakariShell()
        sh._setup_logging(True)

        moc_basicConfig.assert_called_once_with(
            format="%(levelname)s (%(module)s) %(message)s",
            level=logging.DEBUG)
        mock_calls = [
            mock.call('iso8601'),
            mock.call().setLevel(logging.WARNING),
            mock.call('urllib3.connectionpool'),
            mock.call().setLevel(logging.WARNING),
        ]
        moc_getLogger.assert_has_calls(mock_calls)

    @mock.patch.object(logging, 'basicConfig')
    @mock.patch.object(logging, 'getLogger')
    def test_setup_logging_debug_false(self,
                                       moc_getLogger,
                                       moc_basicConfig):
        sh = shell.MasakariShell()
        sh._setup_logging(False)

        moc_basicConfig.assert_called_once_with(
            format="%(levelname)s (%(module)s) %(message)s",
            level=logging.WARNING)
        mock_calls = [
            mock.call('iso8601'),
            mock.call().setLevel(logging.WARNING),
            mock.call('urllib3.connectionpool'),
            mock.call().setLevel(logging.WARNING),
        ]
        moc_getLogger.assert_has_calls(mock_calls)
