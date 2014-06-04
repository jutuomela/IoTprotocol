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

	SENSOR_PORT = None
	CLIENT_PORT = None
	CLIENT_SOCKET = None
	SENSOR_SOCKET = None
	TIMER_INTERVAL = 2
	VERSION = 1;
	HOST = "127.0.0.1"

	thread_lock = None #lock for synchronization
	
	clients = []## list of clients		## need to add clients
	sensor_list = []## list of available sensors


	def __init__(self,s_port, c_port, version):
		self.SENSOR_PORT = int(s_port)
		self.CLIENT_PORT = int(c_port)
		self.thread_lock = threading.Lock()
		self.read_sensor_list()
		if version == "2":
			self.VERSION = 2
			self.logData("Version = 2")
		else:
			self.VERSION = 1
	
	def start_listening_sensor(self):
		try:
			self.SENSOR_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.SENSOR_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.SENSOR_SOCKET.bind((self.HOST,self.SENSOR_PORT))
		except socket.error, (errno,message):
			if self.SENSOR_SOCKET:
				self.SENSOR_SOCKET.close()
			#print "Server: error, failed to open sensor socket " + message
			self.logData("Error, failed to open sensor socket.")
			sys.exit() #or do we want to exit, or just ignore it?
				
	def start_listening_client(self):
		try:
			self.CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.CLIENT_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.CLIENT_SOCKET.bind((self.HOST,self.CLIENT_PORT))
		except socket.error, (errno,message):
			if self.CLIENT_SOCKET:
				self.CLIENT.SOCKET.close()
			#print "Server: error, failed to open client socket " + message
			self.logData("Error, failed to open client socket.")
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
								##print "SERVER: New client connected from (%s, %s)" % addr
								self.logData("New client connected from (%s, %s)" % addr)
								newClient = server_client_rep.Client(self,addr)
								self.clients.append(newClient)
								newClient.threading_lock.acquire(1)
								newClient.received_packet_from_client(data)
								newClient.threading_lock.release()
					
					else:
						#print "SERVER: First client connected from (%s, %s)" % addr
						self.logData("New client connected from (%s, %s)" % addr)
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
						file = open("logs/server_"+ sensorID +".log", "a")
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
						#print "SERVER: Received unknown packet"	
						self.logData("Received unknown packet from a sensor")
			
			

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
			#print("Server: following sensors read")
			#print("\t"+str(sensor_list))
			self.logData("Following sensors read from sensor.list")
			self.logData("\t" + str(sensor_list))
                        for x in sensor_list:
                                self.sensor_list.append(sensor.Sensor(x, re.search("(.*)_.*", x).group(1)))

        def stop_server(self):
                #print '\nSHUTTING DOWN SERVER ...'
		self.logData("SHUTTING DOWN SERVER ...")
                self.timerThread.stop()
                self.timerThread.join(1)
                #print 'Server shut down'
		self.logData('Server shut down')
                sys.exit(0)               

        def logData(self, msg):
                file = open("./logs/server"+".log", "a")
		file.write(str(time.time()))
		file.write("\t")
		file.write(msg)
                file.write("\n")
                file.close()

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
                                                #print("Server: timer thread sending heartbeat")
						server.logData("timer thread sending heartbeat")
                                                c.send_heartbeat()
                                                c.threading_lock.release()
                                        #if time to send packet
                                        if(c.timer_packet <= 0):
                                                c.threading_lock.acquire(1)
                                                if(len(c.current_packet.get_packet()) > 1 ):
                                                        c.prepare_to_send_packet()

                                                c.threading_lock.release()

                def stop(self):
                        self.stop = True
		
	#----------- END OF TIMER_THREAD ------------#

	#----------- END OF SERVER -----------#




def handler(signal, frame):
    a_server.stop_server()
    sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, handler)
    	global a_server
	
	if(len(sys.argv)!=4):
		#print("Server: Usage: server.py <sensor-port> <client-port> <version>")
		a_server.logData("Wrong inputs ... exiting")
		sys.exit()

    	a_server = Server(sys.argv[1], sys.argv[2], sys.argv[3])
	a_server.logData("Server starting to listen")
    	a_server.start_listening()

    	while True:           
        	signal.pause()	
			


					
