#!/bin/bash

for ((i=1;i<=100;i++))
	do echo $i
	. ./reset.sh
	sleep 15
done
