import sys, os, socket, threading, re, time, logging

class Server():
    # key = file name as str
    # val = file as str
    SERVER_DB = dict()

    # Lock for accessing SERVER_DB
    lock = threading.Lock()

    # Regex for handshake
    filePat  = r'^(?P<length>\d+):(?P<name>\w+):(?P<data>.*)'
    
    def __init__(self, name, host, port, loglvl=logging.INFO):
        self.name = name
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.loglvl = loglvl
        logging.basicConfig(level=self.loglvl, format='%(levelname)s %(message)s')

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

        if self.sckt is None:
            logging.error("%s: failed to bind" % self.name)
            sys.exit(1)

        logging.info("%s: listening on %s" % (self.name, self.addr))
        self.sckt.listen(2)
        
    def parseFirst(data):
       match = re.match(Server.filePat, data)
       if match:
           size = int(match.group('length'))
           name = match.group('name')
           data  = match.group('data')
           return size, name, data
       else:
           return None # no match
    
    class ClientHandler(threading.Thread):
        
        activeThreads = 0
        totalThreads = 0
        
        def __init__(self, sock, cliAddr):
            threading.Thread.__init__(self, daemon=True)
            
            with Server.lock.acquire():
                self.name = 'CH' + str(Server.ClientHandler.totalThreads)
                Server.ClientHandler.activeThreads += 1
                Server.ClientHandler.totalThreads += 1
            
            self.pid = os.getpid() # same for all threads
            self.sock = sock
            self.cliAddr = cliAddr
            self.buf = ''
            
            self.start()
            
        def run(self):
            # encourage race condition
            time.sleep(0.01)
            self.handleClient()
            
        def handleClient(self):
            m, start = 0.0, time.time() # double for division later
            while True:
                data = self.sock.recv(32).decode('UTF-8') # hopefully 32 bytes is enough for fname
            
                if not data: # empty or EOF
                    lstr = len(self.buf)
                    if lstr == size:
                        logging.info("%s(%d):%d/%d bytes received from %s at %.2f byte/sec" % (self.name, self.pid, lstr, size, self.cliAddr, m/(time.time() - start)))
                    else:
                        logging.warning("%s(%d): expected %d bytes from %s, got %d bytes" % (self.name, pid, size, self.cliAddr, lstr))
                    break

                if m == 0.0: # first iteration, should have clues
                    try:
                        size, fname, first = Server.parseFirst(data)
                        logging.debug("%s(%d): expecting %d bytes in %s from %s" % (self.name, self.pid, size, fname, self.cliAddr))
                        logging.debug("%s(%d): received '%s' from %s" % (self.name, self.pid, first, self.cliAddr))
                    except:
                        logging.error("%s(%d): bad parse" % (self.name, self.pid))
                        break
                    
                    with Server.lock:
                        if fname in Server.SERVER_DB.keys(): # race condition
                            logging.info("%s(%d): file %s already exists" % (self.name, self.pid, fname))
                            break
                        else:
                            Server.SERVER_DB[fname] = '' # initialize entry
                            logging.info("%s(%d): reserving space for %s" % (self.name, self.pid, fname))
                            
                    self.buf += first
                    m += 1.0
                
                else: # normal case
                    logging.debug("%s(%d): received '%s' from %s" % (self.name, self.pid, data, self.cliAddr))
                    self.buf += data
                    m += 1.0

            self.sock.close()
            with Server.lock:
                logging.debug("%s(%d): finished handling client %s" % (self.name, self.pid, self.cliAddr))
                if(len(self.buf) != 0):
                    Server.SERVER_DB[fname] = self.buf
                Server.ClientHandler.activeThreads += -1
            self.buf = ''

def main():
    listener = Server('fileServer', '127.0.0.1', 10000, logging.INFO)
    listener.sckt.settimeout(10)
    while True:
        try:
            conn, cliAddr = listener.sckt.accept()
            listener.ClientHandler(conn, cliAddr)
        except socket.timeout:
            print('fileServer timed out')
            break

    print(listener.SERVER_DB)

if __name__ == '__main__':
    main()
