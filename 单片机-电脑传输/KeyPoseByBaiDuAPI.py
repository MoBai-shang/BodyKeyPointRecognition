import json
import matplotlib.pyplot as plt#约定俗成的写法plt
import requests
import base64
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
class KeyPose:
    # encoding:utf-8
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    def __init__(self,AK='4NrBOFjarQuuXxdDcZr4o94B',SK='5uUaOZXjyoEAE096IFBTKaZuI1QPDT14'):
        self.body_parts=['left_hip', 'top_head', 'right_mouth_corner', 'neck', 'left_shoulder', 'left_knee', 'left_ankle', 'left_mouth_corner', 'right_elbow', 'right_ear', 'nose', 'left_eye', 'right_eye', 'right_hip', 'left_wrist',  'left_ear', 'left_elbow', 'right_shoulder', 'right_ankle', 'right_knee', 'right_wrist']
        self.part1 = ['left_ankle', 'left_knee', 'left_hip', 'right_hip', 'right_knee', 'right_ankle']
        self.part2 = ['left_wrist', 'left_elbow','left_shoulder','neck','right_shoulder', 'right_elbow','right_wrist']
        self.AK=AK
        self.SK=SK
        self.access_token = '24.db875e68461c3118a027c1968b9bd35e.2592000.1599183596.282335-21802139'
    #获取access_token
    def getToken(self,AK,SK):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + AK + '&client_secret=' + SK
        response = requests.get(host)
        if response:
            print(response.json())
            return response.json()['access_token']
    def setToken(self,access_token):
        self.access_token=access_token
    def getKeyPose(self,imageFile):
        request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis"
        # 二进制方式打开图片文件
        f = open(imageFile, 'rb')
        img = base64.b64encode(f.read())
        params = {"image": img}
        request_url = request_url + "?access_token=" + self.access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        return response
    def writeInJson(self,data,file):
        with open(file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)
    def jsonlizatVisuaional(self,filepath,fontsize=5,alpha=0.8,style='ro'):
        file = open(filepath, "rb")
        fileJson = json.load(file)
        self.dataVisuaional(fileJson,fontsize,alpha,style)
    def dataVisuaional(self,data,fontsize=5,alpha=0.8,style='ro'):
        ax = plt.gca()
        ax.invert_yaxis()  # y轴反向
        plt.axis('equal')
        for info in data['person_info']:
            parts=info['body_parts']
            for item in self.body_parts:
                plt.text(parts[item]['x'], parts[item]['y'],round(parts[item]['score'], 2) , size=fontsize, alpha=alpha)
                plt.plot(parts[item]['x'],parts[item]['y'],style)
            line1_x=[parts[item]['x'] for item in self.part1]
            line1_y = [parts[item]['y'] for item in self.part1]
            line2_x = [parts[item]['x'] for item in self.part2]
            line2_y = [parts[item]['y'] for item in self.part2]
            plt.plot(line1_x,line1_y,'b-')
            plt.plot(line2_x,line2_y,'b-')
            location=info['location']
            plt.vlines(location['left'], location['top'], location['top']+location['height'], colors="b", linestyles="dashed")#vlines(x, ymin, ymax)
            plt.hlines(location['top'], location['left'], location['left']+location['width'], colors="b", linestyles="dashed")#hlines(y, xmin, xmax)
            plt.vlines(location['left']+location['width'], location['top'], location['top'] + location['height'], colors="b",
                       linestyles="dashed")  # vlines(x, ymin, ymax)
            plt.hlines(location['top']+location['height'], location['left'], location['left'] + location['width'], colors="b",
                       linestyles="dashed")  # hlines(y, xmin, xmax)
        plt.show()
    def VisuaionalInImage(self,data,imageFile):
        # 打开图片
        im1 = Image.open(imageFile)
        font = ImageFont.truetype("simkai.ttf", 48)
        # 画图
        draw = ImageDraw.Draw(im1)
        for info in data['person_info']:
            parts=info['body_parts']
            for item in self.body_parts:
                draw.text((parts[item]['x'], parts[item]['y']), "O", (0, 0, 255))  # 设置文字位置/内容/颜色/字体, font=font
        draw = ImageDraw.Draw(im1)  # Just draw it!
        # 另存图片
        im1.save("target_"+imageFile)
        print('done.....')
        im = Image.open("target_" + imageFile)
        im.show()
    def processImage(self,data,imageFile):
        # 打开图片
        im1 = Image.open(imageFile)
        font = ImageFont.truetype("simkai.ttf", 48)
        # 画图
        draw = ImageDraw.Draw(im1)
        for info in data['person_info']:
            parts=info['body_parts']
            for item in self.body_parts:
                draw.text((parts[item]['x'], parts[item]['y']), "O", (0, 0, 255))  # 设置文字位置/内容/颜色/字体, font=font
        draw = ImageDraw.Draw(im1)  # Just draw it!
        # 另存图片
        im1.save("target_"+imageFile)
        return "target_"+imageFile
    def getJsonData(self,jsonFile):
        file = open(jsonFile, "rb")
        fileJson = json.load(file)
        return fileJson

def process(srcImg):
    kp=KeyPose()
    response =kp.getKeyPose(srcImg)
    if response:
        #print (response.json())
        #kp.writeInJson(response.json(),'test.json')
        #kp.dataVisuaional(response.json())
        #kp.VisuaionalInImage(response.json(), imageFile)
        data=response.json()
        print(data)
        if 'person_info' not in data:
            file = open('error.json', "rb")
            data = json.load(file)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!1')
        return kp.processImage(data,srcImg)