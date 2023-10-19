#!/bin/bash

if ! [ $(id -u) = 0 ]; then
   echo "The script needs to be run as root." >&2
   exit 1
fi

if [ $SUDO_USER ]; then
    real_user=$SUDO_USER
else
    real_user=$(whoami)
fi

echo "\n Welcome to the pmap installation script\n"
echo " Usage of this script is at your own risk\n"
echo " The following will be installed:"
echo " * shairport-sync with AirPlay 2 enabled"
echo " Script will reboot Pi once completed\n"
echo " To stop it from running, press ctrl+c within the next 30 seconds\n"

sleep 30

echo "\n**** Running apt-get update and upgrade ****\n"

apt update
apt upgrade -y

# BEGIN shairport-sync installation
# Install Steps have been replicated from -> https://github.com/mikebrady/shairport-sync/blob/master/BUILD.md

echo "\n**** Installing shairport-sync ****\n"

echo "\n* Installing Requirements *\n"

apt-get -y install --no-install-recommends build-essential git autoconf automake libtool \
    libpopt-dev libconfig-dev libasound2-dev avahi-daemon libavahi-client-dev libssl-dev libsoxr-dev \
    libplist-dev libsodium-dev libavutil-dev libavcodec-dev libavformat-dev uuid-dev libgcrypt-dev xxd


echo "\n* Cloning, making and installing nqptp *\n"

cd /home/$real_user/
git clone https://github.com/mikebrady/nqptp.git
cd /home/$real_user/nqptp
autoreconf -fi
./configure --with-systemd-startup
make
make install

#TODO - remove these lines when switching to manually starting nqptp
echo "\n* Enabling nqptp as a service *\n"
systemctl enable nqptp
systemctl start nqptp


echo "\n* Cloning, making and installing shairport-sync *\n"

cd /home/$real_user/
git clone https://github.com/mikebrady/shairport-sync.git
cd /home/$real_user/shairport-sync
autoreconf -fi
./configure --sysconfdir=/etc --with-alsa \
    --with-soxr --with-avahi --with-ssl=openssl --with-systemd --with-airplay-2
make
make install

#TODO - remove these lines when switching to manually starting shairport-sync
echo "\n* Enabling shairport-sync as a service *\n"
systemctl enable shairport-sync

echo "\n**** Installation of shairport-sync completed ****\n"

# END shairport-sync installation


echo "\n* Rebooting in 30 seconds *\n"
sleep 30

reboot now