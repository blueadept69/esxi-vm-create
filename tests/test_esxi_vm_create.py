from unittest import TestCase
import sys
import datetime
if sys.version_info.major == 2:
    from mock import patch, mock_open, call
else:
    from unittest.mock import patch, mock_open
from esxi-vm-create import main

# expected_default_ConfigData = {'HDISK': 20,
#                        'LOG': './esxi-vm.log',
#                        'VMXOPTS': '',
#                        'HOST': 'esxi',
#                        'ISO': 'None',
#                        'VIRTDEV': 'pvscsi',
#                        'GUESTOS': 'centos-64',
#                        'NET': 'None',
#                        'PASSWORD': '',
#                        'CPU': 2,
#                        'STORE': 'LeastUsed',
#                        'isDryRun': False,
#                        'isVerbose': False,
#                        'DISKFORMAT': 'thin',
#                        'MEM': 4,
#                        'isSummary': False,
#                        'USER': 'root'
#                       }
#
# test_esxi_vm_yml = """CPU: 9
# DISKFORMAT: thick
# GUESTOS: centos-48
# HDISK: 42
# HOST: esxhost
# ISO: centos.iso
# LOG: /usr/local/logs/esxi-vm.log
# MEM: 6
# NET: test-net
# PASSWORD: passwd
# STORE: test-ds
# USER: test-user
# VIRTDEV: notpvscsi
# VMXOPTS: vmxopt
# isDryRun: true
# isSummary: true
# isVerbose: true
# """
#
# good_yml_test_ConfigData = {'HDISK': 42,
#                                 'LOG': '/usr/local/logs/esxi-vm.log',
#                                 'VMXOPTS': 'vmxopt',
#                                 'HOST': 'esxhost',
#                                 'ISO': 'centos.iso',
#                                 'VIRTDEV': 'notpvscsi',
#                                 'GUESTOS': 'centos-48',
#                                 'NET': 'test-net',
#                                 'PASSWORD': 'passwd',
#                                 'CPU': 9,
#                             'STORE': 'test-ds',
#                             'isDryRun': True,
#                             'isVerbose': True,
#                             'DISKFORMAT': 'thick',
#                             'MEM': 6,
#                             'isSummary': True,
#                             'USER': 'test-user'
#                             }
#
# test_datetime = datetime.datetime(2019, 12, 8, 21, 30, 9, 31532)
#
# class TestSetup_config(TestCase):
#
#     @patch('os.path.expanduser', return_value=".")
#     @patch('os.path.exists', return_value=None)
#     @patch('__builtin__.open', new_callable=mock_open)
#     def test_setup_config_default(self, open_patch, exists_patch, expanduser_patch):
#         ret_configdata = setup_config()
#         self.assertDictEqual(ret_configdata, expected_default_ConfigData)
#         open_patch.assert_called_with("./.esxi-vm.yml", 'w')
#         exists_patch.assert_called_once()
#         expanduser_patch.assert_has_calls([call("~"), call("~")])
#
#     @patch('os.path.expanduser', return_value=".")
#     @patch('os.path.exists', return_value=True)
#     @patch('__builtin__.open', new_callable=mock_open, read_data=test_esxi_vm_yml)
#     def test_setup_config_with_yml(self, open_patch, exists_patch, expanduser_patch):
#         ret_configdata = setup_config()
#         self.assertDictEqual(ret_configdata, good_yml_test_ConfigData)
#         open_patch.assert_called_with("./.esxi-vm.yml", 'w')
#         exists_patch.assert_called_once()
#         expanduser_patch.assert_has_calls([call("~"), call("~")])
#
#     @patch('os.path.expanduser', return_value=".")
#     @patch('os.path.exists', return_value=True)
#     @patch('__builtin__.open', new_callable=mock_open, read_data=test_esxi_vm_yml)
#     @patch('yaml.dump', side_effect=Exception("Test Except"))
#     def test_setup_config_with_exception(self, yaml_patch, open_patch, exists_patch, expanduser_patch):
#         with self.assertRaises(SystemExit):
#             setup_config()
#
#
# class TestSaveConfig(TestCase):
#     @patch('os.path.expanduser', return_value=".")
#     @patch('__builtin__.open', new_callable=mock_open)
#     def test_save_config(self, open_patch, expanduser_patch):
#         ret_val = SaveConfig(good_yml_test_ConfigData)
#         self.assertEqual(ret_val, 0)
#         open_patch.assert_called_with("./.esxi-vm.yml", 'w')
#         self.assertIn(call(u'/usr/local/logs/esxi-vm.log'),
#                       open_patch().write.mock_calls)
#         expanduser_patch.assert_has_calls([call("~")])
#
#     @patch('os.path.expanduser', return_value=".")
#     @patch('os.path.exists', return_value=True)
#     @patch('__builtin__.open', side_effect=Exception("TestExcept"))
#     def test_save_config_with_except(self, open_patch, exists_patch, expanduser_patch):
#         ret_val = SaveConfig(good_yml_test_ConfigData)
#         self.assertEqual(ret_val, 1)
#         open_patch.assert_called_with("./.esxi-vm.yml", 'w')
#
#
# class TestTheCurrDateTime(TestCase):
#     @patch('datetime.datetime')
#     def test_theCurrDateTime(self, datetime_patch):
#         datetime_patch.now.return_value = test_datetime
#         ret_val = theCurrDateTime()
#         self.assertEqual('2019-12-08T21:30:09.031532', ret_val)
#
#
# class TestFloat2human(TestCase):
#     def test_float2human_zero(self):
#         ret_val = float2human(0)
#         self.assertEqual("0 bytes", ret_val)
#
#     def test_float2human_one(self):
#         ret_val = float2human(1)
#         self.assertEqual("1 byte", ret_val)
#
#     def test_float2human_more(self):
#         ret_val = float2human(4096)
#         self.assertEqual("4 kB", ret_val)