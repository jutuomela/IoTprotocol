import server
import signal

a_server=None

def start_server():
    global a_server
    a_server = server.Server('127.0.0.1')
    a_server.start_listening()


def handler(signal, frame):
    a_server.stop_server()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    start_server()
    while True:           
        signal.pause()

        
