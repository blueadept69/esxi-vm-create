""" esxi_vm_functions.py - Classes and Methods used by esxi_vm_create/esxi_vm_destroy scripts """
import os.path
import sys
import datetime                   # For current Date/Time
import argparse
from math import log
import yaml
# import paramiko                   # For remote ssh

VALID_HW_VERSIONS = ("8",  # ESXi 5.0
                     "9",  # ESXi 5.1
                     "10", # ESXi 5.5
                     "11", # ESXi 6.0
                     "13", # ESXi 6.5
                     "14", # ESXi 6.7
                     "15", # ESXi 6.7 U2, 6.8.7, 6.9.1
                    )
VALID_SHARE_DEFS = ("normal", "low", "high")
VALID_CPU_MMU_PERFS = (("Auto", "Auto"),
                       ("software", "software"),
                       ("hardware", "software"),
                       ("hardware", "hardware"),
                      )
UNIT_LIST = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])


class EsxVmCpu(object):
    """ Class to define VM CPU specs/config """
    def __init__(self, numvcpus=1, corespersocket=1):
        if numvcpus%corespersocket:
            raise ValueError('"numvcpus" must be evenly divisible by "corespersocket"')
        self.params = {}
        self.params['numvcpus'] = numvcpus  # numvcpus
        self.params['corespersocket'] = corespersocket  # cpuid.coresPerSocket - "x"/nonex.
        self.params['cpu_hot_plug'] = False  # vcpu.hotadd - "TRUE"/"FALSE"
        self.params['reservation'] = None  # sched.cpu.min - "0"/"xxx" (in mhz)
        self.params['limit'] = None  # sched.cpu.max - nonexist/"xxx" (in mhz)
        self.params['shares'] = "normal"  # sched.cpu.shares - "normal"/"low"/"high"/"xxxxx"
        self.params['hw_virt'] = False  # vhv.enable - nonexist./"TRUE"
        self.params['perf_counters'] = False  # vpmc.enable - "TRUE"/non-existent
        self.params['affinity'] = "all"  # sched.cpu.affinity - "all"/"n0,n1,n2..."
        self.params['cpu_virt'] = "Auto"  # monitor.virtual_exec - nonex./"software"/"hardware"
        self.params['mmu_virt'] = "Auto"  # monitor.virtual_mmu - nonex./"software"/"hardware"

    def get_sockets(self):
        """ Return how many CPU sockets VM has """
        return self.params['numvcpus']/self.params['corespersocket']

    def set_hot_plug(self, enabled=False):
        """ Set if hot plug feature enabled or not. """
        if not isinstance(enabled, bool):
            raise TypeError("enaabled must be boolean")
        self.params['cpu_hot_plug'] = enabled

    def set_reservation(self, reservation=None):
        """ Set min CPU to reserve for VM. """
        if not isinstance(reservation, int) and reservation is not None:
            raise TypeError("reservation must be integer or None")
        self.params['reservation'] = reservation

    def set_limit(self, limit=None):
        if not isinstance(limit, int) and limit is not None:
            raise TypeError("limit must be integer or None")
        self.params['limit'] = limit

    def set_shares(self, shares="normal"):
        if shares not in VALID_SHARE_DEFS and not isinstance(shares, int):
            raise TypeError("shares must be integeter or one of {}".format(VALID_SHARE_DEFS))
        # Is shares as integer limited to a particular range?
        self.params['shares'] = shares

    def set_hw_virt(self, hw_virt=False):
        """ Enable/disable feature of hw assisted virtualization exposure to guest OS"""
        if not isinstance(hw_virt, bool):
            raise TypeError("hw_virt must be boolean")
        self.params['hw_virt'] = hw_virt

    def set_perf_counters(self, perf_counters=False):
        if not isinstance(perf_counters, bool):
            raise TypeError("oerf_counters must be boolean")
        self.params['perf_counters'] = perf_counters

    def set_affinity(self, affinity="Auto"):
        if isinstance(affinity, str):
            if affinity == "Auto":
                self.params['affinity'] = "Auto"
                return None
        if isinstance(affinity, list) and all([isinstance(_x, int) for _x in affinity]):
            # Should be able ti identify cpus and ensure list is within scope
            self.params['affinity'] = ",".join([str(_x1) for _x1 in affinity])
            return None
        raise TypeError('affinity must be "Auto" or list of integers')

    def set_cpu_mmu_virt(self, cpu_virt="Auto", mmu_virt="Auto"):
        if (cpu_virt not in (_x[0] for _x in VALID_CPU_MMU_PERFS) or
                mmu_virt not in (_x[1] for _x in VALID_CPU_MMU_PERFS)
           ):
            raise TypeError("cpu_virt, mmu_virt must be one of {}".format(VALID_CPU_MMU_PERFS))
        if (cpu_virt, mmu_virt) not in VALID_CPU_MMU_PERFS:
            raise ValueError("(cpu_virt, mmu_virt) combos must be "
                             "one of {}".format(VALID_CPU_MMU_PERFS))
        self.params['cpu_virt'] = cpu_virt
        self.params['mmu_virt'] = mmu_virt


