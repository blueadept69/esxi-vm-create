#!/usr/bin/python
""" esxi_vm_create.py - create VM on ESXi host. """
import sys                        # For args
import re                         # For regex
import paramiko                   # For remote ssh

from esxi_vm_functions import current_datetime_iso_string, Message, Config, parse_args

def main():
    """ main function. """
    #      Defaults and Variable setup
    config_data = Config()
    config_data.setup_config()
    config_data.set("NAME", "")

    # error_messages = ""
    error_messages = Message()
    MAC = ""
    GeneratedMAC = ""
    ISOfound = False
    check_has_errors = False
    LeastUsedDS = ""
    data_store_path = ""
    DSSTORE = ""

    args = parse_args(config_data)

    if args.isDryRunarg:
        config_data['isDryRun'] = True
    if args.isVerbosearg:
        config_data['isVerbose'] = True
    if args.isSummaryarg:
        config_data['isSummary'] = True
    if args.HOST:
        config_data['HOST'] = args.HOST
    if args.USER:
        config_data['USER'] = args.USER
    if args.PASSWORD:
        config_data['PASSWORD'] = args.PASSWORD
    if args.NAME:
        # NAME=args.NAME
        config_data.set("NAME", args.NAME)
    if args.CPU:
        config_data['CPU'] = int(args.CPU)
    if args.mem:
        config_data['MEM'] = int(args.mem)
    if args.HDISK:
        config_data['HDISK'] = int(args.HDISK)
    if args.ISO:
        config_data['ISO'] = args.ISO
    if args.NET:
        config_data['NET'] = args.NET
    if args.MAC:
        MAC = args.MAC
    if args.STORE:
        config_data['STORE'] = args.STORE
    # By rights this should never be reached. If args.STORE is set, then below won't be True.
    # If args.STORE is passed with an empty string, above won't be True. And setup_config
    # should always set this as LeastUsed. Leaving here for future import of default configs
    # from YML file.
    if config_data['STORE'] == "":
        config_data['STORE'] = "LeastUsed"
    if args.GUESTOS:
        config_data['GUESTOS'] = args.GUESTOS
    # This should never be reached since config_data['VMXOPTS'] defaults to ""
    # Leaving here for future import of default configs from YML file.
    if args.VMXOPTS == '' and config_data['VMXOPTS'] != '':
        config_data['VMXOPTS'] = ''
    if args.VMXOPTS and args.VMXOPTS != 'NIL':
        config_data['VMXOPTS'] = args.VMXOPTS.split(",")


    if args.UPDATE:
        print "Saving new Defaults to ~/.esxi-vm.yml"

        # SaveConfig(config_data)
        config_data.save_config()
        if config_data['NAME'] == "":
            sys.exit(0)

    #
    #      main()
    #
    # log_output = '{'
    log_output = Message("{")
    log_output += '"datetime":"{}",'.format(str(current_datetime_iso_string()))

    if config_data['NAME'] == "":
        print "ERROR: Missing required option --name"
        sys.exit(1)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config_data['HOST'],
                    username=config_data['USER'],
                    password=config_data['PASSWORD'])

        (stdin, stdout, stderr) = ssh.exec_command("esxcli system version get |grep Version")
        # type(stdin)
        if re.match("Version", str(stdout.readlines())) is None:
            print "Unable to determine if this is a ESXi Host: " \
                  "%s, username: %s" % (config_data['HOST'], config_data['USER'])
            sys.exit(1)
    except:
        except_info = sys.exc_info()
        print "The Error is " + str(except_info[0]) + " - " + str(except_info[1])
        print "Unable to access ESXi Host: " \
              "%s, username: %s" % (config_data['HOST'], config_data['USER'])
        sys.exit(1)

    #
    #      Get list of DataStores, store in VOLUMES
    #
    try:
        (stdin, stdout, stderr) = ssh.exec_command("esxcli storage filesystem list |"
                                                   "grep '/vmfs/volumes/.*true  VMFS' |sort -nk7")
        # type(stdin)
        VOLUMES = {}
        for line in stdout.readlines():
            splitLine = line.split()
            VOLUMES[splitLine[0]] = splitLine[1]
            LeastUsedDS = splitLine[1]
    except:
        except_info = sys.exc_info()
        print "The Error is " + str(except_info[0]) + " - " + str(except_info[1])
        sys.exit(1)

    if config_data['STORE'] == "LeastUsed":
        config_data['STORE'] = LeastUsedDS


    #
    #      Get list of Networks available, store in VMNICS
    #
    try:
        (stdin, stdout, stderr) = ssh.exec_command("esxcli network vswitch standard list|"
                                                   "grep Portgroups|sed 's/^   Portgroups: //g'")
        # type(stdin)
        VMNICS = []
        for line in stdout.readlines():
            splitLine = re.split(',|\n', line)
            for pg in splitLine:
                VMNICS.append(pg.strip())
    except:
        except_info = sys.exc_info()
        print "The Error is " + str(except_info[0]) + " - " + str(except_info[1])
        sys.exit(1)

    #
    #      Check MAC address
    #
    MACarg = MAC
    if MAC != "":
        MACregex = r'^([a-fA-F0-9]{2}[:|-]){5}[a-fA-F0-9]{2}$'
        if re.compile(MACregex).search(MAC):
            # Full MAC found. OK
            MAC = MAC.replace("-", ":")
        elif re.compile(MACregex).search("00:50:56:" + MAC):
            MAC = "00:50:56:" + MAC.replace("-", ":")
        else:
            print "ERROR: " + MAC + " Invalid MAC address."
            # error_messages += " " + MAC + " Invalid MAC address."
            error_messages += "{} Invalid MAC address.".format(MAC)
            check_has_errors = True


    #
    #      Get from ESXi host if ISO exists
    #
    ISOarg = config_data['ISO']
    if config_data['ISO'] == "None":
        config_data['ISO'] = ""
    if config_data['ISO'] != "":
        try:
            #  If ISO has no "/", try to find the ISO
            if not re.match('/', config_data['ISO']):
                (stdin, stdout, stderr) = ssh.exec_command(
                    "find /vmfs/volumes/ -type f -name {}"
                    " -exec sh -c 'echo $1;"
                    " kill $PPID' sh {{}} 2>/dev/null \;".format(config_data['ISO']))
                type(stdin)
                FoundISOPath = str(stdout.readlines()[0]).strip('\n')
                if config_data['isVerbose']:
                    print "FoundISOPath: " + str(FoundISOPath)
                config_data['ISO'] = str(FoundISOPath)

            (stdin, stdout, stderr) = ssh.exec_command("ls " + str(config_data['ISO']))
            # type(stdin)
            if stdout.readlines() and not stderr.readlines():
                ISOfound = True

        except:
            except_info = sys.exc_info()
            print "The Error is " + str(except_info[0]) + " - " + str(except_info[1])
            sys.exit(1)

    #
    #      Check if VM already exists
    #
    VMID = -1
    try:
        (stdin, stdout, stderr) = ssh.exec_command("vim-cmd vmsvc/getallvms")
        # type(stdin)
        for line in stdout.readlines():
            splitLine = line.split()
            if config_data['NAME'] == splitLine[1]:
                VMID = splitLine[0]
                print "ERROR: VM " + config_data['NAME'] + " already exists."
                # error_messages += " VM " + config_data['NAME'] + " already exists."
                error_messages += "VM {} already exists.".format(config_data['NAME'])
                check_has_errors = True
    except:
        except_info = sys.exc_info()
        print "The Error is " + str(except_info[0]) + " - " + str(except_info[1])
        sys.exit(1)

    #
    #      Do checks here
    #

    #  Check CPU
    if config_data['CPU'] < 1 or config_data['CPU'] > 128:
        print str(config_data['CPU']) + " CPU out of range. [1-128]."
        error_messages += "{} CPU out of range. [1-128].".format(str(config_data['CPU']))
        check_has_errors = True

    #  Check MEM
    if config_data['MEM'] < 1 or config_data['MEM'] > 4080:
        print str(config_data['MEM']) + "GB Memory out of range. [1-4080]."
        error_messages += "{} GB Memory out of range. [1-4080].".format(str(config_data['MEM']))
        check_has_errors = True

    #  Check HDISK
    if config_data['HDISK'] < 1 or config_data['HDISK'] > 63488:
        print "Virtual Disk size " + str(config_data['HDISK']) + "GB out of range. [1-63488]."
        error_messages += "Virtual Disk size {} GB out of range. [1-63488].".\
            format(str(config_data['HDISK']))
        check_has_errors = True

    #  Convert STORE to path and visa-versa
    V = []
    for Path in VOLUMES:
        V.append(VOLUMES[Path])
        if config_data['STORE'] == Path or config_data['STORE'] == VOLUMES[Path]:
            data_store_path = Path
            DSSTORE = VOLUMES[Path]

    if DSSTORE not in V:
        print "ERROR: Disk Storage " + config_data['STORE'] + " doesn't exist. "
        print "    Available Disk Stores: " + str([str(item) for item in V])
        print "    LeastUsed Disk Store : " + str(LeastUsedDS)
        error_messages += "Disk Storage {} doesn't exist.".format(config_data['STORE'])
        check_has_errors = True

    #  Check NIC  (NIC record)
    if (config_data['NET'] not in VMNICS) and (config_data['NET'] != "None"):
        print "ERROR: Virtual NIC " + config_data['NET'] + " doesn't exist."
        print "    Available VM NICs: " + str([str(item) for item in VMNICS]) + " or 'None'"
        error_messages += "Virtual NIC {} doesn't exist.".format(config_data['NET'])
        check_has_errors = True

    #  Check ISO exists
    if config_data['ISO'] != "" and not ISOfound:
        print "ERROR: ISO " + config_data['ISO'] + " not found.  Use full path to ISO"
        error_messages += "ISO {} not found.  Use full path to ISO".format(config_data['ISO'])
        check_has_errors = True

    #  Check if data_store_path/NAME aready exists
    try:
        vmx_dir_full_path = data_store_path + "/" + config_data['NAME']
        (stdin, stdout, stderr) = ssh.exec_command("ls -d " + vmx_dir_full_path)
        # type(stdin)
        if stdout.readlines() and not stderr.readlines():
            print "ERROR: Directory " + vmx_dir_full_path + " already exists."
            error_messages += "Directory {} already exists.".format(vmx_dir_full_path)
            check_has_errors = True
    except:
        pass

    #
    #      Create the VM
    #
    vmx_definition = []
    vmx_definition.append('config.version = "8"')
    vmx_definition.append('virtualHW.version = "8"')
    vmx_definition.append('vmci0.present = "TRUE"')
    vmx_definition.append('displayName = "' + config_data['NAME'] + '"')
    vmx_definition.append('floppy0.present = "FALSE"')
    vmx_definition.append('numvcpus = "' + str(config_data['CPU']) + '"')
    vmx_definition.append('scsi0.present = "TRUE"')
    vmx_definition.append('scsi0.sharedBus = "none"')
    vmx_definition.append('scsi0.virtualDev = "pvscsi"')
    vmx_definition.append('memsize = "' + str(config_data['MEM'] * 1024) + '"')
    vmx_definition.append('scsi0:0.present = "TRUE"')
    vmx_definition.append('scsi0:0.fileName = "' + config_data['NAME'] + '.vmdk"')
    vmx_definition.append('scsi0:0.deviceType = "scsi-hardDisk"')
    if config_data['ISO'] == "":
        vmx_definition.append('ide1:0.present = "TRUE"')
        vmx_definition.append('ide1:0.fileName = "emptyBackingString"')
        vmx_definition.append('ide1:0.deviceType = "atapi-cdrom"')
        vmx_definition.append('ide1:0.startConnected = "FALSE"')
        vmx_definition.append('ide1:0.clientDevice = "TRUE"')
    else:
        vmx_definition.append('ide1:0.present = "TRUE"')
        vmx_definition.append('ide1:0.fileName = "' + config_data['ISO'] + '"')
        vmx_definition.append('ide1:0.deviceType = "cdrom-image"')
    vmx_definition.append('pciBridge0.present = "TRUE"')
    vmx_definition.append('pciBridge4.present = "TRUE"')
    vmx_definition.append('pciBridge4.virtualDev = "pcieRootPort"')
    vmx_definition.append('pciBridge4.functions = "8"')
    vmx_definition.append('pciBridge5.present = "TRUE"')
    vmx_definition.append('pciBridge5.virtualDev = "pcieRootPort"')
    vmx_definition.append('pciBridge5.functions = "8"')
    vmx_definition.append('pciBridge6.present = "TRUE"')
    vmx_definition.append('pciBridge6.virtualDev = "pcieRootPort"')
    vmx_definition.append('pciBridge6.functions = "8"')
    vmx_definition.append('pciBridge7.present = "TRUE"')
    vmx_definition.append('pciBridge7.virtualDev = "pcieRootPort"')
    vmx_definition.append('pciBridge7.functions = "8"')
    vmx_definition.append('guestOS = "' + config_data['GUESTOS'] + '"')
    if config_data['NET'] != "None":
        vmx_definition.append('ethernet0.virtualDev = "vmxnet3"')
        vmx_definition.append('ethernet0.present = "TRUE"')
        vmx_definition.append('ethernet0.networkName = "' + config_data['NET'] + '"')
        if MAC == "":
            vmx_definition.append('ethernet0.addressType = "generated"')
        else:
            vmx_definition.append('ethernet0.addressType = "static"')
            vmx_definition.append('ethernet0.address = "' + MAC + '"')

    #
    #   Merge extra vmx_definition options
    for _vmx_opt in config_data['VMXOPTS']:
        try:
            vmx_opt_name, vmx_opt_value = _vmx_opt.split("=")
        except:
            vmx_opt_name = ""
            vmx_opt_value = ""
        key = vmx_opt_name.lstrip().strip()
        value = vmx_opt_value.lstrip().strip()
        for i in vmx_definition:
            try:
                ikey, _ivalue = i.split("=")
            except:
                # By rights this should never be reached, since vmx_definition is created and
                # populated by this code. Leaving for now since it doesn't hurt anything.
                break
            if ikey.lstrip().strip().lower() == key.lower():
                index = vmx_definition.index(i)
                vmx_definition[index] = ikey + " = " + value
                break
        else:
            if key != '' and value != '':
                vmx_definition.append(key + " = " + value)

    if config_data['isVerbose'] and config_data['VMXOPTS'] != '':
        print "VMX file:"
        for i in vmx_definition:
            print i

    MyVM = vmx_dir_full_path + "/" + config_data['NAME']
    if check_has_errors:
        run_result = "Errors"
    else:
        run_result = "Success"

    if not config_data['isDryRun'] and not check_has_errors:
        try:

            # Create NAME.vmx
            if config_data['isVerbose']:
                print "Create " + config_data['NAME'] + ".vmx file"
            (stdin, stdout, stderr) = ssh.exec_command("mkdir " + vmx_dir_full_path)
            # type(stdin)
            for line in vmx_definition:
                (stdin, stdout, stderr) = ssh.exec_command("echo \'" + line + "\' >>"
                                                           + MyVM + ".vmx")
                type(stdin)

            # Create vmdk
            if config_data['isVerbose']:
                print "Create " + config_data['NAME'] + ".vmdk file"
            (stdin, stdout, stderr) = ssh.exec_command("vmkfstools -c " + str(config_data['HDISK'])
                                                       + "G -d " +
                                                       config_data['DISKFORMAT'] + " "
                                                       + MyVM + ".vmdk",
                                                       get_pty=True)
            for _pty_line in stdout.readlines():
                print _pty_line
            # for _pty_line in iter(stdout.readline, ""):
            #     if config_data['isVerbose']:
            #         print(_pty_line)
            # type(stdin)

            # Register VM
            if config_data['isVerbose']:
                print "Register VM"
            (stdin, stdout, stderr) = ssh.exec_command("vim-cmd solo/registervm " + MyVM + ".vmx")
            # type(stdin)
            VMID = int(stdout.readlines()[0])

            # Power on VM
            if config_data['isVerbose']:
                print "Power ON VM"
            (stdin, stdout, stderr) = ssh.exec_command("vim-cmd vmsvc/power.on " + str(VMID))
            # type(stdin)
            if stderr.readlines():
                print "Error Power.on VM."
                run_result = "Fail"

            # Get Generated MAC
            if config_data['NET'] != "None":
                (stdin, stdout, stderr) = ssh.exec_command(
                    "grep -i 'ethernet0.*ddress = ' " + MyVM + ".vmx |tail -1|awk '{print $NF}'")
                # type(stdin)
                GeneratedMAC = str(stdout.readlines()[0]).strip('\n"')

        except:
            print "There was an error creating the VM."
            except_info = sys.exc_info()
            print "The Error is " + str(except_info[0]) + " - " + str(except_info[1])
            error_messages += "There was an error creating the VM."
            run_result = "Fail"

    #      Print Summary

    #
    #   The output log string
    log_output += '"Host":"' + config_data['HOST'] + '",'
    log_output += '"Name":"' + config_data['NAME'] + '",'
    log_output += '"CPU":"' + str(config_data['CPU']) + '",'
    log_output += '"Mem":"' + str(config_data['MEM']) + '",'
    log_output += '"Hdisk":"' + str(config_data['HDISK']) + '",'
    log_output += '"DiskFormat":"' + config_data['DISKFORMAT'] + '",'
    # Is VIRTDEV used anywhere???
    log_output += '"Virtual Device":"' + config_data['VIRTDEV'] + '",'
    log_output += '"Store":"' + config_data['STORE'] + '",'
    log_output += '"Store Used":"' + data_store_path + '",'
    log_output += '"Network":"' + config_data['NET'] + '",'
    log_output += '"ISO":"' + ISOarg + '",'
    log_output += '"ISO used":"' + config_data['ISO'] + '",'
    log_output += '"Guest OS":"' + config_data['GUESTOS'] + '",'
    log_output += '"MAC":"' + MACarg + '",'
    log_output += '"MAC Used":"' + GeneratedMAC + '",'
    log_output += '"Dry Run":"' + str(config_data['isDryRun']) + '",'
    log_output += '"Verbose":"' + str(config_data['isVerbose']) + '",'
    if error_messages:
        log_output += '"Error Message":"{}",'.format(error_messages)
    log_output += '"Result":"' + run_result + '",'
    log_output += '"Completion Time":"' + str(current_datetime_iso_string()) + '"'
    log_output += '}\n'
    # try:
        # with open(LOG, "a+w") as FD:
        #     FD.write(str(log_output))
    log_output.log_to_file(config_data['LOG'])
    # except:
    #     print "Error writing to log file: " + LOG

    if config_data['isSummary']:
        if config_data['isDryRun']:
            print "\nDry Run summary:"
        else:
            print "\nCreate VM Success:"

        if config_data['isVerbose']:
            print "ESXi Host: " + config_data['HOST']
        print "VM NAME: " + config_data['NAME']
        print "vCPU: " + str(config_data['CPU'])
        print "Memory: " + str(config_data['MEM']) + "GB"
        print "VM Disk: " + str(config_data['HDISK']) + "GB"
        if config_data['isVerbose']:
            print "Format: " + config_data['DISKFORMAT']
        print "DS Store: " + DSSTORE
        print "Network: " + config_data['NET']
        if config_data['ISO']:
            print "ISO: " + config_data['ISO']
        if config_data['isVerbose']:
            print "Guest OS: " + config_data['GUESTOS']
            print "MAC: " + GeneratedMAC
    else:
        pass

    if check_has_errors:
        if config_data['isDryRun']:
            print "Dry Run: Failed."
        sys.exit(1)
    else:
        if config_data['isDryRun']:
            print "Dry Run: Success."
        else:
            print GeneratedMAC
        sys.exit(0)

if __name__ == "__main__":
    main()
