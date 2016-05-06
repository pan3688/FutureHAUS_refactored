#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import division
import time
import Adafruit_ADS1x15
import math
import RPi.GPIO as GPIO
import threading

from ThingSpeak import ThingSpeak
import logging

# Gain (multiplier) -- keep this 1
GAIN = 2 

# the channel id which is reading the sensor value
CHANNEL = 0

# threshold values
HT = 10000
LT = 1000
ALERT_PIN = 27

# max value of ADC
max_adc = 32767

class FSR_ADC():
    def __init__(self, configmap):
        # instantiate the ADC library
        self.adc = Adafruit_ADS1x15.ADS1115()

        # for integration with ThingSpeak
        self.thingSpeak = ThingSpeak()

        # to create an alert on PI
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(ALERT_PIN, GPIO.OUT)

        self.config = configmap

        # for periodic sampling
        self.sleep_interval = int(configmap.get("ForceSensor","sleep_interval"))
        self.reader_sleep = int(configmap.get("ForceSensor","reader_interval"))

        # resistance values used in the circuit
        self.circuit_resistance = int(configmap.get("ForceSensor","cicuit_resistance")) #ohms

        self.hostname = configmap.get("ThingSpeak","hostname")
        self.readAPIKey = configmap.get("ThingSpeak","readAPIKey")
        self.writeAPIKey = configmap.get("ThingSpeak","writeAPIKey")
        self.upstream = configmap.get("ThingSpeak", "FSR_upstream_channel")
        self.downstream = configmap.get("ThingSpeak", "FSR_command_channel")
        self.read_channelID = configmap.get("ThingSpeak", "FSR_read_channelID")

        self.lock = threading.Lock()
        self.raw = False
        self.threshold = 20
        self.periodic = True

    def read_FSR(self):
        logging.info(threading.current_thread().name  + " reading FSR")

        try:
            CUR = self.adc.start_adc_comparator(CHANNEL,
                               HT, LT,
                               gain = GAIN,
                               traditional = True,
                               active_low = True,
                               num_readings = 1,
                               latching = True)
        except e as Exception:
            logging.critical("Error while reading sensor value")

        """
        This is an infinite loop to read the force sensor continuously
        """
        while True:
            cur_value = self.adc.get_last_result()

            cur_force = cur_value

            self.lock.acquire(True)

            cur_periodic = self.periodic
            if not self.raw:
                cur_force = self.get_force(cur_value)

            if cur_force >= self.threshold:
                #self.create_alert()
                self.update_fsr_channel(cur_force)
                logging.debug("Cur force : \t" + str(cur_force))

            self.lock.release()

            # Comment this line while actual testing
            logging.debug("Current channel " + str(CHANNEL) + " value is : " + str (cur_value))

            # updating the ThingSpeak channel
            if self.periodic:
                self.update_fsr_channel(cur_force)

            #Blocking call, if command reader is updating sleep interval
            self.lock.acquire(True)
            # meanwhile, the command reader thread won't be able to update sleep_interval
            self.lock.release()

            try:
                # sleeping before reading the sensor again
                time.sleep(self.sleep_interval)
            except Exception as e:
                logging.error(threading.current_thread().name + " sleep exception.")

        logging.debug("Stopping ADC")
        self.adc.stop_adc()

    def update_fsr_channel(self,cur_value):
        logging.debug("Updating the thingSpeak upstream with :" + str(cur_value))
        self.thingSpeak.updateChannel(self.hostname, self.writeAPIKey, self.upstream, cur_value)

    def read_command(self):
        logging.info(threading.current_thread().name + " reading command from ThingSpeak")
        command = None

        while True:
            try:
                command = self.thingSpeak.readChannel(self.hostname,self.readAPIKey, self.read_channelID, self.downstream)
            except Exception as e:
                logging.error(str(e))

            logging.info("Read command: " + str(command))

            do_update = False
            try:
                temp_sleep_interval = self.sleep_interval
                temp_threshold = self.threshold
                temp_raw = self.raw
                next_periodic = self.periodic

                if command is not None:
                    tokens = command.strip().split(" ")
                    temp_sleep_interval = int(tokens[1].strip())

                    if temp_sleep_interval != self.sleep_interval:
                        do_update = True

                    if command.startswith("PERIODIC"):
                        temp_raw = tokens[2].strip()
                    elif command.startswith("FILTERED"):
                        temp_threshold = float(tokens[2].strip())
                        temp_raw = tokens[3].strip()
                        if temp_threshold != self.threshold or self.periodic:
                            do_update = True
                            next_periodic = False

                    if temp_raw.lower() != str(self.raw).lower:
                        do_update = True
                else:
                    logging.debug("Command is null(None)!")

                if do_update:
                    self.lock.acquire(True)
                    self.sleep_interval = temp_sleep_interval
                    self.threshold = temp_threshold

                    if temp_raw.lower() == "true":
                        self.raw = True
                    else:
                        self.raw = False

                    self.periodic = next_periodic
                    self.lock.release()
                else:
                    pass
            except Exception as e:
                logging.error(str(e))

            #sleep for 1 second and read the command again
            time.sleep(self.reader_sleep)

        return command

    def get_force(self,adc_value):
        cur_resistance = self.circuit_resistance * adc_value / (max_adc - self.circuit_resistance)
        cur_force = ((math.log(144000000 / cur_resistance)) * math.log(100))/ math.log(24000)
        return math.pow(cur_force, math.e)

    # NOT USED
    def create_alert(self):
        GPIO.output(ALERT_PIN, 1)
        # can update ThingSpeak(?) and withdraw the alert pin signal
        logging.info("Sleeping for the ALERT duration.")
        time.sleep(self.sleep_interval)
        GPIO.output(ALERT_PIN, 0)

if __name__== "__main__":
    fsr = FSR_ADC()
    fsr.read_FSR()
