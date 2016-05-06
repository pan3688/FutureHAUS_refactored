#!/usr/bin/python

import urllib2
import random as rand
import time

"""
This is a test script, used to send commands to ThingSpeak upstream,
in the absense of a UI
"""

host = "https://api.thingspeak.com"
writeKey = "3XICIX7N986U4JAS"
readKey = "9HET1Q6CL50BYB15"
field = 2
channel = 108159

def testMethod(command):
    n = rand.randint(5,10)
    
    url = host + "/update?api_key=" + writeKey + "&" + str(field) + "=" + command
    print url

    ret = urllib2.urlopen(url)

    print ret

if __name__=="__main__":
    while True:
        n = rand.randint(5,10)
        m = rand.randint(1,5)

        command = None
        fil = True

        if m % 2 == 0:
            fil = False

        if n % 2 == 0:
            command = "PERIODIC " + str(n) + " " + str(fil)
        else:
            command = "FILTERED " + str(n) + " 0.4 " + str(fil)

        print testMethod(command)
        time.sleep(10)
