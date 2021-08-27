#!/usr/bin/env python3
# coding:utf-8
import socket
import time
import threading
import datetime
import pygame
from pygame.locals import QUIT, KEYDOWN, K_f, K_F11, FULLSCREEN
from KeyPoseByBaiDuAPI import KeyPose,process
local_ip = ""
local_port = 3456
width = 320
height = 240

# jpeg 20 fps
# esp32 spi dma temp buffer MAX Len: 4k

def sendImg(img_bytes,sock):
    print("send len: ", len(img_bytes))
    try:
        length=2048
        block = int(len(img_bytes) / length)
        for i in range(block):
            send_len = sock.send(img_bytes[i * length:(i + 1) * length])
            # time.sleep_ms(500)
        send_len2 = sock.send(img_bytes[block * length:])
        # send_len = sock.send(img_bytes[0:2048])
        # send_len = sock.send(img_bytes[2048:])
        # time.sleep_ms(500)
        if send_len == 0:
            raise Exception("send fail")
    except :
        print("send fail:")
def receiveThread(conn):
    conn.settimeout(10)
    conn_end = False
    pack_size = 1024*5
    while True:
        if conn_end:
            break
        img = b""
        tmp = b''
        while True:
            try:
                client_data = conn.recv(1)
            except socket.timeout:
                conn_end = True
                break
            if tmp == b'\xFF' and client_data == b'\xD8':
                img = b'\xFF\xD8'
                break
            tmp = client_data
        while True:
            try:
                client_data = conn.recv(4096)
            except socket.timeout:
                client_data = None
                conn_end = True
            if not client_data:
                break
            # print("received data,len:",len(client_data) )
            img += client_data
            if img[-2:] == b'\xFF\xD9':
                break
            if len(client_data) > pack_size:
                break
        print("recive end, pic len:", len(img))

        if not img.startswith(b'\xFF\xD8') or not img.endswith(b'\xFF\xD9'):
            print("image error")
            continue
        f = open("tmp.jpg", "wb")
        f.write(img)
        f.close()
        try:
            surface = pygame.image.load("tmp.jpg").convert()
            screen.blit(surface, (0, 0))
            pygame.display.update()
            print("recieve ok")
        except Exception as e:
            print(e)

        #发送处理结果
        fpath = process("tmp.jpg")
        print(fpath)
        myfile = open(fpath, "rb")
        bytes = myfile.read()
        conn.sendall(bytes)
        print("send len: ", len(bytes))
        #sendImg(bytes,conn)
        print('sending done')
        break


    conn.close()
    print("receive thread end")

pygame.init()
screen = pygame.display.set_mode((width, height), 0, 32)
pygame.display.set_caption("pic from client")

ip_port = (local_ip, local_port)
sk = socket.socket()
sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sk.bind(ip_port)
sk.listen(50)
print("accept now,wait for client")


def server():
    while True:
        conn, addr = sk.accept()
        print("hello client,ip:")
        print(addr)
        t = threading.Thread(target=receiveThread, args=(conn,))
        t.setDaemon(True)
        t.start()


tmp = threading.Thread(target=server, args=())
tmp.setDaemon(True)
tmp.start()

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
