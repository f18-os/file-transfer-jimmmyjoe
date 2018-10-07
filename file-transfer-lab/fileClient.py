import sys, os, socket, re, logging

class Client():

    defServer = ('127.0.0.1', 10000)
    testFiles = ['raven1.txt',
                 'abcdefg.txt',
                 'hardtoparse.txt']

    def __init__(self, name, host, port, loglvl=logging.INFO):
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
            logging.info("%s: connected to server %s" % (self.name, svrAddr))
        except:
            logging.error("%s: failed to connect to %s" % (self.name, svrAddr))
            self.sckt.close()
            self.sckt = None

    # deprecated
    def send(self, fname, string):
        l = str(len(string))
        fstring = l+':'+fname+':'+string
        fstring = fstring.encode('UTF-8')
        self.sckt.sendall(fstring)

    def put(self, fname):
        logging.info("%s: sending %s" % (self.name, fname))
        try:
            with open(fname) as putfile:
                fileStr = putfile.read()
        except:
            logging.error("%s: could not read %s" % (self.name, fname))
            sys.exit(1)

        si = re.search('\.', fname).start()
        if si:
            logging.debug("%s: stripping extension from %s" % (self.name, fname))
            fname = fname[:si]
            
        lfile = str(len(fileStr))
        fstring = lfile+':'+fname+':'+fileStr
        self.sckt.sendall(fstring.encode('UTF-8'))

def main():
    
    client0 = Client('fileClient0', '127.0.0.20', 11000)
    if client0.sckt is not None:
        client0.connect(Client.defServer)
        client0.put(Client.testFiles[0])
    
    client1 = Client('fileClient1', '127.0.0.40', 13000)
    if client1.sckt is not None:
        client1.connect(Client.defServer)
        client1.put(Client.testFiles[1])

    client2 = Client('fileClient2', '127.0.0.60', 20000)
    if client2.sckt is not None:
        client2.connect(Client.defServer)
        client2.put(Client.testFiles[2])

if __name__ == '__main__':
    main()
