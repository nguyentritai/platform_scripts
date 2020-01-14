bmc_ip=$1


ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus chassis power on 

