import sys, os, socket, re, logging

global_fileDB = dict()

class Client():

    defServer = ('127.0.0.1', 10000)
    testFiles = ['raven1.txt',
                 'abcdefg.txt',
                 'hardtoparse.txt']

    def __init__(self, name, host, port, loglvl=logging.INFO):
        self.name = name
        self.host = host
        self.port = port
        self.buf = ''
        self.addr = (host, port)
        self.loglvl = loglvl
        
        logging.basicConfig(
            level=self.loglvl,
            format='%(levelname)s %(message)s'
        )


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

    def getBack(self, fileStr):
        global global_fileDB
        fstring = '0'+':'+fileStr+':'+''
        fstring = fstring.encode('UTF-8')
        # send 0:<name>:<empty str>
        logging.info("%s: requesting file %s" % (self.name, fileStr))
        self.sckt.sendall(fstring)

        pid = os.fork()

        if pid == 0: # child
            self.sckt.settimeout(5)

            while True:

                try:
                    conn, addr = self.sckt.accept()
                except socket.timeout:
                    break
                
                chunk = self.sckt.recv(32)
                
                if chunk is None:
                    break

                logging.debug("%s(%d): received %s" % (self.name, pid, chunk))
                self.buf += chunk

            logging.info("%s(%d): received %s" % (self.name, pid, self.buf))
            global_fileDB['test'] = self.buf
            
        else: # parent
            cpid = os.wait()
                    

def main():
    
    client0 = Client('fileClient0', '127.0.0.20', 11000)
    if client0.sckt is not None:
        client0.connect(Client.defServer)
        client0.put(Client.testFiles[0])
    
    client1 = Client('fileClient1', '127.0.0.40', 13000)
    if client1.sckt is not None:
        client1.connect(Client.defServer)
        client1.put(Client.testFiles[1])

    client2 = Client('fileClient2', '127.0.0.60', 20000, logging.DEBUG)
    if client2.sckt is not None:
        client2.connect(Client.defServer)
        client2.put(Client.testFiles[2])
        
        client2.getBack(Client.testFiles[1])

if __name__ == '__main__':
    main()
