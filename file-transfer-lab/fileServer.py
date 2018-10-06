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
        try: # bind to arg
            logging.debug("%s: binding to %s" % (self.name, self.addr))
            self.sckt.bind(self.addr)
        except: # try other ports
            logging.debug("%s: failed to bind to %s" % (self.name, self.addr))
            for prt in range(port, port + 100):
                try:
                    self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sckt.bind((self.host, prt))
                except:
                    self.sckt.close()
                    self.sckt = None

        logging.debug("%s: listening on %s" % (self.name, self.addr))
        self.sckt.listen(2)
        
    def clientHandler(self, conn, addr):
        addrStr = addr[0] + ':' + str(addr[1])
        
        if not addrStr in Server.clientList:
            logging.debug("%s: registering client %s" % (self.name, addr))
            Server.clientList[addrStr] = ''
        else:
            logging.debug("%s: old client" % self.name)
            sys.exit(0)
            
        m, start = 0.0, time.time()
        while(len(self.buf) + 8 < self.bufMax):
            data = conn.recv(8).decode('UTF-8') #string
            
            if not data:
                logging.debug("%s: empty receive" % self.name)
                break

            if m == 0.0: # first iteration, should have clues
                try:
                    size, first = Server.getLength(data)
                    logging.debug("%s: %d byte file" % (self.name, size))
                except:
                    logging.debug("%s: bad getLength" % self.name)
                    sys.exit(1)

                self.buf += first
                m += 1.0
                
            else: # normal case
                logging.debug("%s: received '%s'" % (self.name, data))
                self.buf += data
                m += 1.0
                
        logging.debug("%s: %.2f byte/sec" % (self.name, m/(time.time() - start)))

        # str after done
        Server.clientList[addrStr] += self.buf
        self.buf = ''
        print(Server.clientList[addrStr])

    def getLength(data):        
        match = re.match(Server.pattern, data)
        if not match:
            return None
            
        try:
            size = int(match.group('length'))
        except:
            return None
                
        data = match.group('data')
        return (size, data)

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
