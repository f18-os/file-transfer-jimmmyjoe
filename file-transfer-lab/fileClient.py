import sys, os, socket, logging

class Client():

    defServer = ('127.0.0.1', 10000)

    def __init__(self, name, host, port, loglvl=logging.DEBUG):
        self.name = name
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.loglvl = loglvl
        
        logging.basicConfig(level=self.loglvl)

        for port in range(self.port, self.port + 100):
            try:
                self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sckt.bind((self.host, port))
                logging.debug("%s: bound to port %d" % (self.name, port))
                break
            except:
                logging.debug("%s: port %d unavailable" % (self.name, port))
                self.sckt.close()
                self.sckt = None
                continue
            
    def connect(self, svrAddr):
        try:
            self.sckt.connect(svrAddr)
            logging.debug("%s: connected to %s" % (self.name, svrAddr))
        except:
            logging.debug("%s: failed to connect to %s" % (self.name, svrAddr))
            self.sckt.close()
            self.sckt = None

    def send(self, data):
        self.sckt.sendall(data)

def main():
    client = Client('fileClient', '127.0.0.20', 11000)
    client.connect(Client.defServer)
    data = 'HHLLEEHLE!'*100
    dlen = str(len(data))
    data = dlen+','+data
    client.send(data.encode('UTF-8'))

if __name__ == '__main__':
    main()
