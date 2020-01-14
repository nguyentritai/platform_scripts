#!/bin/bash

bmc_ip=$1
smpro_file=smpmpro_capsule.hpm

ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus raw 0x3c 0x0b 0x01
ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus -z 0x7fff hpm upgrade ${smpro_file}

