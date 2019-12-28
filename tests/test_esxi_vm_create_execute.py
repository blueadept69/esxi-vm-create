"""
test_esxi_vm_create_prepare.py:
    unittests for functions/methods in main esxi_vm_create.py script at point of execution.
"""
from unittest import TestCase
import sys
from esxi_vm_create import main
from tests.test_esxi_vm_functions import TEST_DATETIME
from tests import testcases
from tests.testcases import mock_getitem

if sys.version_info.major == 2:
    from mock import patch, call, mock_open
else:
    from unittest.mock import patch, mock_open  # pylint: disable=no-name-in-module,import-error,ungrouped-imports


class TestMainPrepare(TestCase):
    """ Test main() function after initial work and preparing for changes. """

    @patch('datetime.datetime')
    @patch('sys.stdout')
    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE_ISO_NONE)
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

        sys.stderr.write("=========> IN: test_main_ok_prep_mocked_log\n")
        testcases.MOCK_GETITEM_LOGFILE = "logfile"

        setup_config_patch().__getitem__.side_effect = mock_getitem
        datetime_patch.now.return_value = TEST_DATETIME
        paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)

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
                          '"Guest OS":"guestosarg","MAC":"12:34:56:78:9a:bc","MAC Used":"",'
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
             call.write('ethernet0.addressType = "static"'),
             call.write('\n'),
             call.write('ethernet0.address = "12:34:56:78:9a:bc"'),
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
