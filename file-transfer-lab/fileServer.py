import sys, os, socket, threading, re, time, logging

class Server():
    
    defList = (
        (('127.0.0.1', 10000), 'server0'),
        (('127.0.0.20', 10000), 'server1'))

    clientList = dict()

    pattern = r'^(?P<length>\d+),(?P<data>.*)'
    
    def __init__(self, name, host, port, loglvl=logging.DEBUG):
        self.name = name
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.loglvl = loglvl
        self.buf = ''
        self.bufMax = 512

        logging.basicConfig(level=self.loglvl)
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            logging.debug("%s: binding to %s" % (name, self.addr))
            self.sckt.bind(self.addr)
        except:
            logging.debug("%s: failed to bind to %s" % (name, self.addr))
            self.sckt.close()
            self.sckt = None
            sys.exit(1)

        logging.debug("%s: listening on %s" % (self.name, self.addr))
        self.sckt.listen(2)
        
    def clientHandler(self, conn, addr):
        addrStr = addr[0] + ':' + str(addr[1])
        
        if not addrStr in Server.clientList:
            logging.debug("%s: registering client %s" % (self.name, addr))
            Server.clientList[addrStr] = ''
        else:
            logging.debug("%s: client already helped" % self.name)
            sys.exit(0)
            
        m, start = 0.0, time.time()
        while(len(self.buf) + 8 < self.bufMax):

            #string
            data = conn.recv(8).decode('UTF-8')
            
            if not data:
                logging.debug("%s: empty receive" % self.name)
                break

            if m == 0.0: # first iteration, should have clues
                try:
                    size, payl = Server.getLength(self.name, data)
                except:
                    logging.debug("%s: bad getLength" % self.name)
                    
                print("%s: pattern=%s, data=%s" % (self.name, Server.pattern, data))
                match = re.match(Server.pattern, data)
                if not match:
                    logging.error("%s: bad handshake with %s" % (self.name, addr))
                    conn.close()
                    conn = None
                    sys.exit(1)
                    
                try:
                    size = int(match.group('length'))
                except:
                    logging.error("%s: can't read length" % self.name)
                    sys.exit(1)
                    
                data = match.group('data')
                logging.info("%s: %d length file" % (self.name, size))
                self.buf += data
                m += 1.0
                
            else: # normal case
                logging.debug("%s: received '%s'" % (self.name, data))
                self.buf += data
                m += 1.0
                
        logging.debug("%s: %.2f byte/sec" % (self.name, m/(time.time() - start)))

        # str after done
        Server.clientList[addrStr] += self.buf
        self.buf = b''
        print(Server.clientList[addrStr])

    def getLength(name, data):
        print("%s: pattern=%s, data=%s" % (name,Server.pattern, data))
        
        match = re.match(Server.pattern, data)
        if not match:
            logging.error("%s: bad handshake" % name)
            return None
            
            try:
                size = int(match.group('length'))
            except:
                logging.error("%s: can't read length" % self.name)
                return None
                
            data = match.group('data')
            logging.info("%s: %d length file" % (self.name, size))
            return (size, data)
        
            #self.buf += data
            #m += 1.0

    def addClient(self, addr):
        Client.clientList.add(addr, '')

def main():

    # listen for connections
    listener = Server('fileServer', '127.0.0.1', 10000)
    
    # fork off handler for client conn and wait for more
    while True:
        conn, addr = listener.sckt.accept()

        pid = os.fork()
        
        if pid == 0: # child
            listener.clientHandler(conn, addr)
        else: # parent
            continue
                
if __name__ == '__main__':
    main()
