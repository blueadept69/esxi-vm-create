"""
testcases.py -
module for locating variables and functions for testing various cases used in the unittests.
(named without underscore so unittest discovery won't try to run this itself.)
"""
import sys

if sys.version_info.major == 2:
    from mock import MagicMock
else:
    from unittest.mock import MagicMock  # pylint: disable=no-name-in-module,import-error,ungrouped-imports

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
                  # '--iso', 'isoarg',
                  '--iso', 'None',
                  # '--iso', TEST_ISO_NAME_ARG,
                  # '--net', 'VM Network',
                  # '--mac', '12:34:56',
                  '--mac', '12:34:56:78:9a:bc',
                  # '--store', 'storearg',
                  '--guestos', 'guestosarg',
                  # '--options', '',
                  '--options', 'vmxoptone=1',
                  '--verbose',
                  '--summary',
                  # '--updateDefaults',
                 ]

TEST_ARGV_DRY_EMPTY_NAME_UPDATEDEFAULTS = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_NAME_UPDATEDEFAULTS.extend(['--dry',
                                                '--name', '',
                                                '--store', 'storearg',
                                                '--updateDefaults',
                                                '--iso', TEST_ISO_NAME_ARG,
                                               ])

TEST_ARGV_DRY_EMPTY_NAME_STORE = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_NAME_STORE.extend(['--dry',
                                       '--name', '',
                                       '--store', '',
                                       '--iso', TEST_ISO_NAME_ARG,
                                      ])

TEST_ARGV_DRY_EMPTY_STORE = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_STORE.extend(['--dry',
                                  '--name', 'namearg',
                                  '--store', '',
                                  '--iso', TEST_ISO_NAME_ARG,
                                  '--mac', '12:34:56',
                                 ])

TEST_ARGV_DRY_EMPTY_STORE_BAD_MAC = list(TEST_ARGV_DRY_EMPTY_STORE)
TEST_ARGV_DRY_EMPTY_STORE_BAD_MAC.extend(['--mac', 'bad_mac_arg',
                                         ])

TEST_ARGV_DRY_EMPTY_STORE_NO_ISO_AND_NET = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_STORE_NO_ISO_AND_NET.extend(['--dry',
                                                 '--name', 'namearg',
                                                 '--store', '',
                                                 '--iso', 'None',
                                                ])

TEST_ARGV_PLUS_BAD_CPU_MEM_HDISK = list(TEST_ARGV_BASE)
TEST_ARGV_PLUS_BAD_CPU_MEM_HDISK.extend(['--dry',
                                         '--iso', 'None',
                                         '--name', 'namearg',
                                         '--store', '',
                                         '--cpu', '129',
                                         '--mem', '8192',
                                         '--vdisk', '65536',
                                        ])

TEST_ARGV_PLUS_BAD_DSSTORE_ISO = list(TEST_ARGV_BASE)
TEST_ARGV_PLUS_BAD_DSSTORE_ISO.extend(['--dry',
                                       '--name', 'namearg',
                                       '--store', '',
                                       '--store', 'badstore',
                                       '--iso', TEST_ISO_PATH_ARG,
                                      ])

TEST_EXIST_DSPATH = "/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e"
TEST_EXIST_NAME = "VM-Splunk-ds"
TEST_ARGV_PLUS_EXIST_DSSTORE_CPUS7 = list(TEST_ARGV_BASE)
TEST_ARGV_PLUS_EXIST_DSSTORE_CPUS7.extend(['--dry',
                                           '--store', TEST_EXIST_DSPATH,
                                           '--name', TEST_EXIST_NAME,
                                           '--iso', TEST_ISO_PATH_ARG,
                                           '--options', 'numvcpus = "7"',
                                          ])

TEST_ARGV_DRY_EMPTY_STORE_ISO_NONE = list(TEST_ARGV_BASE)
TEST_ARGV_DRY_EMPTY_STORE_ISO_NONE.extend(['--dry',
                                           '--name', 'namearg',
                                           '--store', '',
                                           '--iso', 'None',
                                           '--net', 'VM Network',
                                          ])

