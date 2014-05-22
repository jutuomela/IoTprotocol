
import packet
import packet_unpacker

new_packet = packet.Packet(11111111)
new_packet.addData("hello. this is test1")
new_packet.addData("hi. this is test2")
new_packet.addHeartBeat("")
new_packet.addNACK("")
packed_packet = new_packet.get_packet()
unpacker = packet_unpacker.Packet_unpacker()
unpacked_packet = unpacker.unpack(packed_packet)
print(unpacked_packet)