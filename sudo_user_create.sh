#!/bin/bash

# Syntax: sudo_user_create.sh <username>

# Assume you have super user privilege
USR=$1

if [ "$USR" = "" ]; then
  echo -e "\tERROR: No username specified!"
  echo -e "\tSyntax: sudo_user_create.sh <username>"
  exit 1
fi

useradd $USR -d /home/$USR
echo "User $USR is created"
echo "Select a password:"
passwd $USR

echo "Granting $USR sudo"
usermod -aG wheel $USR
echo "Done!"

echo "Checking login with new username ..."
su $USR -c "whoami"
su $USR -c "groups"
su $USR -c "id"

