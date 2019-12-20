"""
test_esxi_vm_create.py:
    unittests for functions/methods in main esxi_vm_create.py script.
"""
from unittest import TestCase
import sys
from esxi_vm_create import main

if sys.version_info.major == 2:
    from mock import patch, call, MagicMock
else:
    from unittest.mock import patch, MagicMock  # pylint: disable=no-name-in-module,import-error,ungrouped-imports


class TestMain(TestCase):
    """ Test main() function """

    @patch('sys.stdout')
    @patch('sys.argv', ['esxi_vm_create.py', '-h'])
    @patch('esxi_vm_create.setup_config')
    def test_main_help(self, setup_config_patch, print_patch):
        """ Test mocking -h option passing if sys.exit called. """
        with self.assertRaises(SystemExit):
            main()
        setup_config_patch.assert_called_with()
        self.assertIn("usage", str(print_patch.method_calls))


    @patch('sys.stdout')
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
        """ Test mocking a call with --updateDefaults and no --name provided,
        looking for sys.exit call. """
        with self.assertRaises(SystemExit):
            main()
        setup_config_patch.assert_called_with()
        saveconfig_patch.assert_called_once()
        print_patch.assert_has_calls(
            [call.write('Saving new Defaults to ~/.esxi-vm.yml'), call.write('\n')])


    @patch('sys.stdout')
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
    @patch('esxi_vm_create.setup_config')
    def test_main_no_update_no_name(self, setup_config_patch, print_patch):
        """
        Test mocking call with no --update called and no --name called.
        """
        def mock_getitem(key):
            """ getitem for mock'ed return values to return ints (for keys that get converted to
            int) and a non-empty string for VMXOPTS since string comparison of mocked return
            values would otherwise show as __repr__ for mock and not what we're trying
            to simulate. """
            if key in ('CPU', 'MEM', 'HDISK'):
                return 0
            elif key == 'VMXOPTS':
                return "NIL"
            return ""
        setup_config_patch().__getitem__.side_effect = mock_getitem
        with self.assertRaises(SystemExit):
            main()
        print_patch.assert_has_calls(
            [call.write('ERROR: Missing required option --name'), call.write('\n')])

    @patch('sys.stdout')
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
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_start_ssh(self, paramiko_patch, setup_config_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls raise exception and test except code.
        """
        def mock_getitem(key):
            """ getitem for mock'ed return values to return ints (for keys that get converted to
            int) and a non-empty string for VMXOPTS since string comparison of mocked return
            values would otherwise show as __repr__ for mock and not what we're trying
            to simulate. """
            if key in ('CPU', 'MEM', 'HDISK'):
                return 0
            elif key == 'VMXOPTS':
                return "NIL"
            return ""
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command.side_effect = Exception("TestExcept")
        with self.assertRaises(SystemExit):
            main()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'>"),
             call.write('\n'),
             call.write('Unable to access ESXi Host: hostarg, username: userarg'),
             call.write('\n')])

    @patch('sys.stdout')
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
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_esxcli_version_fail(self, paramiko_patch, setup_config_patch, print_patch):
    # def test_main_esxcli_version_fail(self, paramiko_patch, setup_config_patch):

        """
        Test mocking with --name and mocking ssh calls raise exception and test except code.
        """
        def mock_getitem(key):
            """ getitem for mock'ed return values to return ints (for keys that get converted to
            int) and a non-empty string for VMXOPTS since string comparison of mocked return
            values would otherwise show as __repr__ for mock and not what we're trying
            to simulate. """
            if key in ('CPU', 'MEM', 'HDISK'):
                return 0
            elif key == 'VMXOPTS':
                return "NIL"
            return ""
        setup_config_patch().__getitem__.side_effect = mock_getitem

        def mock_ssh_command(cmd):
            """ mocking the exec_command method of paramiko to return data we need to test for. """
            stdin = MagicMock()
            stdout = MagicMock()
            stderr = MagicMock()
            if cmd == "esxcli system version get |grep Version":
                stdout.readlines.return_value = None
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        print_patch.assert_has_calls(
            [call.write('Unable to determine if this is a ESXi Host: hostarg, username: userarg'),
             call.write('\n'),
             call.write("The Error is <type 'exceptions.SystemExit'>"),
             call.write('\n'),
             call.write('Unable to access ESXi Host: hostarg, username: userarg'),
             call.write('\n')])
