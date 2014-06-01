

import socket, os, sys
import sets
import struct
import packet_settings, packet_unpacker
import packet
import threading
import time

#client class used in server to represent client
class Client():

	packet_seq_num = 0
	sensor_list = sets.Set([]) #list of sensors we listen to
	current_packet = None
	client_addr =None
	client_socket = None
	server = None #pointer to the server this client belongs to
	heartbeats_sent #number of heartbeats sent
	timer_heartbeat =  packet_settings.TIME_UNTIL_HEARTBEAT #timer indicating when next heartbeat must be sent
	timer_packet = packet_settings.TIME_UNTIL_PACKET_SENT #time indicating when the packet being formed must be sent
	threading_lock = None # used by the server class
	queue_thread_lock = None # used by the thread managing the queue.

        #variables related to congestion control
        packet_queue = []
	queue_max_len = 1;
	send_history = []
	send_history_list_max_len = 5;
        packet_sending_rate = 100000 ##bits per second 
 

	
	def __init__(self, server, client_addr):
		self.server = server
		self.client_addr = client_addr
		self.client_socket = socket(socket.AF_INET6, socket.SOCK_DGRAM)
		
		self.packet_seq_num = os.urandom(4) % packet_settings.MAX_SEQ_NUM
		self.packet_seq_num = struct.unpack(">L", packet_seq_num)
		self.threading_lock = threading.Lock()
		self.queue_thread_lock = threading.Lock() 

		
	##sends the packet that has been forming to the client
	def prepare_to_send_packet(self):
                
                ans=self.do_congestion_control(sys.getsizeof(self.current_packet)*8)
                #if the answer from congestion control is 0 we send the packet
                self.queue_thread_lock.acquire(1) #not perhaps necassary to lock entire function but safer this way. 
                if ans == 0:
                        
                        self.send_packet(self.current_packet)
                        self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM
                        self.current_packet = packet.Packet(self.packet_seq_num) 
                        self.timer_packet = packet_settings.TIME_UNTIL_PACKET_SENT
                #if the answer is 1 we add the packet to the queue
                elif ans == 1:
                        self.packet_queue.append(self.current_packet)
                        if len(self.packet_queue == 1):
                                thread.start_new_thread(send_packet_in_queue_thread, ())
                        self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM
                        self.current_packet = packet.Packet(self.packet_seq_num) 
                        self.timer_packet = packet_settings.TIME_UNTIL_PACKET_SENT
                #if ans == 2 we simply drop the current packet. 
                else ans == 2:
                        
                        self.current_packet = packet.Packet(self.packet_seq_num) 
                        self.timer_packet = packet_settings.TIME_UNTIL_PACKET_SENT   
                self.queue_thread_lock.release()
                   
        ##a thread that sends packets in the queue when the sending rate has decreased enough
	def send_packet_in_queue_thread(self):
                while(len(self.packet_queue)>0):
                        #calculate how long we need to sleep to send the next packet
                        self.queue_thread_lock.acquire(1) # lock here so queue isnt changed while we count
                        total_bits=sys.getsizeof(self.packet_queue[0])
                        for tales in self.send_history:
                               total_bits+=tales.packet_size
                        time_future = self.send_history[0].time_sent-total_bits/self.packet_sending_rate;
                        self.queue_thread_lock.release()
                        sleep_time = time_future - time.time();
                        if sleep_time > 0:
                                time.sleep(sleep_time)
                        self.queue_thread_lock.acquire(1) # lock here again both so we send one thing at a time
                                                          # and to ensure poping goes smoothly
                        send_packet(packet_queue.pop(0))
                        self.queue_thread_lock.release()

                        
        # sends the current packet
        def send_packet(self, packet):
                        num_sent=self.client_socket.sendto(self.packet.get_packet(), self.client_addr)
                        if num_sent != len(self.current_packet.get_packet()):
                                print("Error: only part of packet sent")
                        self.send_history.append(packet_history(time.time(), sys.getsizeof(packet)*8))
                        if(len(send_history>5)):
                                self.send_history.pop(0)
                
                        
        ##congestion control. For return values 0=send, 1=store, 2=drop
	def do_congestion_control(self, packet_size):
                #send history has nothing in it we can send immediatly
                if(len(self.send_history) ==0 ):
                        return 0;
                #if packet_queue is at max length we need to send those packets first
                #and can drop the current packet. If the max len is zero dont drop 
                if(len(self.packet_queue)== queue_max_len && queue_max_len != 0):
                        return 2;

                #however if there is space in the queue we will store the packet. 
                if(len(self.packet_queue)>0):
                        return 1;
                
                #calculate the sending rate if current packet sent
                bits_sent = 0
                for tales in self.packet_history:
                        bits_sent = tales.packet_size;
                bits_sent+=packet_size;
                time_dif = time.time() - self.packet_history[0].time_sent
                rate_in_bps = bits_sent / time_dif
                if(rate_in_bps < packet_sending_rate):
                        return 0
                #if we reach here it means max queue len is zero and we cant send the packet
                #so we drop it
		return 2
        
	
	
	## called when we received a packet from a client
	def received_packet_from_client(self, packet):
		unpacker = packet_unpacker.Packet_unpacker() #unpack the packet
		packet = unpacker.unpack(packet)
		position = 3
		self.heartbeats_sent = 0
		self.timer_heartbeat = packet_settings.TIME_UNTIL_HEARTBEAT
		while position < len(packet):
			if(packet[position] == packet_settings.TYPE_ACK):
				#Dont think we need to implement anything here since ack only sent in response to heartbeat
				#and we already reset self.heartbeats_sent to zero
				print("received ack from client") 
				
			if(packet[position] == packet_settings.TYPE_NACK):
				### TODO put congestion control here
				print("Received nack from client")
				
				
			if(packet[position] == packet_settings.TYPE_SUB):
				# add new sensors to clients sensor list
				# remember to check options bit in case of prior subscription
				if(packet[position+1] == 1) 	
					self.sensor_list.clear()
				#parse sensor from data field
                                sensor_subs = packet[position+3].split("\n")
				#append parsed sensor to sensor list
                                replyData=""
                                for x in sensor_subs:
                                        if x not in self.sensor_list:
                                               self.sensor_list.append(x) 
                                               replyData = replyData + x +"\n" 
                                print("Received subs from clients " + sensor_subs)
                                add_ack(data, True)
				
			if(packet[position] == packet_settings.TYPE_UNSUB):
				# remove sensors from clients sensor list
				# remember to check options bit for remove all sensors bit
				if(packet[position+1] == 1) 
					self.sensor_list.clear()
					print("Received unsub for all sensors")
					
				else:
                                        #parse sensor(s) from data field
                                        sensor_unsubs = packet[position+3].split("\n")
                                        
                                        #remove parsed sensor(s) from sensor list
                                        self.sensor_list = [x for x in self.sensor_list if x not in sensor_unsub]

                                        # if no more sensors then delete client from server list
                                if(len(self.sensor_list)==0)
                                        self.server.remove_client(self)
                                        print("Received unsub from client")
                                add_ack("", True)
                                                
                      if(packet[position] == packet_settings.TYPE_REQ):
                               ###TODO: return the list of all sensors
                               print("Received req from client")
			
			#increment our position in the list by four to get to the next chunk 
			position+=4

	## called when the server class the owns this client class has a packet from a sensor
	def received_packet_from_sensor(self, sensor, data):
		if sensor in self.sensor_list:	# check if the sensor is in the sensor list
			self.add_data(data) #add the data to the current packet. 
			return
	
		
	## sends a heartbeat to the client
	def send_heartbeat(self):
		status=self.current_packet.addHeartBeat("")
		
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.prepare_to_send_packet()
			self.send_heartbeat()
			
		elif(status==packet_settings.DATA_TOO_LONG):
			print("ERROR: adding heartbeat to packet resulted in DATA_TOO_LONG status code")
			
		elif(status==packet_settings.OKAY):
			self.prepare_to_send_packet() #heartbeats are sent immediatly
			self.heartbeats_sent+=1		
		else:
			print("ERROR: unknown status code returned by add_heartbeat()")
			
	

	def add_data(self, data):
		status = self.current_packet.addData(data)
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.prepare_to_send_packet()
			self.add_data(data)
			
		elif(status==packet_settings.DATA_TOO_LONG):
			print("ERROR: adding data to packet resulted in DATA_TOO_LONG status code")
			
		elif(status==packet_settings.OKAY):
			#if status okay do nothing
			pass
		
		else:
			print("ERROR: unknown status code returned by add_data(self, data)")

        #if send_immediatly == true the packet gets send immediatly after adding the data.
        def add_ack(self, data, send_immediatly):
		status = self.current_packet.addACK(data)
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.prepare_to_send_packet()
			self.add_ack(data, send_immediatly)
			
		elif(status==packet_settings.DATA_TOO_LONG):
			print("ERROR: adding data to packet resulted in DATA_TOO_LONG status code")
			
		elif(status==packet_settings.OKAY):
			if(send_immediatly):
                                self.prepare_to_send_packet()

		
		else:
			print("ERROR: unknown status code returned by add_data(self, data)")





	
class packet_history:
        time_sent=0;
        packet_size=0; # in bits
        def __init__(self, time_sent, packet_size):
                self.time_sent = time_sent
                self.packet_size=packet_size