SSH_BASE_CONDITIONS = {
    "esxcli system version get |grep Version": {
        'stdout': "Version: 6.5.0",
    },
    "esxcli storage filesystem list |grep '/vmfs/volumes/.*true  VMFS' |sort -nk7": {
        'stdout': [
            "vmfs/volumes/5d992e74-82873bd6-cfe8-d050995bdb9e  VM-Kafka"
            "                       5d992e74-82873bd6-cfe8-d050995bdb9e"
            "     true  VMFS-5    85630910464   13626245120",
            "/vmfs/volumes/5d99349b-7d6bc489-9769-d050995bdb9e  VM-Splunk-ds"
            "                   5d99349b-7d6bc489-9769-d050995bdb9e"
            "     true  VMFS-5    85630910464   13626245120",
            "/vmfs/volumes/5c2125df-7d95f6bd-1be1-001517d9a462  VM-FreeNAS-ds"
            "                  5c2125df-7d95f6bd-1be1-001517d9a462"
            "     true  VMFS-5    68451041280   17566793728",
        ],
    },
    "esxcli network vswitch standard list|grep Portgroups|sed 's/^   Portgroups: //g'": {
        'stdout': [
            "Mgmt Temp PG 1, Mgmt Temp PG 0, VM Network, Management Network",
            "IP over IB PG 1, Management Net IB 0",
            "VM Network 1",
            "IP over IB PG 2, Management IB Net 1",
            "IPoIB Net 0, Management IB Net 0",
        ],
    },
    r"find /vmfs/volumes/ -type f -name {} -exec sh -c 'echo $1; kill $PPID'"
    r" sh {{}} 2>/dev/null \;".format(TEST_ISO_NAME_ARG): {
        'stdout': ["/vmfs/volumes/test/ISOs/{}".format(TEST_ISO_NAME_ARG),
                  ],
    },
    "ls /vmfs/volumes/test/ISOs/{}".format(TEST_ISO_NAME_ARG): {
        'stdout': ["/vmfs/volumes/test/ISOs/{}".format(TEST_ISO_NAME_ARG),],
        'stderr': "",
    },
    "vim-cmd vmsvc/getallvms": {
        'stdout': [
            "Vmid           Name                                            File           "
            "                              Guest OS       Version   Annotation",
            "1      IB-ClearOS-112         [datastore1] IB-ClearOS-112/IB-ClearOS-112.vmx  "
            "                          centos64Guest      vmx-10             ",
            "10     othervm                [VM-othervm-ds] othervm/othervm.vmx             "
            "                          freebsd64Guest     vmx-13             ",
            "11     Backup-Proxy-Host      "
            "[VM-FreeNAS-ds] Backup-Proxy-Host/Backup-Proxy-Host.vmx                   "
            "centos7_64Guest    vmx-14             ",
        ],
    },
    "ls -d ": {
        'stdout': [""],
    },
}

SSH_CONDITIONS = {}

MOCK_GETITEM_LOGFILE = ""

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
        return MOCK_GETITEM_LOGFILE
    return ""

def mock_ssh_command_handler(cmd_param, conditions=None):
    """ Function to handle calls to mock_ssh_command - allowing return values to change
     based on appropriate tests. """
    if not conditions:
        sys.stderr.write("mock_ssh_command_handler: *** No conditions passed in. ***\n")

    stdin = MagicMock()
    stdout = MagicMock()
    stderr = MagicMock()

    found_appropriate_condition = False

    if cmd_param in conditions:
        found_appropriate_condition = conditions.get(cmd_param)
    else:
        for cmd, result in conditions.items():
            # Should use regex, but for now startswith should work OK...
            if cmd_param.startswith(cmd):
                found_appropriate_condition = result
                break
    if found_appropriate_condition:
        if found_appropriate_condition.get('Exception'):
            raise Exception(found_appropriate_condition.get('Exception'))
        elif 'stderr' in found_appropriate_condition.keys():
            stderr.readlines.return_value = found_appropriate_condition.get('stderr')
        stdout.readlines.return_value = found_appropriate_condition.get('stdout')
    if not found_appropriate_condition:
        sys.stderr.write("mock_ssh_command_handler: *** No appropriate condition found. ***\n")
    return stdin, stdout, stderr

def mock_ssh_command(cmd):
    """ mocking the exec_command method of paramiko to return data we need to test for. Relies on
        SSH_CONDITIONS being set by each test. """
    return mock_ssh_command_handler(cmd, SSH_CONDITIONS)
