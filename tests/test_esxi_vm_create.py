from unittest import TestCase
import sys
import io
import datetime

if sys.version_info.major == 2:
    from mock import patch, mock_open, call
else:
    from unittest.mock import patch, mock_open
from esxi_vm_create import main



class TestMain(TestCase):

    @patch('sys.stdout', new_callable=io.BytesIO)
    @patch('sys.argv', ['esxi_vm_create.py', '-h'])
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    def test_main_help(self, saveconfig_patch, setup_config_patch, print_patch):
        with self.assertRaises(SystemExit):
            main()

    @patch('sys.stdout', new_callable=io.BytesIO)
    @patch('sys.argv', ['esxi_vm_create.py',
                        '--dry',
                        '--Host', 'hostarg',
                        '--User', 'userarg',
                        '--Password', 'passwordarg',
                        '--name', '',
                        '--cpu', '9',
                        '--mem', '99',
                        '--vdisk', '999',
                        '--iso', 'isoarg',
                        '--net', 'netarg',
                        '--mac', 'macarg',
                        '--store', 'storearg',
                        '--guestos', 'guestosarg',
                        '--options', 'optionsarg',
                        '--verbose',
                        '--summary',
                        '--updateDefaults',
                       ])
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    def test_main_update_conf_no_name(self, setup_config_patch, saveconfig_patch, print_patch):
        with self.assertRaises(SystemExit):
            main()

    @patch('sys.stdout', new_callable=io.BytesIO)
    @patch('sys.argv', ['esxi_vm_create.py',
                        '--dry',
                        '--Host', 'hostarg',
                        '--User', 'userarg',
                        '--Password', 'passwordarg',
                        '--name', '',
                        '--cpu', '9',
                        '--mem', '99',
                        '--vdisk', '999',
                        '--iso', 'isoarg',
                        '--net', 'netarg',
                        '--mac', 'macarg',
                        '--store', '',
                        '--guestos', 'guestosarg',
                        '--options', 'optionsarg',
                        '--verbose',
                        '--summary',
                        ])
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    def test_main_no_update_no_name(self, setup_config_patch, saveconfig_patch, print_patch):
        def mock_getitem(key):
            if key in ('CPU', 'MEM', 'HDISK'):
                return 0
            elif key in ('VMXOPTS'):
                return "NIL"
            else:
                return ""
        setup_config_patch().__getitem__.side_effect = mock_getitem
        with self.assertRaises(SystemExit):
            main()
        sys.stderr.write("{}\n".format(dir(setup_config_patch)))
        sys.stderr.write("{}\n".format(setup_config_patch.mock_calls))

    @patch('sys.stdout', new_callable=io.BytesIO)
    @patch('sys.argv', ['esxi_vm_create.py',
                        '--dry',
                        '--Host', 'hostarg',
                        '--User', 'userarg',
                        '--Password', 'passwordarg',
                        '--name', 'namearg',
                        '--cpu', '9',
                        '--mem', '99',
                        '--vdisk', '999',
                        '--iso', 'isoarg',
                        '--net', 'netarg',
                        '--mac', 'macarg',
                        '--store', '',
                        '--guestos', 'guestosarg',
                        '--options', 'optionsarg',
                        '--verbose',
                        '--summary',
                        ])
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_start_ssh(self, paramiko_patch, setup_config_patch, saveconfig_patch, print_patch):
        def mock_getitem(key):
            if key in ('CPU', 'MEM', 'HDISK'):
                return 0
            elif key in ('VMXOPTS'):
                return "NIL"
            else:
                return ""
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command.side_effect=Exception("TestExcept")
        with self.assertRaises(SystemExit):
            main()
        sys.stderr.write("{}\n".format(dir(setup_config_patch)))
        sys.stderr.write("{}\n".format(setup_config_patch.mock_calls))
        sys.stderr.write("{}\n".format(paramiko_patch.mock_calls))
        sys.stderr.write("{}\n".format(paramiko_patch.SSHClient().exec_command.mock_calls))
