#bmc_ip=10.76.167.128
#bmc_ip=10.76.190.163
#bmc_ip=10.76.206.126
bmc_ip=10.76.190.164
#bmc_ip=10.76.181.122
#bmc_ip=10.76.190.159
#bmc_ip=10.76.211.135

cmd="ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus mc reset cold"
echo $cmd
ipmitool -H ${bmc_ip} -U ADMIN -P ADMIN -I lanplus mc reset cold
