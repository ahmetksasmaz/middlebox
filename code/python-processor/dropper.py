import asyncio
from nats.aio.client import Client as NATS
import os, random
import sys
from scapy.all import Ether

async def run(drop_probability = None):
    nc = NATS()

    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data #.decode()
        #print(f"Received a message on '{subject}': {data}")
        packet = Ether(data)
        print(packet.show())
        # Publish the received message to outpktsec and outpktinsec
        if drop_probability:
            random_value = random.random()
            # Drop the packet with the given probability
            if random_value < drop_probability:
                print(f"Dropping packet with probability {drop_probability}")
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
    if len(sys.argv) > 1:
        drop_probability = float(sys.argv[1])
    asyncio.run(run(drop_probability))