import sys, os, socket, threading, re, time, logging

fileDB = dict()

class Server():
    
    defList = (
        (('127.0.0.1', 10000), 'server0'),
        (('127.0.0.20', 10000), 'server1'))

    # key = host:port as string
    # val = file as str
    clientList = dict()

    # key = file name as str
    # val = file as str
    fileDB = dict()

    filePat  = r'^(?P<length>\d+):(?P<name>\w+):(?P<data>.*)'
    
    def __init__(self, name, host, port, loglvl=logging.INFO):
        self.name = name
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.loglvl = loglvl
        self.buf = ''

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

        logging.info("%s: listening on %s" % (self.name, self.addr))
        self.sckt.listen(2)

    def registerClient(addr):
        addrStr = addr[0] + ':' + str(addr[1])
        if not addrStr in Server.clientList:
            Server.clientList[addrStr] = ''
        
    def clientHandler(self, conn, addr, pid):
        Server.registerClient(addr)
        m, start = 0.0, time.time()
        while True: # could check for timeout or bufMax
            data = conn.recv(32).decode('UTF-8') #string, 32 bytes enough for fname?
            
            if not data: # empty or EOF
                Server.fileDB[name] = self.buf
                lstr = len(self.buf)
                self.buf = ''
                
                if lstr == size:
                    logging.info("%s(%d):%d/%d bytes received from %s at %.2f byte/sec" % (self.name, pid, lstr, size, addr, m/(time.time() - start)))
                else:
                    logging.warning("%s(%d): expected %d bytes from %s, got %d bytes" % (self.name, pid, size, addr, lstr))
                    
                break

            if m == 0.0: # first iteration, should have clues
                try:
                    size, name, first = Server.parseFirst(data)
                    logging.debug("%s(%d): expecting %d bytes in %s" % (self.name, pid, size, name))
                    logging.debug("%s(%d): received '%s'" % (self.name, pid, first))
                except:
                    logging.error("%s(%d): bad parse" % (self.name, pid))
                    break

                if name in Server.fileDB.keys(): # race condition or local var or both?
                    logging.info("%s: file %s already exists" % (self.name, name))
                    break

                Server.fileDB[name] = '' # initialize entry
                self.buf += first
                m += 1.0
                
            else: # normal case
                logging.debug("%s(%d): received '%s'" % (self.name, pid, data))
                self.buf += data
                m += 1.0

        conn.close()
        logging.debug("%s(%d): exiting" % (self.name, os.getpid()))
        
    def parseFirst(data):
       match = re.match(Server.filePat, data)
       if match:
           size = int(match.group('length'))
           name = match.group('name')
           data  = match.group('data')
           return size, name, data
       else:
           return None # no match

def main():
    listener = Server('fileServer', '127.0.0.1', 10000, logging.INFO)
    listener.sckt.settimeout(10)
    startTime = time.time()
    while(time.time() - startTime <= 30):
        try:
            conn, addr = listener.sckt.accept()
        except socket.timeout:
            continue

        pid = os.fork()
        
        if pid == 0: # child
            listener.clientHandler(conn, addr, os.getpid())
            sys.exit(0)
        else: # parent
            continue
        
if __name__ == '__main__':
    main()
