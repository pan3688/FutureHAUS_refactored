#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib2
import logging

class ThingSpeak:

    """
    Constructor for ThingSpeak object; doesn't have its own fields, so
    any module can use it to connect with any field of any ThingSpeak
    channel, by providing the connection parameters to this object's methods
    """
    def __init__(self):
        pass

    """
    Read a ThingSpeak channel
    """
    def readChannel(self, hostname, readAPIKey, channelId, fieldId):
        url = hostname + "/channels/" + channelId + "/field/" + fieldId + "/last?key=" + readAPIKey
        logging.debug("Reading data from:\t" + url)

        ret = None
        try:
            ret = urllib2.urlopen(url).read()
            logging.debug("Read command :" + str(ret))
        except Exception as e:
            logging.error("Error reading thingSpeak channel " + str(e))

        return ret

    """
    Write to a ThingSpeak channel
    """
    def updateChannel(self, hostname, writeAPIKey, fieldId, value):
        url = hostname + "/update?api_key=" + writeAPIKey + "&" + str(fieldId) + "=" + str(value)
        logging.debug("Updating channel at:\t" + url)

        ret = None
        try:
            ret = urllib2.urlopen(url)
        except Exception as e:
            logging.critical("Error updating thingSpeak channel " + str(e))

        return ret

# FOR testing
if __name__=="__main__":
    thingSpeak = ThingSpeak()
    #print thingSpeak.updateChannel("PHTKY9VQ9FIEYRWB", "1", "8888").read()
    #print thingSpeak.readChannel("QOT8G5E9VF7YW10S", "108160", "1").read()
