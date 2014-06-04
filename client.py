import socket, os
import packet
import packet_settings, packet_unpacker
import struct 
import re, random
import time
import signal,sys	

class Client_ui(): 

	server_port = None
	server_addr = None
	server_socket = None
	packet_seq_num = 0
	last_received_seq_num = None
        name = ""


	def __init__(self,address,port, name):
		self.packet_seq_num = int(random.SystemRandom().random()) % packet_settings.MAX_SEQ_NUM
		self.server_port = port
		self.server_addr = address
		self.name = name
		self.logData(str(address)+":"+str(port) +"  name: " + name)
		try: 
			self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			
		except socket.error, (errno,message):
			self.logData("Error opening socket")
			if self.server_socket:
				self.server_socket.close()
			#print "Client: ERROR - Failed to open socket " + message
			sys.exit() #or do we want to exit, or just ignore it?

	

	def send_packet(self, packet):
		self.server_socket.sendto(packet.get_packet(), (self.server_addr,self.server_port))

	def receive_data(self):
		data, server = self.server_socket.recvfrom(4096)
		self.received_data_from_server(data)


	#possible chunk types: HB,DATA, ACK, , (v2 AGR, NACK)
	def received_data_from_server(self, packet):
		a_client.logData("receiving data")
                ##simulate packet loss
                #if random.randint(1,20)== 20:
                #        #print("client: packet lost on purpose")
                #        return
                
		unpacker = packet_unpacker.Packet_unpacker() 
		packet = unpacker.unpack(packet)
                position = 3
                
		if(self.last_received_seq_num == None):#first message
			self.last_received_seq_num = packet[2]
		elif(self.last_received_seq_num == packet_settings.MAX_SEQ_NUM-1): #sequence number limit is reached, so next number should be 0
			if(packet[2] != 0):
				self.sendNACK()
		elif(self.last_received_seq_num+1 != packet[2]): #next number should be last+1, else NACK
			self.sendNACK()
		
		
		self.last_received_seq_num = packet[2]	
	

		while(position < len(packet)):
                        
                        result = re.search("'dev_id': '(.*?)'",packet[position+3])		
                        if result != None and  len(result.groups()) > 0:
                                self.sensorID = result.group(1)
                        else:
                                self.sensorID = None
                                
			if(packet[position] == packet_settings.TYPE_ACK):
				##subscription was succesfull, datafield contains list of sensors should we retry sensors which are not listed? unsubcription was succedfull, datafield is empty
				#print("Client: received ack from server")
				self.logData("received ack from server")
			if(packet[position] == packet_settings.TYPE_HB):
				#respond with ACK, now
                                #print("Client: received heartbeat from server")
                                self.logData("Received heartbeat from server")
				self.sendACK("")

			if(packet[position] == packet_settings.TYPE_DC):
                                #print("Client: received data chunk from server")
                                self.logData("Received data chunk from server")
				#write received data to log
				self.logContent("Packet Content: " + packet[position+3])

				if result == None: #DC = response to REQ
					#subscribe to all the available sensors 
					self.sendSUB(packet[position+3], 1)
			
			if(packet[position] == packet_settings.TYPE_AGR):
				#print("Client: received data chunk from server")
				self.logData("Received aggregate from server - Packet Content: " + packet[position+3] )


			position+=4 #next chunk


        def logData(self, msg):
                file = open("./logs/client"+"."+self.name+".log", "a")
		file.write(str(time.time()))
		file.write("\t")
		file.write(msg)
                file.write("\n")
                file.close()

        def logContent(self, msg):
                if self.sensorID == None:
                        return
                file = open("./logs/client"+"."+self.name+"_" + self.sensorID +".log" , "a")
		file.write(msg)
                file.write("\n\n")
                file.close()

	def sendACK(self,data):
                self.logData("Sending ACK")
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addACK(data)
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM

	def sendNACK(self):
                self.logData("Sending NACK")
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addNACK("")
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM
	
	def sendSUB(self,data,option): #data: sensors, option: initial/or not
                self.logData("Sending SUB")
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addSub(data,option)
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM	
	
	def sendUNSUB(self,data,option):
                self.logData("Sending UNSUB")
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addUnSub(data,option)
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM	
			
	def sendREQ(self):
                self.logData("Sending REQ")
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addREQ("")
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM	
			
	def sendAGG(self,data):
                self.logData("Sending AGG")
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addAGG(data)
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM




a_client=None

def start_client(args):
    global a_client 
    #a_client = server.Server('127.0.0.1')
    #a_client.start_listening()
    simtime = 160
    start = time.time()
 
    a_client = Client_ui(args[2],int(args[3]), args[1])
    a_client.logData(str(args))
    if(args[4] == "1"):

	    if(len(args) == 5):	#no sensor ids given, req sensor list from server and subscribe to all
		a_client.logData("client started and sending req")
		a_client.sendREQ()
	    else:
		length = len(args)
		i = 5 
		data=""

		while i < length:
			data += args[i] + "\n"
			i+=1
		a_client.logData(str(data))
		a_client.sendSUB(data,1)
    else:
	    if(len(args) == 5):	#no sensor ids given, req sensor list from server and subscribe to all
		a_client.logData("client started and sending req V2")
		a_client.sendREQ()
	    else:
		
		data = '1234;' + args[5] + ';mean;'
		a_client.sendAGG(data)	
		length = len(args)
		i = 5
		data1=""
		while i < length:
			data1 += args[i] + "\n"
			i+=1
		a_client.sendSUB(data1,0)
	
    while(1):
	a_client.receive_data()
	if(time.time() - start >= simtime):
		a_client.sendUNSUB('',1)	#unsub all



def handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)


    if(len(sys.argv) < 5):
	print("Too few arguments. Usage: <name> <server_ip> <server_port> <version_num> <[list of sensor ids]>")
	sys.exit(0)
    else:
	start_client(sys.argv)
	while True:           
            signal.pause()

        



#python, name, server_ip, server_port, [list of sensor ids] temp_0, temp_1





