class EsxVm(object):
    """ Class to define the ESXi VM's configuration """
    def __init__(self, vm_name="", vmx_file=""):
        self.vmx_entries = []
        self.config = {}
        self.vm_name = vm_name
        self.vmx_file = vmx_file

    def set_config_version(self, version="8"):
        """ Set config.version for VM definition """
        self.config['config.version'] = str(version)

    def set_defaults(self):
        """ Set default values """
        self.set_config_version()

    def set_hw_version(self, version="8"):
        """ Set Virtual Hardware version for VMX config """
        if (version not in VALID_HW_VERSIONS
                and 'virtualHW.version' not in self.config):
            self.set_hw_version()
        self.config['virtualHW.version'] = version
        return self.config['virtualHW.version']


class Config(object):
    """ Class to handle program configuration """

    def __init__(self):
        self.data = dict()
        self.homedir = os.path.expanduser("~")
        self._default_yml_file = "{}/.esxi-vm.yml".format(self.homedir)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def set(self, key, value):
        """ Set key/value entry in data dictionary. """
        self.data[key] = value

    def get(self, key):
        """ Get value for key """
        return self.data.get(key)

    def load_config(self, yml_file=None):
        """ Load config data from YML file. """
        ret_val = False
        if not yml_file:
            yml_file = self._default_yml_file
        if os.path.exists(yml_file):
            _yml_config_data = yaml.safe_load(open(yml_file))
            self.data.update(_yml_config_data)
            ret_val = True
        return ret_val

    def logfile(self):
        """ Log data into text log file. """
        logfile = "{}/esxi-vm.log".format(self.homedir)
        return logfile

    def setup_config(self):
        """ Set defaults for Config object """
        self.set('LOG', self.logfile())
        self.set('isDryRun', False)
        self.set('isVerbose', False)
        self.set('isSummary', False)
        self.set('HOST', "esxi")
        self.set('USER', "root")
        self.set('PASSWORD', "")
        self.set('CPU', 2)
        self.set('MEM', 4)
        self.set('HDISK', 20)
        self.set('DISKFORMAT', "thin")
        self.set('VIRTDEV', "pvscsi")
        self.set('STORE', "LeastUsed")
        self.set('NET', "None")
        self.set('ISO', "None")
        self.set('GUESTOS', "centos-64")
        self.set('VMXOPTS', "")
        return self.data

    def save_config(self, yml_file=None):
        """ Save data in object to YML file. """
        ret_val = False
        if not yml_file:
            yml_file = self._default_yml_file
        try:
            with open(yml_file, 'w') as _fd:
                yaml.dump(self.data, _fd, default_flow_style=False)
            _fd.close()
            ret_val = True
        except (IOError, OSError):
            print "Unable to create/update config file {}".format(yml_file)
            except_info = sys.exc_info()
            print "The Error is {} - {}".format(except_info[0], except_info[1])
        return ret_val

class Message(object):
    """ Class to handle error messages """

    def __init__(self, text=""):
        """ Init object """
        self.messages = text

    def __str__(self):
        return str(self.messages)

    def __add__(self, other):
        self.add(other)
        return self

    def __iadd__(self, other):
        self.add(other)
        return self

    def __bool__(self):
        return len(self.messages) > 0

    __nonzero__ = __bool__

    def add(self, text):
        """ Add text to collection of error messages """
        if self.messages and self.messages[-1] not in ('{', ',', '"'):
            self.messages += " "
        self.messages += text

    def show(self):
        """ Show messages collected """
        return self.__str__()

    def tty_print(self):
        """ Print messages to tty """
        print self.messages

    def log_to_file(self, logfile):
        """ Append messages to log file """
        try:
            with open(logfile, "a") as _fd:
                _fd.write(self.__str__())
        except (IOError, OSError):
            print "Error writing to log file: {}".format(logfile)

#
#
#   Functions
#
#

