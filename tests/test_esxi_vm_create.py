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
                        '--store', 'storearg',
                        '--guestos', 'guestosarg',
                        '--options', 'optionsarg',
                        '--verbose',
                        '--summary',
                        ])
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    def test_main_no_update_no_name(self, setup_config_patch, saveconfig_patch, print_patch):
        with self.assertRaises(SystemExit):
            main()
        #sys.stderr.write(dir(self))