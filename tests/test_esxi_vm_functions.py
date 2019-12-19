"""
test_esxi_vm_functions.py:
    unittests for functions/methods in esxi_vm_functions.py module.
"""
from unittest import TestCase
import sys
import datetime

from esxi_vm_functions import setup_config, SaveConfig, theCurrDateTime, float2human

if sys.version_info.major == 2:
    from mock import patch, mock_open, call
else:
    from unittest.mock import patch, mock_open # pylint: disable=no-name-in-module,import-error,ungrouped-imports

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

class TestSetupConfig(TestCase):
    """ Test setup_config function """

    @patch('os.path.expanduser', return_value=".")
    @patch('os.path.exists', return_value=None)
    @patch('__builtin__.open', new_callable=mock_open)
    def test_setup_config_default(self, open_patch, exists_patch, expanduser_patch):
        """ Test mocking user directory to be . and empty config file
        comparing the result with expected_default_ConfigData """
        ret_configdata = setup_config()
        self.assertDictEqual(ret_configdata, EXPECTED_DEFAULT_CONFIGDATA)
        open_patch.assert_called_with("./.esxi-vm.yml", 'w')
        exists_patch.assert_called_once()
        expanduser_patch.assert_has_calls([call("~"), call("~")])

    @patch('os.path.expanduser', return_value=".")
    @patch('os.path.exists', return_value=True)
    @patch('__builtin__.open', new_callable=mock_open, read_data=TEST_ESXI_VM_YML)
    def test_setup_config_with_yml(self, open_patch, exists_patch, expanduser_patch):
        """ Mocking providing test_esxi_vm_yml as test config data, checking that
        results match good_yml_test_ConfigData """
        ret_configdata = setup_config()
        self.assertDictEqual(ret_configdata, GOOD_YML_TEST_CONFIGDATA)
        open_patch.assert_called_with("./.esxi-vm.yml", 'w')
        exists_patch.assert_called_once()
        expanduser_patch.assert_has_calls([call("~"), call("~")])

    @patch('os.path.expanduser', return_value=".")
    @patch('os.path.exists', return_value=True)
    @patch('__builtin__.open', new_callable=mock_open, read_data=TEST_ESXI_VM_YML)
    @patch('yaml.dump', side_effect=Exception("Test Except"))
    def test_setup_config_with_exception(self, yaml_patch, open_patch,
                                         exists_patch, expanduser_patch):
        """ Test, mocking an exception being raised. """
        with self.assertRaises(SystemExit):
            setup_config()
        yaml_patch.assert_called_once()
        self.assertTrue(call('./.esxi-vm.yml') in open_patch.call_args_list)
        self.assertTrue(call('./.esxi-vm.yml', 'w') in open_patch.call_args_list)
        exists_patch.assert_called_with('./.esxi-vm.yml')
        expanduser_patch.assert_called_with("~")


class TestSaveConfig(TestCase):
    """ Test SaveConfig function"""

    @patch('os.path.expanduser', return_value=".")
    @patch('__builtin__.open', new_callable=mock_open)
    def test_save_config(self, open_patch, expanduser_patch):
        """ Test mocking user directory (.) and file open, validating .esxi-vm.yml file and
        /usr/local/logs/esi-vm.log file being opened."""
        ret_val = SaveConfig(GOOD_YML_TEST_CONFIGDATA)
        self.assertEqual(ret_val, 0)
        open_patch.assert_called_with("./.esxi-vm.yml", 'w')
        self.assertIn(call(u'/usr/local/logs/esxi-vm.log'),
                      open_patch().write.mock_calls)
        expanduser_patch.assert_has_calls([call("~")])

    @patch('os.path.expanduser', return_value=".")
    @patch('__builtin__.open', side_effect=Exception("TestExcept"))
    def test_save_config_with_except(self, open_patch, expanduser_patch):
        """ Test with file open raising exception. """
        ret_val = SaveConfig(GOOD_YML_TEST_CONFIGDATA)
        self.assertEqual(ret_val, 1)
        open_patch.assert_called_with("./.esxi-vm.yml", 'w')
        expanduser_patch.assert_called_with("~")



class TestTheCurrDateTime(TestCase):
    """ Test theCurrDateTime function """

    @patch('datetime.datetime')
    def test_the_curr_date_time(self, datetime_patch):
        """ Mock datetime, and validate function returns expected object. """
        datetime_patch.now.return_value = TEST_DATETIME
        ret_val = theCurrDateTime()
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
