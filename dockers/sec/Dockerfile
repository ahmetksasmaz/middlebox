FROM ubuntu:latest

#RUN apt update && apt install -y tshark iproute2 iptables dnsmasq jq netmask bsdmainutils conntrack iputils-ping dnsutils  net-tools 
RUN apt update -y && apt upgrade -y && apt install -y systemd tshark jq iputils-ping dnsutils net-tools iperf tcpdump netcat-traditional curl iproute2 ethtool iptables nftables

RUN echo 'net.ipv4.ip_forward=0' >> /etc/sysctl.conf && sysctl -p

RUN apt update && apt install -y python3 python3-pip build-essential cmake libpcap-dev vim

# Requirements to configure and build iputils repository
RUN apt install -y --no-install-recommends clang docbook-xsl-ns file gcc gettext git iproute2 jq libcap-dev libidn2-0-dev meson pkg-config xsltproc

WORKDIR /code/sec