#!/usr/bin/env python2.7

import os
import commands
import platform
import sys
import string
import collections
import re
import time

LINE_BR = '+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+='

#SMBIOS tables
SMBIOS_BIOS = '0'
SMBIOS_SYSTEM = '1'
SMBIOS_BASE_BOARD = '2'
SMBIOS_CHASSIS = '3'
SMBIOS_PROCESSOR = '4'
SMBIOS_CACHE = '7'
SMBIOS_MEMORY_DEVICE = '17'

SKYLARK_BASE_FREQ = 3000

def __get_platform():
    """Return the current OS platform.

    For example: if current os platform is Ubuntu then a string "ubuntu"
    will be returned (which is the name of the module).
    This string is used to decide which platform module should be imported.
    """
    # linux_distribution is deprecated and will be removed in Python 3.7
    # Warings *not* disabled, as we certainly need to fix this.
    tuple_platform = platform.linux_distribution()
    current_platform = tuple_platform[0]    
    if "Ubuntu" in current_platform:
        return "ubuntu"
    elif "CentOS" in current_platform:
        return "centos"
    elif "oracle" in current_platform:
        return "oracle"
    elif "debian" in current_platform:
        # Stock Python does not detect Ubuntu and instead returns debian.
        # Or at least it does in some build environments like Travis CI
        return "ubuntu"
    else:
        return "Unknown"

def __get_fullplatform():
    """Return the current OS platform.

    For example: if current os platform is Ubuntu then a string "ubuntu"
    will be returned (which is the name of the module).
    This string is used to decide which platform module should be imported.
    """
    # linux_distribution is deprecated and will be removed in Python 3.7
    # Warings *not* disabled, as we certainly need to fix this.
    tuple_platform = platform.linux_distribution()
    return '%s %s %s' % (tuple_platform[0], tuple_platform[1], tuple_platform[2])

def lpi_ctrl(ctl = 'on'):
    for cpu in range(0, 32):
        for state in [ '0', '1', '2', '3', '4', '5' ]:
            cpustate = '/sys/devices/system/cpu/cpu' + str(cpu) + '/cpuidle/state' + state + '/disable'
            cmd = 'cat ' + cpustate
            a = commands.getoutput(cmd)
            if ctl is 'off':
                if a is '1':
                    return
                cmd = 'echo 1 > ' + cpustate
            else:
                if a is '0':
                    return
                cmd = 'echo 0 > ' + cpustate
            commands.getoutput(cmd)
    # delay to make sure all RB registers accessible
    if ctl is 'off':
        time.sleep(3)

def get_cpu_info():
    # Processor information
    cmd = 'dmidecode -t %s' % SMBIOS_PROCESSOR
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    cpu_ver = max_speed = cores = cores_online = 'Unknown'
    for txt in ss:
	match = re.search(r'^\s?Version:', txt)
        if match:
            cpu_ver = match.string
        match = re.search(r'^\s?Max Speed:', txt)
        if match:
            max_speed = match.string
        match = re.search(r'^\s?Core Count:', txt)
        if match:
            cores = match.string

    # Turbo
    turbo = 'No'
    tmp = 0
    for a in max_speed.split(' '):
        match = re.search(r'\d', a) 
        if match:
            tmp = int(match.string)
            break
    if tmp > SKYLARK_BASE_FREQ:
        turbo = 'Yes'

    # Cache(s) information
    cmd = 'dmidecode -t %s' % SMBIOS_CACHE
    s = commands.getoutput(cmd)
    ss = re.split('\n\n+', s)
    caches = []
    for txt in ss:
        _txt = re.split('\n+', txt)
        for a in _txt:
            match = re.search(r'^\s?Socket Designation:', a)
            if match:
                cache = match.string.split(':')[1][1:]
            match = re.search(r'^\s?Installed Size:', a)
            if match:
                cache = cache + ':' + match.string.split(':')[1]
		caches.append(cache)

    # Look for online CPU list
    cmd = 'lscpu'
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    for txt in ss:
	match = re.search(r'^On-line CPU+', txt)
        if match:
            cores_online = match.string
    cpus = cpu_ver + '\n' + max_speed + '\n' + '\tTurbo support: %s' % turbo + '\n' + cores + '\n\t' + cores_online

    # Output
    print cpus
    for _cache in caches:
        print '\t' + _cache

    # CCCR
    lpi_ctrl(ctl = 'off')
    rb_base = 0x7c0c0000
    tmp_cccr = 0xffffffff
    err = False
    for cpu in range(0, 32):
        addr = hex(rb_base + cpu * 0x100000)
        cmd = './regutil/regutil -s -r %s' % addr
        s = commands.getoutput(cmd)
        match = re.search(r'^0x\d', s)
        if not match:
           err = True
           break
        if tmp_cccr == 0xffffffff:
           tmp_cccr = int(s, 16)
        else:
           if tmp_cccr != int(s, 16):
               print '\t*** Non-Identical CCCR settings CPU%d: 0x%08x ***' %(cpu, int(s, 16))
               err = True
               break
    if err is True:
        cccr = '\tCCCR [all CPUs]: Unknown'
    else:
        cccr = '\tCCCR [all CPUs]: 0x%08x' % tmp_cccr
    lpi_ctrl(ctl = 'on')
    print cccr

