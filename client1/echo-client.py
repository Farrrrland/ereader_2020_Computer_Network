# -*- coding: utf-8 -*-
import socket
import os
import _thread
from tkinter import *
import tkinter.messagebox
import shutil

HOST = "127.0.0.1"
PORT = 65432
DOWNLOAD_PORT = 65500
READING_PORT = 65501

Books = []
BookMks = {}
actions = ["在线阅读", "下载", "返回"]
chapter_num = -1

font, win = "", Tk()
win.resizable(False,False)
win.geometry('600x800+40+20')
PG_SIZE = 1024

def download_cpt(file_name, cpt, fold):
    path = ".\\" + fold + "\\" + file_name + "\\" + file_name + str(cpt) + ".txt"
    tcp_download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_download_socket.connect((HOST, DOWNLOAD_PORT))
    msg = bytes(file_name, encoding = "utf-8")
    length = len(msg)
    tcp_download_socket.send(length.to_bytes(length=2, byteorder='big', signed=True))
    tcp_download_socket.send(msg)
    tcp_download_socket.send(cpt.to_bytes(length=2, byteorder='big', signed=True))
    recv_data = tcp_download_socket.recv(1024)
    while recv_data:
        with open(path, "ab") as f:
            f.write(recv_data)
        recv_data = tcp_download_socket.recv(1024)

def temp_download_cpt(file_name, cpt):
    tcp_tmp_download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_tmp_download_socket.connect((HOST, READING_PORT))
    msg = bytes(file_name, encoding = "utf-8")
    length = len(msg)
    tcp_tmp_download_socket.send(length.to_bytes(length=2, byteorder='big', signed=True))
    tcp_tmp_download_socket.send(msg)
    tcp_tmp_download_socket.send(cpt.to_bytes(length=2, byteorder='big', signed=True))
    recv_data = tcp_tmp_download_socket.recv(1024)
    while recv_data:
        fold = "Temp"
        dir_name = ".\\" + fold + "\\" + file_name
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        path = ".\\" + fold + "\\" + file_name + "\\" + file_name + str(cpt) + ".txt"
        with open(path, "ab") as f:
            f.write(recv_data)
        recv_data = tcp_tmp_download_socket.recv(1024)

def download(file_name, fold):
    path = ".\\" + fold + "\\" + file_name + "\\" + file_name + str(1) + ".txt"
    if os.path.exists(path) and fold == "Downloads":
        hint = "《" + file_name + "》已经下载过了，重新下载将会覆盖文件。"
        Continue = tkinter.messagebox.askquestion('下载提示', hint)
        print(Continue)
        if Continue == "yes":
            for i in range(chapter_num):
                path = ".\\" + fold + "\\" + file_name + "\\" + file_name + str(i+1) + ".txt"
                os.remove(path)
        else: 
            return
    try:
        dir_name = ".\\" + fold + "\\" + file_name
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        cpt = 1
        while cpt <= chapter_num:
            print("ask for downloading chapter %d..." % cpt)
            _thread.start_new_thread(download_cpt, (file_name, cpt, fold))
            cpt += 1
    except Exception:        
        err = "《" + file_name + "》下载失败。"
        tkinter.messagebox.showerror("下载错误", err)
    i = 1
    while i <= chapter_num:
        while True:
            try:
                f = open(".\\" + fold + "\\" + file_name + "\\" + file_name + str(i) + ".txt", "rb")
                f.close()
            except Exception:
                continue
            break
        i += 1
    hint = "《" + file_name + "》下载完成！"
    tkinter.messagebox.showinfo("完成", hint)

def pg_Next(file_name, cpt, pg, interface, sock):
    path = ".\Temp\\" + file_name + "\\" + file_name + str(cpt) + ".txt"
    pg += 1
    with open(path,'r')as f:
        for i in range(pg):
            content = f.read(PG_SIZE)
    if len(content) == 0:
        cpt += 1
        pg = 1
        if cpt > chapter_num:
            tkinter.messagebox.showinfo("结束", "这是本书的最后一页了。")
        else:
            interface.destroy()
            reading_page(file_name, cpt, pg, sock)
    else:
        interface.destroy()
        reading_page(file_name, cpt, pg, sock)

def pg_Prev(file_name, cpt, pg, interface, sock):
    pg -= 1
    if pg == 0:
        cpt -= 1
        if cpt == 0:
            tkinter.messagebox.showinfo("结束", "这已经是本书的第一页了。")
        else:
            interface.destroy()
            reading_page(file_name, cpt, pg, sock)
    else:
        interface.destroy()
        reading_page(file_name, cpt, pg, sock)

def switch_to_cpt(file_name, interface, sock):
    interface.destroy()
    show_chapters(file_name, sock)

