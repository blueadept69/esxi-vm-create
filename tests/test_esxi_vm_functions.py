"""
test_esxi_vm_functions.py:
    unittests for functions/methods in esxi_vm_functions.py module.
"""
from unittest import TestCase
import sys
import datetime

from esxi_vm_functions import current_datetime_iso_string, float2human, Message
from esxi_vm_functions import Config, EsxVm, EsxVmCpu

if sys.version_info.major == 2:
    from mock import patch, mock_open, call
else:
    from unittest.mock import patch, mock_open  # pylint: disable=no-name-in-module,import-error,ungrouped-imports

EXPECTED_DEFAULT_CONFIGDATA = {'HDISK': 20,
                               'LOG': './esxi-vm.log',
                               'VMXOPTS': '',
                               'HOST': 'esxi',
                               'ISO': 'None',
                               'VIRTDEV': 'pvscsi',
                               'GUESTOS': 'centos-64',
                               'NET': 'None',
                               'PASSWORD': '',
                               'CPU': 2,
                               'STORE': 'LeastUsed',
                               'isDryRun': False,
                               'isVerbose': False,
                               'DISKFORMAT': 'thin',
                               'MEM': 4,
                               'isSummary': False,
                               'USER': 'root'
                              }

TEST_ESXI_VM_YML = """CPU: 9
DISKFORMAT: thick
GUESTOS: centos-48
HDISK: 42
HOST: esxhost
ISO: centos.iso
LOG: /usr/local/logs/esxi-vm.log
MEM: 6
NET: test-net
PASSWORD: passwd
STORE: test-ds
USER: test-user
VIRTDEV: notpvscsi
VMXOPTS: vmxopt
isDryRun: true
isSummary: true
isVerbose: true
"""

GOOD_YML_TEST_CONFIGDATA = {'HDISK': 42,
                            'LOG': '/usr/local/logs/esxi-vm.log',
                            'VMXOPTS': 'vmxopt',
                            'HOST': 'esxhost',
                            'ISO': 'centos.iso',
                            'VIRTDEV': 'notpvscsi',
                            'GUESTOS': 'centos-48',
                            'NET': 'test-net',
                            'PASSWORD': 'passwd',
                            'CPU': 9,
                            'STORE': 'test-ds',
                            'isDryRun': True,
                            'isVerbose': True,
                            'DISKFORMAT': 'thick',
                            'MEM': 6,
                            'isSummary': True,
                            'USER': 'test-user'
                           }

TEST_DATETIME = datetime.datetime(2019, 12, 8, 21, 30, 9, 31532)


