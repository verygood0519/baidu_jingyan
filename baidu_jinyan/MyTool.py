import os
import re

from PIL import Image
from urllib.request import urlretrieve
from googletrans import Translator
import pytesseract

#图片合成
def composite_image(pathA,pathB,pathC):
    imageA = Image.open(pathA)
    imageA = imageA.convert('RGBA')
    widthA, heightA = imageA.size

    imageB = Image.open(pathB)
    imageB = imageB.convert('RGBA')
    widthB, heightB = imageB.size

    # 新建透明底图
    resultPicture = Image.new('RGB', imageA.size, (0, 0, 0, 0))  # RGB->.JPG  RGBA->.PNG
    resultPicture.paste(imageA, (0, 0))

    right_bottom = (widthA - widthB - 28, heightA - heightB - 3)
    resultPicture.paste(imageB, right_bottom, imageB)
    resultPicture.save(pathC)
    print(pathC)

def file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        print(root)  # 当前目录路径
        for file in files:
            # print(root + "/" + file)
            composite_image(root + "/" + file,'sign.png','newimg/' + file)

#下载图片
def down_image(url,file_path):
    names = url.split('/')
    name = names[len(names) - 1]
    print(name)
    print(urlretrieve(url,file_path + "i.jpg"))

#翻译
def my_trans(translator,text):
    return translator.translate(text,src='zh-cn').text

'''
获取图片
'''
def getImage(path):
    img = Image.open(path)
    # 打印当前图片的模式以及格式
    print('未转化前的: ', img.mode, img.format)
    # 使用系统默认工具打开图片
    img.show()
    return img

'''
1) 将图片进行降噪处理, 通过二值化去掉后面的背景色并加深文字对比度
'''
def convert_Image(img, standard=127.5):
    '''
    【灰度转换】
    '''
    image = img.convert('L')

    '''
    【二值化】
    根据阈值 standard , 将所有像素都置为 0(黑色) 或 255(白色), 便于接下来的分割
    '''
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y] > standard:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    return image

def change_Image_to_text(img):
    textCode = pytesseract.image_to_string(img)
    # # 去掉非法字符，只保留字母数字
    # textCode = re.sub("\W", "", textCode)
    return textCode



if __name__ == '__main__':
    # file_name('img')
    #down_image('https://imgsa.baidu.com/exp/w=500/sign=60fbeb9270d98d1076d40c31113fb807/ca1349540923dd541868da06dd09b3de9c824840.jpg','img/')
    down_image('https://exp-picture.cdn.bcebos.com/6a408cdd3340b6f375d541aa12c0affce086eee8.jpg?x-bce-process=image%2Fresize%2Cm_lfit%2Cw_500%2Climit_1','img/')
    # print(pytesseract.image_to_string(Image.open()))
    # img = convert_Image(getImage('img/test.png'))
    # img.save('img/test2.png')
    # print('识别的结果：', change_Image_to_text(img))