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

echo "\n Welcome to the \033[0;36mpmap\033[0m installation script\n"
echo " Usage of this script is at your own risk\n"
echo " Designed for Raspberry Pi OS Lite (32-bit Bookworm) on Pi Zero 2 W\n"
echo " \033[1;31mDo not\033[0m make any changes to config.txt before running this script\n"
echo " The following will be set up:"
echo " * I2S, SPI and config.txt\n"
echo " The following will be installed:"
echo " * shairport-sync enabling AirPlay 2"
echo " * raspotify enabling Spotify Connect"
echo " * pmap enabling button and screen control\n"
echo " Script will reboot Pi once completed\n"
echo " To stop it from running, press ctrl+c within the next 30 seconds\n"

sleep 30

echo "\033[0;36m\n**** Running apt-get update and upgrade ****\033[0m\n"

apt-get update
apt-get upgrade -y

# BEGIN enable i2c and spi and modifying config.txt ****************************************************

echo "\033[0;36m\n**** Enabling SPI and I2C using raspi-config ****\033[0m\n"

raspi-config nonint do_spi 0
raspi-config nonint do_i2c 0

echo "\033[0;36m\n**** Adding lines to config.txt to recognize Pirate Audio pHAT ****\033[0m\n"

echo "dtoverlay=hifiberry-dac" >> /boot/config.txt
echo "gpio=25=op,dh" >> /boot/config.txt

# END enable i2c and spi and modifying config.txt ****************************************************

# BEGIN shairport-sync installation ****************************************************
# Install Steps have been replicated from -> https://github.com/mikebrady/shairport-sync/blob/master/BUILD.md

echo "\033[0;36m\n**** Installing shairport-sync ****\033[0m\n"

echo "\033[0;36m\n* Installing Requirements *\033[0m\n"

apt-get -y install --no-install-recommends build-essential git autoconf automake libtool \
    libpopt-dev libconfig-dev libasound2-dev avahi-daemon libavahi-client-dev libssl-dev libsoxr-dev \
    libplist-dev libsodium-dev libavutil-dev libavcodec-dev libavformat-dev uuid-dev libgcrypt-dev xxd

echo "\033[0;36m\n* Cloning, making and installing nqptp *\033[0m\n"

cd /home/$real_user/
git clone https://github.com/mikebrady/nqptp.git
cd /home/$real_user/nqptp
autoreconf -fi
./configure --with-systemd-startup
make
make install

echo "\033[0;36m\n* Cloning, making and installing shairport-sync *\033[0m\n"

cd /home/$real_user/
git clone https://github.com/mikebrady/shairport-sync.git
cd /home/$real_user/shairport-sync
autoreconf -fi
./configure --sysconfdir=/etc --with-alsa \
    --with-soxr --with-avahi --with-ssl=openssl --with-systemd --with-airplay-2
make
make install

echo "\033[0;36m\n**** Installation of shairport-sync completed ****\033[0m\n"

# END shairport-sync installation ****************************************************

# BEGIN raspotify installation ****************************************************

echo "\033[0;36m\n**** Installing raspotify ****\033[0m\n"

curl -sL https://dtcooper.github.io/raspotify/install.sh | sh

# disabling raspotify as a service. librespot will be called by user action

systemctl disable raspotify.service

# END raspotify installation ****************************************************

# BEGIN pmap installation ****************************************************

echo "\033[0;36m\n**** Installing dependencies and downloading pmap ****\033[0m\n"

# required for INA219.py
apt-get -y install python3-smbus
# required for st7789
apt-get -y install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy
# required for pmap.py
apt-get -y install python3-gpiozero

pip3 install st7789 --break-system-packages

sudo -u "$real_user" bash <<EOF #run the following commands as $real_user https://unix.stackexchange.com/a/231986

cd /home/$real_user/
mkdir pmap
cd pmap

curl -O https://raw.githubusercontent.com/kavinaidoo/pmap/dev/pmap/INA219.py
curl -O https://raw.githubusercontent.com/kavinaidoo/pmap/dev/pmap/pmap.py
curl -O https://raw.githubusercontent.com/kavinaidoo/pmap/dev/pmap/config.json

sed -i 's|/home/pi|/home/$real_user|g' pmap.py

#installating ubuntu font

cd /home/$real_user/pmap

curl -OSL https://github.com/google/fonts/raw/main/ufl/ubuntu/Ubuntu-Regular.ttf

mkdir ubuntu_font_license_etc
cd /home/$real_user/pmap/ubuntu_font_license_etc

curl -O https://raw.githubusercontent.com/google/fonts/main/ufl/ubuntu/COPYRIGHT.txt
curl -O https://raw.githubusercontent.com/google/fonts/main/ufl/ubuntu/TRADEMARKS.txt
curl -O https://raw.githubusercontent.com/google/fonts/main/ufl/ubuntu/UFL.txt

#installating pmap_icons font

cd /home/$real_user/pmap

curl -O https://raw.githubusercontent.com/kavinaidoo/pmap/dev/pmap/pmap_icons.ttf
mkdir pmap_icons_license_etc
cd /home/$real_user/pmap/pmap_icons_license_etc

curl -O https://raw.githubusercontent.com/kavinaidoo/pmap/main/pmap_icons_license_etc/LICENSE.txt
curl -O https://raw.githubusercontent.com/kavinaidoo/pmap/main/pmap_icons_license_etc/README.txt

# End
EOF

echo "\033[0;36m\n**** Installating dependencies and downloading pmap completed ****\033[0m\n"

# END pmap installation ****************************************************

# START setting up pmap as a service ****************************************************

echo "\033[0;36m\n**** Setting up pmap as a service ****\033[0m\n"

cd /etc/systemd/system/
curl -O https://raw.githubusercontent.com/kavinaidoo/pmap/dev/pmap/pmap.service

sed -i "s|/home/pi|/home/$real_user|g" pmap.service # https://askubuntu.com/questions/76808/how-do-i-use-variables-in-a-sed-command
sed -i "s|User=pi|User=$real_user|g" pmap.service

systemctl daemon-reload
systemctl enable pmap.service

echo "\033[0;36m\n**** Setting up pmap as a service completed ****\033[0m\n"

# END setting up pmap as a service ****************************************************

echo "\033[0;36m\n* Rebooting in 30 seconds *\033[0m\n"
sleep 30

reboot now