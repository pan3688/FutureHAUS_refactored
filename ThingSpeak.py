#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib2

hostname = "https://api.thingspeak.com"

writeAPIKey = "3XICIX7N986U4JAS"
readAPIKey = None

#TODO -- should have a config file to read channel numbers, read/write API Keys (ThingSpeak) and field ids

class ThingSpeak:

    def __init__(self):
        self.hostname = hostname

        # ADD key-value pairs to this map to update other ThingSpeak fields
        self.fields = {"FSR":1}
    
    def getLastFeed(self, readAPIKey, channelId, fieldId):
        url = self.hostname + "/channels/" + channelId + "/field/" + fieldId + "/last?key=" + readAPIKey
        return urllib2.urlopen(url)
    
    def updateChannel(self, writeAPIKey, fieldId, value):
        url = self.hostname + "/update?api_key=" + writeAPIKey + "&" + str(fieldId) + "=" + str(value)
        return urllib2.urlopen(url)

    def update_fsr_channel(self, value):
        fieldID = self.fields.get("FSR")
        return self.updateChannel(writeAPIKey, fieldID, value).read()

# FOR testing
if __name__=="__main__":
    thingSpeak = ThingSpeak()
    #print thingSpeak.updateChannel("PHTKY9VQ9FIEYRWB", "1", "8888").read()
    #print thingSpeak.getLastFeed("QOT8G5E9VF7YW10S", "108160", "1").read()
    thingSpeak.update_fsr_channel(24)
