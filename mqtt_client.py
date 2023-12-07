import sys
import time
import argparse
import paho.mqtt.client as mqtt

# Global variable to track message receipt
is_message_received = False


# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT broker")
    else:
        print(f"Connection failed with code {rc}", file=sys.stderr)


# Callback when a message is received from the server
def on_message(client, userdata, msg):
    global is_message_received
    is_message_received = True
    print(msg.topic + " " + str(msg.payload.decode()))

    # Disconnect after receiving the message
    client.disconnect()


def main():
    parser = argparse.ArgumentParser(description='MQTT Client Example')
    parser.add_argument('netid', type=str, default="jacobda2", help='Your NetID')
    parser.add_argument('action', type=str, help='Action to perform')
    parser.add_argument('message', type=str, help='Message to send')
    parser.add_argument('-p', '--port', type=int, default=1883, help='Port number, default is 1883')
    parser.add_argument('--host', type=str, default='localhost', help='Host, default is localhost')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    client = mqtt.Client(client_id=args.netid)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.host, args.port, 60)  # Connect to the server
        client.loop_start()  # Start the loop

        # Subscribe to the response topic
        response_topic = f"{args.netid}/{args.action}/response"
        client.subscribe(response_topic, qos=1)

        # Publish the message
        request_topic = f"{args.netid}/{args.action}/request"
        client.publish(request_topic, args.message, qos=1)

        # Wait for the message to be received or the client to disconnect
        while not is_message_received or client.is_connected():
            time.sleep(0.1)  # Sleep to allow processing time for the message

        client.loop_stop()  # Stop the loop

    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        sys.exit(0)


if __name__ == '__main__':
    main()
