import socket, os
import packet
import packet_settings, packet_unpacker
import struct 
import re, random
import time
import signal,sys
import select

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

	def receive_data(self, timeout):
                read, write, error = select.select([self.server_socket],[],[],timeout)
                if(len(read)!=0):
                    data, server = self.server_socket.recvfrom(4096)
                    return self.received_data_from_server(data)
                else:
                    return "timeout"

	#possible chunk types: HB,DATA, ACK, , (v2 AGR, NACK)
	def received_data_from_server(self, packet):
		a_client.logData("receiving data")
                ##simulate packet loss
                if random.randint(1,20)== 20:
                        #print("client: packet lost on purpose")
                        return
                
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
                                #self.logData("Received heartbeat from server")
				self.sendACK("")
				

			if(packet[position] == packet_settings.TYPE_DC):
                                #print("Client: received data chunk from server")
                                #self.logData("Received data chunk from server")
				#write received data to log
				self.logContent(packet[position+3]+"\n")
                                
				if result == None: #DC = response to REQ
					return([packet_settings.TYPE_DC] + packet[position+3].split("\n"))

				
			
			if(packet[position] == packet_settings.TYPE_AGR):
				#print("Client: received agr chunk from server")
				self.logData("AGR : Packet Content: " + packet[position+3] )


			position+=4 #next chunk
		return(None)


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
    simtime = 180 #seconds
    start = time.time()
    version = args[4];
    a_client = Client_ui(args[2],int(args[3]), args[1])
    a_client.logData(str(args))
    sensor_list = []
    while(True): #ask for sensor list
        a_client.sendREQ()
        sensor_list=a_client.receive_data(5)
        a_client.logData("Sent sensor list request, received : "+ str(sensor_list))
        if(sensor_list!="timeout"): break
        
    while(True): #subscibe to all sensors
        ackn = []
        a_client.sendSUB("\n".join(sensor_list[1:-1]),0)
        ackn = a_client.receive_data(10)
        if(ackn!="timeout"): break

    periodic = time.time()
    while(True): #start receiving packets
        if(time.time() - start > simtime): #if simtime over send unsub and exit
            a_client.sendUNSUB('', 1)
            return;
        if(time.time()-periodic > 5 and version == "2"): #if version two send occasional aggregate data requests. 
            rand = random.randint(0,len(sensor_list)-1)
            #data='1234:'+sensor_list[rand] + ';mean;'
            data='1234;'+"temp_0" + ';mean;'
            a_client.sendAGG(data);
            periodic=time.time()
        a_client.receive_data(20)
        

            
def handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)


    if(len(sys.argv) !=5 ):
	print("Error. Usage: <name> <server_ip> <server_port> <version_num> ")
	sys.exit(0)
    else:
	start_client(sys.argv)
	while True:           
            signal.pause()

        























