#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib2
import logging

class ThingSpeak:

    def __init__(self):
        pass
    
    def readCommand(self, hostname, readAPIKey, channelId, fieldId):
        url = hostname + "/channels/" + channelId + "/field/" + fieldId + "/last?key=" + readAPIKey
        logging.debug("Reading data from:\t" + url)

        ret = None
        try:
            ret = urllib2.urlopen(url)
        except e as Exception:
            logging.error("Error reading thingSpeak channel " + e)

        return ret
    
    def updateChannel(self, hostname, writeAPIKey, fieldId, value):
        url = hostname + "/update?api_key=" + writeAPIKey + "&" + str(fieldId) + "=" + str(value)
        logging.debug("Updating channel at:\t" + url)

        ret = None
        try:
            ret = urllib2.urlopen(url)
        except e as Exception:
            logging.critical("Error updating thingSpeak channel " + e)

        return ret

    """
    def update_fsr_channel(self, value):
        fieldID = 1
        hostname = "https://api.thingspeak.com"
        writeAPIKey = "3XICIX7N986U4JAS"
        readAPIKey = None

        return self.updateChannel(hostname, writeAPIKey, fieldID, value).read()
    """

# FOR testing
if __name__=="__main__":
    thingSpeak = ThingSpeak()
    #print thingSpeak.updateChannel("PHTKY9VQ9FIEYRWB", "1", "8888").read()
    #print thingSpeak.readCommand("QOT8G5E9VF7YW10S", "108160", "1").read()
    thingSpeak.update_fsr_channel(24)
