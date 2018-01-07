#!/usr/bin/env python
import pika
import ssl
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

ssl_options=dict(
        ssl_version=ssl.PROTOCOL_TLSv1_2,
        ca_certs=FILE_DIR + "/cacert.pem",
        keyfile=FILE_DIR + "/key.pem",
        certfile=FILE_DIR + "/cert.pem",
        cert_reqs=ssl.CERT_REQUIRED)


class hyperAMQPClient(object):
    def __init__(self, host='vulong1602.ddns.net',
                 port=5671,
                 ssl_options = ssl_options):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,
                                            port=port,
                                            heartbeat_interval = 0,
                                            ssl = True,
                                            ssl_options = ssl_options))
        self.channel = self.connection.channel()
    def declareTopic(self, topic):
        print("Declare topic: ", topic)
        self.channel.queue_declare(queue=topic)

    def printMessage(ch, method, properties, body):
        print(" [x] Received %r" % body)

    def topicGenerator(self, mac_address, model, task, method):
        if len(mac_address) != 12:
            return -1
        if len(model) != 4:
            return -1
        if len(task) <= 0:
            return -1
        if method != 'pub' and method != 'sub':
            return -1
        key = 0
        for c in mac_address:
            c_int = int(c, 16)
            key += c_int
        key *= int(mac_address[10],16)
        key += int(mac_address[11],16)
        # print("key = %x" % key)
        if len(hex(key)[2:]) == 1:
            strKey = mac_address[8] + mac_address[9] + "00" + hex(key)[2:]
        elif len(hex(key)[2:]) == 2:
            strKey = mac_address[8] + mac_address[9] + "0" + hex(key)[2:]
        elif len(hex(key)[2:]) == 3:
            strKey = mac_address[8] + mac_address[9] + hex(key)[2:]
        # print("key = %x" % key)
        retStr = strKey + '/' + model + '/' + task + '/' + method
        return retStr


    def publishMessage(self, routing_key, message):
        print("Publish message: ", message, "to topic: ", routing_key)
        self.channel.basic_publish(exchange='',
                      routing_key=routing_key,
                      body=message)

    def startSubcribe(self, received_callback, topic):
        self.channel.basic_consume(received_callback,
                              queue=topic,
                              no_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def closeConnection(self):
        self.connection.close()
