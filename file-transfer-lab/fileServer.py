import sys, os, socket, threading, re, time, logging

class Server():
    
    defList = (
        (('127.0.0.1', 10000), 'server0'),
        (('127.0.0.20', 10000), 'server1'))

    clientList = dict()
    
    def __init__(self, name, host, port, loglvl=logging.DEBUG):
        self.name = name
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.loglvl = loglvl
        self.buf = b''
        self.bufMax = 128

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
            
        while(len(self.buf) + 8 < self.bufMax):
            data = conn.recv(8)
            
            if not data:
                logging.debug("%s: empty receive" % self.name)
                break
            else:
                logging.debug("%s: received '%s'" % (self.name, data))
                self.buf += data

        Server.clientList[addrStr] = self.buf
        self.buf = b''
        print(Server.clientList[addrStr])

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
