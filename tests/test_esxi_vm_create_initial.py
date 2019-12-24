"""
test_esxi_vm_create_initial.py:
    unittests for functions/methods in main esxi_vm_create.py script.
"""
from unittest import TestCase
import sys
from esxi_vm_create import main

if sys.version_info.major == 2:
    from mock import patch, call, MagicMock
else:
    from unittest.mock import patch, MagicMock  # pylint: disable=no-name-in-module,import-error,ungrouped-imports

TEST_ISO_NAME_ARG = "isoarg"
TEST_ISO_PATH_ARG = "/vmfs/volumes/path/to/iso"
TEST_ARGV_BASE = ['esxi_vm_create.py',
                  # '--dry',
                  '--Host', 'hostarg',
                  '--User', 'userarg',
                  '--Password', 'passwordarg',
                  # '--name', '',
                  '--cpu', '9',
                  '--mem', '99',
                  '--vdisk', '999',
                  '--iso', TEST_ISO_NAME_ARG,
                  '--net', 'VM Network',
                  '--mac', '12:34:56',
                  # '--store', 'storearg',
                  '--guestos', 'guestosarg',
                  '--options', '',
                  '--verbose',
                  '--summary',
                  # '--updateDefaults',
                 ]

TEST_ARGV_DRY_EMPTY_NAME_UPDATEDEFAULTS = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_NAME_UPDATEDEFAULTS.extend(['--dry',
                                                '--name', '',
                                                '--store', 'storearg',
                                                '--updateDefaults',
                                               ])

TEST_ARGV_DRY_EMPTY_NAME_STORE = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_NAME_STORE.extend(['--dry',
                                       '--name', '',
                                       '--store', '',
                                      ])

TEST_ARGV_DRY_EMPTY_STORE = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_STORE.extend(['--dry',
                                  '--name', 'namearg',
                                  '--store', '',
                                 ])

TEST_ARGV_DRY_EMPTY_STORE_BAD_MAC = list(TEST_ARGV_DRY_EMPTY_STORE)
TEST_ARGV_DRY_EMPTY_STORE_BAD_MAC.extend(['--mac', 'bad_mac_arg',
                                         ])

