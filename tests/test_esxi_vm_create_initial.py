"""
test_esxi_vm_create_initial.py:
    unittests for functions/methods in main esxi_vm_create.py script.
"""
from unittest import TestCase
import sys
from esxi_vm_create import main
from tests import testcases
from tests.testcases import mock_getitem

if sys.version_info.major == 2:
    from mock import patch, call
else:
    from unittest.mock import patch, call  # pylint: disable=no-name-in-module,import-error,ungrouped-imports


class TestMainInitial(TestCase):
    """ Test main() function - initial steps of program run. """

    testcases.MOCK_GETITEM_LOGFILE = ""

    @patch('sys.stdout')
    @patch('sys.argv', ['esxi_vm_create.py', '-h'])
    @patch('esxi_vm_create.setup_config')
    def test_main_help(self, setup_config_patch, print_patch):
        """ Test mocking -h option passing if sys.exit called. """
        sys.stderr.write("=========> IN: test_main_help\n")
        with self.assertRaises(SystemExit):
            main()
        setup_config_patch.assert_called_with()
        self.assertIn("usage", str(print_patch.method_calls))


    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_NAME_UPDATEDEFAULTS)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    def test_main_update_conf_no_name(self, setup_config_patch, saveconfig_patch, print_patch):
        """ Test mocking a call with --updateDefaults and no --name provided,
        looking for sys.exit call. """
        sys.stderr.write("=========> IN: test_main_update_conf_no_name\n")
        with self.assertRaises(SystemExit):
            main()
        setup_config_patch.assert_called_with()
        saveconfig_patch.assert_called_once()
        print_patch.assert_has_calls(
            [call.write('Saving new Defaults to ~/.esxi-vm.yml'), call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_NAME_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    def test_main_no_update_no_name(self, setup_config_patch, saveconfig_patch, print_patch):
        """
        Test mocking call with no --update called and no --name called.
        """
        sys.stderr.write("=========> IN: test_main_no_update_no_name\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('ERROR: Missing required option --name'), call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_start_ssh(self, paramiko_patch, setup_config_patch,
                            saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls raise exception and test except code.
        """
        sys.stderr.write("=========> IN: test_main_start_ssh\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command.side_effect = Exception("TestExcept")
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestExcept"),
             call.write('\n'),
             call.write('Unable to access ESXi Host: hostarg, username: userarg'),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_esxcli_version_fail(self, paramiko_patch, setup_config_patch,
                                      saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning None to esxcli call to test
        handling of bad result.
        """
        sys.stderr.write("=========> IN: test_main_esxcli_version_fail\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "esxcli system version get |grep Version": {
                    'stdout': None,
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('Unable to determine if this is a ESXi Host: hostarg, username: userarg'),
             call.write('\n'),
             call.write("The Error is <type 'exceptions.SystemExit'> - 1"),
             call.write('\n'),
             call.write('Unable to access ESXi Host: hostarg, username: userarg'),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_esxcli_volume_fail(self, paramiko_patch, setup_config_patch,
                                     saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "valid" version but raising
        exception reading from volume list to test exception handling.

        ******** THIS CODE IN ESXI_VM_CREATE.PY NEEDS TO BE FIXED - REGEX MATCH FOR Version
        DOES NOT WORK CORRECTLY. THIS TEST (AND COPIED TESTS BELOW) IS
        TECHNICALLY INVALID!!!! **************

        """
        sys.stderr.write("=========> IN: test_main_esxcli_volume_fail\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "esxcli storage filesystem list |grep '/vmfs/volumes/.*true  VMFS' |sort -nk7": {
                    'Exception': 'TestVolumeFail',
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestVolumeFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_esxcli_portgroups_fail(self, paramiko_patch, setup_config_patch,
                                         saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list, raising exception on run of esxcli command for portgroups list.
        """
        sys.stderr.write("=========> IN: test_main_esxcli_portgroups_fail\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "esxcli network vswitch standard list|grep Portgroups|"
                "sed 's/^   Portgroups: //g'": {
                    'Exception': 'TestPortgroupFail',
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestPortgroupFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_find_iso_fail_mac1(self, paramiko_patch, setup_config_patch,
                                     saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list and PGs and MAC, raising exception on run of find command for ISO file.
        """
        sys.stderr.write("=========> IN: test_main_find_iso_fail_mac1\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                r"find /vmfs/volumes/ -type f -name {} -exec sh -c 'echo $1; kill $PPID' "
                r"sh {{}} 2>/dev/null \;".format(testcases.TEST_ISO_NAME_ARG): {
                    'Exception': 'TestFindISOFail',
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestFindISOFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE_BAD_MAC)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_find_iso_fail_mac2(self, paramiko_patch, setup_config_patch,
                                     saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list and PGs and MAC, raising exception on run of find command for ISO file.
        """
        sys.stderr.write("=========> IN: test_main_find_iso_fail_mac2\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                r"find /vmfs/volumes/ -type f -name {} -exec sh -c 'echo $1; kill $PPID' "
                r"sh {{}} 2>/dev/null \;".format(testcases.TEST_ISO_NAME_ARG): {
                    'Exception': 'TestFindISOFail',
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestFindISOFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_ok_find_iso_fail_getallvms(self, paramiko_patch, setup_config_patch,
                                             saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list and PGs and MAC, raising exception on run of find command for ISO file.
        """
        sys.stderr.write("=========> IN: test_main_ok_find_iso_fail_getallvms\n")
        setup_config_patch().__getitem__.side_effect = mock_getitem
        paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "vim-cmd vmsvc/getallvms": {
                    'Exception': 'TEST_GETALLVMS_FAIL',
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('FoundISOPath: /vmfs/volumes/test/ISOs/isoarg'),
             call.write('\n'),
             call.write("The Error is <type 'exceptions.Exception'> - TEST_GETALLVMS_FAIL"),
             call.write('\n')])
