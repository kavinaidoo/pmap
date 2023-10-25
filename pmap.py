#!/usr/bin/env python3

# Credits
# ST7789-related code based on https://github.com/pimoroni/st7789-python/blob/master/examples/shapes.py
# INA219-related code based on INA219.py

# imports used to interact with UPS HAT
from INA219 import INA219
import time

# imports used to interact with screen
import sys
from PIL import Image       # type: ignore
from PIL import ImageDraw   # type: ignore
from PIL import ImageFont   # type: ignore
import ST7789               # type: ignore


# imports used for buttons + temperature sensing
from gpiozero import Button # type: ignore
from gpiozero import CPUTemperature # type: ignore
from gpiozero import PWMLED # type: ignore

import os

# global vars

airplay_status_text = ""

# initialize INA219
ina219 = INA219(addr=0x43)

# setup display
disp = ST7789.ST7789(
    height=240,
    rotation=90,
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    dc=9,
    #backlight=13,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000,
    offset_left=0,
    offset_top=0
)

# Initialize display
disp.begin()

WIDTH = disp.width
HEIGHT = disp.height

# Initialize backlight
backlight = PWMLED(13)
backlight.value = 0.1

# Initialize buttons + button functions
a_but = Button(5)
b_but = Button(6)
x_but = Button(16)
y_but = Button(24)


def a_pressed():
    os.system('sudo nqptp &')
    os.system('sudo shairport-sync &')
    global airplay_status_text
    airplay_status_text = "AirPlay Enabled"

def b_pressed():
    os.system('sudo pkill nqptp')
    os.system('sudo pkill shairport-sync')
    global airplay_status_text
    airplay_status_text = "AirPlay Disabled"

def x_pressed():
    os.system('sudo reboot now')

def y_pressed():
    os.system('sudo shutdown now')

a_but.when_pressed = a_pressed
b_but.when_pressed = b_pressed
x_but.when_pressed = x_pressed
y_but.when_pressed = y_pressed


def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    box_size = draw.textbbox((0, 0),text, font=font)
    width, height = box_size[2], box_size[3]
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)



while True:

    # Getting Battery Values
    bus_voltage = ina219.getBusVoltage_V()             # voltage on V- (load side)
    shunt_voltage = ina219.getShuntVoltage_mV() / 1000 # voltage between V+ and V- across the shunt
    current = ina219.getCurrent_mA()                   # current in mA
    power = ina219.getPower_W()                        # power in W
    p = (bus_voltage - 3)/1.2*100
    if(p > 100):p = 100
    if(p < 0):p = 0

    # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
    #print("PSU Voltage:   {:6.3f} V".format(bus_voltage + shunt_voltage))
    #print("Shunt Voltage: {:9.6f} V".format(shunt_voltage))

    lv = "Load Voltage:  {:6.3f} V".format(bus_voltage)
    curr = "Current:       {:6.3f} A".format(current/1000)
    pow = "Power:         {:6.3f} W".format(power)
    perc = "Percent:       {:3.1f}%".format(p)

    # Print values to terminal
    print(lv)
    print(curr)
    print(pow)
    print(perc)
    print("")

    cpu = CPUTemperature()

    cpu_temp = "CPU Temp:     "+str(cpu.temperature)

    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load Fonts
    font = ImageFont.truetype("Ubuntu-Regular.ttf", 15)
    icons = ImageFont.truetype("pmap_icons.ttf", 30)

    draw_rotated_text(img, lv, (0, 0), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, curr, (0, 20), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, pow, (0, 40), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, perc, (0, 60), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, cpu_temp, (0, 100), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, airplay_status_text, (0, 160), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, "\uF240 \uF1BC \uE814 \uF2C7", (0, 120), 0, icons, fill=(255, 255, 255))


    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)


    time.sleep(2)