# class TestSetupConfig(TestCase):
#     """ Test setup_config function """
#
#     @patch('os.path.expanduser', return_value=".")
#     @patch('os.path.exists', return_value=None)
#     @patch('__builtin__.open', new_callable=mock_open)
#     def test_setup_config_default(self, open_patch, exists_patch, expanduser_patch):
#         """ Test mocking user directory to be . and empty config file
#         comparing the result with expected_default_ConfigData """
#         ret_configdata = setup_config()
#         self.assertDictEqual(ret_configdata, EXPECTED_DEFAULT_CONFIGDATA)
#         open_patch.assert_called_with("./.esxi-vm.yml", 'w')
#         exists_patch.assert_called_once()
#         expanduser_patch.assert_has_calls([call("~"), call("~")])
#
#     @patch('os.path.expanduser', return_value=".")
#     @patch('os.path.exists', return_value=True)
#     @patch('__builtin__.open', new_callable=mock_open, read_data=TEST_ESXI_VM_YML)
#     def test_setup_config_with_yml(self, open_patch, exists_patch, expanduser_patch):
#         """ Mocking providing test_esxi_vm_yml as test config data, checking that
#         results match good_yml_test_ConfigData """
#         ret_configdata = setup_config()
#         self.assertDictEqual(ret_configdata, GOOD_YML_TEST_CONFIGDATA)
#         open_patch.assert_called_with("./.esxi-vm.yml", 'w')
#         exists_patch.assert_called_once()
#         expanduser_patch.assert_has_calls([call("~"), call("~")])
#
#     @patch('sys.stdout')
#     @patch('os.path.expanduser', return_value="/test1")
#     @patch('os.path.exists', return_value=True)
#     @patch('__builtin__.open', new_callable=mock_open, read_data=TEST_ESXI_VM_YML)
#     @patch('yaml.dump', side_effect=Exception("Test_Setup_Config Except"))
#     # def test_setup_config_with_exception(self, yaml_patch, open_patch,
#     #                                      exists_patch, expanduser_patch, stdout_patch):
#     def test_setup_config_with_exception(self, *args):
#         """ Test, mocking an exception being raised. """
#         (yaml_patch, open_patch, exists_patch, expanduser_patch, stdout_patch) = args
#         with self.assertRaises(SystemExit):
#             setup_config()
#         yaml_patch.assert_called_once()
#         self.assertTrue(call('/test1/.esxi-vm.yml') in open_patch.call_args_list)
#         self.assertTrue(call('/test1/.esxi-vm.yml', 'w') in open_patch.call_args_list)
#         exists_patch.assert_called_with('/test1/.esxi-vm.yml')
#         expanduser_patch.assert_called_with("~")
#         stdout_patch.assert_has_calls(
#             [call.write('Unable to create/update config file /test1/.esxi-vm.yml'),
#              call.write('\n'),
#              call.write("The Error is <type 'exceptions.Exception'> - Test_Setup_Config Except"),
#              call.write('\n')]
#         )


# class TestSaveConfig(TestCase):
#     """ Test SaveConfig function"""
#
#     @patch('os.path.expanduser', return_value=".")
#     @patch('__builtin__.open', new_callable=mock_open)
#     def test_save_config(self, open_patch, expanduser_patch):
#         """ Test mocking user directory (.) and file open, validating .esxi-vm.yml file and
#         /usr/local/logs/esi-vm.log file being opened."""
#         ret_val = SaveConfig(GOOD_YML_TEST_CONFIGDATA)
#         self.assertEqual(ret_val, 0)
#         open_patch.assert_called_with("./.esxi-vm.yml", 'w')
#         self.assertIn(call(u'/usr/local/logs/esxi-vm.log'),
#                       open_patch().write.mock_calls)
#         expanduser_patch.assert_has_calls([call("~")])
#
#     @patch('sys.stdout')
#     @patch('os.path.expanduser', return_value="/test2")
#     @patch('__builtin__.open', side_effect=Exception("TestSaveConfigExcept"))
#     def test_save_config_with_except(self, open_patch, expanduser_patch, stdout_patch):
#         """ Test with file open raising exception. """
#         ret_val = SaveConfig(GOOD_YML_TEST_CONFIGDATA)
#         self.assertEqual(ret_val, 1)
#         open_patch.assert_called_with("/test2/.esxi-vm.yml", 'w')
#         expanduser_patch.assert_called_with("~")
#         stdout_patch.assert_has_calls(
#             [call.write('Unable to create/update config file /test2/.esxi-vm.yml'),
#              call.write('\n'),
#              call.write("The Error is <type 'exceptions.Exception'> - TestSaveConfigExcept"),
#              call.write('\n')
#             ])


class TestTheCurrDateTime(TestCase):
    """ Test theCurrDateTime function """

    @patch('datetime.datetime')
    def test_the_curr_date_time(self, datetime_patch):
        """ Mock datetime, and validate function returns expected object. """
        datetime_patch.now.return_value = TEST_DATETIME
        ret_val = current_datetime_iso_string()
        self.assertEqual('2019-12-08T21:30:09.031532', ret_val)


