import usocket, network, time
import lcd, image
from Maix import GPIO
from machine import UART
from fpioa_manager import fm, board_info
import network, socket, time, sensor, image
from machine import UART
from Maix import GPIO
from fpioa_manager import fm, board_info
import lcd
# IO map for ESP32 on Maixduino
fm.register(25,fm.fpioa.GPIOHS10)#cs
fm.register(8,fm.fpioa.GPIOHS11)#rst
fm.register(9,fm.fpioa.GPIOHS12)#rdy
fm.register(28,fm.fpioa.GPIOHS13)#mosi
fm.register(26,fm.fpioa.GPIOHS14)#miso
fm.register(27,fm.fpioa.GPIOHS15)#sclk
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
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
def getImage():
    print('采集照片.....')
    img = sensor.snapshot()
    lcd.display(img)
    img = img.compress(quality=60)
    img_bytes = img.to_bytes()
    import ubinascii
    img_bytes=ubinascii.b2a_base64(img_bytes)
    return img_bytes

ur='https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis?access_token=24.db875e68461c3118a027c1968b9bd35e.2592000.1599183596.282335-21802139'
err = 0
sock = socket.socket()
while 1:
    try:
        addr = socket.getaddrinfo("aip.baidubce.com", 80)[0][-1]
        # addr = socket.getaddrinfo("192.168.0.183", 8099)[0][-1]
        break
    except Exception:
        err += 1
    if err > 5:
        raise Exception("get ip failed!")
sock.connect(addr)
#sock.send(b'GET /MAIX/MaixPy/assets/Alice.jpg HTTP/1.1\r\nHost: dl.sipeed.com\r\ncache-control: no-cache\r\nUser-Agent: MaixPy\r\nConnection: close')
sock.send('''POST /rest/2.0/image-classify/v1/body_analysis?access_token=24.db875e68461c3118a027c1968b9bd35e.2592000.1599183596.282335-21802139 HTTP/1.1
Host: aip.baidubce.com
cache-control: no-cache
User-Agent: MaixPy
content-type: application/x-www-form-urlencoded
Connection: close

''')
img = b""
sock.settimeout(5)
while True:
    data = sock.recv(4096)
    if len(data) == 0: # connection closed
        break
    print("rcv:", len(data))
    img = img + data

sock.close()
begin=img.find(b"\r\n\r\n")+4
print(begin)
img = img[begin:-1]
print("image len:", len(img))
print(img)

import image, lcd

img = image.Image(img, from_bytes=True)
lcd.init()
lcd.display(img)
del img

