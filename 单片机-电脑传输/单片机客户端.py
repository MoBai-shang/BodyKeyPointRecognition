
# Send image(jpeg) to server and display on server(PC),
# server code refer to ../tools_on_PC/network/pic_server.py
def receiveImg(sock):
    img = b""
    sock.settimeout(5)
    while True:
        data = sock.recv(4096)
        if len(data) == 0: # connection closed
            break
        print("rcv:", len(data))
        img = img + data
    #sock.close()
    lcd.draw_string(100, 100, "receive done", lcd.RED, lcd.BLACK)
    print("rcv len:", len(img))
    #begin=img.find(b"\r\n\r\n")+4
    #print(begin)
    #img = img[begin:begin+len(img)]   ## jpg file size is 43756 byte
    #if len(img) != 43756:
    #   raise Exception("recv jpg not complete, try again")
    print("image len:", len(img))
    img = image.Image(img, from_bytes=True)
    lcd.init()
    lcd.display(img)
    print('img coming')
    #del img

def wifiGet():
    WIFI_SSID = "@PHICOMM_7C"
    WIFI_PASSWD = "15978576465"
    lcd.init()
    lcd.draw_string(100, 100, "wifi connecting....", lcd.RED, lcd.BLACK)
    nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11,rdy=fm.fpioa.GPIOHS12, mosi=fm.fpioa.GPIOHS13,miso=fm.fpioa.GPIOHS14,sclk=fm.fpioa.GPIOHS15)
    if not nic.isconnected():
        print("connect WiFi now")
        try:
            err = 0
            while 1:
                try:
                    nic.connect(WIFI_SSID, WIFI_PASSWD)
                except Exception:
                    err += 1
                    print("Connect AP failed, now try again")
                    if err > 3:
                        raise Exception("Conenct AP fail")
                    continue
                break
            nic.ifconfig()
            print('wifi is ok')
        except Exception:
            print('wifi failed')
    if not nic.isconnected():
        print("WiFi connect fail")
    lcd.init()
    lcd.draw_string(100, 100, "wifi is ok", lcd.RED, lcd.BLACK)


import network, socket, time, sensor, image
from machine import UART
from Maix import GPIO
from fpioa_manager import fm, board_info
import lcd
########## config ################
WIFI_SSID = "@PHICOMM_7C"
WIFI_PASSWD = "15978576465"
server_ip      = '192.168.2.183'
server_port    = 3456
##################################

# IO map for ESP32 on Maixduino
fm.register(25,fm.fpioa.GPIOHS10)#cs
fm.register(8,fm.fpioa.GPIOHS11)#rst
fm.register(9,fm.fpioa.GPIOHS12)#rdy
fm.register(28,fm.fpioa.GPIOHS13)#mosi
fm.register(26,fm.fpioa.GPIOHS14)#miso
fm.register(27,fm.fpioa.GPIOHS15)#sclk

nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11,rdy=fm.fpioa.GPIOHS12, mosi=fm.fpioa.GPIOHS13,miso=fm.fpioa.GPIOHS14,sclk=fm.fpioa.GPIOHS15)

addr = (server_ip, server_port)

clock = time.clock()
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
lcd.draw_string(100, 100, "wifi connecting...", lcd.RED, lcd.BLACK)
wifiGet()#获取网络连接
while True:
    # send pic
    sock = socket.socket()
    try:
        sock.connect(addr)
    except Exception as e:
        print("connect error:", e)
        sock.close()
        continue
    sock.settimeout(5)
    lcd.draw_string(100, 100, "socket connected", lcd.RED, lcd.BLACK)
    count = 0
    err   = 0
    while True:
        clock.tick()
        if err >=10:
            print("socket broken")
            break
        img = sensor.snapshot()
        lcd.display(img)
        img = img.compress(quality=60)
        img_bytes = img.to_bytes()
        print("send len: ", len(img_bytes))
        try:
            block = int(len(img_bytes)/2048)
            for i in range(block):
                send_len = sock.send(img_bytes[i*2048:(i+1)*2048])
                #time.sleep_ms(500)
            send_len2 = sock.send(img_bytes[block*2048:])
            #send_len = sock.send(img_bytes[0:2048])
            #send_len = sock.send(img_bytes[2048:])
            #time.sleep_ms(500)
            if send_len == 0:
                raise Exception("send fail")
        except OSError as e:
            if e.args[0] == 128:
                print("connection closed")
                break
        except Exception as e:
            print("send fail:", e)
            time.sleep(1)
            err += 1
            continue
        count += 1
        print("send:", count)
        print("fps:", clock.fps())
        #lcd.init()
        lcd.draw_string(100, 100, "send done", lcd.RED, lcd.BLACK)
        #time.sleep_ms(500)
        receiveImg(sock)
        break
    print("close now")
    sock.close()
    break
