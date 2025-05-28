import asyncio
from nats.aio.client import Client as NATS
import os, random
import sys
from scapy.all import Ether

def prepare_response(data):
    packet = Ether(data)
    packet["IP"]["ICMP"].fields["type"] = 0  # Set ICMP type to Echo Reply
    packet["IP"]["ICMP"].fields["chksum"] = None  # Reset checksum to recalculate
    # Switch the source and destination IP addresses
    packet["IP"].src, packet["IP"].dst = packet["IP"].dst, packet["IP"].src
    packet["IP"].chksum = None  # Reset checksum to recalculate
    packet["IP"].len = None  # Reset length to recalculate
    new_data = bytes(packet)
    return new_data

async def run(drop_probability = None, mitigate_probability = None):
    nc = NATS()

    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data #.decode()
        #print(f"Received a message on '{subject}': {data}")
        packet = Ether(data)
        # Publish the received message to outpktsec and outpktinsec
        if drop_probability:
            random_value = random.random()
            # Drop the packet with the given probability
            if random_value < drop_probability:
                print(f"Dropping packet with probability {drop_probability}")
                return
        
        # We decide to pass the packet
        # Mitigator Algorithm
        # If we create a response packet, and sent it back to the sender
        # So that the sender will think that the packet was received and acked
        # But the receiver will not receive it
        # If it is the last packet of the covert bit sequence, there will be a bit error
        # Else the covert bit sequence will be received correctly
        
        if packet.haslayer("IP"):
                if packet["IP"].haslayer("ICMP"):
                    print(packet.show())

        if mitigate_probability and subject in ["inpktsec"]:
            if packet.haslayer("IP"):
                if packet["IP"].haslayer("ICMP"):
                    random_value = random.random()
                    # Mitigate the packet with the given probability
                    if random_value < mitigate_probability:
                        new_data = prepare_response(msg.data)
                        await nc.publish("outpktsec", new_data)
                    else:
                        await nc.publish("outpktinsec", msg.data)
                else:
                    await nc.publish("outpktinsec", msg.data)
            else:
                await nc.publish("outpktinsec", msg.data)
        elif mitigate_probability and subject in ["inpktinsec"]:
            await nc.publish("outpktsec", msg.data)
        else:
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
    mitigate_probability = None
    if len(sys.argv) > 2:
        drop_probability = float(sys.argv[1])
        mitigate_probability = float(sys.argv[2])
    elif len(sys.argv) > 1:
        drop_probability = float(sys.argv[1])
    asyncio.run(run(drop_probability, mitigate_probability))