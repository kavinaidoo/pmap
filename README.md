# Portable Modular Audio Player (PMAP)

PMAP is a battery-powered portable audio player built around the "[pHAT](https://www.okdo.com/blog/your-guide-to-hats-and-phats/)" form factor.

---

### Features
* Install script sets up config.txt and enables SPI and I2C.
* Supports AirPlay 2 and Spotify Connect.
* Control screen rotation and brightness, AirPlay 2/Spotify Connect, reboot and shutdown using screen and buttons
* Dynamic battery icon (shows charge level + charge status)
* Settings for backlight, screen rotation and last used renderer persist across reboots.

---


### The Sandwich
(Note, due to updates, UI may be different to the image below:)

![pmap](pmap.jpg)

The basic components are stacked and connected using the 40 pin GPIO:
````
i2s DAC + Screen
------40 Pin GPIO------
Single Board Computer
------40 Pin GPIO------
Battery System
````
and then held securely using standoffs.

---

### Compatible Hardware
i2s DAC + Screen
* Pirate Audio: Headphone Amp for Raspberry Pi -> https://shop.pimoroni.com/products/pirate-audio-headphone-amp

Single Board Computer
* Raspberry Pi Zero 2 W -> https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/

Battery System (Optional)
* Waveshare UPS HAT (C) -> https://www.waveshare.com/wiki/UPS_HAT_(C)

---

### Installation Guide
1. Setup Hardware using "Setup Guide" section here -> https://kavi.sblmnl.co.za/pmap/
2. Flash Raspberry Pi OS Lite (32-bit) to SD Card using Raspberry Pi Imager. Make sure WiFi settings are added and SSH is enabled. (Click ⚙️ to see these options). Hostname will be used as the AirPlay 2 and Spotify Connect device name.
3. [SSH into Pi](https://www.raspberrypi.com/documentation/computers/remote-access.html#secure-shell-from-linux-or-mac-os) and run:
````
curl -sL https://raw.githubusercontent.com/kavinaidoo/pmap/main/install.sh | sudo sh
````
4. At the end of the install, your screen should look similar to the one in the image above.
5. Look at the [User Guide](https://github.com/kavinaidoo/pmap/blob/main/docs/USERGUIDE.md) for more instructions and information.
---

### Icons
Guide [here](https://github.com/kavinaidoo/pmap/blob/main/docs/ICONS.md)

---

### Disclaimer
**This project is in active development. The interface and features may change unexpectedly. Running any software or script is entirely at your own risk!**

---

### Credits
This project would not be possible without the contributors to it's numerous dependencies. A list can be found in [CREDITS](https://github.com/kavinaidoo/pmap/blob/main/docs/CREDITS.md).
