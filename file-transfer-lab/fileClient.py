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
                logging.debug("%s: bound to %s" % (self.name, (self.host, port)))
                break
            except:
                logging.debug("%s: port %d unavailable" % (self.name, port))
                self.sckt.close()
                self.sckt = None
                continue
            
        if self.sckt is None:
            logging.error("%s: socket failure" % self.name)
            return None
            
    def connect(self, svrAddr):
        try:
            self.sckt.connect(svrAddr)
            logging.debug("%s: connected to %s" % (self.name, svrAddr))
        except:
            logging.debug("%s: failed to connect to %s" % (self.name, svrAddr))
            self.sckt.close()
            self.sckt = None

    def send(self, data):

        def formatStr(string):
            l = str(len(string))
            data = l+','+string
            data = data.encode('UTF-8')
            return data

        if isinstance(data, str):
            fdata = formatStr(data)
            self.sckt.sendall(fdata)
            pass
        elif isinstance(data, file):
            sendFile(data)
            pass
        else:
            pass

    def sendFile(file):
        pass

def main():
    
    client0 = Client('fileClient0', '127.0.0.20', 11000)
    if client0.sckt is not None:
        client0.connect(Client.defServer)
        client0.send('Fifty'*50)
    
    client1 = Client('fileClient1', '127.0.0.40', 13000)
    if client1.sckt is not None:
        client1.connect(Client.defServer)
        client1.send('Hi'*30)

    client2 = Client('fileClient2', '127.0.0.60', 20000)
    if client2.sckt is not None:
        client2.connect(Client.defServer)
        client2.send('Twenty'*20)

if __name__ == '__main__':
    main()
