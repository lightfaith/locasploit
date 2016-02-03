#!/usr/bin/env python3

from source.libs.include import *
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

# My version of Scapy does not have stopper parameter in sniff() function for some reason.
# Reimplementation is necessary.
def sniff(count=0, store=1, offline=None, prn = None, lfilter=None, L2socket=None, timeout=None,
          opened_socket=None, stop_filter=None, stopper=None, *arg, **karg):
    """Sniff packets
sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args) -> list of packets

  count: number of packets to capture. 0 means infinity
  store: wether to store sniffed packets or discard them
    prn: function to apply to each packet. If something is returned,
         it is displayed. Ex:
         ex: prn = lambda x: x.summary()
lfilter: python function applied to each packet to determine
         if further action may be done
         ex: lfilter = lambda x: x.haslayer(Padding)
offline: pcap file to read packets from, instead of sniffing them
timeout: stop sniffing after a given time (default: None)
L2socket: use the provided L2socket
opened_socket: provide an object ready to use .recv() on
stop_filter: python function applied to each packet to determine
             if we have to stop the capture after this packet
             ex: stop_filter = lambda x: x.haslayer(TCP)
stopper: function returning true or false to stop the sniffing process
    """
    c = 0
    
    if opened_socket is not None:
        s = opened_socket
    else:
        if offline is None:
            if L2socket is None:
                L2socket = conf.L2listen
            s = L2socket(type=ETH_P_ALL, *arg, **karg)
        else:
            s = PcapReader(offline)

    lst = []
    if timeout is not None:
        stoptime = time.time()+timeout
    remain = None
    while 1:
		# if True, stop the loop
        if stopper is not None and stopper():
            break
        try:
            if timeout is not None:
                remain = stoptime-time.time()
                if remain <= 0:
                    break
            sel = select.select([s],[],[],remain)
            if s in sel[0]:
                p = s.recv(MTU)
                if p is None:
                    break
                if lfilter and not lfilter(p):
                    continue
                if store:
                    lst.append(p)
                c += 1
                if prn:
                    r = prn(p)
                    if r is not None:
                        print(r)
                if stop_filter and stop_filter(p):
                    break
                if count > 0 and c >= count:
                    break

        except KeyboardInterrupt:
            break
    if opened_socket is None:
        s.close()
    return plist.PacketList(lst,"Sniffed")

