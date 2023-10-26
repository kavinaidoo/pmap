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

# import used to send terminal commands
import os

# Global Variables

airplay_status = 1 # on
screen = 1 # home screen
font = ImageFont.truetype("Ubuntu-Regular.ttf", 30)
font_small = ImageFont.truetype("Ubuntu-Regular.ttf", 20)
icons = ImageFont.truetype("pmap_icons.ttf", 30)

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
    global screen

    if screen == 1:
        screen = 5
    elif screen > 1 and screen < 6:
        screen = 1
    elif screen == 5:
        screen = 1

def b_pressed():

    global airplay_status
    global screen

    if screen == 1 and airplay_status == 0:
        os.system('sudo nqptp &')
        os.system('sudo shairport-sync &')
        airplay_status = 1
    elif screen == 1 and airplay_status == 1:
        os.system('sudo pkill nqptp')
        os.system('sudo pkill shairport-sync')
        airplay_status = 0

    if screen == 3:
        screen = 6
        time.sleep(1)
        os.system('sudo shutdown now')

def x_pressed():
    global screen
    if screen == 1:
        screen = 2

    if screen == 3:
        os.system('sudo reboot now')

def y_pressed():
    global screen
    if screen == 1:
        screen = 3

a_but.when_pressed = a_pressed
b_but.when_pressed = b_pressed
x_but.when_pressed = x_pressed
y_but.when_pressed = y_pressed

# Icons
icon_settings = "\uE801"
icon_batt_100 = "\uF240"
icon_batt_75 = "\uF241"
icon_batt_50 = "\uF242"
icon_batt_25 = "\uF243"
icon_batt_0 = "\uF244"
icon_airplay = "\uE814"
icon_power = "\uE810"
icon_left_arrow = "\uE806"
icon_reload = "\uE809"


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

def battery_stats():
    # Getting Battery Values
    bus_voltage = ina219.getBusVoltage_V()             # voltage on V- (load side)
    current = ina219.getCurrent_mA()                   # current in mA
    power = ina219.getPower_W()                        # power in W
    p = (bus_voltage - 3)/1.2*100
    if(p > 100):p = 100
    if(p < 0):p = 0

    # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
    #print("PSU Voltage:   {:6.3f} V".format(bus_voltage + shunt_voltage))
    #print("Shunt Voltage: {:9.6f} V".format(shunt_voltage))

    lv = round(bus_voltage,3)
    curr = round(current/1000,3)
    pow = round(power,3)
    perc = round(p,0)

    return lv,curr,pow,perc

def cpu_temp():
    cpu = CPUTemperature()

    return round(cpu.temperature,2)

def render_screen_1(): # Home Screen
    
    #Getting battery info
    batt = battery_stats()
    curr = batt[1]    
    perc = batt[3]
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 

    # Top Left - Settings Icon
    draw_rotated_text(img, icon_settings, (0, 0), 0, icons, fill=(255, 255, 255))

    # Bottom Left - AirPlay Icon
    if airplay_status == 1:
        draw_rotated_text(img, icon_airplay, (0, 200), 0, icons, fill=(127, 255, 127))
    elif airplay_status == 0:
        draw_rotated_text(img, icon_airplay, (0, 200), 0, icons, fill=(255, 127, 127))
    else:
        draw_rotated_text(img, icon_airplay, (0, 200), 0, icons, fill=(255, 255, 255))

    # Top Right - Battery Icon
    fill_col = (255, 255, 255) #white, default
    if curr > 0: #charging
        fill_col = (127, 255, 127) #green, charging
    elif perc < 10: #not charging, batt < 10%
        fill_col = (255, 127, 127) #red, needs to charge
  
    if perc > 90:
        draw_rotated_text(img, icon_batt_100, (200, 0), 0, icons, fill=fill_col)
    elif perc > 75:
        draw_rotated_text(img, icon_batt_75, (200, 0), 0, icons, fill=fill_col)
    elif perc > 50:
        draw_rotated_text(img, icon_batt_50, (200, 0), 0, icons, fill=fill_col)
    elif perc > 25:
        draw_rotated_text(img, icon_batt_25, (200, 0), 0, icons, fill=fill_col)
    else:
        draw_rotated_text(img, icon_batt_0, (200, 0), 0, icons, fill=fill_col)
    
    # Bottom Right - Power Icon
    draw_rotated_text(img, icon_power, (200, 200), 0, icons, fill=(255, 255, 255))
    
    
    draw_rotated_text(img, "pmap", (120, 120), 0, font, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)    

def render_screen_2(): # Battery Screen
    
    batt = battery_stats()
    
    lv = batt[0]
    curr = batt[1]    
    pow = batt[2]
    perc = batt[3]

    lv_text = "Load Voltage:  {:6.3f} V".format(lv)
    curr_text = "Current:       {:6.3f} A".format(curr)
    pow_text = "Power:         {:6.3f} W".format(pow)
    perc_text = "Percent:       {:3.1f}%".format(perc)
    temp_text = "CPU Temp:     "+str(cpu_temp())
    
    # Print values to terminal
    print(lv_text)
    print(curr_text)
    print(pow_text)
    print(perc_text)
    print(temp_text)
    print("")
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 

    # Top left - Back Icon
    draw_rotated_text(img, icon_left_arrow, (0, 0), 0, icons, fill=(255, 255, 255))

    draw_rotated_text(img, "Battery", (40, 0), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, lv_text, (10, 50), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, curr_text, (10, 70), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, pow_text, (10, 90), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, perc_text, (10, 110), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_screen_3(): # Power Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 

    # Top left - Back Icon
    draw_rotated_text(img, icon_left_arrow, (0, 0), 0, icons, fill=(255, 255, 255))

    draw_rotated_text(img, "Power", (40, 0), 0, font, fill=(255, 255, 255))

    # Bottom Left - Shutdown Icon
    draw_rotated_text(img, icon_power, (0, 200), 0, icons, fill=(255, 127, 127))

    # Top Right - Reboot Icon
    fill_col = (255, 255, 255) #white, default
    draw_rotated_text(img, icon_reload, (200, 0), 0, icons, fill=fill_col)


    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_screen_5(): # Settings Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    temp_text = "CPU Temp:     "+str(cpu_temp())+"°C"

    # Refer to global font variables
    global font 
    global icons 

    # Top left - Back Icon
    draw_rotated_text(img, icon_left_arrow, (0, 0), 0, icons, fill=(255, 255, 255))

    draw_rotated_text(img, "Settings", (40, 0), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, "No Settings yet :)", (10, 50), 0, font_small, fill=(255, 255, 255))

    draw_rotated_text(img, temp_text, (10, 90), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_screen_6(): # Shutdown Complete Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 

    draw_rotated_text(img, "Shutting down", (40, 0), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, "Wait for RPi status light", (10, 50), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, "to turn off before", (10, 70), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, "switching off power", (10, 90), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)


while True:

    match screen: # type: ignore
        case 1:
            render_screen_1()
        case 2:
            render_screen_2()
        case 3:
            render_screen_3()
        case 5:
            render_screen_5()
        case 6:
            render_screen_6()
        case _:
            ...

    time.sleep(2)