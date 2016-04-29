#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import division
import time
import Adafruit_ADS1x15
import math
import RPi.GPIO as GPIO
import threading

from ThingSpeak import ThingSpeak

# Gain (multiplier) -- keep this 1
GAIN = 2 

# the channel id which is reading the sensor
CHANNEL = 0

# threshold values -- TODO -- convert into grams or ohms
HT = 10000
LT = 1000
ALERT_WT = 50
ALERT_PIN = 27

# resistance values used in the circuit
circuit_resistance = 20000

# max value of ADC
max_adc = 32767

# for periodic sampling
num_observations = 5
sleep_interval = 5 # in seconds

class FSR_ADC():
    def __init__(self):
        # instantiate the ADC library
        self.adc = Adafruit_ADS1x15.ADS1115()

        # for integration with ThingSpeak
        # self.thingSpeak = ThingSpeak()

        # to create an alert on PI
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(ALERT_PIN, GPIO.OUT)

    def __call__(self):
        pass

    def run(self):
        self.read_FSR

    def read_FSR(self):
        print "Starting thread to read FSR..."

        CUR = self.adc.start_adc_comparator(CHANNEL,
                               HT, LT,
                               gain = GAIN,
                               traditional = True,
                               active_low = True,
                               num_readings = 1,
                               latching = True)
        i = 0
        val_array = []

        """
        This is an infinite loop to read the force sensor continuously
        """
        while True:
            cur_value = self.adc.get_last_result()
            cur_force = self.get_force(cur_value)

            if cur_force >= ALERT_WT:
                self.create_alert()
                #self.thingSpeak.update_fsr_channel(cur_force)
                print "Cur force : \t" + str(cur_force)
                #break # REMOVE -- just for testing
                # GPIO.cleanup()

            val_array.append(cur_force)
            
            # Comment this line while actual testing
            print ('Current channel {} value is {} = {} grams; at iteration {}'.format(CHANNEL, cur_value, cur_force, i))

            i += 1

            if i >= num_observations:
                avg_force = float(sum(val_array)) / len(val_array)
                #self.thingSpeak.update_fsr_channel(avg_force)
                print "Average force = " + str(avg_force)
                val_array = []
                i = 0

            # updating the ThingSpeak channel
            time.sleep(sleep_interval)

        self.adc.stop_adc()

    def get_force(self,adc_value):
        cur_resistance = circuit_resistance * adc_value / (max_adc - circuit_resistance)
        cur_force = ((math.log(144000000 / cur_resistance)) * math.log(100))/ math.log(24000)
        return math.pow(cur_force, math.e)

    def create_alert(self):
        GPIO.output(ALERT_PIN, 1)
        # TODO -- update ThingSpeak and withdraw the alert pin signal
        # REMOVE the print and sleep
        # print "Sleeping for 5 seconds because of the ALERT!"
        time.sleep(5)
        GPIO.output(ALERT_PIN, 0)

if __name__== "__main__":
    fsr = FSR_ADC()
    fsr.read_FSR()