def parse_args(config_data):
    """ Setup and parse arguments provided to program. Return parsed args object """
    parser = argparse.ArgumentParser(description='ESXi Create VM utility.')

    parser.add_argument('-d', '--dry',
                        dest='isDryRunarg', action='store_true',
                        help="Enable Dry Run mode  (" + str(config_data['isDryRun']) + ")")
    parser.add_argument("-H", "--Host",
                        dest='HOST', type=str,
                        help="ESXi Host/IP  (" + str(config_data['HOST']) + ")")
    parser.add_argument("-U", "--User",
                        dest='USER', type=str,
                        help="ESXi Host username  (" + str(config_data['USER']) + ")")
    parser.add_argument("-P", "--Password",
                        dest='PASSWORD', type=str,
                        help="ESXi Host password  (*****)")
    parser.add_argument("-n", "--name",
                        dest='NAME', type=str,
                        help="VM name")
    parser.add_argument("-c", "--cpu",
                        dest='CPU', type=int,
                        help="Number of vCPUS  (" + str(config_data['CPU']) + ")")
    parser.add_argument("-m", "--mem",
                        type=int,
                        help="Memory in GB  (" + str(config_data['MEM']) + ")")
    parser.add_argument("-v", "--vdisk",
                        dest='HDISK', type=str,
                        help="Size of virt hdisk  (" + str(config_data['HDISK']) + ")")
    parser.add_argument("-i", "--iso",
                        dest='ISO', type=str,
                        help="CDROM ISO Path | None  (" + str(config_data['ISO']) + ")")
    parser.add_argument("-N", "--net",
                        dest='NET', type=str,
                        help="Network Interface | None  (" + str(config_data['NET']) + ")")
    parser.add_argument("-M", "--mac",
                        dest='MAC', type=str,
                        help="MAC address")
    parser.add_argument("-S", "--store",
                        dest='STORE', type=str,
                        help="vmfs Store | LeastUsed  (" + str(config_data['STORE']) + ")")
    parser.add_argument("-g", "--guestos",
                        dest='GUESTOS', type=str,
                        help="Guest OS. (" + str(config_data['GUESTOS']) + ")")
    parser.add_argument("-o", "--options",
                        dest='VMXOPTS', type=str, default='NIL',
                        help="Comma list of VMX Options.")
    parser.add_argument('-V', '--verbose',
                        dest='isVerbosearg', action='store_true',
                        help="Enable Verbose mode  (" + str(config_data['isVerbose']) + ")")
    parser.add_argument('--summary',
                        dest='isSummaryarg', action='store_true',
                        help="Display Summary  (" + str(config_data['isSummary']) + ")")
    parser.add_argument("-u", "--updateDefaults",
                        dest='UPDATE', action='store_true',
                        help="Update Default VM settings stored in ~/.esxi-vm.yml")
    # parser.add_argument("--showDefaults",
    #                     dest='SHOW', action='store_true',
    #                     help="Show Default VM settings stored in ~/.esxi-vm.yml")

    return parser.parse_args()

# def setup_config():
#
#     #
#     #   System wide defaults
#     #
#     ConfigData = dict(
#
#         #   Your logfile
#         LOG= os.path.expanduser("~") + "/esxi-vm.log",
#
#         #  Enable/Disable dryrun by default
#         isDryRun=False,
#
#         #  Enable/Disable Verbose output by default
#         isVerbose=False,
#
#         #  Enable/Disable exit summary by default
#         isSummary=False,
#
#         #  ESXi host/IP, root login & password
#         HOST="esxi",
#         USER="root",
#         PASSWORD="",
#
#         #  Default number of vCPU's, GB Mem, & GB boot disk
#         CPU=2,
#         MEM=4,
#         HDISK=20,
#
#         #  Default Disk format thin, zeroedthick, eagerzeroedthick
#         DISKFORMAT="thin",
#
#         #  Virtual Disk device type
#         VIRTDEV="pvscsi",
#
#         #  Specify default Disk store to "LeastUsed"
#         STORE="LeastUsed",
#
#         #  Default Network Interface (vswitch)
#         NET="None",
#
#         #  Default ISO
#         ISO="None",
#
#         #  Default GuestOS type.  (See VMware documentation for all available options)
#         GUESTOS="centos-64",
#
#         # Extra VMX options
#         VMXOPTS=""
#     )
#
#     ConfigDataFileLocation = os.path.expanduser("~") + "/.esxi-vm.yml"
#
#     #
#     # Get ConfigData from ConfigDataFile, then merge.
#     #
#     if os.path.exists(ConfigDataFileLocation):
#         FromFileConfigData = yaml.safe_load(open(ConfigDataFileLocation))
#         ConfigData.update(FromFileConfigData)
#
#     # print("{}".format(type(open)))
#     # raise(Exception)
#     try:
#         with open(ConfigDataFileLocation, 'w') as FD:
#             yaml.dump(ConfigData, FD, default_flow_style=False)
#         FD.close()
#     except:
#         print "Unable to create/update config file " + ConfigDataFileLocation
#         e = sys.exc_info()
#         print "The Error is " + str(e[0]) + " - " + str(e[1])
#         sys.exit(1)
#     return ConfigData

# def SaveConfig(ConfigData):
#     """ Take configuration in Config object and save as YML file. """
#     ConfigDataFileLocation = os.path.expanduser("~") + "/.esxi-vm.yml"
#     try:
#         with open(ConfigDataFileLocation, 'w') as FD:
#             yaml.dump(ConfigData, FD, default_flow_style=False)
#         FD.close()
#     except:
#         print "Unable to create/update config file " + ConfigDataFileLocation
#         except_info = sys.exc_info()
#         print "The Error is " + str(except_info[0]) + " - " + str(except_info[1])
#         return 1
#     return 0


def current_datetime_iso_string():
    """ Simply return the current time/date as ISO string """
    i = datetime.datetime.now()
    return str(i.isoformat())



def float2human(num):
    """Integer to Human readable"""
    ret_val = ""
    if num > 1:
        exponent = min(int(log(float(num), 1024)), len(UNIT_LIST) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = UNIT_LIST[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        ret_val = format_string.format(quotient, unit)
    if num == 0:
        ret_val = '0 bytes'
    if num == 1:
        ret_val = '1 byte'
    return ret_val