def JumpPg(cpt, pg, file_name, interface, sock, root):
    cpt = int(cpt.get())
    pg = int(pg.get())
    if cpt-1 not in range(0, chapter_num):
        tkinter.messagebox.showerror("章溢出", "没有这一章！")
        root.quit()
        root.destroy()
        return
    fold = "Temp"
    path = ".\\" + fold + "\\" + file_name + "\\" + file_name + str(cpt) + ".txt"
    if os.path.exists(path):
        pass
    else:
        temp_download_cpt(file_name, cpt)
    with open(path,'r')as f:
        if pg < 1:
            tkinter.messagebox.showerror("无效页", "非法的页号！")
            root.quit()
            root.destroy()
            return
        for i in range(pg):
            content = f.read(PG_SIZE)
            if len(content) == 0:
                tkinter.messagebox.showerror("章溢出", "第 " + str(cpt) + " 章没有这么多页！")
                root.quit()
                root.destroy()
                return
    root.quit()
    root.destroy()
    interface.destroy()
    reading_page(file_name, cpt, pg, sock)

def JumpMk(file_name, interface, sock, root):
    if BookMks[file_name] == (-1, -1):
        tkinter.messagebox.showerror("找不到书签", "《" + file_name + "》还没添加任何书签！")
        root.quit()
        root.destroy()
    else:
        root.quit()
        root.destroy()
        interface.destroy()
        reading_page(file_name, BookMks[file_name][0], BookMks[file_name][1], sock)

def Jump(file_name, sock, interface):
    root = Tk()
    root.title("Save Image")
    root.geometry('300x300')
    l1 = Label(root, text="请输入目标章：")
    l1.pack()
    cpt_text = StringVar()
    cpt = Entry(root, textvariable = cpt_text, width = 30)
    cpt_text.set(" ")
    cpt.pack(fill = "y", pady = (0, 20))
    l2 = Label(root, text="请输入目标页号：")
    l2.pack()
    pg_text = StringVar()
    pg = Entry(root, textvariable = pg_text, width = 30)
    pg_text.set(" ")
    pg.pack(fill = "y")

    JumpButton = Button(root, text="跳转", relief = GROOVE, width=15, command = lambda: JumpPg(cpt, pg, file_name, interface, sock, root))
    JumpButton.pack(fill = "y", pady = (0, 20))
    MkButton = Button(root, text="跳转到书签", relief = GROOVE, width=15, command = lambda: JumpMk(file_name, interface, sock, root))
    MkButton.pack(fill = "y")
    root.mainloop()

def SaveBookMk(file_name, cpt, pg):
    if BookMks[file_name] == (-1, -1):
        pass
    elif BookMks[file_name] == (cpt, pg):
        tkinter.messagebox.showinfo("提示", "这一页已经是书签了，请勿重复操作。")
        return
    else:
        prevCpt = BookMks[file_name][0]
        prevPg = BookMks[file_name][1]
        Continue = tkinter.messagebox.askquestion("覆写警告", "当前书签为第" + str(prevCpt) + "章第" + str(prevPg) + "页，继续添加将覆盖当前书签。")
        if Continue == "no":
            return
    BookMks[file_name] = (cpt, pg)
    tkinter.messagebox.showinfo("完成", "成功保存为书签。")

def reading_page(file_name, cpt, pg, sock):
    fold = "Temp"
    path = ".\\" + fold + "\\" + file_name + "\\" + file_name + str(cpt) + ".txt"
    if os.path.exists(path):
        pass
    else:
        temp_download_cpt(file_name, cpt)
    if pg == 0:
            with open(path,'r')as f:
                while True:
                    content = f.read(1024)
                    if len(content) == 0:
                        break
                    pg += 1
    win.title("Reading Screen")
    interface = Frame(win)
    tit = "第" + str(cpt) + "章_第" + str(pg) + "页"
    title = Label(interface, text = tit, font=(font, 15))
    title.pack(fill="x", pady = "50")
    bar = Scrollbar(interface)
    bar.pack(side = RIGHT, fill = Y)
    text = Text(interface, yscrollcommand = bar.set, width=80, height=30, font="kaiti")
    with open(path, 'r')as f:
        for i in range(pg):
            content = f.read(PG_SIZE)
    f.close()
    text.insert(END, content)
    text.pack(fill = "y", pady = (0, 20))
    bar.config(command=text.yview)
    
    PgPrev = Button(interface, text="上一页", relief = GROOVE, width = 14, command = lambda: pg_Prev(file_name, cpt, pg, interface, sock))
    PgPrev.pack(side = LEFT, ipadx = 4)

    PgNext = Button(interface, text="下一页", relief = GROOVE, width=14, command = lambda: pg_Next(file_name, cpt, pg, interface, sock))
    PgNext.pack(side = LEFT, ipadx = 4)

    MkButton = Button(interface, text="存为书签", relief = GROOVE, width=14, command = lambda: SaveBookMk(file_name, cpt, pg))
    MkButton.pack(side = LEFT, ipadx = 4)
    
    CptButton = Button(interface, text="章节选择", relief = GROOVE, width=14, command = lambda: switch_to_cpt(file_name, interface, sock))
    CptButton.pack(side = LEFT, ipadx = 4)

    PgJump = Button(interface, text="跳页", relief = GROOVE, width=14, command = lambda: Jump(file_name, sock, interface))
    PgJump.pack(side = LEFT, ipadx = 4)

    interface.pack()
    win.mainloop()