def get_ddr_info():
    cmd = 'dmidecode -t %s' % SMBIOS_MEMORY_DEVICE
    s = commands.getoutput(cmd)
    ss = re.split('\n\n+', s)
    dimms = []
    total_size = 0
    bsize = 'MB'
    bsize_first = ''
    for txt in ss:
        _txt = re.split('\n+', txt)
        locator = _type = manuft = part_no = speed = ranks = size = 'Unknown'        
        for a in _txt:
            match = re.search(r'^\s?Locator:', a)
            if match:
                locator = match.string.split(':')[1][1:]
            match = re.search(r'^\s?Type:', a)
            if match:
                _type = match.string.split(':')[1]
            match = re.search(r'^\s?Manufacturer:', a)
            if match:
                manuft = match.string.split(':')[1]
            match = re.search(r'^\s?Part Number:', a)
            if match:
                part_no = match.string.split(':')[1][1:]
            match = re.search(r'^\s?Configured Clock Speed:', a)
            if match:
                speed = match.string.split(':')[1]
            match = re.search(r'^\s?Rank:', a)
            if match:
                ranks = match.string.split(':')[1][1:]
            match = re.search(r'^\s?Size:', a)
            if match:
                size = match.string.split(' ')[1]
                if len(match.string.split(' '))>2:
                    bsize = match.string.split(' ')[2]                
        if size != 'No' and size != 'Unknown':
            if 'Not Specified' in manuft:
                dimm = '[%s]: %s' % (locator, manuft)
            else:
                dimm = '[%s]: %s %s %s %s %s %sR %s' % (locator, manuft,_type, size, bsize, speed, ranks, part_no)
            total_size += int(size)
            if bsize_first == '':
                bsize_first = bsize
            dimms.append(dimm)

    # Output
    print '\tTotal DRAM size: %s %s' % (total_size, bsize_first)
    for _dimm in dimms:
        print '\t' + _dimm

def get_os_info():
    cmd = 'uname -r'
    os_ver = commands.getoutput(cmd)    

    # PM governer
    pm_gov = "Unknown"
    cmd = 'cpupower frequency-info | grep -e "The governor"'
    s = commands.getoutput(cmd)    
    if s:
        pm_gov = re.split('\"', s)[1]

    # LPI support/status
    lpi_en = lpi_state = tmp = 'Unknown'
    identical = 'Yes'
    for cpu in range(0, 32):
        for state in [ '0', '1', '2', '3', '4', '5' ]:
            cpustate = '/sys/devices/system/cpu/cpu'+str(cpu)+'/cpuidle/state'+state+'/disable'
            cmd = 'cat ' + cpustate
            a = commands.getoutput(cmd)
	    if a in ['0', '1']:
                lpi_en = 'Supported'
                if a is '0':
                    lpi_state = 'Enabled'
                else:
                    lpi_state = 'Disabled'
                if tmp == 'Unknown':
                    tmp = lpi_state
                elif tmp is not lpi_state: 
                    identical = 'No'
                    break
            else:
                lpi_en = 'Not supported'

        if identical is 'No':
            lpi_state = 'Non-identical settings'
            break
    lpi = 'LPI [all CPUs]: ' + lpi_en + ' [%s]' % lpi_state
    os_platform = __get_fullplatform()
    os = '\tOS: %s\n' % os_platform + '\tKernel: %s\n' % os_ver + '\tPower Management policy: %s' % pm_gov + '\n\t' + lpi
    print os

def get_bios_fw_info():
    cmd = 'dmidecode -t %s' % SMBIOS_BIOS
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    bios_rev = '\tBIOS Revision: Unknown'
    fw_rev = '\tFirmware Revision: Unknown'
    build_ver = '\tVersion: Unknown'
    date = '\tRelease Date: Unknown'
    for txt in ss:
        match = re.search(r'^\s?BIOS Revision:', txt)
        if match:
            bios_rev = match.string
        match = re.search(r'^\s?Firmware Revision:', txt)
        if match:
            fw_rev = match.string
        match = re.search(r'^\s?Release Date:', txt)
        if match:
            date = match.string
        match = re.search(r'^\s?Version:', txt)
        if match:
            build_ver = match.string

    bios = build_ver + '\n' + bios_rev + '\n' + fw_rev + '\n' + date

    print bios
        
