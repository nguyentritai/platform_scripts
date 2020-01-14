#!/bin/bash

bmc_ip=$1
bios_file=bios_capsule.hpm

cmd="ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus raw 0x3c 0x0b 0x01"
echo $cmd
eval $cmd
cmd="ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus -z 0x7fff hpm upgrade ${bios_file} component 2"
echo $cmd
eval $cmd

