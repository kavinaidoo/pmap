#!/usr/bin/env python3

# imports used to interact with UPS HAT
from INA219 import INA219
import time

# imports used to interact with screen
import sys
from PIL import Image       # type: ignore
from PIL import ImageDraw   # type: ignore
from PIL import ImageFont   # type: ignore
import ST7789               # type: ignore


# initialize INA219
ina219 = INA219(addr=0x43)

# setup display
disp = ST7789.ST7789(
    height=240,
    rotation=90,
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000,
    offset_left=0,
    offset_top=0
)

# Initialize display.
disp.begin()

WIDTH = disp.width
HEIGHT = disp.height



def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
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

    print(lv)
    print(curr)
    print(pow)
    print(perc)
    print("")

    
    # Display Battery values
 
    # Clear the display to a red background.
    # Can pass any tuple of red, green, blue values (from 0 to 255 each).
    # Get a PIL Draw object to start drawing on the display buffer.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 0, 0))

    draw = ImageDraw.Draw(img)

    # Load default font.
    font = ImageFont.load_default()

    # Define a function to create rotated text.  Unfortunately PIL doesn't have good
    # native support for rotated fonts, but this function can be used to make a
    # text image and rotate it so it's easy to paste in the buffer.

    
    # Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
    #draw_rotated_text(img, 'Hello World!', (0, 0), 90, font, fill=(255, 255, 255))
    draw_rotated_text(img, lv, (0, 0), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, curr, (0, 15), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, pow, (0, 30), 0, font, fill=(255, 255, 255))
    draw_rotated_text(img, perc, (0, 45), 0, font, fill=(255, 255, 255))

    draw_rotated_text(img, 'it works!', (10, HEIGHT - 10), 0, font, fill=(255, 255, 255))

    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)


    time.sleep(2)