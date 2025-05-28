import asyncio
from nats.aio.client import Client as NATS
import os, random
import sys
from scapy.all import Ether
import signal

PACKET_COUNTER = -1

file = open("normal_ping_dataset.txt", "a+")
def log_packet(packet, label):
    global PACKET_COUNTER, file
    PACKET_COUNTER += 1
    file.write(f"{PACKET_COUNTER}\t{label}\t{packet["IP"]["ICMP"].fields["type"]}\t{packet['IP']['ICMP'].fields['id']}\t{packet['IP']['ICMP'].fields['seq']}\n")

def signal_handler(signal, frame):
    global file
    file.close()
    sys.exit(0)
signal.signal(signal.SIGTERM, signal_handler)

async def run(drop_probability = None, label = None):
    nc = NATS()

    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data #.decode()
        #print(f"Received a message on '{subject}': {data}")
        packet = Ether(data)
        # Publish the received message to outpktsec and outpktinsec
        if packet.haslayer("IP"):
                if packet["IP"].haslayer("ICMP"):
                    # print(f"Packet has ICMP layer")
                    log_packet(packet, label)
        if drop_probability:
            random_value = random.random()
            # Drop the packet with the given probability
            if random_value < drop_probability:
                # print(f"Dropping packet with probability {drop_probability}")
                return
        if subject == "inpktsec":
            await nc.publish("outpktinsec", msg.data)
        else:
            await nc.publish("outpktsec", msg.data)
   
    # Subscribe to inpktsec and inpktinsec topics
    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)

    # print("Subscribed to inpktsec and inpktinsec topics")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        await nc.close()

if __name__ == '__main__':
    drop_probability = None
    label = None
    if len(sys.argv) >= 2:
        drop_probability = float(sys.argv[1])
        label = sys.argv[2]
    else:
        print("Usage: python3 dropper_w_log.py <drop_probability> <label>")
        exit(1)
    asyncio.run(run(drop_probability, label))