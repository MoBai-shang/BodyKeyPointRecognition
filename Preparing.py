import os,shutil
import json
import pandas as pd
from PIL import Image
import numpy as np
import math
import matplotlib.pyplot as plt#约定俗成的写法plt
class Preparing:
    def __init__(self,errorPath='ErrorPicture',noDataPath='noData',oldSize=1280,newSize=128):
        self.errorPath=errorPath
        if not os.path.exists(errorPath):
            os.makedirs(errorPath)  # 创建路径
            print('directy of ',errorPath,' build successfully')
        if not os.path.exists(noDataPath):
            os.makedirs(noDataPath)
        x1 = [16, 14, 0, 1, 8, 9, 10]
        x2 = [17, 15, 0, 1, 11, 12, 13]
        x3 = [4, 3, 2, 1, 5, 6, 7]
        self.X = [x1, x2, x3]
        self.joints=18
        self.oldSize=oldSize
        self.newSize=newSize
        self.noDataPath=noDataPath
    def getDateOfJson(self,filepath):
        file = open(filepath, "rb")
        fileJson = json.load(file)
        data=fileJson['people']
        n=len(data)
        if n>1:
            which, data = self.screen(data, n)
            fpath, fname = os.path.split(filepath)  # 分离文件名和路径
            print('File', filepath, 'have more than one people recode,having copy to dirs of',self.errorPath)
            dstfile = os.path.join(self.errorPath, str(which)+'_'+fname)
            shutil.copyfile(filepath, dstfile)  # 复制文件
        elif n<1:
            print(filepath,'no data','!'*20)
            fpath, fname = os.path.split(filepath)
            dstfile = os.path.join(self.noDataPath,fpath.replace('\\','_')+'_'+fname)
            shutil.copyfile(filepath,dstfile)  # 复制文件
            return None
        else:
            data=data[0]['pose_keypoints_2d']
        extract = data[:24]#8 * 3
        extract.extend(data[27:57])#9 * 3:19* 3
        rate=self.oldSize/self.newSize
        for i in range(54):
            if i%3==2:
                continue
            extract[i]/=rate
        return extract
    def screen(self,data,n):
        Data=[item['pose_keypoints_2d'] for item in data]
        x_point=[[]]*n
        for i in range(n):
            x_point[i]=[Data[i][j*3] for j in range(19)]
            x_point[i]=[it for it in x_point[i] if it>0]
        record=[max(it)-min(it) for it in x_point]
        index=record.index(max(record))
        return index,Data[index]
    def jsonlizatVisuaional(self,filepath,fontsize=5,alpha=0.8,style='r-'):
        b=self.getDateOfJson(filepath)
        ax = plt.gca()
        ax.invert_yaxis()  # y轴反向
        plt.axis('equal')
        imageSize=(self.newSize,self.newSize)
        for it in self.X:
            x = []
            y = []
            for i in it:
                t = i * 3
                if b[t] > 0 and b[t + 1] > 0:
                    x.append(b[t])
                    y.append(b[t + 1])
                plt.text(b[t], b[t + 1], i, size=fontsize, alpha=alpha)
            plt.plot(x, y, style)
        #plt.xlim(0, imageSize[0])
        #plt.ylim(imageSize[1],0)
        plt.vlines(0, 0, imageSize[1], colors="b", linestyles="dashed")#vlines(x, ymin, ymax)
        plt.hlines(0, 0, imageSize[0], colors="b", linestyles="dashed")#hlines(y, xmin, xmax)
        plt.vlines(imageSize[0], 0, imageSize[1], colors="b", linestyles="dashed")  # vlines(x, ymin, ymax)
        plt.hlines(imageSize[1], 0, imageSize[0], colors="b", linestyles="dashed")
        plt.show()
    def NPYlizatVisuaional(self,npy,fontsize=5,alpha=0.8,style='r.'):
        b=np.load(npy)
        imageSize=b.shape
        ax = plt.gca()
        ax.invert_yaxis()  # y轴反向
        plt.axis('equal')
        x,y=np.nonzero(b)
        print('非零元素数：',len(x))
        print("稀疏率：",len(x)/128/128)
        plt.plot(x, y, style)
        #plt.xlim(0, imageSize[0])
        #plt.ylim(imageSize[1],0)
        plt.vlines(0, 0, imageSize[1], colors="b", linestyles="dashed")#vlines(x, ymin, ymax)
        plt.hlines(0, 0, imageSize[0], colors="b", linestyles="dashed")#hlines(y, xmin, xmax)
        plt.vlines(imageSize[0], 0, imageSize[1], colors="b", linestyles="dashed")  # vlines(x, ymin, ymax)
        plt.hlines(imageSize[1], 0, imageSize[0], colors="b", linestyles="dashed")
        plt.show()
    def jsonAlllizatVisuaional(self,filepath,fontsize=5,alpha=0.8,style='r-'):
        file = open(filepath, "rb")
        fileJson = json.load(file)
        data = fileJson['people']
        Data = [item['pose_keypoints_2d'] for item in data]
        for item in data:
            b=item['pose_keypoints_2d'][:24]
            b.extend(item['pose_keypoints_2d'][27:57])
            ax = plt.gca()
            ax.invert_yaxis()  # y轴反向
            plt.axis('equal')
            imageSize=(self.oldSize,self.oldSize)

            for it in self.X:
                x = []
                y = []
                for i in it:
                    t = i * 3
                    if b[t] > 0 and b[t + 1] > 0:
                        x.append(b[t])
                        y.append(b[t + 1])
                    plt.text(b[t], b[t + 1], i, size=fontsize, alpha=alpha)

                plt.plot(x, y, style)
            #plt.xlim(0, imageSize[0])
            #plt.ylim(imageSize[1],0)
            plt.vlines(0, 0, imageSize[1], colors="b", linestyles="dashed")#vlines(x, ymin, ymax)
            plt.hlines(0, 0, imageSize[0], colors="b", linestyles="dashed")#hlines(y, xmin, xmax)
            plt.vlines(imageSize[0], 0, imageSize[1], colors="b", linestyles="dashed")  # vlines(x, ymin, ymax)
            plt.hlines(imageSize[1], 0, imageSize[0], colors="b", linestyles="dashed")
            plt.show()
    def getImageSize(self,filepath):
        image = filepath.replace('_keypoints.json', '.jpg')
        try:
            img = Image.open(image)
        except:
            try:
                image = filepath.replace('_keypoints.json', '.png')
                img = Image.open(image)
            except:
                print('图片文件格式不属于jpg,png或文件不存在……')
                return (0,0)
        return img.size  # 大小/尺寸
    def toNpy(self,filepath,savefile):
        date=np.zeros((self.newSize,self.newSize,self.joints+1))
        date[::, ::, :-2:-1]=1
        location=self.getDateOfJson(filepath)
        if location:
            for joint in range(self.joints):
                base=joint*3
                x=round(location[base])
                y=round(location[base+1])
                try:
                    date[x][y][joint]=1
                    date[x][y][-1] = 0
                except:
                    x=min(x,self.newSize-1)
                    y=min(y,self.newSize-1)
                    date[x][y][joint] = 1
                    date[x][y][-1] = 0
            #(filepath, tempfilename) = os.path.split(file_path)
            #(filename, extension) = os.path.splitext(filepath)
            #np.save(filepath.replace('_keypoints.json', '.npy'), date)
            np.save(savefile, date)
            print(filepath," saved to .npy done")
    def toNpy2(self,filepath,savefile):
        date=np.zeros((self.joints+1,self.newSize,self.newSize))
        date[:-2:-1,::, ::]=1
        location=self.getDateOfJson(filepath)
        if location:
            for joint in range(self.joints):
                base=joint*3
                x=round(location[base])
                y=round(location[base+1])
                try:
                    date[joint][x][y]=1
                    date[-1][x][y] = 0
                except:
                    x=min(x,self.newSize-1)
                    y=min(y,self.newSize-1)
                    date[joint][x][y] = 1
                    date[-1][x][y] = 0
            #(filepath, tempfilename) = os.path.split(file_path)
            #(filename, extension) = os.path.splitext(filepath)
            #np.save(filepath.replace('_keypoints.json', '.npy'), date)
            np.save(savefile, date)
            print(filepath," saved to .npy done")
    def toNpy3(self,filepath,savefile):
        date=np.zeros((self.newSize,self.newSize))
        location=self.getDateOfJson(filepath)
        if location:
            for joint in range(self.joints):
                base=joint*3
                x=round(location[base])
                y=round(location[base+1])
                try:
                    date[x][y]=joint+1
                    #date[x][y] = 1000
                except:
                    x=min(x,self.newSize-1)
                    y=min(y,self.newSize-1)
                    date[x][y] = joint+1
                    #date[x][y] = 1000
            #(filepath, tempfilename) = os.path.split(file_path)
            #(filename, extension) = os.path.splitext(filepath)
            #np.save(filepath.replace('_keypoints.json', '.npy'), date)
            np.save(savefile, date)
            print(filepath," saved to .npy done")
    def toNpy3R(self,filepath,savefile,R=3):
        date=np.zeros((self.newSize,self.newSize))
        location=self.getDateOfJson(filepath)
        ma=self.newSize-1
        if location:
            for joint in range(self.joints):
                base=joint*3

                x=round(location[base])
                y=round(location[base+1])
                value=joint+1
                try:
                    date[x][y]=value
                    #date[x][y] = 1000
                except:
                    x=min(x,ma)
                    y=min(y,ma)
                    date[x][y] = value
                    #date[x][y] = 1000
                for i in range(max(0,x-R),min(ma,x+R+1)):
                    for j in range(max(0,y-R),min(ma,y+R+1)):
                        try:
                            if math.sqrt(math.pow(i-x,2)+math.pow(j-y,2))<=R:
                                date[i][j]=value
                                if i>126 or j>126:
                                    print(i,j,'+++')
                        except:
                            pass
            #(filepath, tempfilename) = os.path.split(file_path)
            #(filename, extension) = os.path.splitext(filepath)
            #np.save(filepath.replace('_keypoints.json', '.npy'), date)

            np.save(savefile, date)
            print(filepath," saved to .npy done")
    def toNpy3Rbase2(self,filepath,savefile,R=4):
        date=np.zeros((self.newSize,self.newSize))
        location=self.getDateOfJson(filepath)
        value = 1
        if location:
            for joint in range(self.joints):
                base=joint*3
                x=round(location[base])
                y=round(location[base+1])

                try:
                    date[x][y]=value
                    #date[x][y] = 1000
                except:
                    x=min(x,self.newSize-1)
                    y=min(y,self.newSize-1)
                    date[x][y] = value
                    #date[x][y] = 1000
                for i in range(x-R,x+R+1):
                    for j in range(y-R,y+R+1):
                        try:
                            if math.sqrt(math.pow(i-x,2)+math.pow(j-y,2))<=R:
                                date[i][j]=value
                        except:
                            pass
            #(filepath, tempfilename) = os.path.split(file_path)
            #(filename, extension) = os.path.splitext(filepath)
            #np.save(filepath.replace('_keypoints.json', '.npy'), date)
            np.save(savefile, date)
            print(filepath," saved to .npy done")
    def toNpy5(self, filepath, savefile):
        date = np.ones((self.newSize, self.newSize))*self.joints
        location = self.getDateOfJson(filepath)
        if location:
            for joint in range(self.joints):
                base = joint * 3
                x = round(location[base])
                y = round(location[base + 1])
                try:
                    date[x][y] = joint
                    # date[x][y] = 1000
                except:
                    x = min(x, self.newSize - 1)
                    y = min(y, self.newSize - 1)
                    date[x][y] = joint
                    # date[x][y] = 1000
            # (filepath, tempfilename) = os.path.split(file_path)
            # (filename, extension) = os.path.splitext(filepath)
            # np.save(filepath.replace('_keypoints.json', '.npy'), date)
            np.save(savefile, date)
            print(filepath, " saved to .npy done")
    def cropImage(self,srcPath, dstPath):  # 将位于srcPath下的图片压缩处理后结果存于dstPath下
        # 如果不存在目的目录则创建一个，保持层级结构
        if not os.path.exists(dstPath):
            os.makedirs(dstPath)
            print(dstPath, '创建成功！')
        for filename in os.listdir(srcPath):
            # 拼接完整的文件或文件夹路径
            srcFile = os.path.join(srcPath, filename)
            dstFile = os.path.join(dstPath, filename)
            # 如果是文件就处理
            if os.path.isfile(srcFile):
                try:
                    # 打开原图片缩小后保存，可以用if srcFile.endswith(".jpg")或者split，splitext等函数等针对特定文件压缩
                    sImg = Image.open(srcFile)
                    w, h = sImg.size
                    longer_side = max(w, h)
                    horizontal_padding = (longer_side - w) / 2
                    vertical_padding = (longer_side - h) / 2
                    img2 = sImg.crop(
                        (
                            -horizontal_padding,
                            -vertical_padding,
                            w + horizontal_padding,
                            h + vertical_padding
                        )
                    )
                    dImg = img2.resize((self.oldSize, self.oldSize), Image.ANTIALIAS)  # 设置压缩尺寸和选项，注意尺寸要用括号
                    dImg.save(dstFile)  # 也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码选项JPEG之类的
                    print(dstFile + " 成功！")
                except Exception:
                    print(dstFile + "失败！")
            # 如果是文件夹就递归
            if os.path.isdir(srcFile):
                self.cropImage(srcFile, dstFile)
    def resizeImage(self,srcPath, dstPath,size=128):  # 将位于srcPath下的图片压缩处理后结果存于dstPath下
        # 如果不存在目的目录则创建一个，保持层级结构
        if not os.path.exists(dstPath):
            os.makedirs(dstPath)
            print(dstPath, '创建成功！')
        for filename in os.listdir(srcPath):
            # 拼接完整的文件或文件夹路径
            srcFile = os.path.join(srcPath, filename)
            dstFile = os.path.join(dstPath, filename)
            # 如果是文件就处理
            if os.path.isfile(srcFile):
                try:
                    # 打开原图片缩小后保存，可以用if srcFile.endswith(".jpg")或者split，splitext等函数等针对特定文件压缩
                    sImg = Image.open(srcFile)

                    dImg = sImg.resize((size,size), Image.ANTIALIAS)  # 设置压缩尺寸和选项，注意尺寸要用括号
                    dImg.save(dstFile)  # 也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码选项JPEG之类的
                    print(dstFile + " 成功！")
                except Exception:
                    print(dstFile + "失败！")
            # 如果是文件夹就递归
            if os.path.isdir(srcFile):
                self.cropImage(srcFile, dstFile)
    def scanJson(self,srcPath,dstPath,saveFile=None):
        if not os.path.exists(dstPath):
            os.makedirs(dstPath)
            print(dstPath, '创建成功！')
        record={}
        for filename in os.listdir(srcPath):
            # 拼接完整的文件或文件夹路径
            srcFile = os.path.join(srcPath, filename)
            if os.path.isfile(srcFile):
                data = self.getDateOfJson(srcFile)
                if data:
                    num = self.joints - data.count(0)//3
                else:
                    num=0
                record[filename]=num
            # 如果是文件夹就递归
            if os.path.isdir(srcFile):
                self.scanJson(srcFile,dstPath,filename+'Record.csv')
        new_df = pd.DataFrame.from_dict(record, orient='index')
        if saveFile:
            name=os.path.join(dstPath, saveFile)
            new_df.to_csv(name)
            print(srcPath,'scan done!',name)
    def toNpys(self,srcPath, dstPath):  # 将位于srcPath下的图片压缩处理后结果存于dstPath下
        # 如果不存在目的目录则创建一个，保持层级结构
        if not os.path.exists(dstPath):
            os.makedirs(dstPath)
            print(dstPath, '创建成功！')
        for filename in os.listdir(srcPath):
            # 拼接完整的文件或文件夹路径
            srcFile = os.path.join(srcPath, filename)

            # 如果是文件就处理
            if os.path.isfile(srcFile):
                dstFile = os.path.join(dstPath, filename.replace('_keypoints.json', '.npy'))
                self.toNpy3R(srcFile,dstFile)
            # 如果是文件夹就递归
            if os.path.isdir(srcFile):
                dstFile = os.path.join(dstPath, filename)
                self.toNpys(srcFile, dstFile)

    def jsonslizatVisuaional(self,Path):  # 将位于srcPath下的图片压缩处理后结果存于dstPath下
        for filename in os.listdir(Path):
            # 拼接完整的文件或文件夹路径
            File = os.path.join(Path, filename)
            # 如果是文件就处理
            if os.path.isfile(File):
                self.jsonlizatVisuaional(File)
            # 如果是文件夹就递归
            if os.path.isdir(File):
                self.jsonslizatVisuaional(File)
