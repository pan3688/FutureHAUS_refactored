#!/usr/bin/env python

import urllib2

hostname = "https://api.thingspeak.com"

class ThingSpeak:

    def __init__(self):
        self.hostname = hostname
        
    def getLastFeed(self, readAPIKey, channelId, fieldId):
        url = self.hostname + "/channels/" + channelId + "/field/" \
              + fieldId + "/last?key=" + readAPIKey
        return urllib2.urlopen(url)
    
    def updateChannel(self, writeAPIKey, fieldId, value):
        url = self.hostname + "/update?api_key=" + writeAPIKey + "&" + str(fieldId) + "=" + str(value)
        return urllib2.urlopen(url)

    def update_fsr_channel(self, value):
        writeAPIKey = "3XICIX7N986U4JAS"
        fieldID = 1
        return self.updateChannel(writeAPIKey, fieldID, value).read()

if __name__=="__main__":
    #curhost = "https://api.thingspeak.com"
    
    thingSpeak = ThingSpeak()
    
    print thingSpeak.updateChannel("PHTKY9VQ9FIEYRWB", "1", "8888").read()
    print thingSpeak.getLastFeed("QOT8G5E9VF7YW10S", "108160", "1").read()
