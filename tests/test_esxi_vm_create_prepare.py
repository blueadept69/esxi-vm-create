"""
test_esxi_vm_create_prepare.py:
    unittests for functions/methods in main esxi_vm_create.py script at point of preparation.
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
                  #'--iso', 'isoarg',
                  '--iso', 'None',
                  '--mac', '12:34:56:78:9a:bc',
                  # '--store', 'storearg',
                  '--guestos', 'guestosarg',
                  '--options', 'vmxoptone=1',
                  '--verbose',
                  '--summary',
                  # '--updateDefaults',
                 ]

TEST_ARGV_DRY_EMPTY_STORE = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_STORE.extend(['--dry',
                                  '--name', 'namearg',
                                  '--store', '',
                                 ])

TEST_ARGV_PLUS_BAD_CPU_MEM_HDISK = list(TEST_ARGV_DRY_EMPTY_STORE)
TEST_ARGV_PLUS_BAD_CPU_MEM_HDISK.extend(['--cpu', '129',
                                         '--mem', '8192',
                                         '--vdisk', '65536',
                                        ])

TEST_ARGV_PLUS_BAD_DSSTORE_ISO = list(TEST_ARGV_DRY_EMPTY_STORE)
TEST_ARGV_PLUS_BAD_DSSTORE_ISO.extend(['--store', 'badstore',
                                       '--iso', TEST_ISO_PATH_ARG,
                                      ])

TEST_EXIST_DSPATH = "/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e"
TEST_EXIST_NAME = "VM-Splunk-ds"
TEST_ARGV_PLUS_EXIST_DSSTORE_CPUS7 = list(TEST_ARGV_BASE)
TEST_ARGV_PLUS_EXIST_DSSTORE_CPUS7.extend(
    #['--store', '/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e',
    ['--dry',
     '--store', TEST_EXIST_DSPATH,
     #'--name', 'VM-Splunk-ds',
     '--name', TEST_EXIST_NAME,
     '--iso', TEST_ISO_PATH_ARG,
     '--options', 'numvcpus = "7"',
    ])

class TestMainPrepare(TestCase):
    """ Test main() function after initial work and preparing for changes. """

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
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_ok_thru_getallvms_dry_true_empty_log(self, paramiko_patch, setup_config_patch,
                                                       saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
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
                stdout.readlines.return_value = [
                    "Vmid           Name                                            File           "
                    "                              Guest OS       Version   Annotation",
                    "1      IB-ClearOS-112         [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx  "
                    "                          centos64Guest      vmx-10             ",
                    "10     namearg                [VM-namearg-ds] namearg/namearg.vmx             "
                    "                          freebsd64Guest     vmx-13             ",
                    "11     Backup-Proxy-Host      "
                    "[VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                   "
                    "centos7_64Guest    vmx-14             ",
                    ]
            elif cmd.startswith("ls -d "):
                stdout.readlines.return_value = [""]
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("ERROR: Virtual NIC  doesn't exist."),
             call.write('\n'),
             call.write("    Available VM NICs: ['Mgmt Temp PG 1', 'Mgmt Temp PG 0', 'VM Network', "
                        "'Management Network', 'IP over IB PG 1', 'Management Net IB 0', "
                        "'VM Network 1', 'IP over IB PG 2', 'Management IB Net 1', 'IPoIB Net 0', "
                        "'Management IB Net 0'] or 'None'"),
             call.write('\n'),
             call.write('VMX file:'),
             call.write('\n'),
             call.write('config.version = "8"'),
             call.write('\n'),
             call.write('virtualHW.version = "8"'),
             call.write('\n'),
             call.write('vmci0.present = "TRUE"'),
             call.write('\n'),
             call.write('displayName = "namearg"'),
             call.write('\n'),
             call.write('floppy0.present = "FALSE"'),
             call.write('\n'),
             call.write('numvcpus = "9"'),
             call.write('\n'),
             call.write('scsi0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0.sharedBus = "none"'),
             call.write('\n'),
             call.write('scsi0.virtualDev = "pvscsi"'),
             call.write('\n'),
             call.write('memsize = "101376"'),
             call.write('\n'),
             call.write('scsi0:0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0:0.fileName = "namearg.vmdk"'),
             call.write('\n'),
             call.write('scsi0:0.deviceType = "scsi-hardDisk"'),
             call.write('\n'),
             call.write('ide1:0.present = "TRUE"'),
             call.write('\n'),
             call.write('ide1:0.fileName = "emptyBackingString"'),
             call.write('\n'),
             call.write('ide1:0.deviceType = "atapi-cdrom"'),
             call.write('\n'),
             call.write('ide1:0.startConnected = "FALSE"'),
             call.write('\n'),
             call.write('ide1:0.clientDevice = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge0.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge4.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge5.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge5.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge5.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge6.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge6.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge6.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge7.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge7.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge7.functions = "8"'),
             call.write('\n'),
             call.write('guestOS = "guestosarg"'),
             call.write('\n'),
             call.write('ethernet0.virtualDev = "vmxnet3"'),
             call.write('\n'),
             call.write('ethernet0.present = "TRUE"'),
             call.write('\n'),
             call.write('ethernet0.networkName = ""'),
             call.write('\n'),
             call.write('ethernet0.addressType = "static"'),
             call.write('\n'),
             call.write('ethernet0.address = "12:34:56:78:9a:bc"'),
             call.write('\n'),
             call.write('vmxoptone = 1'),
             call.write('\n'),
             call.write('Error writing to log file: '),
             call.write('\n'),
             call.write('\nDry Run summary:'),
             call.write('\n'),
             call.write('ESXi Host: hostarg'),
             call.write('\n'),
             call.write('VM NAME: namearg'),
             call.write('\n'),
             call.write('vCPU: 9'),
             call.write('\n'),
             call.write('Memory: 99GB'),
             call.write('\n'),
             call.write('VM Disk: 999GB'),
             call.write('\n'),
             call.write('Format: '),
             call.write('\n'),
             call.write('DS Store: VM-FreeNAS-ds'),
             call.write('\n'),
             call.write('Network: '),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_PLUS_BAD_CPU_MEM_HDISK)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_bad_cpu_mem_and_hdisk(self, paramiko_patch, setup_config_patch,
                                        saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
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
                stdout.readlines.return_value = [
                    "Vmid           Name                                            File           "
                    "                              Guest OS       Version   Annotation",
                    "1      IB-ClearOS-112         [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx  "
                    "                          centos64Guest      vmx-10             ",
                    "10     namearg                [VM-namearg-ds] namearg/namearg.vmx             "
                    "                          freebsd64Guest     vmx-13             ",
                    "11     Backup-Proxy-Host      "
                    "[VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                   "
                    "centos7_64Guest    vmx-14             ",
                ]
            elif cmd.startswith("ls -d "):
                stdout.readlines.return_value = [""]
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('ERROR: VM namearg already exists.'),
             call.write('\n'),
             call.write('129 CPU out of range. [1-128].'),
             call.write('\n'),
             call.write('8192GB Memory out of range. [1-4080].'),
             call.write('\n'),
             call.write('Virtual Disk size 65536GB out of range. [1-63488].'),
             call.write('\n'),
             call.write("ERROR: Virtual NIC  doesn't exist."),
             call.write('\n'),
             call.write("    Available VM NICs: ['Mgmt Temp PG 1', 'Mgmt Temp PG 0', 'VM Network',"
                        " 'Management Network', 'IP over IB PG 1', 'Management Net IB 0',"
                        " 'VM Network 1', 'IP over IB PG 2', 'Management IB Net 1', 'IPoIB Net 0',"
                        " 'Management IB Net 0'] or 'None'"),
             call.write('\n'),
             call.write('VMX file:'),
             call.write('\n'),
             call.write('config.version = "8"'),
             call.write('\n'),
             call.write('virtualHW.version = "8"'),
             call.write('\n'),
             call.write('vmci0.present = "TRUE"'),
             call.write('\n'),
             call.write('displayName = "namearg"'),
             call.write('\n'),
             call.write('floppy0.present = "FALSE"'),
             call.write('\n'),
             call.write('numvcpus = "129"'),
             call.write('\n'),
             call.write('scsi0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0.sharedBus = "none"'),
             call.write('\n'),
             call.write('scsi0.virtualDev = "pvscsi"'),
             call.write('\n'),
             call.write('memsize = "8388608"'),
             call.write('\n'),
             call.write('scsi0:0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0:0.fileName = "namearg.vmdk"'),
             call.write('\n'),
             call.write('scsi0:0.deviceType = "scsi-hardDisk"'),
             call.write('\n'),
             call.write('ide1:0.present = "TRUE"'),
             call.write('\n'),
             call.write('ide1:0.fileName = "emptyBackingString"'),
             call.write('\n'),
             call.write('ide1:0.deviceType = "atapi-cdrom"'),
             call.write('\n'),
             call.write('ide1:0.startConnected = "FALSE"'),
             call.write('\n'),
             call.write('ide1:0.clientDevice = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge0.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge4.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge5.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge5.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge5.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge6.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge6.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge6.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge7.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge7.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge7.functions = "8"'),
             call.write('\n'),
             call.write('guestOS = "guestosarg"'),
             call.write('\n'),
             call.write('ethernet0.virtualDev = "vmxnet3"'),
             call.write('\n'),
             call.write('ethernet0.present = "TRUE"'),
             call.write('\n'),
             call.write('ethernet0.networkName = ""'),
             call.write('\n'),
             call.write('ethernet0.addressType = "static"'),
             call.write('\n'),
             call.write('ethernet0.address = "12:34:56:78:9a:bc"'),
             call.write('\n'),
             call.write('vmxoptone = 1'),
             call.write('\n'),
             call.write('Error writing to log file: '),
             call.write('\n'),
             call.write('\nDry Run summary:'),
             call.write('\n'),
             call.write('ESXi Host: hostarg'),
             call.write('\n'),
             call.write('VM NAME: namearg'),
             call.write('\n'),
             call.write('vCPU: 129'),
             call.write('\n'),
             call.write('Memory: 8192GB'),
             call.write('\n'),
             call.write('VM Disk: 65536GB'),
             call.write('\n'),
             call.write('Format: '),
             call.write('\n'),
             call.write('DS Store: VM-FreeNAS-ds'),
             call.write('\n'),
             call.write('Network: '),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_PLUS_BAD_DSSTORE_ISO)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_bad_dsstore_and_iso(self, paramiko_patch, setup_config_patch,
                                      saveconfig_patch, print_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
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
                stdout.readlines.return_value = [
                    "Vmid           Name                                            File           "
                    "                              Guest OS       Version   Annotation",
                    "1      IB-ClearOS-112         [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx  "
                    "                          centos64Guest      vmx-10             ",
                    "10     namearg                [VM-namearg-ds] namearg/namearg.vmx             "
                    "                          freebsd64Guest     vmx-13             ",
                    "11     Backup-Proxy-Host      "
                    "[VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                   "
                    "centos7_64Guest    vmx-14             ",
                ]
            elif cmd.startswith("ls -d "):
                raise Exception("TestLSException")
                # stdout.readlines.return_value = [""]
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('ERROR: VM namearg already exists.'),
             call.write('\n'),
             call.write("ERROR: Disk Storage badstore doesn't exist. "),
             call.write('\n'),
             call.write("    Available Disk Stores: ['VM-FreeNAS-ds', 'VM-Kafka', 'VM-Splunk-ds']"),
             call.write('\n'),
             call.write('    LeastUsed Disk Store : VM-FreeNAS-ds'),
             call.write('\n'),
             call.write("ERROR: Virtual NIC  doesn't exist."),
             call.write('\n'),
             call.write("    Available VM NICs: ['Mgmt Temp PG 1', 'Mgmt Temp PG 0', 'VM Network',"
                        " 'Management Network', 'IP over IB PG 1', 'Management Net IB 0',"
                        " 'VM Network 1', 'IP over IB PG 2', 'Management IB Net 1', 'IPoIB Net 0',"
                        " 'Management IB Net 0'] or 'None'"),
             call.write('\n'),
             call.write('ERROR: ISO /vmfs/volumes/path/to/iso not found.  Use full path to ISO'),
             call.write('\n'),
             call.write('VMX file:'),
             call.write('\n'),
             call.write('config.version = "8"'),
             call.write('\n'),
             call.write('virtualHW.version = "8"'),
             call.write('\n'),
             call.write('vmci0.present = "TRUE"'),
             call.write('\n'),
             call.write('displayName = "namearg"'),
             call.write('\n'),
             call.write('floppy0.present = "FALSE"'),
             call.write('\n'),
             call.write('numvcpus = "9"'),
             call.write('\n'),
             call.write('scsi0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0.sharedBus = "none"'),
             call.write('\n'),
             call.write('scsi0.virtualDev = "pvscsi"'),
             call.write('\n'),
             call.write('memsize = "101376"'),
             call.write('\n'),
             call.write('scsi0:0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0:0.fileName = "namearg.vmdk"'),
             call.write('\n'),
             call.write('scsi0:0.deviceType = "scsi-hardDisk"'),
             call.write('\n'),
             call.write('ide1:0.present = "TRUE"'),
             call.write('\n'),
             call.write('ide1:0.fileName = "/vmfs/volumes/path/to/iso"'),
             call.write('\n'),
             call.write('ide1:0.deviceType = "cdrom-image"'),
             call.write('\n'),
             call.write('pciBridge0.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge4.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge5.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge5.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge5.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge6.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge6.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge6.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge7.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge7.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge7.functions = "8"'),
             call.write('\n'),
             call.write('guestOS = "guestosarg"'),
             call.write('\n'),
             call.write('ethernet0.virtualDev = "vmxnet3"'),
             call.write('\n'),
             call.write('ethernet0.present = "TRUE"'),
             call.write('\n'),
             call.write('ethernet0.networkName = ""'),
             call.write('\n'),
             call.write('ethernet0.addressType = "static"'),
             call.write('\n'),
             call.write('ethernet0.address = "12:34:56:78:9a:bc"'),
             call.write('\n'),
             call.write('vmxoptone = 1'),
             call.write('\n'),
             call.write('Error writing to log file: '),
             call.write('\n'),
             call.write('\nDry Run summary:'),
             call.write('\n'),
             call.write('ESXi Host: hostarg'),
             call.write('\n'),
             call.write('VM NAME: namearg'),
             call.write('\n'),
             call.write('vCPU: 9'),
             call.write('\n'),
             call.write('Memory: 99GB'),
             call.write('\n'),
             call.write('VM Disk: 999GB'),
             call.write('\n'),
             call.write('Format: '),
             call.write('\n'),
             call.write('DS Store: '),
             call.write('\n'),
             call.write('Network: '),
             call.write('\n'),
             call.write('ISO: /vmfs/volumes/path/to/iso'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])

    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_PLUS_EXIST_DSSTORE_CPUS7)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    def test_main_dspath_name_exists(self, paramiko_patch, setup_config_patch,
                                     saveconfig_patch, print_patch):
                                     # saveconfig_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
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
                stdout.readlines.return_value = [
                    "Vmid           Name                                            File           "
                    "                              Guest OS       Version   Annotation",
                    "1      IB-ClearOS-112         [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx  "
                    "                          centos64Guest      vmx-10             ",
                    "10     namearg                [VM-namearg-ds] namearg/namearg.vmx             "
                    "                          freebsd64Guest     vmx-13             ",
                    "11     Backup-Proxy-Host      "
                    "[VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                   "
                    "centos7_64Guest    vmx-14             ",
                ]
            elif cmd == "ls -d {}/{}".format(TEST_EXIST_DSPATH, TEST_EXIST_NAME):
                stdout.readlines.return_value = ["{}/{}".format(TEST_EXIST_DSPATH,
                                                                TEST_EXIST_NAME)]
                stderr.readlines.return_value = []
            return stdin, stdout, stderr
        paramiko_patch.SSHClient().exec_command = mock_ssh_command
        with self.assertRaises(SystemExit):
            main()
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write("ERROR: Virtual NIC  doesn't exist."),
             call.write('\n'),
             call.write("    Available VM NICs: ['Mgmt Temp PG 1', 'Mgmt Temp PG 0', 'VM Network',"
                        " 'Management Network', 'IP over IB PG 1', 'Management Net IB 0',"
                        " 'VM Network 1', 'IP over IB PG 2', 'Management IB Net 1', 'IPoIB Net 0',"
                        " 'Management IB Net 0'] or 'None'"),
             call.write('\n'),
             call.write('ERROR: ISO /vmfs/volumes/path/to/iso not found.  Use full path to ISO'),
             call.write('\n'),
             call.write('ERROR: Directory /vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e/'
                        'VM-Splunk-ds already exists.'),
             call.write('\n'),
             call.write('VMX file:'),
             call.write('\n'),
             call.write('config.version = "8"'),
             call.write('\n'),
             call.write('virtualHW.version = "8"'),
             call.write('\n'),
             call.write('vmci0.present = "TRUE"'),
             call.write('\n'),
             call.write('displayName = "VM-Splunk-ds"'),
             call.write('\n'),
             call.write('floppy0.present = "FALSE"'),
             call.write('\n'),
             ########################
             ########## NOTE THE EXTRA SPACE!!!
             ########################
             call.write('numvcpus  = "7"'),
             call.write('\n'),
             call.write('scsi0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0.sharedBus = "none"'),
             call.write('\n'),
             call.write('scsi0.virtualDev = "pvscsi"'),
             call.write('\n'),
             call.write('memsize = "101376"'),
             call.write('\n'),
             call.write('scsi0:0.present = "TRUE"'),
             call.write('\n'),
             call.write('scsi0:0.fileName = "VM-Splunk-ds.vmdk"'),
             call.write('\n'),
             call.write('scsi0:0.deviceType = "scsi-hardDisk"'),
             call.write('\n'),
             call.write('ide1:0.present = "TRUE"'),
             call.write('\n'),
             call.write('ide1:0.fileName = "/vmfs/volumes/path/to/iso"'),
             call.write('\n'),
             call.write('ide1:0.deviceType = "cdrom-image"'),
             call.write('\n'),
             call.write('pciBridge0.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge4.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge4.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge5.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge5.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge5.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge6.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge6.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge6.functions = "8"'),
             call.write('\n'),
             call.write('pciBridge7.present = "TRUE"'),
             call.write('\n'),
             call.write('pciBridge7.virtualDev = "pcieRootPort"'),
             call.write('\n'),
             call.write('pciBridge7.functions = "8"'),
             call.write('\n'),
             call.write('guestOS = "guestosarg"'),
             call.write('\n'),
             call.write('ethernet0.virtualDev = "vmxnet3"'),
             call.write('\n'),
             call.write('ethernet0.present = "TRUE"'),
             call.write('\n'),
             call.write('ethernet0.networkName = ""'),
             call.write('\n'),
             call.write('ethernet0.addressType = "static"'),
             call.write('\n'),
             call.write('ethernet0.address = "12:34:56:78:9a:bc"'),
             call.write('\n'),
             call.write('Error writing to log file: '),
             call.write('\n'),
             call.write('\nDry Run summary:'),
             call.write('\n'),
             call.write('ESXi Host: hostarg'),
             call.write('\n'),
             call.write('VM NAME: VM-Splunk-ds'),
             call.write('\n'),
             call.write('vCPU: 9'),
             call.write('\n'),
             call.write('Memory: 99GB'),
             call.write('\n'),
             call.write('VM Disk: 999GB'),
             call.write('\n'),
             call.write('Format: '),
             call.write('\n'),
             call.write('DS Store: VM-Splunk-ds'),
             call.write('\n'),
             call.write('Network: '),
             call.write('\n'),
             call.write('ISO: /vmfs/volumes/path/to/iso'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])