def checkNPY3(npy):
    data=np.load(npy)
    print('data shape:',data.shape)
    print(data)
    count=0
    for x in range(128):
        for y in range(128):
            if data[x][y]>0:
                count=count+1
                print(count,'  (',x,y,')=',data[x][y])
def checkNPY2(npy):
    data=np.load(npy)
    print('data shape:',data.shape)
    count=0
    for z in range(19):
        for x in range(128):
            for y in range(128):
                if data[z][x][y]>1:
                    count=count+1
                    print(count,' (',z,x,y,')=',data[z][x][y])
def checkNPY2xy(npy,x,y):
    data=np.load(npy)
    print('data shape:',data.shape)
    for i in range(x):
        for j in range(y):
            print(data[::,i,j])
ff=Preparing('problem',oldSize=1280)
#ff.cropImage('picture_source','picture_process128')
#ff.cropImage('picture_source','picture_process')
#print(ff.getDateOfJson('790_0_keypoints.json'))
#ff.toNpy(filename)
#date=np.load('picture_npy/2_0.npy')
#print(date.shape)
#print(date[63][23])
#print(date[67][38])
#ff.jsonslizatVisuaional('picture_process\\1_out')
#ff.toNpys('joint2','picture_npyR=3')
#checkNPY('picture_npy2/6_0.npy')
#checkNPY2xy('picture_npy2/6_0.npy',20,1)
#ff.scanJson('joint','Recode')
#ff.jsonAlllizatVisuaional('test_keypoints.json')
#ff.jsonAlllizatVisuaional('joint/16_0_keypoints.json')
#ff.NPYlizatVisuaional('picture_npyR=3/295_1.npy')
ff.toNpys('test_out','pnew')
#ff.resizeImage('OutBlack-White','resizeBlack-white')