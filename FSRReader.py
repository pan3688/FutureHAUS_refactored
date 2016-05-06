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

# Gain (multiplier) -- keep this 2 
GAIN = 2 

# ADC channel that is reading the FSR
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

        # to create an alert on PI, NOT used
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
        zero_value = -1

        try:
            CUR = self.adc.start_adc_comparator(CHANNEL,
                               HT, LT,
                               gain = GAIN,
                               traditional = True,
                               active_low = True,
                               num_readings = 1,
                               latching = True)
            
	    # The value FSR reports, when no force is applied (error value)
            zero_value = self.get_force(CUR)
            logging.info("zero value = " + str(zero_value))

        except e as Exception:
            logging.critical("Error while reading sensor value")

        prev = zero_value
        """
        This is an infinite loop to read the force sensor continuously
        """
        while True:
            cur_value = self.adc.get_last_result()

            cur_force = cur_value

            self.lock.acquire(True)
            """
            Acquired the FSR object lock, read the required parameters,
            such as threshold, raw data boolean AND
            sampling_period (sleep interval for this thread) 
            
            """
            # for accurate weight, more calibration is required
            if not self.raw:
                cur_force = self.get_force(cur_value) - zero_value

            cur_threshold = self.threshold
            cur_interval = self.sleep_interval
            self.lock.release()

            logging.debug("Current ADC channel " + str(CHANNEL) + " value is : " + str (cur_force))

            # updating the ThingSpeak channel
            if self.periodic:
                self.update_fsr_channel(cur_force)
            elif math.fabs(cur_force - prev) >= cur_threshold:
                self.update_fsr_channel(cur_force)

            """
            Blocking call, if command reader thread is updating sleep interval
            then let it complete the update operation
            """
            try:
                logging.debug(threading.current_thread().name + " sleeping before reading the sensor again")
                time.sleep(cur_interval)
            except Exception as e:
                logging.error(threading.current_thread().name + " sleep exception.")

            prev = cur_force

        logging.info("Stopping " + threading.current_thread().name)
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

                    if temp_raw.lower() != str(self.raw).lower():
                        do_update = True
                else:
                    logging.debug("Command is null(None)!")

                if do_update:
                    logging.debug(threading.current_thread().name + 
                      "Locking the FSR object for updating its parameters")

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

            #sleep for 1 second and read the command from ThingSpeak again
            time.sleep(self.reader_sleep)

        logging.info("Stopping " + threading.current_thread().name)
        return command

    def get_force(self,adc_value):
        """
        These parametric constants of these equations are derived by
        looking at the data sheet of the FSR, and their derivation
        depends on the circuit design, HENCE change these equations
        if your circuit design differs from the one we have in our
        documentation
        """
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

#FOR TESTING the FSR and ADC without ThingSpeak
if __name__== "__main__":
    fsr = FSR_ADC()
    fsr.read_FSR()