def get_pcie_info():
    cmd = 'lspci'
    s = commands.getoutput(cmd)

    pcie = re.split('\n+', s)
    for p in pcie:
        print '\t%s' % p

def get_disk_info():
    disks = []
    for dev in string.ascii_lowercase:
        cmd = 'smartctl -i /dev/sd%c' % dev
        s = commands.getoutput(cmd)
        match = re.search(r'=== START OF+', s)
        if match:
            ss = match.string.split('SECTION ===\n')[1]
            sss = re.split('\n+', ss)            
            family = 'Model Family: Unknown'
            model = 'Device Model: Unknown'
            capacity = 'User Capacity: Unknown'
            ver = 'SATA Version: Unknown'
            for txt in sss:
                match = re.search(r'^\s?Model Family:', txt)
                if match:
                    family = match.string
                match = re.search(r'^\s?Device Model:', txt)
                if match:
                    model = match.string
                match = re.search(r'^\s?User Capacity:', txt)
                if match:
                    capacity = match.string                
                match = re.search(r'^\s?SATA Version is:', txt)
                if match:
                    ver = match.string
            txt = '[/dev/sd%c]\n\n' %dev + '\t' + family + '\n\t' + model + '\n\t' + capacity + '\n\t' + ver
            disks.append(txt)

    for disk in disks:
        print disk 

def get_sys_base_chasiss_info():
    cmd = 'dmidecode -t %s' % SMBIOS_SYSTEM
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    sys_manuf = 'Manufacturer: Unknown'
    sys_prod = 'Product Name: Unknown'
    sys_serial = 'Serial Number: Unknown'
    sys_family = 'Family: Unknown'
    for txt in ss:
        match = re.search(r'^\s?Manufacturer:', txt)
        if match:
            sys_manuf = match.string
        match = re.search(r'^\s?Product Name:', txt)
        if match:
            sys_prod = match.string
        match = re.search(r'^\s?Serial Number:', txt)
        if match:
            sys_serial = match.string
        match = re.search(r'^\s?Family:', txt)
        if match:
            sys_family = match.string
    sys = "System Information:\n" + sys_manuf + '\n' + sys_prod + '\n' + sys_serial + '\n' + sys_family + '\n'

    cmd = 'dmidecode -t %s' % SMBIOS_BASE_BOARD
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    base_manuf = 'Manufacturer: Unknown'
    base_prod = 'Product Name: Unknown'
    base_serial = 'Serial Number: Unknown'    
    base_ver = 'Version: Unknown'
    base_asset_tag = 'Asset Tag: Unknown'
    for txt in ss:
        match = re.search(r'^\s?Manufacturer:', txt)
        if match:
            base_manuf = match.string
        match = re.search(r'^\s?Product Name:', txt)
        if match:
            base_prod = match.string
        match = re.search(r'^\s?Version:', txt)
        if match:
            base_ver = match.string
        match = re.search(r'^\s?Serial Number:', txt)
        if match:
            base_serial = match.string
        match = re.search(r'^\s?Asset Tag:', txt)
        if match:
            base_asset_tag = match.string
    base = "Base Board Information:\n" + base_manuf + '\n' + base_prod + '\n' + base_ver + '\n' + base_serial + '\n' + base_asset_tag + '\n'

    cmd = 'dmidecode -t %s' % SMBIOS_CHASSIS
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    chass_manuf = 'Manufacturer: Unknown'
    chass_ver = 'Version: Unknown'
    chass_serial = 'Serial Number: Unknown'
    chass_asset = 'Asset Tag: Unknown'
    for txt in ss:
        match = re.search(r'^\s?Manufacturer:', txt)
        if match:
            chass_manuf = match.string
        match = re.search(r'^\s?Version:', txt)
        if match:
            chass_ver = match.string
        match = re.search(r'^\s?Serial Number:', txt)
        if match:
            chass_serial = match.string
        match = re.search(r'^\s?Asset Tag:', txt)
        if match:
            chass_asset = match.string
    chassis = 'Chassis Information:\n' + chass_manuf + '\n' + chass_ver + '\n' + chass_serial + '\n' + chass_asset
 
    print sys + base + chassis