class TestMain(TestCase):
    """ Test main() function """

    @staticmethod
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
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_NAME_UPDATEDEFAULTS)
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
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_NAME_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    def test_main_no_update_no_name(self, setup_config_patch, saveconfig_patch, print_patch):
        """
        Test mocking call with no --update called and no --name called.
        """
        setup_config_patch().__getitem__.side_effect = self.mock_getitem
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('ERROR: Missing required option --name'), call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_start_ssh(self, paramiko_patch, setup_config_patch,
                            saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls raise exception and test except code.
        """
        setup_config_patch().__getitem__.side_effect = self.mock_getitem
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
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_esxcli_version_fail(self, paramiko_patch, setup_config_patch,
                                      saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning None to esxcli call to test
        handling of bad result.
        """
        setup_config_patch().__getitem__.side_effect = self.mock_getitem

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
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('Unable to determine if this is a ESXi Host: hostarg, username: userarg'),
             call.write('\n'),
             call.write("The Error is <type 'exceptions.SystemExit'> - 1"),
             call.write('\n'),
             call.write('Unable to access ESXi Host: hostarg, username: userarg'),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
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
        setup_config_patch().__getitem__.side_effect = self.mock_getitem

        def mock_ssh_command(cmd):
            """ mocking the exec_command method of paramiko to return data we need to test for. """
            stdin = MagicMock()
            stdout = MagicMock()
            stderr = MagicMock()
            if cmd == "esxcli system version get |grep Version":
                stdout.readlines.return_value = "Version: 6.5.0"
            elif cmd == "esxcli storage filesystem list |" \
                        "grep '/vmfs/volumes/.*true  VMFS' |sort -nk7":
                stdout.readlines.side_effect = Exception("TestVolumeFail")
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestVolumeFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_esxcli_portgroups_fail(self, paramiko_patch, setup_config_patch,
                                         saveconfig_patch, print_patch):
                                        # saveconfig_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list, raising exception on run of esxcli command for portgroups list.
        """
        setup_config_patch().__getitem__.side_effect = self.mock_getitem

        def mock_ssh_command(cmd):
            """ mocking the exec_command method of paramiko to return data we need to test for. """
            stdin = MagicMock()
            stdout = MagicMock()
            stderr = MagicMock()
            if cmd == "esxcli system version get |grep Version":
                stdout.readlines.return_value = "Version: 6.5.0"
            elif cmd == "esxcli storage filesystem list |" \
                        "grep '/vmfs/volumes/.*true  VMFS' |sort -nk7":
                stdout.readlines.return_value = [
                    "vmfs/volumes/5d992e74-82873bd6-cfe8-d050995bdb9e  VM-Kafka"
                    "                       5d992e74-82873bd6-cfe8-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e  VM-Splunk-ds"
                    "                   5d99349b-7d6bc489-9769-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462  VM-FreeNAS-ds"
                    "                  5c2125df-7d95f6bd-1be1-001517d9a462"
                    "     true  VMFS-5    68451041280   17566793728",
                ]
            elif cmd == "esxcli network vswitch standard list|grep Portgroups|" \
                    "sed 's/^   Portgroups: //g'":
                raise Exception("TestPortgroupFail")
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestPortgroupFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_find_iso_fail_mac1(self, paramiko_patch, setup_config_patch,
                                     saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list and PGs and MAC, raising exception on run of find command for ISO file.
        """
        setup_config_patch().__getitem__.side_effect = self.mock_getitem

        def mock_ssh_command(cmd):
            """ mocking the exec_command method of paramiko to return data we need to test for. """
            stdin = MagicMock()
            stdout = MagicMock()
            stderr = MagicMock()
            if cmd == "esxcli system version get |grep Version":
                stdout.readlines.return_value = "Version: 6.5.0"
            elif cmd == "esxcli storage filesystem list |" \
                        "grep '/vmfs/volumes/.*true  VMFS' |sort -nk7":
                stdout.readlines.return_value = [
                    "vmfs/volumes/5d992e74-82873bd6-cfe8-d050995bdb9e  VM-Kafka"
                    "                       5d992e74-82873bd6-cfe8-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e  VM-Splunk-ds"
                    "                   5d99349b-7d6bc489-9769-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462  VM-FreeNAS-ds"
                    "                  5c2125df-7d95f6bd-1be1-001517d9a462"
                    "     true  VMFS-5    68451041280   17566793728",
                ]
            elif cmd == "esxcli network vswitch standard list|grep Portgroups|" \
                        "sed 's/^   Portgroups: //g'":
                stdout.readlines.return_value = [
                    "Mgmt Temp PG 1, Mgmt Temp PG 0, VM Network, Management Network",
                    "IP over IB PG 1, Management Net IB 0",
                    "VM Network 1",
                    "IP over IB PG 2, Management IB Net 1",
                    "IPoIB Net 0, Management IB Net 0",
                ]
            elif (cmd == r"find /vmfs/volumes/ -type f -name {} -exec sh -c 'echo $1; "
                         r"kill $PPID' sh {{}} 2>/dev/null \;".format(TEST_ISO_NAME_ARG)):
                raise Exception("TestFindISOFail")
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestFindISOFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE_BAD_MAC)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_find_iso_fail_mac2(self, paramiko_patch, setup_config_patch,
                                     saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list and PGs and MAC, raising exception on run of find command for ISO file.
        """
        setup_config_patch().__getitem__.side_effect = self.mock_getitem

        def mock_ssh_command(cmd):
            """ mocking the exec_command method of paramiko to return data we need to test for. """
            stdin = MagicMock()
            stdout = MagicMock()
            stderr = MagicMock()
            if cmd == "esxcli system version get |grep Version":
                stdout.readlines.return_value = "Version: 6.5.0"
            elif cmd == "esxcli storage filesystem list |" \
                        "grep '/vmfs/volumes/.*true  VMFS' |sort -nk7":
                stdout.readlines.return_value = [
                    "vmfs/volumes/5d992e74-82873bd6-cfe8-d050995bdb9e  VM-Kafka"
                    "                       5d992e74-82873bd6-cfe8-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e  VM-Splunk-ds"
                    "                   5d99349b-7d6bc489-9769-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462  VM-FreeNAS-ds"
                    "                  5c2125df-7d95f6bd-1be1-001517d9a462"
                    "     true  VMFS-5    68451041280   17566793728",
                ]
            elif cmd == "esxcli network vswitch standard list|grep Portgroups|" \
                        "sed 's/^   Portgroups: //g'":
                stdout.readlines.return_value = [
                    "Mgmt Temp PG 1, Mgmt Temp PG 0, VM Network, Management Network",
                    "IP over IB PG 1, Management Net IB 0",
                    "VM Network 1",
                    "IP over IB PG 2, Management IB Net 1",
                    "IPoIB Net 0, Management IB Net 0",
                ]
            elif (cmd == r"find /vmfs/volumes/ -type f -name {} -exec sh -c 'echo $1; "
                         r"kill $PPID' sh {{}} 2>/dev/null \;".format(TEST_ISO_NAME_ARG)):

                raise Exception("TestFindISOFail")
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("The Error is <type 'exceptions.Exception'> - TestFindISOFail"),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_ok_find_iso_fail_getallvms(self, paramiko_patch, setup_config_patch,
                                             saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See above) and
        valid volume list and PGs and MAC, raising exception on run of find command for ISO file.
        """
        setup_config_patch().__getitem__.side_effect = self.mock_getitem

        def mock_ssh_command(cmd):
            """ mocking the exec_command method of paramiko to return data we need to test for. """
            stdin = MagicMock()
            stdout = MagicMock()
            stderr = MagicMock()
            if cmd == "esxcli system version get |grep Version":
                stdout.readlines.return_value = "Version: 6.5.0"
            elif cmd == "esxcli storage filesystem list |" \
                        "grep '/vmfs/volumes/.*true  VMFS' |sort -nk7":
                stdout.readlines.return_value = [
                    "vmfs/volumes/5d992e74-82873bd6-cfe8-d050995bdb9e  VM-Kafka"
                    "                       5d992e74-82873bd6-cfe8-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e  VM-Splunk-ds"
                    "                   5d99349b-7d6bc489-9769-d050995bdb9e"
                    "     true  VMFS-5    85630910464   13626245120",
                    "/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462  VM-FreeNAS-ds"
                    "                  5c2125df-7d95f6bd-1be1-001517d9a462"
                    "     true  VMFS-5    68451041280   17566793728",
                ]
            elif cmd == "esxcli network vswitch standard list|grep Portgroups|" \
                        "sed 's/^   Portgroups: //g'":
                stdout.readlines.return_value = [
                    "Mgmt Temp PG 1, Mgmt Temp PG 0, VM Network, Management Network",
                    "IP over IB PG 1, Management Net IB 0",
                    "VM Network 1",
                    "IP over IB PG 2, Management IB Net 1",
                    "IPoIB Net 0, Management IB Net 0",
                ]
            elif (cmd == r"find /vmfs/volumes/ -type f -name {} -exec sh -c 'echo $1; "
                         r"kill $PPID' sh {{}} 2>/dev/null \;".format(TEST_ISO_NAME_ARG)):
                stdout.readlines.return_value = ["/vmfs/volumes/test/" \
                                                 "ISOs/{}".format(TEST_ISO_NAME_ARG),]
            elif cmd == "ls /vmfs/volumes/test/ISOs/{}".format(TEST_ISO_NAME_ARG):
                stdout.readlines.return_value = ["/vmfs/volumes/test/" \
                                                 "ISOs/{}".format(TEST_ISO_NAME_ARG),]
                stderr.readlines.return_value = ""
            elif cmd == "vim-cmd vmsvc/getallvms":
                raise Exception("TEST_GETALLVMS_FAIL")
            return stdin, stdout, stderr

        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('FoundISOPath: /vmfs/volumes/test/ISOs/isoarg'),
             call.write('\n'),
             call.write("The Error is <type 'exceptions.Exception'> - TEST_GETALLVMS_FAIL"),
             call.write('\n')])
