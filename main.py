#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join, dirname
import os.path
import sys
import os
import time
import traceback
import onionGpio

TOP_DIR = os.path.dirname(os.path.realpath(__file__))

def exitProgram():
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/AMQP"))
    import amqp_utils as amqp
except ImportError:
    print("File: " + __file__ + " - Import AMQP failed")
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils as js
except ImportError:
    print("File: " + __file__ + " - Import AMQP failed")
    exitProgram()


try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/network"))
    import wifi_utils as wf
except ImportError:
    print("File: " + __file__ + " - Import network failed")
    exitProgram()
        

def AMQPReceiveMessageCallback(ch, method, properties, body):
    message = body.decode('utf-8')
    print("Receive: %s" % message)
    command = js.jsonSimpleParser(message,"command")
    if command == "set":
        value = js.jsonSimpleParser(message,"value")
        gpioObj.setValue(value)
    elif command == "get":
        responeTopic = js.jsonSimpleParser(message,"respone_topic")
        AMQPClient.declareTopic(responeTopic)
        gpioValue = gpioObj.getValue()
        print('Value is: %d'%(int(gpioValue)))
        if int(gpioValue) == 0:
            sendMessage = js.jsonSimpleGenerate("state","0")
        else:
            sendMessage = js.jsonSimpleGenerate("state","1")
        AMQPClient.publishMessage(responeTopic, sendMessage)

gpioNum = 16
gpioObj = onionGpio.OnionGpio(gpioNum)
AMQPClient = amqp.hyperAMQPClient()
def main():
    HOST_MAC_ADDRESS = wf.getMACString()
    print("Device MAC address: " + HOST_MAC_ADDRESS)

    # Connect for sending:
    
    AMQPPubTopic = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "pub")
    print("Pub topic", AMQPSendTopic_lightManager)
    AMQPClient.declareTopic(AMQPSendTopic_lightManager)

    # For receiving:
    AMQPRcvTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "sub")
    AMQPClient.declareTopic(AMQPRcvTopic_lightManager)
    AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPRcvTopic_lightManager)

    gpioNum = 16
    gpioObj = onionGpio.OnionGpio(gpioNum)

    status  = gpioObj.setOutputDirection(0)
    if status == 0:
        print('GPIO%d set to output,'%(gpioNum))
    else:
        print('FAILED: GPIO%d set to output ,'%(gpioNum))
    
    value = gpioObj.getValue()
    print('Initial value: %d'%(int(value)))

    while True:
        try:
            if (int(value) != int(gpioObj.getValue())):
                value = gpioObj.getValue()
                print('Value is changed: %d'%(int(value)))
                if int(value) == 0:
                    message = js.jsonSimpleGenerate("state","0")
                else:
                    message = js.jsonSimpleGenerate("state","1")
                AMQPClient.publishMessage(AMQPPubTopic, message)
            time.sleep(1)
        except Exception as e:
            print("Failed to run Humidifier Process: exception={})".format(e))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.log(logging.DEBUG, 'Interrupted')
        exitProgram()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(type(e))
    
    
        
