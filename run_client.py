import client


a = client.Client_ui('127.0.0.1',6006, "test")

a.sendREQ()

while(1):
	a.receive_data()


