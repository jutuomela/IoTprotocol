
import socket
import sys





class Server: 

	PORT = 1079
	HOST = '' #localhost? 127.0.0.1
	SOCKET = None
	
	def start_listening(self):
		try:
			self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.SOCKET.bind((self.HOST,self.PORT))
			self.SOCKET.listen(5) #queue 5 connect requests, before refusing outside connections
		except socket.error, (errno,message):
			if self.SOCKET:
				self.SOCKET.close()
			print "Failed to open socket " + message
			sys.exit() #or do we want to exist, or just ignore it?
		while 1:
			#data,addr = s.recvfrom(1024)
			#
			
