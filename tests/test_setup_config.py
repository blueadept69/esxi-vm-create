from unittest import TestCase
import sys
if sys.version_info.major == 2:
    from mock import patch
else:
    from unittest.mock import patch
from esxi_vm_functions import setup_config

expected_ConfigData = {'HDISK': 20,
                       'LOG': './esxi-vm.log',
                       'VMXOPTS': '',
                       'HOST': 'esxi',
                       'ISO': 'None',
                       'VIRTDEV': 'pvscsi',
                       'GUESTOS': 'centos-64',
                       'NET': 'None',
                       'PASSWORD': '',
                       'CPU': 2,
                       'STORE': 'LeastUsed',
                       'isDryRun': False,
                       'isVerbose': False,
                       'DISKFORMAT': 'thin',
                       'MEM': 4,
                       'isSummary': False,
                       'USER': 'root'
                       }

class TestSetup_config(TestCase):

    @patch('os.path.expanduser', return_value=".")
    @patch('os.path.exists', return_value=None)
    def test_setup_config(self, exists_patch, expanduser_patch):
        ret_ConfigData = setup_config()
        self.assertDictEqual(ret_ConfigData, expected_ConfigData)
