"""
test_esxi_vm_create_prepare.py:
    unittests for functions/methods in main esxi_vm_create.py script at point of preparation.
"""
from unittest import TestCase
import sys
from esxi_vm_create import main
from tests import testcases
from tests.testcases import mock_getitem, mock_keys

if sys.version_info.major == 2:
    from mock import patch, call
else:
    from unittest.mock import patch  # pylint: disable=no-name-in-module,import-error,ungrouped-imports


class TestMainPrepare(TestCase):
    """ Test main() function after initial work and preparing for changes. """

    testcases.MOCK_GETITEM_LOGFILE = ""

    def setUp(self):

        print_patcher = patch('sys.stdout')
        log_patcher = patch('esxi_vm_create.Message.log_to_file')
        saveconfig_patcher = patch('esxi_vm_create.SaveConfig')
        paramiko_patcher = patch('esxi_vm_create.paramiko')
        setup_config_patcher = patch('esxi_vm_create.setup_config')

        self.print_patch = print_patcher.start()
        self.log_patch = log_patcher.start()
        self.saveconfig_patch = saveconfig_patcher.start()
        self.paramiko_patch = paramiko_patcher.start()
        self.setup_config_patch = setup_config_patcher.start()

        self.paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command
        self.setup_config_patch().__getitem__.side_effect = mock_getitem
        self.setup_config_patch().keys.side_effect = mock_keys

        self.addCleanup(print_patcher.stop)
        self.addCleanup(log_patcher.stop)
        self.addCleanup(saveconfig_patcher.stop)
        self.addCleanup(paramiko_patcher.stop)
        self.addCleanup(setup_config_patcher.stop)


    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE_NO_ISO_AND_NET)
    def test_main_ok_thru_getallvms_dry_true_empty_log(self):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        sys.stderr.write("=========> IN: test_main_ok_thru_getallvms_dry_true_empty_log\n")

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "vim-cmd vmsvc/getallvms": {
                    'stdout': [
                        "Vmid           Name          "
                        "                                  File                                    "
                        "     Guest OS       Version   Annotation",
                        "1      IB-ClearOS-112        "
                        " [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx                           "
                        " centos64Guest      vmx-10             ",
                        "10     namearg               "
                        " [VM-namearg-ds] namearg/namearg.vmx                                      "
                        " freebsd64Guest     vmx-13             ",
                        "11     Backup-Proxy-Host     "
                        " [VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                  "
                        " centos7_64Guest    vmx-14             ",
                    ],
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        self.saveconfig_patch.assert_not_called()
        self.print_patch.assert_has_calls(
            [call.write('ERROR: VM namearg already exists.'),
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
             call.write('Format: thin'),
             call.write('\n'),
             call.write('DS Store: VM-FreeNAS-ds'),
             call.write('\n'),
             call.write('Network: None'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])

    @patch('sys.argv', testcases.TEST_ARGV_PLUS_BAD_CPU_MEM_HDISK)
    def test_main_bad_cpu_mem_and_hdisk(self):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        sys.stderr.write("=========> IN: test_main_bad_cpu_mem_and_hdisk\n")
        testcases.MOCK_GETITEM_LOGFILE = ""

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "vim-cmd vmsvc/getallvms": {
                    'stdout': [
                        "Vmid           Name          "
                        "                                  File                                    "
                        "     Guest OS       Version   Annotation",
                        "1      IB-ClearOS-112        "
                        " [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx                           "
                        " centos64Guest      vmx-10             ",
                        "10     namearg               "
                        " [VM-namearg-ds] namearg/namearg.vmx                                      "
                        " freebsd64Guest     vmx-13             ",
                        "11     Backup-Proxy-Host     "
                        " [VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                  "
                        " centos7_64Guest    vmx-14             ",
                    ],
                }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        self.saveconfig_patch.assert_not_called()
        self.print_patch.assert_has_calls(
            [call.write('ERROR: VM namearg already exists.'),
             call.write('\n'),
             call.write('129 CPU out of range. [1-128].'),
             call.write('\n'),
             call.write('8192GB Memory out of range. [1-4080].'),
             call.write('\n'),
             call.write('Virtual Disk size 65536GB out of range. [1-63488].'),
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
             call.write('vmxoptone = 1'),
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
             call.write('Format: thin'),
             call.write('\n'),
             call.write('DS Store: VM-FreeNAS-ds'),
             call.write('\n'),
             call.write('Network: None'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])

    @patch('sys.argv', testcases.TEST_ARGV_PLUS_BAD_DSSTORE_ISO)
    def test_main_bad_dsstore_and_iso(self):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        sys.stderr.write("=========> IN: test_main_bad_dsstore_and_iso\n")

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "vim-cmd vmsvc/getallvms": {
                    'stdout': [
                        "Vmid           Name          "
                        "                                  File                                    "
                        "     Guest OS       Version   Annotation",
                        "1      IB-ClearOS-112        "
                        " [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx                           "
                        " centos64Guest      vmx-10             ",
                        "10     namearg               "
                        " [VM-namearg-ds] namearg/namearg.vmx                                      "
                        " freebsd64Guest     vmx-13             ",
                        "11     Backup-Proxy-Host     "
                        " [VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                  "
                        " centos7_64Guest    vmx-14             ",
                    ],
                },
            }
        )

        with self.assertRaises(SystemExit):
            main()
        self.saveconfig_patch.assert_not_called()
        self.print_patch.assert_has_calls(
            [call.write('ERROR: VM namearg already exists.'),
             call.write('\n'),
             call.write("ERROR: Disk Storage badstore doesn't exist. "),
             call.write('\n'),
             call.write("    Available Disk Stores: ['VM-FreeNAS-ds', 'VM-Kafka', 'VM-Splunk-ds']"),
             call.write('\n'),
             call.write('    LeastUsed Disk Store : VM-FreeNAS-ds'),
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
             call.write('Format: thin'),
             call.write('\n'),
             call.write('DS Store: '),
             call.write('\n'),
             call.write('Network: None'),
             call.write('\n'),
             call.write('ISO: /vmfs/volumes/path/to/iso'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])

    @patch('sys.argv', testcases.TEST_ARGV_PLUS_EXIST_DSSTORE_CPUS7)
    def test_main_dspath_name_exists(self):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        sys.stderr.write("=========> IN: test_main_dspath_name_exists\n")

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "vim-cmd vmsvc/getallvms": {
                    'stdout': [
                        "Vmid           Name          "
                        "                                  File                                    "
                        "     Guest OS       Version   Annotation",
                        "1      IB-ClearOS-112        "
                        " [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx                           "
                        " centos64Guest      vmx-10             ",
                        "10     namearg               "
                        " [VM-namearg-ds] namearg/namearg.vmx                                      "
                        " freebsd64Guest     vmx-13             ",
                        "11     Backup-Proxy-Host     "
                        " [VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                  "
                        " centos7_64Guest    vmx-14             ",
                    ],
                },
                "ls -d {}/{}".format(testcases.TEST_EXIST_DSPATH,
                                     testcases.TEST_EXIST_NAME):
                    {
                        'stdout': ["{}/{}".format(testcases.TEST_EXIST_DSPATH,
                                                  testcases.TEST_EXIST_NAME)],
                        'stderr': []
                    }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        self.saveconfig_patch.assert_not_called()
        self.print_patch.assert_has_calls(
            [call.write('ERROR: ISO /vmfs/volumes/path/to/iso not found.  Use full path to ISO'),
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
             call.write('Format: thin'),
             call.write('\n'),
             call.write('DS Store: VM-Splunk-ds'),
             call.write('\n'),
             call.write('Network: None'),
             call.write('\n'),
             call.write('ISO: /vmfs/volumes/path/to/iso'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])

    @patch('sys.argv', testcases.TEST_ARGV_PLUS_EXIST_DSSTORE_BAD_VMXOPTS_NET)
    def test_main_ssh_ls_except_bad_vmxopts_net(self):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run. Raise exception when ssh ls -d runs, and
        pass in invalid vmxopts
        """
        sys.stderr.write("=========> IN: test_main_ssh_ls_except_bad_vmxopts\n")

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "vim-cmd vmsvc/getallvms": {
                    'stdout': [
                        "Vmid           Name          "
                        "                                  File                                    "
                        "     Guest OS       Version   Annotation",
                        "1      IB-ClearOS-112        "
                        " [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx                           "
                        " centos64Guest      vmx-10             ",
                        "10     namearg               "
                        " [VM-namearg-ds] namearg/namearg.vmx                                      "
                        " freebsd64Guest     vmx-13             ",
                        "11     Backup-Proxy-Host     "
                        " [VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                  "
                        " centos7_64Guest    vmx-14             ",
                    ],
                },
                "ls -d {}/{}".format(testcases.TEST_EXIST_DSPATH,
                                     testcases.TEST_EXIST_NAME):
                    {
                        'Exception': 'TestLSFail',
                    }
            }
        )

        with self.assertRaises(SystemExit):
            main()
        self.saveconfig_patch.assert_not_called()
        self.print_patch.assert_has_calls(
            [call.write("ERROR: Virtual NIC BadNet doesn't exist."),
             call.write('\n'),
             call.write("    Available VM NICs: ['Mgmt Temp PG 1', 'Mgmt Temp PG 0', 'VM Network', 'Management Network', 'IP over IB PG 1', 'Management Net IB 0', 'VM Network 1', 'IP over IB PG 2', 'Management IB Net 1', 'IPoIB Net 0', 'Management IB Net 0'] or 'None'"),
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
             call.write('displayName = "VM-Splunk-ds"'),
             call.write('\n'),
             call.write('floppy0.present = "FALSE"'),
             call.write('\n'),
             ########################
             ########## NOTE THE **LACK OF** EXTRA SPACE!!!
             ########################
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
             call.write('ethernet0.networkName = "BadNet"'),
             call.write('\n'),
             call.write('ethernet0.addressType = "static"'),
             call.write('\n'),
             call.write('ethernet0.address = "12:34:56:78:9a:bc"'),
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
             call.write('Format: thin'),
             call.write('\n'),
             call.write('DS Store: VM-Splunk-ds'),
             call.write('\n'),
             call.write('Network: BadNet'),
             call.write('\n'),
             call.write('ISO: /vmfs/volumes/path/to/iso'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write('Dry Run: Failed.'),
             call.write('\n')])
