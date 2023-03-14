from grove_rgb_lcd import *
import time,sys, grovepi

# Setting up display:
if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)
# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e
# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# Set display text \n for second line(or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
	
#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    while len(text) < 32: #clears the rest of the screen
        text += ' '
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

    
    
# Setting up Ultrasonic Sensor:
# set I2C to use the hardware bus
grovepi.set_bus("RPI_1")

# Connect the Grove Ultrasonic Ranger to digital port D4
# SIG,NC,VCC,GND
ultrasonic_ranger = 4

# Setting up Rotarty Angle Sensor:
# Connect the Grove Rotary Angle Sensor to analog port A0
# SIG,NC,VCC,GND
potentiometer = 0
grovepi.pinMode(potentiometer,"INPUT")
grovepi.pinMode(ultrasonic_ranger,"OUTPUT")
time.sleep(1)

# Reference voltage of ADC is 5v
adc_ref = 5

# Vcc of the grove interface is normally 5v
grove_vcc = 5

# Full value of the rotary angle is 300 degrees, as per it's specs (0 to 300)
full_angle = 300

while True:
    try:
        # Read sensor value from potentiometer
        # sensor_value = grovepi.analogRead(potentiometer)
        thresh_dist = int(grovepi.analogRead(potentiometer));
        # Calculate voltage
        # voltage = round((float)(sensor_value) * adc_ref / 1023, 2)
        # Calculate rotation in degrees (0 to 300)
        # degrees = round((voltage * full_angle) / grove_vcc, 2)
        # Calculate Distance (0 to 255) from degrees (0 to 300)
        # max_dist = 300
        # thresh_dist = int(degrees / full_angle * max_dist);

        # Read distance value from Ultrasonic
        act_dist = int(grovepi.ultrasonicRead(ultrasonic_ranger))
        
        setRGB(0,128,64)
        
        if(act_dist <= thresh_dist):
          setText_norefresh("%3dcm OBJ PRES \n%3dcm" %(thresh_dist, act_dist))
        else:
          setText_norefresh("%3dcm          \n%3dcm" %(thresh_dist, act_dist))
        
	       
    except Exception as e:
    	print ("Error:{}".format(e))

    time.sleep(0.1) # don't overload the i2c bus 
