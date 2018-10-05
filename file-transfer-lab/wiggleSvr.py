import sys, os, re, socket, threading, time

name = 'wiggleSvr'
# list comprehension
defList = (
(('127.0.0.1', 6000), 'server0'),
(('127.0.0.20', 6001), 'server1'))
buffer = b''
        
def main():
    global name, buffer
    # parse args
    listener = startServer()
    if listener is None:
        print("%s: socket failure" % name)
        sys.exit(1)

    pid = os.fork()
    
    if pid == 0: # child / client
        name = 'wiggleCli'
        cliAddr = ('127.0.0.50', 7000)
        svrAddr = listener.getsockname()
        client = testClient('wiggleCli', cliAddr, svrAddr)
        if client is None:
            print("%s: socket failure" % name)
            sys.exit(1)

        client.sendall(b'Hello World!')
        client.close()
        sys.exit(0)
        
    else: # parent / server
        conn, cliAddr = listener.accept()
        with conn:
            while(True):
                chunk = handleConnection(conn, cliAddr)
                if not chunk:
                    conn.close()
                    break
                print("%s: received %s" % (name, chunk))

def startServer():
    global name, defList
    failCount = 0
    listening = False
    for svr in defList:
        listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("%s: attempting listen on %s" % (name, svr))
            listenSock.bind(svr[0])
            listenSock.listen(2)
            print("%s: listening on %s" % (name, svr))
            listening = True
            break
        except:
            print("%s: failed listening on %s" % (name, svr))
            listenSock.close()
            listening = False
            failCount += 1
            continue
        finally:
            if not listening:
                print("%s: closing socket after %d fails" % (name, failCount))
                #listenSock.shutdown(socket.SHUT_RD)
                listenSock.close()
                listenSock = None

    return listenSock

def testClient(name, cliAddr, svrAddr):
    host, port = cliAddr
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #clientSock.settimeout(3)
    bound = False
    while not bound:
        try:
            clientSock.bind((host, port))
            bound = True
            print("%s: bound to %s" % (name, (host, port)))
        except:
            bound = False
            port += 1
            continue

    try:
        print("%s: attempting connect to %s" % (name, svrAddr))
        clientSock.connect(svrAddr)
        print("%s: connected to %s" % (name, svrAddr))
    except:
        print("%s: failed connect to %s" % (name, svrAddr))
        clientSock.close()
        clientSock = None

    return clientSock

def handleConnection(conn, cliAddr):
    global buffer

    try:
        chunk = conn.recv(8)
        buffer += chunk
    except:
        print("%s: recieve failed" % name)
        return None

    return chunk
            
if __name__ == "__main__":
    main()
