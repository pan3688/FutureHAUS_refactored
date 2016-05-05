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
        logging.basicConfig(filename=logfile, format='%(asctime)s\t%(filename)s\t%(funcName)s\t%(levelname)s\t%(message)s', level=loglevel)

        logging.info("Logging started")

    def init_thingspeak(self):
        pass

if  __name__=="__main__":
    sensePi = SensePi()
    t = threading.Thread(target = FSR_ADC(sensePi.config).read_FSR)
    t.setDaemon(True)
    t.start()

    while True:
        print "main thread..."
        time.sleep(4)
