

import socket, os, sys
import sets
import struct
import packet_settings, packet_unpacker
import packet
import threading
import time
import random
import re


#client class used in server to represent client
class Client():

	packet_seq_num = 0
	sensor_list = sets.Set([]) #list of sensors we listen to
	agg_list = [] #list of all pending aggregate requests
	current_packet = None
	client_addr =None
	client_socket = None
	server = None #pointer to the server this client belongs to
	heartbeats_sent = 0 #number of heartbeats sent
	timer_heartbeat =  packet_settings.TIME_UNTIL_HEARTBEAT #time(s) indicating when next heartbeat must be sent
	timer_packet = packet_settings.TIME_UNTIL_PACKET_SENT #time(s) indicating when the packet being formed must be sent
	threading_lock = None # used by the server class
	queue_thread_lock = None # used by the thread managing the queue.

    #variables related to congestion control
	packet_queue = []
	queue_max_len = 1
	send_history = []
	send_history_list_max_len = 5
	packet_sending_rate = 10000 ##bits per second
	bits_sent = 0
	dropped_packets = 0
        

	
	def __init__(self, server, client_addr):
		self.server = server
		self.client_addr = client_addr
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		self.packet_seq_num = int(random.SystemRandom().random()) % packet_settings.MAX_SEQ_NUM
		#self.packet_seq_num = struct.unpack(">L", self.packet_seq_num) ??
		self.threading_lock = threading.Lock()
		self.queue_thread_lock = threading.Lock() 
		self.current_packet=packet.Packet(self.packet_seq_num)
		
	##sends the packet that has been forming to the client
	def prepare_to_send_packet(self):
                #if the packet is empty, aside from the header with length 1, do nothing
                if(len(self.current_packet.get_packet())<2):
                        self.timer_packet = packet_settings.TIME_UNTIL_PACKET_SENT
                        return
                
                #increase sending rate if we have sent 10 times the max sending rate of bits
                #this is an entirly arbitrary number and we have no idea whether any of this is
                #reasonable
                if(self.bits_sent > self.packet_sending_rate * 7):
                        self.bits_sent = 0
                        #only increase rate if certain amount of dropped packets observed, to indicate we are on the bit rate limit.
                        #this avoids needles growth we are only sending at lower rates anyways. 
                        if(self.dropped_packets > 2):
                                self.dropped_packets = 0
                                self.packet_sending_rate = self.packet_sending_rate * 1.3
                #next get an answer from congestion control on what to do with the current packet
                ans=self.do_congestion_control(sys.getsizeof(self.current_packet)*8)
                #if the answer from congestion control is 0 we send the packet
                self.queue_thread_lock.acquire(1) #not perhaps necassary to lock entire function but safer this way. 
                if ans == 0:
                        #print("Server sending packet")
                        self.send_packet(self.current_packet)
                        self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM

                #if the answer is 1 we add the packet to the queue
                elif ans == 1:
                        self.packet_queue.append(self.current_packet)
                        if len(self.packet_queue == 1):
                                thread.start_new_thread(send_packet_in_queue_thread, ())
                        self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM

                #if ans == 2 we simply drop the current packet. 
                elif ans == 2:
                        #print("Congestion control says to drop packet")
                        self.dropped_packets+=1

                self.current_packet = packet.Packet(self.packet_seq_num) 
                self.timer_packet = packet_settings.TIME_UNTIL_PACKET_SENT
                self.queue_thread_lock.release()
                   
        ##a thread that sends packets in the queue when the sending rate has decreased enough.
        ## The convoluted locking scheme hopefully prevents any sync bugs
	def send_packet_in_queue_thread(self):
                
                self.queue_thread_lock.acquire(1)
                while(len(self.packet_queue)>0): #while check is always done inside lock.
                        
                        #calculate how long we need to sleep to send the next packet
                        total_bits=len(self.packet_queue[0].get_packet())*8
                        for tales in self.send_history:
                               total_bits+=tales.packet_size
                        time_future = self.send_history[0].time_sent-total_bits/self.packet_sending_rate;
                        self.queue_thread_lock.release()
                        sleep_time = time_future - time.time();
                        if sleep_time > 0:
                                time.sleep(sleep_time)
                        self.queue_thread_lock.acquire(1) # lock here again both so we send one thing at a time and to ensure poping goes smoothly   
                        self.send_packet(packet_queue.pop(0))

                self.queue_thread_lock.release()

                        
        # sends the current packet
        def send_packet(self, cur_packet):
                        num_sent=self.client_socket.sendto(cur_packet.get_packet(), self.client_addr)
                        if num_sent != len(cur_packet.get_packet()):
				server.logData("Error only part of packet sent")
                                #print("Error: only part of packet sent")
                        self.send_history.append(packet_history(time.time(), len(cur_packet.get_packet())*8))
                        self.bits_sent += len(cur_packet.get_packet())*8
                        if len(self.send_history)>5:
                                self.send_history.pop(0)
                
                        
        ##congestion control. For return values 0=send, 1=store, 2=drop
	def do_congestion_control(self, packet_size):
                #send history is short we can send immediatly
                if(len(self.send_history) < self.send_history_list_max_len ):
                        return 0;
                #if packet_queue is at max length we need to send those packets first
                #and can drop the current packet. If the max len is zero dont drop 
                if(len(self.packet_queue) == self.queue_max_len and self.queue_max_len != 0):
                        return 2;

                #however if there is space in the queue we will store the packet. 
                if(len(self.packet_queue)>0):
                        return 1;
                
                #calculate the sending rate if current packet sent
                bits = 0
                for tales in self.send_history:
                        bits = tales.packet_size;
                bits+=packet_size;
                time_dif = time.time() - self.send_history[0].time_sent
                rate_in_bps = bits / time_dif
               ##print("Congestion control: allowed bitrate = " + str(self.packet_sending_rate) + " -- proposed bitrate = " + str(rate_in_bps))
		#server.logData("Congestion control: allowed bitrate = " + str(self.packet_sending_rate) + " -- proposed bitrate = " + str(rate_in_bps))
                if(rate_in_bps < self.packet_sending_rate):
                        return 0
                #if we reach here it means max queue len is zero and we cant send the packet
                #so we drop it
		return 2
        
	
	
	## called when we received a packet from a client
	def received_packet_from_client(self, packet):
		#print("Received a packet")
		unpacker = packet_unpacker.Packet_unpacker() #unpack the packet
		packet = unpacker.unpack(packet)
		position = 3
		self.heartbeats_sent = 0
		self.timer_heartbeat = packet_settings.TIME_UNTIL_HEARTBEAT
		while position < len(packet):
			if(packet[position] == packet_settings.TYPE_ACK):
				#Dont think we need to implement anything here since ack only sent in response to heartbeat
				#and we already reset self.heartbeats_sent to zero
				#print("received ack from client") 
				server.logData("received ack from client")
				
			if(packet[position] == packet_settings.TYPE_NACK):
                                #got a nack so we will do some congestion control. This is really quite crude and a lot of problems with it.
				self.sent_bits=0;
				self.packet_sending_rate = self.packet_sending_rate * .5
				#print("Received nack from client")
			
			if(packet[position] == packet_settings.TYPE_SUB):
				# add new sensors to clients sensor list
				# remember to check options bit in case of prior subscription
				if(packet[position+1] == 1): 	
					self.sensor_list.clear()
				#parse sensor from data field
				sensor_subs = packet[position+3].split("\n")
				#print("received subs"+ str(sensor_subs))
				#append parsed sensor to sensor list
				replyData=""
				
				for x in sensor_subs:
					if x not in self.sensor_list:
						sensor_found = 0
						for y in self.server.sensor_list:
							if(y.sname == x):
								sensor_found = 1
								break
						if sensor_found == 0:
							continue
						self.sensor_list.add(x) 
						replyData = replyData + x +"\n" 
				#print("Received subs from clients " + str(sensor_subs))
				self.add_ack(replyData, True)
			
			if(packet[position] == packet_settings.TYPE_UNSUB):
				# remove sensors from clients sensor list
				# remember to check options bit for remove all sensors bit
				if(packet[position+1] == 1): 
					self.sensor_list.clear()
					#print("Received unsub for all sensors")
					
				else:
					#parse sensor(s) from data field
					sensor_unsubs = packet[position+3].split("\n")
					
					#remove parsed sensor(s) from sensor list
					self.sensor_list = [x for x in self.sensor_list if x not in sensor_unsub]
					
					# if no more sensors then delete client from server list
					if(len(self.sensor_list)==0):
						self.server.remove_client(self)
					print("Received unsub from client")
					self.add_ack("", True)
                                        
			if(packet[position] == packet_settings.TYPE_REQ):
				response=""
				for x in self.server.sensor_list:
					response += x.sname + "\n"
				self.add_data(response)	
				self.prepare_to_send_packet()
				#print("Received req from client")
				
			self.server.logData("Version: "+str(self.server.VERSION)+" packet type: " +str(packet[position]))

          		if (self.server.VERSION == 2):
		            if(packet[position] == packet_settings.TYPE_AGG):
                                    
		                    req=re.findall("(.*?);", packet[position+3])
		                    self.server.logData(str(req))
		                    if(len(req)>=3):
		                            req_id=req[0] # request id
		                            sensor_name=req[1] # sensor id
		                            agg = req[2]  # type of aggregate request
		                            sensor = None
		                            for x in self.server.sensor_list:

		                                    if sensor_name==x.sname:
		                                            sensor = x
		                                            break
		                            if sensor == None:
						   server.logData("Sensor not found.")
		                                   self.add_nack(req_id)
		                                   return
		                            if sensor.stype=="camera" or sensor.stype == "asd" or sensor.stype == "gps":
		                                    self.add_nack(req_id)
		                                    return
		                            ans=None;
		                            if agg == "min":
		                                    ans=sensor.get_min()
		                            if agg == "max":
		                                    ans=sensor.get_max()
		                            if agg == "mean":
		                                    ans=sensor.get_mean()
		                            if agg == "std":
		                                    ans=sensor.get_std()
		                                    
		                            if ans==None:
		                                   self.add_nack(req_id)
		                                   server.logData("rule not found")
		                                   return;
		                            else:
		                                	self.add_agr(req_id, sensor_name, ans)
		                                	self.server.logData("answer: " + str(ans))
                	           	    if(len(self.sensor_list)==0):
	                    				self.server.remove_client(self)
		                           
                                
                          
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
			##print("ERROR: adding heartbeat to packet resulted in DATA_TOO_LONG status code")
                        pass
			
		elif(status==packet_settings.OKAY):
			self.prepare_to_send_packet() #heartbeats are sent immediatly
			self.heartbeats_sent+=1		
		else:
			server.logData("ERROR: unknown status code returned by add_heartbeat()")
			
	

	def add_data(self, data):
		status = self.current_packet.addData(data)
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			#print("server: not enough space in client. Data length = " + str(len(data)))
			self.prepare_to_send_packet()
			self.add_data(data)
			
		elif(status==packet_settings.DATA_TOO_LONG):
                        pass
			#print("ERROR: adding data to packet resulted in DATA_TOO_LONG status code. Data length = " + str(len(data)))
			
		elif(status==packet_settings.OKAY):
			#if status okay do nothing
			pass
		
		else:
			server.logData("ERROR: unknown status code returned by add_data(self, data). status = " + str(status))

        #if send_immediatly == true the packet gets send immediatly after adding the data.
        def add_ack(self, data, send_immediatly):
		status = self.current_packet.addACK(data)
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.prepare_to_send_packet()
			self.add_ack(data, send_immediatly)
			
		elif(status==packet_settings.DATA_TOO_LONG):
			#print("ERROR: adding data to packet resulted in DATA_TOO_LONG status code")
                        pass
			
		elif(status==packet_settings.OKAY):
			if(send_immediatly):
                                self.prepare_to_send_packet()

		
		else:
			server.logData("ERROR: unknown status code returned by add_data(self, data)")



        def add_nack(self, data):
                status = self.current_packet.addNACK(data)
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.prepare_to_send_packet()
			self.add_nack(data)
		elif(status==packet_settings.DATA_TOO_LONG):
			#print("ERROR: adding data to packet resulted in DATA_TOO_LONG status code")
			pass
			
		elif(status==packet_settings.OKAY):
			return

		
		else:
			server.logData("ERROR: unknown status code returned by add_data(self, data)")

	def add_agr(self, req_id, sen_id, ans):
                status = self.current_packet.addAGR(str(req_id)+";"+str(sen_id)+";"+str(ans)+";")
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.prepare_to_send_packet()
			self.add_agr(req_id, sen_id, ans)
		elif(status==packet_settings.DATA_TOO_LONG):
			#print("ERROR: adding data to packet resulted in DATA_TOO_LONG status code")
                        pass
			
		elif(status==packet_settings.OKAY):
			return

		
		else:
			server.logData("ERROR: unknown status code returned by add_data(self, data)")

	
class packet_history:
        time_sent=0
        packet_size=0 # in bits
        def __init__(self, time_sent, packet_size):
                self.time_sent = time_sent
                self.packet_size=packet_size


class agg_req:
        req_id=0
        sensor=None
        operation=""
        params = []
        def __init__(self, req_id, sensor, operation, params):
                self.req_id=req_id
                self.sensor=sensor
                self.operation=operation
                self.params=params

