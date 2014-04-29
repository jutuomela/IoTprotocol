
import socket
import sys
import re
import client
import select
import threading, time


class Server(): 

	SENSOR_PORT = 6005
	CLIENT_PORT = 6006
	HOST = None #'127.0.0.1' localhost is it ok?
	CLIENT_SOCKET = None
	SENSOR_SOCKET = None
	TIMER_INTERVAL = 2

	thread_lock = None #lock for synchronization
	
	clients = []## list of clients		## need to add clients
	
	def __init__(self,host):
		self.HOST = host
		self.thread_lock = threading.Lock()
	
	def start_listening_sensor(self):
		try:
			self.SENSOR_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.SENSOR_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.SENSOR_SOCKET.bind((self.HOST,self.SENSOR_PORT))
		except socket.error, (errno,message):
			if self.SENSOR_SOCKET:
				self.SENSOR_SOCKET.close()
			print "Failed to open socket " + message
			sys.exit() #or do we want to exist, or just ignore it?
				
	def start_listening_client(self):
		try:
			self.CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.CLIENT_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.CLIENT_SOCKET.bind((self.HOST,self.CLIENT_PORT))
		except socket.error, (errno,message):
			if self.CLIENT_SOCKET:
				self.CLIENT.SOCKET.close()
			print "Failed to open socket " + message
			sys.exit() #or do we want to exist, or just ignore it?

	
	def start_listening(self):
		
		self.start_listening_sensor()
		self.start_listening_client()
		
		
		CONNECTION_LIST = []
		
		CONNECTION_LIST.append(self.CLIENT_SOCKET)
		CONNECTION_LIST.append(self.SENSOR_SOCKET)

		self.timerThread = timer_Thread(self.clients)
		timerThread.start()
		
		while 1:
			
			read,write,error = select.select(CONNECTION_LIST,[],[])
			
			for sock in read:
				
				if sock == self.CLIENT_SOCKET:
					data,addr = self.CLIENT_SOCKET.recvfrom(2048)
					print "SERVER: Client connected from (%s, %s)" % addr 							#for testing 
					for c in self.clients:
						if c.client_addr == addr:
                                                        c.threading_lock.acquire(1)
							c.received_packet_from_client(data)
							c.threading_lock.release()
							break
						elif self.clients[-1] == c:
                                                        newClient = client(addr)
							self.clients.append(newClient)
							newClient.threading_lock.acquire(1)
							newClient.received_packet_from_client(data)
                                                        newClient.threading_lock.release()
					
				
				if sock == self.SENSOR_SOCKET:
					data,addr = self.SENSOR_SOCKET.recvfrom(2048)
					print "SERVER: Sensor connected from (%s, %s)" % addr							#for testing 
					print "SERVER: " + data
					result = re.search("'dev_id': '(.*)', 'sensor_data'",data)
					
					if result != None:
						sensorID = result.group(1)
					
						for c in self.clients:
                                                        client.threading_lock.acquire(1)
							c.received_packet_from_sensor(sensorID, data)
							client.threading_lock.release(1)
					else:
						print "SERVER: Received unknown packet"	
			
			
			
	def remove_client(self,client):
		self.clients.remove(client)
			
	#thread that will handle the timers in each client
	class timer_Thread(threading.Thread):
                
                clients = None
                
                def __init__(self, clientList):
                        threading.Thread.__init__(self)
                        self.clients = clients

                def run(self):
                        time.sleep(TIMER_INTERVAL)
                        for c in clients:
                                c.timer_heartbeat=-TIMER_INTERVAL
                                c.timer_packet=-TIMER_INTERVAL
                                #if time to send heartbeat
                                if(c.timer_heartbeat <= 0):
                                        c.threading_lock.acquire(1) #each client has a lock for sync
                                        c.send_heartbeat()
                                        c.threading_lock.release()
                                #if time to send packet
                                if(c.timer_packet <= 0):
                                        c.threading_lock.acquire(1)
                                        c.send_packet()
                                        c.threading_lock.release()

                                        
                                
					
			
					
