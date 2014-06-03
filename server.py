#!/usr/bin/python

import socket
import sys
import re
import server_client_rep
import select
import threading, time
import sensor
import signal


class Server(): 

	SENSOR_PORT = 6005
	CLIENT_PORT = 6006
	HOST = None #'127.0.0.1' localhost is it ok?
	CLIENT_SOCKET = None
	SENSOR_SOCKET = None
	TIMER_INTERVAL = 2
	VERSION = 1;

	thread_lock = None #lock for synchronization
	
	clients = []## list of clients		## need to add clients
	sensor_list = []## list of available sensors


	def __init__(self,host):
		self.HOST = host
		self.thread_lock = threading.Lock()
		self.read_sensor_list()
	
	def start_listening_sensor(self):
		try:
			self.SENSOR_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.SENSOR_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.SENSOR_SOCKET.bind((self.HOST,self.SENSOR_PORT))
		except socket.error, (errno,message):
			if self.SENSOR_SOCKET:
				self.SENSOR_SOCKET.close()
			print "Server: error, failed to open sensor socket " + message
			sys.exit() #or do we want to exit, or just ignore it?
				
	def start_listening_client(self):
		try:
			self.CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.CLIENT_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.CLIENT_SOCKET.bind((self.HOST,self.CLIENT_PORT))
		except socket.error, (errno,message):
			if self.CLIENT_SOCKET:
				self.CLIENT.SOCKET.close()
			print "Server: error, failed to open client socket " + message
			sys.exit() #or do we want to exit, or just ignore it?

	
	def start_listening(self):
		
		self.start_listening_sensor()
		self.start_listening_client()
		
		
		CONNECTION_LIST = []
		
		CONNECTION_LIST.append(self.CLIENT_SOCKET)
		CONNECTION_LIST.append(self.SENSOR_SOCKET)

		self.timerThread = self.timer_Thread(self.clients, self)
		self.timerThread.start()
		
		while 1:
			
			read,write,error = select.select(CONNECTION_LIST,[],[])
			
			for sock in read:
				
				if sock == self.CLIENT_SOCKET:
					data,addr = self.CLIENT_SOCKET.recvfrom(2048)

					if(len(self.clients)!=0):
						for c in self.clients:
							if c.client_addr == addr:
								c.threading_lock.acquire(1)
								c.received_packet_from_client(data)
								c.threading_lock.release()
								break
							#if we are on the last client and it doesnt match, then create new client
							elif self.clients[-1] == c:
								print "SERVER: New client connected from (%s, %s)" % addr
								newClient = server_client_rep.Client(self,addr)
								self.clients.append(newClient)
								newClient.threading_lock.acquire(1)
								newClient.received_packet_from_client(data)
								newClient.threading_lock.release()
					
					else:
						print "SERVER: First client connected from (%s, %s)" % addr
						newClient = server_client_rep.Client(self,addr)
						self.clients.append(newClient)
						newClient.threading_lock.acquire(1)
						newClient.received_packet_from_client(data)
						newClient.threading_lock.release()
				if sock == self.SENSOR_SOCKET:
					data,addr = self.SENSOR_SOCKET.recvfrom(2048)			
					result = re.search("'dev_id': '(.*?)'",data)
                                        
					if result != None:
						sensorID = result.group(1)
                                                self.update_sensor_info(sensorID, data)
						#write received data to log
						file = open("server_"+ sensorID +".log", "a")
						file.write(str(time.time()))
						file.write("\t")
						file.write(data)
						file.write("\n")
						file.close()

						for c in self.clients:
                                                        c.threading_lock.acquire(1)
							c.received_packet_from_sensor(sensorID, data)
							c.threading_lock.release()
					else:
						print "SERVER: Received unknown packet"	
			
			

        #updates the data stored about a sensor.
        def update_sensor_info(self, sensorID, data):
                for sensor in self.sensor_list:
                        if sensorID == sensor.sname:
                                value = re.search("'sensor_data': '(.*?) ", data)
                                if value != None:
                                        sensor.add_value(value.group(1))

                                        
                
	def remove_client(self,client):
		self.clients.remove(client)
			
	# reads sensor.list file to sensor_list, file must have unieque sensor-ids on separate lines 
	#	sensor1\n
	#	sensor2\n
	#	sensor3\n
	# 	<end of file>

	
	def read_sensor_list(self):
		with open('sensor.list') as f:
			sensor_list = f.readlines()
			sensor_list = [x.strip('\n') for x in sensor_list]
			print("Server: following sensors read")
			print("\t"+str(sensor_list))
                        for x in sensor_list:
                                self.sensor_list.append(sensor.Sensor(x, re.search("(.*)_.*", x).group(1)))
                                
        def stop_server(self):
                print '\nSHUTTING DOWN SERVER ...'
                self.timerThread.stop()
                self.timerThread.join(1)
                print 'Server shut down'
                sys.exit(0)               


	#thread that will handle the timers in each client
	class timer_Thread(threading.Thread):
                
                clients = None
                server = None
                stop = False
                
                def __init__(self, clientList, server):
                        threading.Thread.__init__(self)
                        self.clients = clientList
                        self.server = server

                def run(self):
                        while(1):
                                if(self.stop == True):
                                        return
                                time.sleep(self.server.TIMER_INTERVAL)
                                
                                for c in self.clients:
                                        c.timer_heartbeat-=self.server.TIMER_INTERVAL
                                        c.timer_packet-=self.server.TIMER_INTERVAL

                                        #if time to send heartbeat
                                        if(c.timer_heartbeat <= 0):
                                                c.threading_lock.acquire(1) #each client has a lock for sync
                                                print("Server: timer thread sending heartbeat")
                                                c.send_heartbeat()
                                                c.threading_lock.release()
                                        #if time to send packet
                                        if(c.timer_packet <= 0):
                                                c.threading_lock.acquire(1)
                                                if(len(c.current_packet.get_packet()) > 1 ):
                                                        print("Server: timer thread sending current packet")
                                                        c.prepare_to_send_packet()

                                                c.threading_lock.release()

                def stop(self):
                        self.stop = True
		


			
			
					
