'''
A library that allows simple access to 74HC595 shift registers connected to the FT232H breakout board.
'''

# Import GPIO and FT232H modules.
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
from time import sleep

# Temporarily disable the built-in FTDI serial driver on Mac & Linux platforms.
FT232H.use_FT232H()

# Create an FT232H object that grabs the first available FT232H device found.
ft232h = FT232H.FT232H()

version = "0.2ft"
version_info = (0, 2, 'ft')

# Define MODES
ALL  = -1
HIGH = 1
LOW  = 0

# Define pins
_SER_pin   = 8    #pin C0 on the FT232H
_RCLK_pin  = 9    #pin C1 on the FT232H
_SRCLK_pin = 10   #pin C2 on the FT232H

# is used to store states of all pins
_registers = list()

#How many of the shift registers - you can change them with shiftRegisters method
_number_of_shiftregisters = 1

def pinsSetup(**kwargs):
    '''
    Allows the user to define custom pins
    '''
    global _SER_pin, _RCLK_pin, _SRCLK_pin

    custompins = 0
    serpin = _SER_pin
    rclkpin = _RCLK_pin
    srclkpin = _SRCLK_pin

    if len(kwargs) > 0:
        custompins = 1

        _SER_pin = kwargs.get('ser', _SER_pin)
        _RCLK_pin = kwargs.get('rclk', _RCLK_pin)
        _SRCLK_pin = kwargs.get('srclk', _SRCLK_pin)

#    if custompins:
#        if _SER_pin != serpin or _RCLK_pin != rclkpin or _SRCLK_pin != srclkpin:
#            GPIO.setwarnings(True)
#    else:
#        GPIO.setwarnings(False)

    ft232h.setup(_SER_pin, GPIO.OUT)
    ft232h.setup(_RCLK_pin, GPIO.OUT)
    ft232h.setup(_SRCLK_pin, GPIO.OUT)

def startupMode(mode, execute = False):
    '''
    Allows the user to change the default state of the shift registers outputs
    '''
    if isinstance(mode, int):
        if mode is HIGH or mode is LOW:
            _all(mode, execute)
        else:
            raise ValueError("The mode can be only HIGH or LOW or Dictionary with specific pins and modes")
    elif isinstance(mode, dict):
        for pin, mode in mode.iteritems():
            _setPin(pin, mode)
        if execute:
            _execute()
    else:
        raise ValueError("The mode can be only HIGH or LOW or Dictionary with specific pins and modes")


def shiftRegisters(num):
    '''
    Allows the user to define the number of shift registers are connected
    '''
    global _number_of_shiftregisters
    _number_of_shiftregisters = num
    _all(LOW)

def digitalWrite(pin, mode):
    '''
    Allows the user to set the state of a pin on the shift register
    '''
    if pin == ALL:
        _all(mode)
    else:
        if len(_registers) == 0:
            _all(LOW)

        _setPin(pin, mode)
    _execute()

def digitalWrite8(registernum, data):
	'''
	Set 8 pins (bits) in one operation
	Value of variable registernum should range from 1 to _number_of_shiftregisters
	'''
	if registernum > _number_of_shiftregisters:
		raise ValueError("The registernum can be less than or equal to the number of shiftregisters")
	fromPin = (registernum - 1) * 8
	bitPattern = map(int, list("{0:0>8b}".format(data & 0xFF))[::-1])
#	print "data=",data, bitPattern[::-1]
	for idx, mode in enumerate(bitPattern):
#		print "pin=",fromPin + idx, "mode=", mode
		if mode == HIGH:
			_setPin(fromPin + idx, HIGH)
#			print "_setPin(", fromPin + idx, ",", HIGH, ")"
		else:
			_setPin(fromPin + idx, LOW)
#			print "_setPin(", fromPin + idx, ",", LOW, ")"
	_execute()

def delay(millis):
    '''
    Used for creating a delay between commands
    '''
    millis_to_seconds = float(millis)/1000
    return sleep(millis_to_seconds)

def _all_pins():
    return _number_of_shiftregisters * 8

def _all(mode, execute = True):
    all_shr = _all_pins()

    for pin in range(0, all_shr):
        _setPin(pin, mode)
    if execute:
        _execute()

    return _registers

def _setPin(pin, mode):
    try:
        _registers[pin] = mode
    except IndexError:
        _registers.insert(pin, mode)

def _execute():
    all_pins = _all_pins()
    ft232h.output(_RCLK_pin, GPIO.LOW)

    for pin in range(all_pins -1, -1, -1):
        ft232h.output(_SRCLK_pin, GPIO.LOW)

        pin_mode = _registers[pin]

        ft232h.output(_SER_pin, pin_mode)
        ft232h.output(_SRCLK_pin, GPIO.HIGH)

    ft232h.output(_RCLK_pin, GPIO.HIGH)

pinsSetup()
