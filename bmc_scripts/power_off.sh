#!/bin/bash
bmc_ip=$1

cmd="ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus chassis power off"
echo $cmd
eval $cmd