class TestFloat2human(TestCase):
    """ Test float2human function """

    def test_float2human_zero(self):
        """ Test that 0 returns '0 bytes' """
        ret_val = float2human(0)
        self.assertEqual("0 bytes", ret_val)

    def test_float2human_one(self):
        """ Test that 1 returns '1 byte' """
        ret_val = float2human(1)
        self.assertEqual("1 byte", ret_val)

    def test_float2human_more(self):
        """ Test that 4096 returns '4 kB' """
        ret_val = float2human(4096)
        self.assertEqual("4 kB", ret_val)


class TestConfig(TestCase):
    """ Unit tests for Config class """

    def setUp(self):
        """ Setup object and patches before tests """
        expanduser_patcher = patch('os.path.expanduser')

        self.expanduser_patch = expanduser_patcher.start()

        self.expanduser_patch.return_value = "mockhome"

        self.addCleanup(expanduser_patcher.stop)

        self.test_obj = Config()

    def test_set(self):
        """ Test Config.set """
        self.test_obj.set('test_set', 'test_set_value')
        self.assertEqual('test_set_value', self.test_obj.data.get('test_set'))

    def test_get(self):
        """ Test Config.get """
        self.test_obj.data['test_get'] = 'test_get_value'
        self.assertEqual('test_get_value', self.test_obj.get('test_get'))

    @patch('os.path.exists', return_value=False)
    def test_load_config_bad_yml_given(self, path_exists_patch):
        """ Test Config.load_config with file existing being mock'ed to False """
        self.assertFalse(self.test_obj.load_config(yml_file="testfile"))
        path_exists_patch.assert_called_once()

    @patch('yaml.safe_load', return_value={'load_config_test': 'load_config_test_value'})
    @patch('__builtin__.open')
    @patch('os.path.exists', return_value=True)
    def test_load_config_good_default_yml(self, path_exists_patch, open_patch,
                                          yaml_safe_load_patch):
        """ Test Config.load_config with file existing mock'ed to True, file open being
        patched, and yaml load mock'ing dict return. """
        self.assertTrue(self.test_obj.load_config())
        self.assertEqual('load_config_test_value', self.test_obj.data.get('load_config_test'))
        self.assertListEqual([call('mockhome/.esxi-vm.yml')], path_exists_patch.mock_calls)
        self.assertListEqual([call('mockhome/.esxi-vm.yml')], open_patch.mock_calls)
        yaml_safe_load_patch.assert_called_once()

    def test_logfile(self):
        """ Test Config.logfie """
        self.assertEqual("mockhome/esxi-vm.log", self.test_obj.logfile())

    def test_setup_config(self):
        """ Test Config.setup_config sets up object with expected defaults """
        ret_dict = self.test_obj.setup_config()
        self.assertDictEqual(
            {
                'CPU': 2,
                'DISKFORMAT': 'thin',
                'GUESTOS': 'centos-64',
                'HDISK': 20,
                'HOST': 'esxi',
                'ISO': 'None',
                'LOG': 'mockhome/esxi-vm.log',
                'MEM': 4,
                'NET': 'None',
                'PASSWORD': '',
                'STORE': 'LeastUsed',
                'USER': 'root',
                'VIRTDEV': 'pvscsi',
                'VMXOPTS': '',
                'isDryRun': False,
                'isSummary': False,
                'isVerbose': False
            }, ret_dict)

    @patch('__builtin__.open', side_effect=OSError)
    def test_save_config_except(self, open_patch):
        """ Test Config.save_config mock'ing file open to Raise exception """
        self.assertFalse(self.test_obj.save_config())
        open_patch.assert_has_calls([call('mockhome/.esxi-vm.yml', 'w')])

    @patch('__builtin__.open', new_callable=mock_open)
    def test_save_config_good(self, open_patch):
        """ Test Config.save_config with file open being patched and testing expected calls """
        self.test_obj.data = {"test_save_config": "test_save_config_value"}
        self.assertTrue(self.test_obj.save_config())
        open_patch.assert_has_calls([call('mockhome/.esxi-vm.yml', 'w'),
                                     call().__enter__(),
                                     call().encoding.__nonzero__(),
                                     call().write(u'test_save_config'),
                                     call().write(u':'),
                                     call().write(u' '),
                                     call().write(u'test_save_config_value'),
                                     call().write(u'\n'),
                                     call().flush(),
                                     call().flush(),
                                     call().__exit__(None, None, None),
                                     call().close()])


