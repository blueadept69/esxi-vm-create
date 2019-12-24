"""
test_esxi_vm_create_prepare.py:
    unittests for functions/methods in main esxi_vm_create.py script at point of preparation.
"""
from unittest import TestCase
import sys
import datetime
from esxi_vm_create import main

if sys.version_info.major == 2:
    from mock import patch, call, MagicMock, mock_open
else:
    from unittest.mock import patch, MagicMock, mock_open  # pylint: disable=no-name-in-module,import-error,ungrouped-imports

TEST_DATETIME = datetime.datetime(2019, 12, 8, 21, 30, 9, 31532)

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
                  '--mac', '',
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
                                  '--net', 'VM Network',
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
        elif key == 'LOG':
            return "logfile"
        return ""

    @patch('datetime.datetime')
    @patch('sys.stdout')
    @patch('sys.argv', TEST_ARGV_DRY_EMPTY_STORE)
    @patch('esxi_vm_create.SaveConfig')
    @patch('esxi_vm_create.setup_config')
    @patch('esxi_vm_create.paramiko')
    @patch('__builtin__.open', new_callable=mock_open)
    def test_main_ok_prep_mocked_log(self, *args):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        (open_patch, paramiko_patch, setup_config_patch,
         saveconfig_patch, print_patch, datetime_patch) = args

        setup_config_patch().__getitem__.side_effect = self.mock_getitem
        datetime_patch.now.return_value = TEST_DATETIME

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
                    "10     othervm                [VM-othervm-ds] othervm/othervm.vmx             "
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
        open_patch.assert_called()
        open_patch.assert_has_calls(
            [call('logfile', 'a+w'),
             call().__enter__(),
             call().write('{"datetime":"2019-12-08T21:30:09.031532",'
                          '"Host":"hostarg","Name":"namearg",'
                          '"CPU":"9","Mem":"99","Hdisk":"999","DiskFormat":"","Virtual Device":"",'
                          '"Store":"VM-FreeNAS-ds",'
                          '"Store Used":"/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462",'
                          '"Network":"VM Network","ISO":"None","ISO used":"",'
                          '"Guest OS":"guestosarg","MAC":"","MAC Used":"",'
                          '"Dry Run":"True","Verbose":"True",'
                          '"Result":"Success",'
                          '"Completion Time":"2019-12-08T21:30:09.031532"}\n'),
             call().__exit__(None, None, None)])
        saveconfig_patch.assert_not_called()
        print_patch.assert_has_calls(
            [call.write('VMX file:'),
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
             call.write('ethernet0.networkName = "VM Network"'),
             call.write('\n'),
             call.write('ethernet0.addressType = "generated"'),
             call.write('\n'),
             call.write('vmxoptone = 1'),
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
             call.write('Network: VM Network'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Success.'),
             call.write('\n')])