def show_chapters(file_name, sock):
    # win = Tk()
    interface = Frame(win)
    win.title("Book Screen")
    title = Label(interface, text = file_name + " 章节", font=(font, 24, 'bold'))
    title.pack(fill="x", pady = "50")
    bar = Scrollbar(interface)
    bar.pack(side = RIGHT, fill = Y) 
    lb = Listbox(interface, yscrollcommand = bar.set, selectmode='single', width=60, height=25, font="kaiti")

    def CurSelet(evt):
        value=lb.get(lb.curselection())
        pos, cpt, i = len(value) - 3, 0, 0
        while True:
            cpt += int(value[pos]) * (10 ** i)
            pos -= 1
            i += 1
            if value[pos] == " ":
                break
        interface.destroy()
        reading_page(file_name, cpt, 1, sock)
    
    lb.bind('<<ListboxSelect>>',CurSelet)
    for i in range(chapter_num):
        lb.insert(END,"第 " + str(i+1) + " 章")
    lb.pack(fill = "y", pady = (0, 20))
    bar.config(command=lb.yview)
    CptButton = Button(interface, text="返回", relief = GROOVE, width=30, command = lambda: switch_to_book(file_name, sock, interface))
    CptButton.pack()
    interface.pack()
    win.mainloop()

def switch_to_home(sock, interface):
    interface.destroy()
    Home_page(sock)

def Book_page(book_name, sock):
    win.title("Book Screen")
    interface = Frame(win)

    title = Label(interface, text = book_name, font=(font, 24, 'bold'))
    title.pack(fill="x", pady = "50")

    readButton = Button(interface, text="在线阅读", relief = GROOVE, width = 50, command = lambda: switch_to_cpt(book_name, interface, sock))
    readButton.pack(fill = "y", pady = (0, 20))

    downloadButton = Button(interface, text="下载", relief = GROOVE, width=50, command = lambda: download(book_name, "Downloads"))
    downloadButton.pack(fill = "y", pady = (0, 20))

    returnButton = Button(interface, text="返回", relief = GROOVE, width=50, command = lambda:switch_to_home(sock, interface))
    returnButton.pack(fill = "y")

    interface.pack()
    win.mainloop()

def switch_to_book(book_name, sock, interface):
    global chapter_num
    global downloaded
    downloaded = 0
    # fetch information first
    msg_file = bytes(book_name, encoding = "utf-8")
    sock.send(len(msg_file).to_bytes(length=2, byteorder='big', signed=True))
    sock.send(msg_file)
    print("File_name request sent")
    # get chapter_num from server
    chapter_num = sock.recv(2)
    print("Chapters recieved")
    chapter_num = int().from_bytes(chapter_num, byteorder='big', signed=True)
    print("Totally %d chapters" % chapter_num)
    # switch window
    interface.destroy()
    Book_page(book_name, sock)

def quit_system():
    temp_dir = ".\Temp"
    shutil.rmtree(temp_dir)
    global win
    win.destroy()
    os.mkdir(temp_dir)

def Home_page(sock):
    win.title("Home Screen")
    interface = Frame(win)
    title = Label(interface, text = "小说阅读器", font=(font, 24, 'bold'))
    title.pack(fill="x", pady = "50")

    for book_name in Books:
        playButton = Button(interface, text = book_name, relief = GROOVE, width = 50, command = lambda book_name = book_name: switch_to_book(book_name, sock, interface))
        playButton.pack(fill = "y", pady = (0, 20))
    
    QuitButton = Button(interface, text = "退出", relief = GROOVE, width = 50, command = quit_system)
    QuitButton.pack(fill = "y", pady = (0, 20))
    interface.pack()
    win.mainloop()

def main():
    global chapter_num
    tcp_client_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client_connection_socket.connect((HOST, PORT))
    print("Login at ( %s: %d )" % (HOST, PORT))
    # Receive book list from server, get a header first
    end = -1
    header = tcp_client_connection_socket.recv(2)
    header = int().from_bytes(header, byteorder='big', signed=True)
    while header != end:
        book_name = tcp_client_connection_socket.recv(header)
        book_name = book_name.decode("utf-8")
        Books.append(book_name)
        BookMks[book_name] = (-1, -1)
        header = tcp_client_connection_socket.recv(2)
        header = int().from_bytes(header, byteorder='big', signed=True)
    # Start UI
    Home_page(tcp_client_connection_socket)
    tcp_client_connection_socket.close()

if __name__ == '__main__':
    main()