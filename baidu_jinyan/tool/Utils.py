import base64
from urllib.request import urlretrieve

from googletrans import Translator
from WatermarkRemover import WatermarkRemover
import uuid
import traceback
import os
import time


class Utils(object):

    def __init__(self, watermark_template):
        self.translator = Translator(service_urls=[
            'translate.google.cn', ])

        self.remover = WatermarkRemover()
        self.remover.load_watermark_template(watermark_template)

    def translate_to_es(self,context,link):
        """翻译成西班牙语并返回"""
        text_es = '翻译失败'
        try:
            text_es = self.translator.translate(context, src='zh-cn', dest='es').text
        except Exception as e:
            self.save_file('log.txt',"翻译失败报错：" + link + "\n" + traceback.format_exc())
        return text_es

    def wipe_lm(self, origin_pic,new_pic_file):
        """去水印返回新图片的本地地址"""

        # new_pic_file = str(uuid.uuid1()) + os.path.splitext(origin_pic)[-1]
        self.remover.remove_watermark(origin_pic, new_pic_file)
        return new_pic_file

    def down_image(self,url,file_path):
        if url == '':
            return ''
        return urlretrieve(url,file_path + "image.jpg")

    def base64_image(self,imageUrls,link):
        base64_images = []
        # return base64_images
        i = 1;
        if len(imageUrls) == 0 :
            return []
        try:
            for imageUrl in imageUrls:
                if imageUrl == '':
                    continue
                fileName = str(i)
                urlretrieve(imageUrl, fileName + ".jpg")
                self.wipe_lm(fileName + ".jpg",fileName + "_new.jpg")
                with open(fileName + "_new.jpg", 'rb') as f:
                    image = f.read()
                    image_base64 = str(base64.b64encode(image), encoding='utf-8')
                    base64_images.append(image_base64)
                    f.close()
                os.remove(fileName + ".jpg")
                os.remove(fileName + "_new.jpg")
                i = i + 1
        except Exception as e:
            self.save_file('log.txt',"图片base64失败报错：" + link + "\n" +traceback.format_exc())
        return base64_images

    def save_file(self,file_name,content):
        with open(file_name, 'a+') as f:
            f.write('===========================================  ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +
                    '===========================================\n')  # 加\n换行显示
            f.write(content + '\n')  # 加\n换行显示
            f.write('===========================================================================================================\n')  # 加\n换行显示
            f.close()
if __name__ == '__main__':
    utils = Utils("../baidu.jpg")
    # utils.wipe_lm("../img/image.jpg")
    # print(utils.translate_to_es("冬寒菜 500克"))
