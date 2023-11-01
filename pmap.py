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

# import used to send terminal commands + get hostname
import os

# import used to interact with settings
import json

# Global Variables
battery_status = 1 #battery present
rotation_icon_angle = 0
screen = "home" # home screen
font = ImageFont.truetype("/home/pi/pmap/Ubuntu-Regular.ttf", 30)
font_small = ImageFont.truetype("/home/pi/pmap/Ubuntu-Regular.ttf", 20)
icons = ImageFont.truetype("/home/pi/pmap/pmap_icons.ttf", 30)
icons_large = ImageFont.truetype("/home/pi/pmap/pmap_icons.ttf", 60)
hostname = os.uname()[1]

# Read settings with error handling
try: 
    with open('/home/pi/pmap/config.json', 'r') as f:
        config = json.load(f)
        screen_rotation = config['screen_rotation']
        backlight_brightness_percentage = config['backlight_brightness_percentage']
        startup_renderer = config['startup_renderer']

except: #catch all errors, whether it's related to opening the file or reading keys
    config = { #create a default config to be used in this session
        "screen_rotation": 90,
        "backlight_brightness_percentage": 10,
        "startup_renderer":"airplay"
    }
    with open('/home/pi/pmap/config.json', 'w') as f: #write default config to file
        json.dump(config, f)
        f.close()

screen_rotation = config['screen_rotation']
backlight_brightness_percentage = config['backlight_brightness_percentage']
startup_renderer = config['startup_renderer']

renderer = startup_renderer

# starting the correct renderer on startup
if renderer == "airplay":
    os.system('sudo nqptp &')
    os.system('sudo shairport-sync &')
elif renderer == "spotify":
    os.system('librespot --disable-audio-cache --disable-credential-cache -q -n "'+hostname+'" --device-type "audiodongle" -b 320 --initial-volume 20 --enable-volume-normalisation --autoplay &')

# initialize INA219
try:
    ina219 = INA219(addr=0x43)
except:
    battery_status = 0 #if battery can't be initialized, this var disables all battery stats/references

