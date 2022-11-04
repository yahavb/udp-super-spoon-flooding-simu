#!/usr/bin/env python3

import random
import socket
import threading
import os
import enet
import time
import psycopg2

udp_socket_port=int(os.environ.get('UDP_SOCKET_PORT'))
udp_socket_ip=os.environ.get('UDP_SOCKET_IP')
udp_flood_packet_size=int(os.environ.get('UDP_FLOOD_PACKET_SIZE'))
num_of_flood_threads=int(os.environ.get('NUM_OF_FLOOD_THREADS'))
sleep_between_flood=int(os.environ.get('SLEEP_BETWEEN_FLOOD'))
port_range_min=int(os.environ.get('UDP_PORT_MIN'))
port_range_max=int(os.environ.get('UDP_PORT_MAX'))
user=os.environ['PGUSER']
password=os.environ['PGPASSWORD']
host=os.environ['PGHOST']
database=os.environ['PGUSER']


def db_read(sql,param):
  print("in db_read",flush=True)
  try:
    connection = psycopg2.connect(user=user,
      password=password,
      host=host,
      port="5432",
      database=database)
    cursor = connection.cursor()
    cursor.execute(sql,param)
    rows = cursor.fetchall()
    return rows
  except (Exception, psycopg2.Error) as error:
    print("Failed to insert/update", error)
    sys.stdout.flush()
  finally:
    if connection:
        cursor.close()
        connection.close()

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

def scan_endpoints():
  sql = """select ipv4 from ipv4_usw;"""
  params = []
  rows = list(db_read(sql,params))
  for ipv4 in rows:
    for port in range(port_range_min,port_range_max):
      print("{0}:{1} is {2}".format(ipv4[0],port,check_udp_endpoint(ipv4[0],port)),flush=True)
      time.sleep(sleep_between_flood)
      #TODO - add healthy endpoints to db table 

scan_endpoints()
#endpoint_status=check_udp_endpoint(udp_socket_ip,udp_socket_port)
#print("udp endpoint {0}:{1} health is {2}".format(udp_socket_ip,udp_socket_port,endpoint_status),flush=True)
#if endpoint_status=="true":
#  for y in range(num_of_flood_threads):
#   _thread=threading.Thread(target=flood_endpoint(udp_socket_ip,udp_socket_port))
#   _thread.start()