class TestMessage(TestCase):
    """ Unit tests for Message class """

    def setUp(self):
        """ Setup object and patches before testing """
        self.test_obj = Message()

        print_patcher = patch('sys.stdout')
        open_patcher = patch('__builtin__.open')

        self.print_patch = print_patcher.start()
        self.open_patch = open_patcher.start()

        self.open_patch.new_callable = mock_open

        self.addCleanup(print_patcher.stop)
        self.addCleanup(open_patcher.stop)

    def test_tty_print(self):
        """ Test Message.tty_print """
        self.test_obj.messages = "Test print message."
        self.test_obj.tty_print()
        self.print_patch.assert_has_calls([call.write('Test print message.'), call.write('\n')])

    def test_log_to_file_except(self):
        """ Test Message.log_to_file with open being mock'ed to return IOError """
        self.open_patch.side_effect = IOError
        self.test_obj.messages = "Should Not See"
        self.test_obj.log_to_file(logfile="BadFile")
        self.assertListEqual(
            [call.write('Error writing to log file: BadFile'), call.write('\n')],
            self.print_patch.mock_calls
        )

    def test_log_to_file_ok(self):
        """ Test Message.log_to_file clearing open mock side_effect and testing called OK """
        if 'side_effect' in self.open_patch:
            del self.open_patch.side_effect
        self.test_obj.messages = "Test Log Message"
        self.test_obj.log_to_file(logfile="OKLogFile")

        self.assertListEqual([], self.print_patch.mock_calls)
        self.open_patch.assert_has_calls(
            [call('OKLogFile', 'a'),
             call().__enter__(),
             call().__enter__().write('Test Log Message'),
             call().__exit__(None, None, None)
            ])
        self.assertEqual(5, len(self.open_patch.mock_calls))

    def test_add(self):
        """ Test Message.add """
        self.test_obj.messages = ""
        self.test_obj += "Test First Message."
        self.test_obj = self.test_obj + "Test Second Message With Comma,"
        self.test_obj += "Test Third Message."
        self.assertEqual("Test First Message. Test Second Message With Comma,Test Third Message.",
                         self.test_obj.messages)

    def test_show(self):
        """ Test Message.show """
        self.test_obj.messages = "test_show test message"
        self.assertEqual("test_show test message", self.test_obj.show())


class TestEsxVm(TestCase):
    """ Unit tests for EsxVm Class """

    def setUp(self):
        self.test_obj = EsxVm(vm_name="test_vm_name", vmx_file="/test/vmx/file")

    def test_set_config_version(self):
        """ test for setting config version """
        self.test_obj.set_config_version(version="test_set_version")
        self.assertEqual("test_set_version", self.test_obj.config['config.version'])

    def test_set_defaults(self):
        """ test for setting defaults """
        self.test_obj.set_defaults()
        self.assertDictEqual({'config.version': '8'}, self.test_obj.config)

    def test_set_hw_version_ok(self):
        """ test for setting HW version with proper choice """
        ret_val = self.test_obj.set_hw_version("11")
        self.assertEqual("11", ret_val)
        self.assertEqual("11", self.test_obj.config['virtualHW.version'])

    def test_set_hw_version_bad_new(self):
        """ test for setting HW version with bad choice not set previously.
        Expect that new setting will be default. """
        if 'virtualHW.version' in self.test_obj.config:
            del self.test_obj.config['virtualHW.version']
        ret_val = self.test_obj.set_hw_version("2")
        self.assertNotEqual("8", ret_val)
        self.assertNotEqual("8", self.test_obj.config['virtualHW.version'])

    def test_set_hw_version_bad_update(self):
        """ test for setting HW version with bad choice and previously set.
        Expect that previous setting won't be overridden.
        """
        self.test_obj.config['virtualHW.version'] = "9"
        ret_val = self.test_obj.set_hw_version("2")
        self.assertNotEqual("9", ret_val)
        self.assertNotEqual("9", self.test_obj.config['virtualHW.version'])


