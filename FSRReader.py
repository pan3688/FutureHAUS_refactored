#!/usr/bin/python

from __future__ import division
import time
import Adafruit_ADS1x15
import math

from ThingSpeak import ThingSpeak

adc = Adafruit_ADS1x15.ADS1115()

# Gain (multiplier) -- keep this 1
GAIN = 2 

# the channel id which is reading the sensor
CHANNEL = 0

# threshold values -- TODO -- convert into grams or ohms
HT = 10000
LT = 1000

# resistance values used in the circuit
circuit_resistance = 20000

# max value of ADC
max_adc = 32767

CUR = adc.start_adc_comparator(CHANNEL,
                               HT, LT,
                               gain = GAIN,
                               traditional = True,
                               active_low = True,
                               num_readings = 1,
                               latching = True)

i = 0
# integration with ThingSpeak
thingSpeak = ThingSpeak()

def get_force(adc_value):
    cur_resistance = circuit_resistance * cur_value / (max_adc - circuit_resistance)
    cur_force = ((math.log(144000000 / cur_resistance)) * math.log(100))/ math.log(24000)
    return math.pow(cur_force, math.e)

while True:
    cur_value = adc.get_last_result()
    cur_force = get_force(cur_value)

    print ('Current channel {} value is {} = {} grams; at iteration {}'.format(CHANNEL, cur_value, cur_force, i))
    i += 1
    if i > 5:
        break

    # updating the ThingSpeak channel
    print thingSpeak.update_fsr_channel(cur_force)

    time.sleep(4)

adc.stop_adc()