def get_bmc_info():
    # Get BMC LAN information
    cmd = 'ipmitool -U ADMIN -P ADMIN lan print'
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    ip = 'IP Address: Unknown'
    mac = 'MAC Address: Unknown'
    subnet = 'Subnet Mask: Unknown'
    gateway = 'Default Gateway IP: Unknown'
    for txt in ss:
        match = re.search(r'^\s?IP Address+', txt)
        if match:
            ip = match.string
        match = re.search(r'^\s?MAC Address+', txt)
        if match:
            mac = match.string
        match = re.search(r'^\s?Subnet Mask+', txt)
        if match:
            subnet = match.string
        match = re.search(r'^\s?Default Gateway IP+', txt)
        if match:
            gateway = match.string
    bmc_lan = '\t%s\n' % mac + '\t%s\n' % ip + '\t%s\n' % subnet + '\t%s' % gateway


    # Get BMC ROM version
    cmd = 'ipmitool -U ADMIN -P ADMIN mc info'
    s = commands.getoutput(cmd)
    ss = re.split('\n+', s)
    core_rev = 'Firmware Revision: Unknown'
    aux = 'Aux Firmware Rev Info: Unknown'
    bmc_ver = "Unknown"
    if s.find("Could not open device") == -1:
        for txt in ss:
            match = re.search(r'^\s?Firmware Revision+', txt)
            if match:
                core_rev = match.string.split(':')[1]

        ss = re.split('Aux Firmware Rev Info     :', s)[1]
        sss = re.split('\n+', ss)
        auxB2 = re.sub(r'\W+', '', sss[2])
        auxB1 = re.sub(r'\W+', '', sss[1])
        aux = str(int(auxB2, 16) * 256 + int(auxB1, 16))
        bmc_ver = core_rev + '.' + aux 

    print "BMC LAN information:\n" + bmc_lan
    print "BMC ROM version: %s" % bmc_ver
 

def __check_requirements(tools):
    if tools:
        cmd = 'which %s' % tools 
        s = commands.getoutput(cmd)
        pattern = 'no %s in' % tools
        match = re.search(pattern, s)
        if match:
            return 'No'

        return 'Okay'

def __check_package_installed(tools):
    if tools:
        os = __get_platform()
        if os == 'ubuntu':
            cmd = 'dpkg -l | grep %s' % tools         
        else:
            cmd = 'yum list installed | grep %s' % tools         
        s = commands.getoutput(cmd)
        if s.find(tools):        
            return 'Okay'
        return 'NO'

def __check_regutil():
    cwd = os.getcwd()
    regutil = cwd + '/utils/regutil'
    ret = os.path.exists(regutil) 
    if ret is False:
            print 'No regutil utility found!'
    
# Required utilities: dmidecode lspci lscpu smartctl ipmitool cpupower regutil
def check_requirements():
    __check_regutil()

    requirements = ['dmidecode', 'lspci', 'lscpu', 'smartctl', 'ipmitool', 'cpupower']
    centos_packages = {'dmidecode' : 'dmidecode', 'lspci' : 'pciutils', "lscpu" : 'util-linux', 'smartctl' : 'smartmontools', 'ipmitool' : 'ipmitool', 'cpupower' : 'kernel-tools'}
    
    for tool in requirements:
        ret = __check_requirements(tools = tool)
        if ret is 'No':
            print 'Checking for %s FAILED! Please install it and try again!' % tool
            print 'E.g [CentOS/RHEL]:\n\tyum install %s' % centos_packages[tool]
            return 'No'
    return 'Okay'

def help():
    print '\t\thelp     : print out help'
    print '\t\tsystem   : print out System/Base Board/Chassis'
    print '\t\tcpu      : print out Processor'
    print '\t\tmem      : print out Memory'
    print '\t\tbios     : print out BIOS/Firmware'
    print '\t\tplatform : print out Operating System'
    print '\t\tpcie     : print out PCIE'
    print '\t\tdisk     : print out Disk'
    print '\t\tbmc      : print out BMC'
    print '\t\tprint out all if not option'
    
def main():
    ret = check_requirements()
    if ret is 'No':
        return -1
    show = 'system cpu mem bios platform pcie disk bmc'    
    usage = 'Usage: %s help %s' % (sys.argv[0], show)
    print '\t%s\n' % usage
    if len(sys.argv)>1:
        show = ''.join(str(e) for e in sys.argv)        
    
    if 'help' in show:        
        help()
    if 'system' in show:
        print 'System/Base Board/Chassis information:\n' + LINE_BR
        get_sys_base_chasiss_info()
    if 'cpu' in show:
        print '\nProcessor information:\n' + LINE_BR
        get_cpu_info()    
    if 'mem' in show:
        print '\nMemory information:\n' + LINE_BR
        get_ddr_info()
    if 'bios' in show:
        print '\nBIOS/Firmware information:\n' + LINE_BR
        get_bios_fw_info()
    if 'platform' in show:
        print '\nOperating System information:\n' + LINE_BR
        get_os_info()
    if 'pcie' in show:
        print '\nPCIE information:\n' + LINE_BR
        get_pcie_info()
    if 'disk' in show:
        print '\nDisk information:\n' + LINE_BR
        get_disk_info()
    if 'bmc' in show:
        print '\nBMC information:\n' + LINE_BR
        get_bmc_info()    

if __name__ == '__main__':
    main()
