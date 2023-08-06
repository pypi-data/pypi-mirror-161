import socket
import time
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while sock.connect_ex(('localhost', 3306)) != 0: # 'db' is the host, 3306 is the port
    print('MySQL is not ready yet.')
    print(sock)
    time.sleep(2)
# sock.close()
print("Now it's up and running! Bye!")