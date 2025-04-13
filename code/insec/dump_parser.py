import datetime
import sys
import argparse
import os

class Receiver:
    def __init__(self, quiet_output=False,  file_output=False, output_dir="."):
        self.quiet_output = quiet_output
        self.file_output = file_output
        self.output_dir = output_dir
        self.sessions = {}
    
    def check_session(self, source_ip):
        return source_ip in self.sessions.keys()

    def add_session(self, source_ip):
        self.sessions[source_ip] = {
            "last_max_seq": 0,
            "bit_array": [],
            "filename": self.output_dir + "/" + source_ip + ".txt",
            "file": None
        }
        if self.file_output:
            self.sessions[source_ip]["file"] = open(self.sessions[source_ip]["filename"], "a")
            self.sessions[source_ip]["file"].write("\n")
    
    def parse_dump_record(self, dump_record):
        # 16:04:26.864695 IP 10.1.0.21 > 10.0.0.21: ICMP echo request, id 1387, seq 4, length 64
        dump_record = dump_record.split(" ")
        source_ip = dump_record[2]
        icmp_seq = int(dump_record[11][:-1]) # remove ,
        if not self.check_session(source_ip):
            self.add_session(source_ip)
        
        if self.sessions[source_ip]["last_max_seq"] > icmp_seq:
            if self.sessions[source_ip]["last_max_seq"] >= 3:
                self.add_bit(source_ip, self.sessions[source_ip]["last_max_seq"] % 2)
            else:
                pass
            self.sessions[source_ip]["last_max_seq"] = icmp_seq
        elif self.sessions[source_ip]["last_max_seq"] < icmp_seq:
            self.sessions[source_ip]["last_max_seq"] = icmp_seq

        if not self.quiet_output:
            self.print_sessions()

    def print_sessions(self):
        print("Datetime : " + str(datetime.datetime.now()))

        for session in self.sessions.keys():
            ascii = ""
            i = 0
            max_i = len(self.sessions[session]["bit_array"])
            while i + 8 <= max_i:
                num = 0
                for j in range(8):
                    num += int(self.sessions[session]["bit_array"][i + j]) * (2 ** (7 - j))
                ascii += chr(num)
                i += 8
            if max_i % 8 == 0:
                ascii += "="
            else:
                ascii += "?"
                
            print("Session : " + session + " : " + ascii + "  : " + " : " + "".join(self.sessions[session]["bit_array"]))
    
    def add_bit(self, source_ip, bit):
        bit = str(bit)
        self.sessions[source_ip]["bit_array"].append(bit)
        if self.file_output:
            self.sessions[source_ip]["file"].write(str(bit))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parser for tcpdump output using icmp sequence number covert channel.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Enable quiet output.")
    parser.add_argument("-f", "--file", action="store_true", help="Enable file output.")
    parser.add_argument("-o", "--output", type=str, default=".", help="Output directory name. Every session will be saved in a separate file.")
    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

    receiver = Receiver(args.quiet, args.file, args.output)

    while True:
        input_line = sys.stdin.readline()
        if not input_line:
            break
        dump_record = input_line.strip()
        if not dump_record:
            continue
        receiver.parse_dump_record(dump_record)