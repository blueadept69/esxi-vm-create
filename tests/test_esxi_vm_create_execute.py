"""
test_esxi_vm_create_prepare.py:
    unittests for functions/methods in main esxi_vm_create.py script at point of execution.
"""
from unittest import TestCase
import sys
from esxi_vm_create import main
from tests.test_esxi_vm_functions import TEST_DATETIME
from tests import testcases
# from tests.testcases import mock_getitem, mock_keys

if sys.version_info.major == 2:
    from mock import patch, call, mock_open
else:
    from unittest.mock import patch, mock_open  # pylint: disable=no-name-in-module,import-error,ungrouped-imports


class TestMainExecute(TestCase):
    """ Test main() function after initial work and preparing for changes. """

    def setUp(self):
        mock_getitem_logfile = "logfile"

        print_patcher = patch('sys.stdout')
        # saveconfig_patcher = patch('esxi_vm_create.SaveConfig')
        new_save_config_patcher = patch('esxi_vm_create.Config.save_config')
        paramiko_patcher = patch('esxi_vm_create.paramiko')
        # setup_config_patcher = patch('esxi_vm_create.setup_config')
        datetime_patcher = patch('datetime.datetime')
        logfile_patcher = patch('esxi_vm_create.Config.logfile')

        self.print_patch = print_patcher.start()
        # self.saveconfig_patch = saveconfig_patcher.start()
        self.new_save_config_patch = new_save_config_patcher.start()
        self.paramiko_patch = paramiko_patcher.start()
        # self.setup_config_patch = setup_config_patcher.start()
        self.datetime_patch = datetime_patcher.start()
        self.logfile_patch = logfile_patcher.start()

        self.paramiko_patch.SSHClient().exec_command = testcases.mock_ssh_command
        # self.setup_config_patch().__getitem__.side_effect = mock_getitem
        # self.setup_config_patch().keys.side_effect = mock_keys
        self.datetime_patch.now.return_value = TEST_DATETIME
        self.logfile_patch.return_value = mock_getitem_logfile

        self.addCleanup(print_patcher.stop)
        # self.addCleanup(saveconfig_patcher.stop)
        self.addCleanup(new_save_config_patcher.stop)
        self.addCleanup(paramiko_patcher.stop)
        # self.addCleanup(setup_config_patcher.stop)
        self.addCleanup(datetime_patcher.stop)
        self.addCleanup(logfile_patcher.stop)

    @patch('sys.argv', testcases.TEST_ARGV_DRY_EMPTY_STORE_MAC_ISO_NONE)
    @patch('__builtin__.open', new_callable=mock_open)
    def test_main_ok_prep_mocked_log(self, open_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        sys.stderr.write("=========> IN: test_main_ok_prep_mocked_log\n")
        testcases.MOCK_GETITEM_LOGFILE = "logfile"

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)

        with self.assertRaises(SystemExit):
            main()
        open_patch.assert_called()
        open_patch.assert_has_calls(
            [call('logfile', 'a'),
             call().__enter__(),
             call().write('{"datetime":"2019-12-08T21:30:09.031532",'
                          '"Host":"hostarg","Name":"namearg",'
                          '"CPU":"9","Mem":"99","Hdisk":"999","DiskFormat":"thin",'
                          '"Virtual Device":"pvscsi","Store":"VM-FreeNAS-ds",'
                          '"Store Used":"/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462",'
                          '"Network":"VM Network","ISO":"None","ISO used":"",'
                          '"Guest OS":"guestosarg","MAC":"","MAC Used":"",'
                          '"Dry Run":"True","Verbose":"True",'
                          '"Result":"Success",'
                          '"Completion Time":"2019-12-08T21:30:09.031532"}\n'),
             call().__exit__(None, None, None)])
        # self.saveconfig_patch.assert_not_called()
        self.new_save_config_patch.assert_not_called()
        self.print_patch.assert_has_calls(
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
             call.write('Format: thin'),
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

    ###########################
    # By rights, the execution this test is testing should fail since disk format is being passed
    # as empty string...
    @patch('sys.argv', testcases.TEST_ARGV_EMPTY_STORE_ISO_NONE)
    @patch('__builtin__.open', new_callable=mock_open)
    def test_main_ok_execute_mocked_log(self, open_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        sys.stderr.write("=========> IN: test_main_ok_prep_mocked_log\n")
        testcases.MOCK_GETITEM_LOGFILE = "logfile"

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)

        with self.assertRaises(SystemExit):
            main()
        open_patch.assert_called()
        open_patch.assert_has_calls(
            [call('logfile', 'a'),
             call().__enter__(),
             call().write('{"datetime":"2019-12-08T21:30:09.031532",'
                          '"Host":"hostarg","Name":"namearg",'
                          '"CPU":"9","Mem":"99","Hdisk":"999","DiskFormat":"thin",'
                          '"Virtual Device":"pvscsi","Store":"VM-FreeNAS-ds",'
                          '"Store Used":"/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462",'
                          '"Network":"VM Network","ISO":"None","ISO used":"",'
                          '"Guest OS":"guestosarg","MAC":"12:34:56:78:9a:bc",'
                          # ***** NOTE **** Why is MAC Used different from MAC?????
                          '"MAC Used":"00:0c:29:e3:f9:8e","Dry Run":"False","Verbose":"True",'
                          '"Result":"Fail",'
                          '"Completion Time":"2019-12-08T21:30:09.031532"}\n'),
             call().__exit__(None, None, None)])
        # self.saveconfig_patch.assert_not_called()
        self.new_save_config_patch.assert_not_called()
        self.print_patch.assert_has_calls(
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
             call.write('Create namearg.vmx file'),
             call.write('\n'),
             call.write('Create namearg.vmdk file'),
             call.write('\n'),
             call.write('Create: 100% done.'),
             call.write('\n'),
             call.write('Register VM'),
             call.write('\n'),
             call.write('Power ON VM'),
             call.write('\n'),
             call.write('Error Power.on VM.'),
             call.write('\n'),
             call.write('\nCreate VM Success:'),
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
             call.write('Network: VM Network'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: 00:0c:29:e3:f9:8e'),
             call.write('\n'),
             call.write('00:0c:29:e3:f9:8e'),
             call.write('\n')])

    @patch('sys.argv', testcases.TEST_ARGV_EMPTY_STORE_ISO_NONE)
    @patch('__builtin__.open', new_callable=mock_open)
    def test_main_ok_execute_exception(self, open_patch):
        """
        Test mocking with --name and mocking ssh calls returning "Valid" Version (See elsewhere) and
        valid info discovery - set to run as dry run.
        """
        sys.stderr.write("=========> IN: test_main_ok_prep_mocked_log\n")
        testcases.MOCK_GETITEM_LOGFILE = "logfile"

        testcases.SSH_CONDITIONS = dict(testcases.SSH_BASE_CONDITIONS)
        testcases.SSH_CONDITIONS.update(
            {
                "mkdir ": {
                    'Exception': 'TestMKDIRFail',
                },
            }
        )

        with self.assertRaises(SystemExit):
            main()
        open_patch.assert_called()
        open_patch.assert_has_calls(
            [call('logfile', 'a'),
             call().__enter__(),
             call().write('{"datetime":"2019-12-08T21:30:09.031532",'
                          '"Host":"hostarg","Name":"namearg",'
                          '"CPU":"9","Mem":"99","Hdisk":"999","DiskFormat":"thin",'
                          '"Virtual Device":"pvscsi","Store":"VM-FreeNAS-ds",'
                          '"Store Used":"/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462",'
                          '"Network":"VM Network","ISO":"None","ISO used":"",'
                          '"Guest OS":"guestosarg","MAC":"12:34:56:78:9a:bc",'
                          # ***** NOTE **** Why is MAC Used different from MAC?????
                          '"MAC Used":"","Dry Run":"False","Verbose":"True",'
                          '"Error Message":"There was an error creating the VM.",'
                          '"Result":"Fail",'
                          '"Completion Time":"2019-12-08T21:30:09.031532"}\n'),
             call().__exit__(None, None, None)])
        # self.saveconfig_patch.assert_not_called()
        self.new_save_config_patch.assert_not_called()
        self.print_patch.assert_has_calls(
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
             call.write('Create namearg.vmx file'),
             call.write('\n'),
             call.write('There was an error creating the VM.'),
             call.write('\n'),
             call.write("The Error is <type 'exceptions.Exception'> - TestMKDIRFail"),
             call.write('\n'),
             call.write('\nCreate VM Success:'),
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
             call.write('Network: VM Network'),
             call.write('\n'),
             call.write('Guest OS: guestosarg'),
             call.write('\n'),
             call.write('MAC: '),
             call.write('\n'),
             call.write(''),
             call.write('\n')])
