#!/usr/bin/env python3

import random
import socket
import threading
import os
import enet
import time

udp_socket_port=int(os.environ.get('UDP_SOCKET_PORT'))
udp_socket_ip=os.environ.get('UDP_SOCKET_IP')
udp_flood_packet_size=int(os.environ.get('UDP_FLOOD_PACKET_SIZE'))
num_of_flood_threads=int(os.environ.get('NUM_OF_FLOOD_THREADS'))
sleep_between_flood=int(os.environ.get('SLEEP_BETWEEN_FLOOD'))

def check_udp_endpoint(udp_socket_ip,udp_socket_port):
  _udp_socket_ip=udp_socket_ip.encode('utf-8')
  host = enet.Host(None, 1, 0, 0) 
  addr=enet.Address(_udp_socket_ip,udp_socket_port)
  peer = host.connect(addr,1)
  status="unknown"
  if peer:
    print("%s:" % peer)
    event = host.service(1000)
    if event.type == enet.EVENT_TYPE_CONNECT:
      print("%s: CONNECT" % event.peer.address)
      status="true"
    elif event.type == enet.EVENT_TYPE_DISCONNECT:
      print("%s: DISCONNECT" % event.peer.address)
      status="false"
  return status 

def flood_endpoint(udp_socket_ip,udp_socket_port):
  data = random._urandom(udp_flood_packet_size)
  while True:
    try:
      s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
      addr = (udp_socket_ip,udp_socket_port)
      s.sendto(data,addr)
      print("sent to {0}".format(addr),flush=True)
    except:
      print("error with {0}".format(addr),flush=True)
    time.sleep(sleep_between_flood)


endpoint_status=check_udp_endpoint(udp_socket_ip,udp_socket_port)
print("udp endpoint {0}:{1} health is {2}".format(udp_socket_ip,udp_socket_port,endpoint_status),flush=True)
if endpoint_status=="true":
  #flood_endpoint(udp_socket_ip,udp_socket_port) 
  for y in range(num_of_flood_threads):
   _thread=threading.Thread(target=flood_endpoint(udp_socket_ip,udp_socket_port))
   _thread.start()