# setup display
disp = ST7789.ST7789(
    height=240,
    rotation=screen_rotation,
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
backlight.value = backlight_brightness_percentage/100

# Initialize buttons + button functions

if screen_rotation == 0:     # Maps buttons to pins depending on rotation
    a_map,b_map,x_map,y_map = 16,5,24,6 
elif screen_rotation == 90:
    a_map,b_map,x_map,y_map = 5,6,16,24 # Default config is a 90 degree screen rotation
elif screen_rotation == 180:
    a_map,b_map,x_map,y_map = 6,24,5,16
elif screen_rotation == 270:
    a_map,b_map,x_map,y_map = 24,16,6,5

a_but = Button(a_map) # top left button
b_but = Button(b_map) # bottom left button
x_but = Button(x_map) # top right button
y_but = Button(y_map) # bottom right button

def a_pressed():
    global screen

    if screen == "home":
        screen = "rotation"
    else:
        screen = "home"

def b_pressed():

    global screen
    global config
    global renderer

    if screen == "home" and renderer == "spotify":
        os.system('sudo pkill librespot')
        os.system('sudo nqptp &')
        os.system('sudo shairport-sync &')
        renderer = "airplay"
    elif screen == "home" and renderer == "airplay":
        os.system('sudo pkill nqptp')
        os.system('sudo pkill shairport-sync')
        os.system('librespot --disable-audio-cache --disable-credential-cache -q -n "headphones" --device-type "audiodongle" -b 320 --initial-volume 20 --enable-volume-normalisation --autoplay &')
        renderer = "spotify"
    elif screen == "power":
        screen = "shutdown"
        config['startup_renderer'] = renderer
        with open('/home/pi/pmap/config.json', 'w') as f: #write config to file
            json.dump(config, f)
            f.close()
        time.sleep(1)
        os.system('sudo shutdown now')
    elif screen == "rotation":
        screen = "brightness"
    elif screen == "brightness":
        screen = "temperature"
    elif screen == "temperature":
        screen = "rotation"

def x_pressed():
    global screen
    global rotation_icon_angle
    global screen_rotation
    global backlight_brightness_percentage
    global config

    if screen == "home":
        screen = "power"
    elif screen == "rotation":

        screen_rotation = screen_rotation + rotation_icon_angle
        screen_rotation = screen_rotation%360

        config['screen_rotation'] = screen_rotation
        with open('/home/pi/pmap/config.json', 'w') as f: #write default config to file
            json.dump(config, f)
            f.close()
        screen = "restart"
        time.sleep(2)
        os.system('sudo reboot now')
    elif screen == "brightness":

        if backlight_brightness_percentage < 10: backlight_brightness_percentage = 10
        elif backlight_brightness_percentage > 100: backlight_brightness_percentage = 100

        config['backlight_brightness_percentage'] = backlight_brightness_percentage
        with open('/home/pi/pmap/config.json', 'w') as f: #write default config to file
            json.dump(config, f)
            f.close()
        screen = "home"
        
def y_pressed():
    global screen
    global rotation_icon_angle
    global backlight_brightness_percentage
    global renderer

    if screen == "power":
        screen = "restart"
        config['startup_renderer'] = renderer
        with open('/home/pi/pmap/config.json', 'w') as f: #write config to file
            json.dump(config, f)
            f.close()
        time.sleep(2)
        os.system('sudo reboot now')
    elif screen == "rotation":
        rotation_icon_angle = rotation_icon_angle + 90
    elif screen == "brightness":
        backlight_brightness_percentage = backlight_brightness_percentage + 10


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
icon_spotify = "\uF1BC"
icon_power = "\uE810"
icon_plug = "\uF1E6"
icon_left_arrow = "\uE806"
icon_right_arrow = "\uE807"
icon_down_arrow = "\uE805"
icon_reload = "\uE809"
icon_tick = "\uE813"
icon_music_note = "\uE800"


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

def render_home(): # Home Screen
    global renderer

    #Getting battery info
    if battery_status:
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

    # Bottom Left - Renderer Icon
    if renderer == "airplay":
        draw_rotated_text(img, icon_airplay, (0, 200), 0, icons, fill=(255, 255, 255))
    elif renderer == "spotify":
        draw_rotated_text(img, icon_spotify, (0, 200), 0, icons, fill=(255, 255, 255))

    if battery_status:
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
    else:
        draw_rotated_text(img, icon_plug, (200, 0), 0, icons, fill=(255, 255, 255))
    
    draw_rotated_text(img, "pmap", (80, 100), 0, font, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)    

def render_power(): # Power Screen
    
    if battery_status:
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
    
    '''
    # Print values to terminal
    print(lv_text)
    print(curr_text)
    print(pow_text)
    print(perc_text)
    print(temp_text)
    print("")
    '''
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 

    # Top left - Back Icon
    draw_rotated_text(img, icon_left_arrow, (0, 0), 0, icons, fill=(255, 255, 255))

    # Bottom Left - Shutdown Icon
    draw_rotated_text(img, icon_power, (0, 200), 0, icons, fill=(255, 127, 127))

    # Bottom Right - Reboot Icon
    fill_col = (255, 255, 255) #white, default
    draw_rotated_text(img, icon_reload, (200, 200), 0, icons, fill=(255, 255, 255))

    draw_rotated_text(img, "Power", (40, 0), 0, font, fill=(255, 255, 255))

    if battery_status:
        #Battery Stats
        draw_rotated_text(img, lv_text, (10, 50), 0, font_small, fill=(255, 255, 255))
        draw_rotated_text(img, curr_text, (10, 70), 0, font_small, fill=(255, 255, 255))
        draw_rotated_text(img, pow_text, (10, 90), 0, font_small, fill=(255, 255, 255))
        draw_rotated_text(img, perc_text, (10, 110), 0, font_small, fill=(255, 255, 255))
    else:
        draw_rotated_text(img,"Battery not found", (10, 50), 0, font_small, fill=(255, 255, 255))


    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_settings_temperature(): # Temperature Settings Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    temp_text = "CPU Temp:     "+str(cpu_temp())+"°C"

    # Refer to global font variables
    global font 
    global icons 

    # Top left - Back Icon
    draw_rotated_text(img, icon_left_arrow, (0, 0), 0, icons, fill=(255, 255, 255))
    # Bottom Left - Down Icon
    draw_rotated_text(img, icon_down_arrow, (0, 200), 0, icons, fill=(255, 255, 255))

    draw_rotated_text(img, "Temperature", (40, 0), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, temp_text, (10, 90), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_shutdown(): # Shutdown Complete Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 

    draw_rotated_text(img, "Shutting down", (0, 0), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, "Wait for RPi status light", (10, 50), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, "to turn off before", (10, 70), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, "switching off power", (10, 90), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_restart(): # Restart Complete Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 

    draw_rotated_text(img, "Restarting", (0, 0), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, "pmap will return after", (10, 50), 0, font_small, fill=(255, 255, 255))
    draw_rotated_text(img, "a short break...", (10, 70), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_settings_rotation(): # Rotation Settings Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 
    global rotation_icon_angle


    # Top left - Back Icon
    draw_rotated_text(img, icon_left_arrow, (0, 0), 0, icons, fill=(255, 255, 255))
    # Top Right - Tick Icon
    draw_rotated_text(img, icon_tick, (200, 0), 0, icons, fill=(255, 255, 255))
    # Bottom Left - Down Icon
    draw_rotated_text(img, icon_down_arrow, (0, 200), 0, icons, fill=(255, 255, 255))
    # Bottom Right - Right Icon
    draw_rotated_text(img, icon_right_arrow, (200, 200), 0, icons, fill=(255, 255, 255))

    draw_rotated_text(img, "Rotation", (40, 0), 0, font, fill=(255, 255, 255))

    
    if rotation_icon_angle > 359: #stops angle from multiple rotations
        rotation_icon_angle = 0
    
    draw_rotated_text(img, icon_music_note, (90, 90), rotation_icon_angle, icons_large, fill=(255, 255, 255))

    #draw_rotated_text(img, temp_text, (10, 90), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

def render_settings_brightness(): # Brightness Settings Screen
    
    # Clear the display to a black background.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Refer to global font variables
    global font 
    global icons 
    global backlight
    global backlight_brightness_percentage


    # Top left - Back Icon
    draw_rotated_text(img, icon_left_arrow, (0, 0), 0, icons, fill=(255, 255, 255))
    # Top Right - Tick Icon
    draw_rotated_text(img, icon_tick, (200, 0), 0, icons, fill=(255, 255, 255))
    # Bottom Left - Down Icon
    draw_rotated_text(img, icon_down_arrow, (0, 200), 0, icons, fill=(255, 255, 255))
    # Bottom Right - Right Icon
    draw_rotated_text(img, icon_right_arrow, (200, 200), 0, icons, fill=(255, 255, 255))

    draw_rotated_text(img, "Brightness", (40, 0), 0, font, fill=(255, 255, 255))

    if backlight_brightness_percentage > 100: #stops > 100
        backlight_brightness_percentage = 10
    
    draw_rotated_text(img, str(backlight_brightness_percentage)+"%", (90, 90), 0, font, fill=(255, 255, 255))

    backlight.value = backlight_brightness_percentage/100


    #draw_rotated_text(img, temp_text, (10, 90), 0, font_small, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

while True:
    
    match screen: # type: ignore
        case "home":
            render_home()   # Home Screen
        case "power":
            render_power()   # Power Screen
        case "rotation":
            render_settings_rotation()   # Rotation Settings Screen
        case "temperature":
            render_settings_temperature()   # Temperature Settings Screen
        case "brightness":
            render_settings_brightness()   # Brightness Settings Screen
        case "shutdown":
            render_shutdown()   # Shutdown Complete Screen
        case "restart":
            render_restart()   # Restart Complete Screen
 
        case _:
            ...

    time.sleep(0.25)   #base refresh rate (4fps)