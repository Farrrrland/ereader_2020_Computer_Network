import socket
import _thread

HOST="127.0.0.1"
PORT = 65432
DOWNLOAD_PORT = 65500
READING_PORT = 65501

Books = ["欢若平生", "传染病"]
Chapters = {"欢若平生": 45, "传染病": 3}
actions = ["在线阅读", "下载", "退出"]

def child_connection(index, connection, client_addr):
    try:
        connection.settimeout(3600)
        print("Client online at: %s, is connection %d" % (str(client_addr), index))
        # Send book list to client
        # Preventing package-sticking caused by TCP
        pos = 0
        while pos < len(Books):
            msg = bytes(Books[pos], encoding = "utf-8")
            length = len(msg)
            connection.send(length.to_bytes(length=2, byteorder='big', signed=True))
            connection.send(msg)
            pos += 1
        end = -1
        connection.send(end.to_bytes(length=2, byteorder='big', signed=True))

        header = connection.recv(2)
        header = int().from_bytes(header, byteorder='big', signed=True)
        while header != end:
            file_name = connection.recv(header).decode("utf-8")
            chapters = Chapters[file_name]
            connection.send(chapters.to_bytes(length=2, byteorder='big', signed=True))
            header = connection.recv(2)
            header = int().from_bytes(header, byteorder='big', signed=True)
    except socket.timeout:
        print("Connection time out!")
        connection.close()
    _thread.exit()

def download_connection(index, connection, client_addr):
    try:
        connection.settimeout(36000)
        length = connection.recv(2)
        length = int().from_bytes(length, byteorder='big', signed=True)
        file_name = connection.recv(length).decode("utf-8")
        chapter_index = connection.recv(2)
        chapter_index = int().from_bytes(chapter_index, byteorder='big', signed=True)
        print("Begin downloading %d at client address: %s" % (index, client_addr))
        print("file name:", file_name)
        print("chapter index:", chapter_index)
        file_content = None
        try:
            f = open(".\Books\\" + file_name + "\\" + file_name + str(chapter_index) + ".txt", "rb")
            file_content = f.read()
            f.close()
        except Exception as res:
            path = ".\Books\\" + file_name + "\\" + file_name + str(chapter_index) + ".txt"
            print("Invalid file name:", path)
        if file_content:
            connection.send(file_content)
        print("Download connection %d closed" % index)
        connection.close()
    except socket.timeout:
        print("Downloading time out!")
        connection.close()
    _thread.exit()

def reading_connection(index, connection, client_addr): 
    try:
        connection.settimeout(3600)
        length = connection.recv(2)
        length = int().from_bytes(length, byteorder='big', signed=True)
        file_name = connection.recv(length).decode("utf-8")
        chapter_index = connection.recv(2)
        chapter_index = int().from_bytes(chapter_index, byteorder='big', signed=True)
        print("Begin downloading %d at client address for reading: %s" % (index, client_addr))
        print("file name:", file_name)
        print("chapter index:", chapter_index)
        file_content = None
        try:
            f = open(".\Books\\" + file_name + "\\" + file_name + str(chapter_index) + ".txt", "rb")
            file_content = f.read()
            f.close()
        except Exception as res:
            path = ".\Books\\" + file_name + "\\" + file_name + str(chapter_index) + ".txt"
            print("Invalid file name:", path)
        if file_content:
            connection.send(file_content)
            connection.close()
        print("Read-downloading connection %d closed" % index)
    except socket.timeout:
        print("Read-downloading time out!")
        connection.close()
    _thread.exit()

def listen_download(name, sock):
    index = 0
    while True:
        new_socket_client, client_addr = sock.accept()
        index += 1
        _thread.start_new_thread(download_connection,(index, new_socket_client, client_addr))
        if index > 1024:
            break
    sock.close()
    _thread.exit()

def listen_connection(name, sock):
    index = 0
    while True:
        new_socket_client, client_addr = sock.accept()
        index += 1
        _thread.start_new_thread(child_connection,(index, new_socket_client, client_addr))
        if index > 1024:
            break
    sock.close()
    _thread.exit()

def listen_reading(name, sock):
    index = 0
    while True:
        new_socket_client, client_addr = sock.accept()
        index += 1
        _thread.start_new_thread(reading_connection,(index, new_socket_client, client_addr))
        if index > 1024:
            break
    sock.close()
    _thread.exit()

def main():
    tcp_server_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_reading_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcp_server_connection_socket.bind((HOST,PORT))
    tcp_server_download_socket.bind((HOST,DOWNLOAD_PORT))
    tcp_server_reading_socket.bind((HOST,READING_PORT))

    tcp_server_connection_socket.listen(128)
    tcp_server_download_socket.listen(128)
    tcp_server_reading_socket.listen(128)

    _thread.start_new_thread(listen_connection,("Listen connection", tcp_server_connection_socket))
    _thread.start_new_thread(listen_download, ("Listen download", tcp_server_download_socket))
    _thread.start_new_thread(listen_reading, ("Listen reading", tcp_server_reading_socket))

    while True:
        if getattr(tcp_server_connection_socket, '_closed') == True:
            print("Main server stop")
            break

if __name__ == '__main__':
    main()