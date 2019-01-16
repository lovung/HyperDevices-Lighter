#!/usr/bin/env python
import pika
import ssl

ssl_options=dict(
        ssl_version=ssl.PROTOCOL_TLSv1_2,
        ca_certs="./cacert.pem",
        keyfile="./key.pem",
        certfile="./cert.pem",
        cert_reqs=ssl.CERT_REQUIRED)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='vulong1602.ddns.net',
                                            port=5671,
                                            heartbeat_interval = 0,
                                            ssl = True,
                                            ssl_options = ssl_options))
channel = connection.channel()

channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
