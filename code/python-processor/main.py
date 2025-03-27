import asyncio
from nats.aio.client import Client as NATS
import os, random
import sys
from scapy.all import Ether

async def run(delay_lambda = None):
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
        if delay_lambda:
            # delay_lambda = X ms -> event occur every X ms -> 1e3 / X events per second
            delay = random.expovariate(1e3 / delay_lambda)
            await asyncio.sleep(delay)
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
    delay_lambda = None
    if len(sys.argv) > 1:
        delay_lambda = float(sys.argv[1])
    asyncio.run(run(delay_lambda))