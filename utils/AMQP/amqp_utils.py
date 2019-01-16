import sys
import os.path
import logging
import json

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "network"))
    import wifi_utils
except ImportError:
    print("File: " + __file__ + " - Import network failed")
    exit()

try:
    import amqp_client as amqp
except ImportError:
    print("File: " + __file__ + " - Import AMQP failed")
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "logger"))
    import logger as log
except ImportError:
    print("File: " + __file__ + " - Import logger failed")
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "audio"))
    import microphone
    import speaker
except ImportError:
    print("File: " + __file__ + " - Import audio failed")
    exit()

OMEGA2P_MAC_ADDRESS = "40a36bc02daf"
HOST_MAC_ADDRESS = wifi_utils.getMACString()
ALL_TASKS = ['lightManager','musicManager','timeManager','answerCenter']

def AMQPReceiveMessageCallback(ch, method, properties, body):
    print("Receive: %s" % body.decode('utf-8'))

def AMQPProcess(log_q, send_q, rcv_q, cmd_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "AMQPProcess is started")
    for task in ALL_TASKS:
        # Connect for sending:
        AMQPClient = amqp.hyperAMQPClient()
        AMQPSendTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", task, "sub")
        logger.log(logging.DEBUG, AMQPSendTopic_lightManager)
        AMQPClient.declareTopic(AMQPSendTopic_lightManager)

        # For receiving:
        AMQPRcvTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", task, "pub")
        AMQPClient.declareTopic(AMQPRcvTopic_lightManager)
        AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPRcvTopic_lightManager)

    while True:
        try:
            jsonStr = send_q.get()
        except Exception as e:
            continue
        try:
            jsonStr = json.loads(jsonStr)

            AMQPClient.publishMessage(routing_key=AMQPSendTopic_lightManager)
        except Exception as e:
            logger.log(logging.ERROR, "Failed to run Humidifier Process: exception={})".format(e))
