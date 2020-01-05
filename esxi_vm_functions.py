import os.path
import yaml
import sys
import datetime                   # For current Date/Time
import paramiko                   # For remote ssh
from math import log


#
#
#   Functions
#
#

class Config:
    """ Class to handle program configuration """

    def __init__(self):
        self.data = dict()

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def set(self, key, value):
        sys.stderr.write("******* Config.set(key='{}', value='{}')\n".format(key, value))
        self.data[key] = value
        sys.stderr.write("******* Config.data: {}\n".format(self.data))

    def get(self, key):
        return self.data.get(key)


class Message:
    """ Class to handle error messages """

    def __init__(self, text=""):
        """ Init object """
        self.messages = text

    def __repr__(self):
        return "Message({})".format(self.messages)

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
        print(self.messages)

    def log_to_file(self, logfile):
        """ Append messages to log file """
        try:
            with open(logfile, "a+w") as _fd:
                _fd.write(self.__str__())
        except Exception as e:
            print "Error writing to log file: {}".format(logfile)


def setup_config():

    #
    #   System wide defaults
    #
    ConfigData = dict(

        #   Your logfile
        LOG= os.path.expanduser("~") + "/esxi-vm.log",

        #  Enable/Disable dryrun by default
        isDryRun=False,

        #  Enable/Disable Verbose output by default
        isVerbose=False,

        #  Enable/Disable exit summary by default
        isSummary=False,

        #  ESXi host/IP, root login & password
        HOST="esxi",
        USER="root",
        PASSWORD="",

        #  Default number of vCPU's, GB Mem, & GB boot disk
        CPU=2,
        MEM=4,
        HDISK=20,

        #  Default Disk format thin, zeroedthick, eagerzeroedthick
        DISKFORMAT="thin",

        #  Virtual Disk device type
        VIRTDEV="pvscsi",

        #  Specify default Disk store to "LeastUsed"
        STORE="LeastUsed",

        #  Default Network Interface (vswitch)
        NET="None",

        #  Default ISO
        ISO="None",

        #  Default GuestOS type.  (See VMware documentation for all available options)
        GUESTOS="centos-64",

        # Extra VMX options
        VMXOPTS=""
    )

    ConfigDataFileLocation = os.path.expanduser("~") + "/.esxi-vm.yml"

    #
    # Get ConfigData from ConfigDataFile, then merge.
    #
    if os.path.exists(ConfigDataFileLocation):
        FromFileConfigData = yaml.safe_load(open(ConfigDataFileLocation))
        ConfigData.update(FromFileConfigData)

    # print("{}".format(type(open)))
    # raise(Exception)
    try:
        with open(ConfigDataFileLocation, 'w') as FD:
            yaml.dump(ConfigData, FD, default_flow_style=False)
        FD.close()
    except:
        print "Unable to create/update config file " + ConfigDataFileLocation
        e = sys.exc_info()
        print "The Error is " + str(e[0]) + " - " + str(e[1])
        sys.exit(1)
    return ConfigData

def SaveConfig(ConfigData):
    ConfigDataFileLocation = os.path.expanduser("~") + "/.esxi-vm.yml"
    try:
        with open(ConfigDataFileLocation, 'w') as FD:
            yaml.dump(ConfigData, FD, default_flow_style=False)
        FD.close()
    except:
        print "Unable to create/update config file " + ConfigDataFileLocation
        e = sys.exc_info()
        print "The Error is " + str(e[0]) + " - " + str(e[1])
        return 1
    return 0


def theCurrDateTime():
    i = datetime.datetime.now()
    return str(i.isoformat())


unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
def float2human(num):
    """Integer to Human readable"""
    if num > 1:
        exponent = min(int(log(float(num), 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'