class TestEsxVmCpu(TestCase):
    """ Unit tests for EsxVmCpu Class """
    def setUp(self):
        self.test_obj = EsxVmCpu()

    def test_get_sockets(self):
        self.test_obj.params["numvcpus"] = 12
        self.test_obj.params["corespersocket"] = 3
        self.assertEqual(4, self.test_obj.get_sockets())

    def test_set_hot_plug(self):
        self.test_obj.set_hot_plug(enabled=True)
        self.assertEqual(True, self.test_obj.params['cpu_hot_plug'])

    def test_set_hot_plug_except(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_hot_plug(enabled="bad")

    def test_set_reservation_none(self):
        self.test_obj.params['reservation'] = "seed"
        self.test_obj.set_reservation()
        self.assertIsNone(self.test_obj.params['reservation'])

    def test_set_reservation_except(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_reservation(reservation="bad")

    def test_set_reservation_good(self):
        self.test_obj.params['reservation'] = "seed"
        self.test_obj.set_reservation(reservation=42)
        self.assertEqual(42, self.test_obj.params['reservation'])

    def test_set_limit_none(self):
        self.test_obj.params['limit'] = "seed"
        self.test_obj.set_limit()
        self.assertIsNone(self.test_obj.params['limit'])

    def test_set_limit_except(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_limit(limit="bad")

    def test_set_limit_good(self):
        self.test_obj.set_limit(limit=42)
        self.assertEqual(42, self.test_obj.params['limit'])

    def test_set_shares_except(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_shares(shares="bad")

    def test_set_shares_good(self):
        self.test_obj.set_shares(shares="low")
        self.assertEqual("low", self.test_obj.params['shares'])

    def test_set_hw_virt(self):
        self.test_obj.set_hw_virt(hw_virt=True)
        self.assertTrue(self.test_obj.params['hw_virt'])

    def test_set_hw_virt_except(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_hw_virt(hw_virt="bad")

    def test_set_perf_counters_except(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_perf_counters(perf_counters="bad")

    def test_set_perf_counters_good(self):
        self.test_obj.set_perf_counters(perf_counters=True)
        self.assertTrue(self.test_obj.params['perf_counters'])

    def test_set_affinity_except(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_affinity(affinity="bad")

    def test_set_affinity_auto(self):
        self.test_obj.params['affinity'] = "seed"
        self.test_obj.set_affinity()
        self.assertEqual("Auto", self.test_obj.params['affinity'])

    def test_set_affinity_int_list(self):
        self.test_obj.set_affinity(affinity=[1, 3, 4])
        self.assertEqual("1,3,4", self.test_obj.params['affinity'])

    def test_set_cpu_mmu_virt_bad_type(self):
        with self.assertRaises(TypeError):
            self.test_obj.set_cpu_mmu_virt(cpu_virt="bad")

    def test_set_cpu_mmu_virt_bad_value(self):
        with self.assertRaises(ValueError):
            self.test_obj.set_cpu_mmu_virt(cpu_virt="Auto", mmu_virt="software")

    def test_set_cpu_mmu_virt_good(self):
        self.test_obj.set_cpu_mmu_virt(cpu_virt="software", mmu_virt="software")
        self.assertTupleEqual(("software", "software"),
                              (self.test_obj.params['cpu_virt'],
                               self.test_obj.params['mmu_virt']))
