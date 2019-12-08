from unittest import TestCase
import sys
if sys.version_info.major == 2:
    from mock import patch, mock_open, call
else:
    from unittest.mock import patch, mock_open
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
    @patch('__builtin__.open', new_callable=mock_open, read_data="CPU: 9")
    def test_setup_config_default(self, open_patch, exists_patch, expanduser_patch):
        ret_ConfigData = setup_config()
        self.assertDictEqual(ret_ConfigData, expected_ConfigData)
        open_patch.assert_called_with("./.esxi-vm.yml", 'w')
        exists_patch.assert_called_once()
        print(dir(expanduser_patch))
        print(expanduser_patch.mock_calls)
        expanduser_patch.assert_has_calls([call("~"), call("~")])
