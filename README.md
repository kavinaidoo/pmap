# Portable Modular Audio Player (PMAP)

PMAP is a battery-powered portable audio player built around the "[pHAT](https://www.okdo.com/blog/your-guide-to-hats-and-phats/)" form factor.

---


### Features
* Supports AirPlay 2 using [shairport-sync](https://github.com/mikebrady/shairport-sync)

---


### The Sandwich
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

Battery System
* Waveshare UPS HAT (C) -> https://www.waveshare.com/wiki/UPS_HAT_(C)

---

### Installation Guide
1. Setup Hardware and moOde using guide here -> https://kavi.sblmnl.co.za/pidap/
    * Important: The guides Flash image_2023-09-05-moode-r836-arm64-lite.zip from https://github.com/moode-player/moode/releases/tag/r836prod to your SD card as this ensures compatibility
2. Flash to SD Card using Raspberry Pi Imager. Make sure WiFi settings are added and SSH is enabled (Click ⚙️ to see these options)
3. SSH into Pi and run 
````
curl -sL https://raw.githubusercontent.com/kavinaidoo/pmap/main/install.sh | sudo sh
````
---

### Project Breakdown
* install.sh - Installs pmap and all supporting software (eg. shairport-sync)
* pmap.py - Code that runs the screen, GPIO etc.

---
### Disclaimer
**This project is in active development. Files may change, features may change, run the install script at your own risk!**