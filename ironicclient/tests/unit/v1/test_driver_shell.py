# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import mock

from ironicclient.common import cliutils
from ironicclient.tests.unit import utils
import ironicclient.v1.driver as v1_driver
import ironicclient.v1.driver_shell as d_shell


class DriverShellTest(utils.BaseTestCase):
    def setUp(self):
        super(DriverShellTest, self).setUp()
        client_mock = mock.MagicMock()
        driver_mock = mock.MagicMock(spec=v1_driver.DriverManager)
        client_mock.driver = driver_mock
        self.client_mock = client_mock

    def test_driver_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            driver = object()
            d_shell._print_driver_show(driver)
        exp = ['hosts', 'name']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_driver_vendor_passthru_with_args(self):
        client_mock = self.client_mock
        args = mock.MagicMock()
        args.driver_name = 'driver_name'
        args.http_method = 'POST'
        args.method = 'method'
        args.arguments = [['arg1=val1', 'arg2=val2']]

        d_shell.do_driver_vendor_passthru(client_mock, args)
        client_mock.driver.vendor_passthru.assert_called_once_with(
            args.driver_name, args.method, http_method=args.http_method,
            args={'arg1': 'val1', 'arg2': 'val2'})

    def test_do_driver_vendor_passthru_without_args(self):
        client_mock = self.client_mock
        args = mock.MagicMock()
        args.driver_name = 'driver_name'
        args.http_method = 'POST'
        args.method = 'method'
        args.arguments = [[]]

        d_shell.do_driver_vendor_passthru(client_mock, args)
        client_mock.driver.vendor_passthru.assert_called_once_with(
            args.driver_name, args.method, args={},
            http_method=args.http_method)

    def test_do_driver_properties(self):
        client_mock = self.client_mock
        args = mock.MagicMock()
        args.driver_name = 'driver_name'

        d_shell.do_driver_properties(client_mock, args)
        client_mock.driver.properties.assert_called_once_with("driver_name")

    @mock.patch('ironicclient.common.cliutils.print_dict')
    def test_do_driver_properties_with_wrap_default(self, mock_print_dict):
        client_mock = self.client_mock
        client_mock.driver.properties.return_value = {
            'foo': 'bar',
            'baz': 'qux'}
        args = mock.MagicMock()
        args.driver_name = 'driver_name'
        args.wrap = 0

        d_shell.do_driver_properties(client_mock, args)
        mock_print_dict.assert_called_with(
            {'foo': 'bar', 'baz': 'qux'},
            dict_value='Description',
            wrap=0)

    @mock.patch('ironicclient.common.cliutils.print_dict')
    def test_do_driver_properties_with_wrap(self, mock_print_dict):
        client_mock = self.client_mock
        client_mock.driver.properties.return_value = {
            'foo': 'bar',
            'baz': 'qux'}
        args = mock.MagicMock()
        args.driver_name = 'driver_name'
        args.wrap = 80

        d_shell.do_driver_properties(client_mock, args)
        mock_print_dict.assert_called_with(
            {'foo': 'bar', 'baz': 'qux'},
            dict_value='Description',
            wrap=80)

    def test_do_driver_show(self):
        client_mock = self.client_mock
        args = mock.MagicMock()
        args.driver_name = 'fake'

        d_shell.do_driver_show(client_mock, args)
        client_mock.driver.get.assert_called_once_with('fake')

    def test_do_driver_list(self):
        client_mock = self.client_mock
        args = mock.MagicMock()

        d_shell.do_driver_list(client_mock, args)
        client_mock.driver.list.assert_called_once_with()

    def test_do_driver_get_vendor_passthru_methods(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver_name = 'fake'
        d_shell.do_driver_get_vendor_passthru_methods(client_mock, args)
        mock_method = client_mock.driver.get_vendor_passthru_methods
        mock_method.assert_called_once_with('fake')
