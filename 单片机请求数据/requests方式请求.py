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
class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


def request(method, url, data=None, json=None, headers={}, stream=None, parse_headers=True):
    redir_cnt = 1
    if json is not None:
        assert data is None
        import ujson
        data = ujson.dumps(json)

    while True:
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""
        if proto == "http:":
            port = 80
        elif proto == "https:":
            import ussl
            port = 443
        else:
            raise ValueError("Unsupported protocol: " + proto)

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
        ai = ai[0]

        resp_d = None
        if parse_headers is not False:
            resp_d = {}

        s = usocket.socket(ai[0], ai[1], ai[2])
        try:
            s.connect(ai[-1])
            if proto == "https:":
                s = ussl.wrap_socket(s, server_hostname=host)
            s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
            if not "Host" in headers:
                s.write(b"Host: %s\r\n" % host)
            # Iterate over keys to avoid tuple alloc
            for k in headers:
                print('+'*10,k,headers[k])
                s.write(k)
                s.write(b": ")
                s.write(headers[k])
                s.write(b"\r\n")
            if json is not None:
                s.write(b"Content-Type: application/json\r\n")
            if data:
                s.write(b"Content-Length: %d\r\n" % len(data))
            s.write(b"Connection: close\r\n\r\n")
            if data:
                s.write(data)
            l = s.readline()
            print('*******************',l)
            l = l.split(None, 2)
            status = int(l[1])
            reason = ""
            if len(l) > 2:
                reason = l[2].rstrip()
            while True:
                l = s.readline()
                if not l or l == b"\r\n":
                    break
                #print(l)

                if l.startswith(b"Transfer-Encoding:"):
                    if b"chunked" in l:
                        raise ValueError("Unsupported " + l)
                elif l.startswith(b"Location:") and 300 <= status <= 399:
                    if not redir_cnt:
                        raise ValueError("Too many redirects")
                    redir_cnt -= 1
                    url = l[9:].decode().strip()
                    #print("redir to:", url)
                    status = 300
                    break

                if parse_headers is False:
                    pass
                elif parse_headers is True:
                    l = l.decode()
                    k, v = l.split(":", 1)
                    resp_d[k] = v.strip()
                else:
                    parse_headers(l, resp_d)
        except OSError:
            s.close()
            raise

        if status != 300:
            break

    resp = Response(s)
    resp.status_code = status
    resp.reason = reason
    if resp_d is not None:
        resp.headers = resp_d
    return resp


def head(url, **kw):
    return request("HEAD", url, **kw)

def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def patch(url, **kw):
    return request("PATCH", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)
wifiGet()#获取网络连接
headers ={
    "User-Agent": "MaixPy"
}
#params = {"image": img_bytes}
headers = {'content-type': 'application/x-www-form-urlencoded'}
access_token='24.db875e68461c3118a027c1968b9bd35e.2592000.1599183596.282335-21802139'
ur='https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis?access_token=24.db875e68461c3118a027c1968b9bd35e.2592000.1599183596.282335-21802139'
res = post(ur, headers=headers)
print("response:", res.status_code)
content = res.content
print("get img, length:{}, should be:{}".format(len(content), int(res.headers['Content-Length'])))

if len(content)!= int(res.headers['Content-Length']):
    print("download img fail, not complete, try again")
else:
    print(content)


