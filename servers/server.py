#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import socket


Chapters = {"欢若平生": 2, "传染病": 2 }

def main():
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = '127.0.0.1'
    CONNECT_PORT = 65432
    DOWNLOAD_PORT = 65500
    READING_PORT = 60000
    tcp_server_socket.bind((HOST, CONNECT_PORT))
    tcp_server_socket.listen(128)
    client_check_socket, client_addr = tcp_server_socket.accept()
    file_name = client_check_socket.recv(1024).decode("utf-8")
    chapters = Chapters[file_name]
    client_check_socket.send(chapters.to_bytes(length=2, byteorder='big', signed=True))
    print("Client address： %s" % str(client_addr))
    file_content = None
    chapter_num = 0
    i = 1

    while i<chapters+1:
        tcp_download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_download_socket.bind((HOST, DOWNLOAD_PORT))
        tcp_download_socket.listen(128)
        download_socket_client, client_addr = tcp_download_socket.accept()
        chapter_num = download_socket_client.recv(2).decode("utf-8")
        print("Connect client adddress", str(client_addr), "for downloading chapter %d" % int(chapter_num))
        f = open(".\Books\\" + file_name + "\\" + file_name + str(i) + ".txt", "rb")
        file_content = f.read()
        f.close()
        if file_content:
            print("Start sending data......")
            download_socket_client.send(file_content)
        download_socket_client.close()
        i += 1
    client_check_socket.close()
    tcp_server_socket.close()
 
if __name__ == '__main__':
    main()