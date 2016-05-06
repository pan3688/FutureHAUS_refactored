#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
from FSRReader import FSR_ADC
import time
from ThingSpeak import ThingSpeak

import ConfigParser
import sys
import logging

class SensePi:
    def __init__(self):

        """
        Requires the config file to start operation
        """
        if len(sys.argv) < 2:
            print "Config file missing"
            return

        configfile = sys.argv[1].strip()
        self.config = ConfigParser.ConfigParser()
        
        try:
            #Reading the configuration file
            self.config.read(configfile)
        except:
            print "Exception reading configuration file\n"

        logfile = self.config.get("logging","logfilename")
        #print "Log file is : " + logfile

        loglevel = self.config.get("logging","loglevel")
        logging.basicConfig(filename=logfile, format='%(asctime)s\t%(levelname)s\t%(funcName)s\t%(filename)s\t%(message)s', level=loglevel)

        logging.info("Logging started")

    def init_thingspeak(self):
        pass

if  __name__=="__main__":
    sensePi = SensePi()
    fsr = FSR_ADC(sensePi.config)

    """
    Starting a thread to read the ThingSpeak command channel;
    setting it as a daeomon thread so that the main thread can
    continue execution
    """
    t_reader = threading.Thread(target = fsr.read_command)
    t_reader.setDaemon(True)
    t_reader.start()

    """
    Starting a thread to read the sensor and send the read value
    to upstream ThingSpeak channel
    """
    t = threading.Thread(target = fsr.read_FSR)
    t.setDaemon(True)
    t.start()

    """
    Wait for both daemon threads to finish, which will never happen
    since they are both executing an infinite loop;
    HENCE this main thread will never exit as desired!
    """
    t_reader.join()
    t.join()
