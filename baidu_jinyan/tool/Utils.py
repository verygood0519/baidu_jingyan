import base64
import socket
from urllib.request import urlretrieve

#from googletrans import Translator
import pymysql
from google_trans_new import google_translator
from WatermarkRemover import WatermarkRemover
import uuid
import traceback
import os
import time
import json

class Utils(object):

    def __init__(self, watermark_template="../baidu.jpg"):
        self.translator = google_translator(timeout=10)

        self.remover = WatermarkRemover()
        self.remover.load_watermark_template(watermark_template)

    def translate_to_es(self,context,link):
        """翻译成西班牙语并返回"""
        text_es = '翻译失败'
        # return text_es  #不翻译
        context = context.replace('\n','').replace('​','')
        if str.strip(context) == '':
            return ''
        try:
            text_es = self.translator.translate(context, lang_tgt='es')
        except Exception as e:
            tran_count = 1
            while tran_count <= 5:
                try:
                    text_es = self.translator.translate(context, lang_tgt='es')
                    break
                except Exception as e:
                    err_info = 'ReTraning for %d time' % tran_count if tran_count == 1 else 'ReTraning for %d times' % tran_count
                    print(err_info)
                    self.save_file('log.txt', err_info)
                    tran_count += 1
            if tran_count > 5:
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
        # return base64_images #不下载图片
        i = 1;
        if len(imageUrls) == 0 :
            return []
        try:
            for imageUrl in imageUrls:
                if imageUrl == '':
                    continue
                fileName = str(i)
                # 设置超时时间为30s
                socket.setdefaulttimeout(20)
                # 解决下载不完全问题且避免陷入死循环
                try:
                    urlretrieve(imageUrl, fileName + ".jpg")
                except socket.timeout:
                    count = 1
                    while count <= 5:
                        try:
                            urlretrieve(imageUrl, fileName + ".jpg")
                            break
                        except socket.timeout:
                            err_info = 'Reloading for %d time' % count if count == 1 else 'Reloading for %d times' % count
                            print(err_info)
                            self.save_file('log.txt', err_info)
                            count += 1
                    if count > 5:
                        print("downloading picture fialed!")
                        self.save_file('log.txt', "downloading picture fialed!" )
                        base64_images.append('下载失败')
                        continue
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
    def updateTran(self):
        self.conn = pymysql.connect('localhost', 'root', '123456', 'funnydb',
                                    charset='utf8mb4')  # 有中文要存入数据库的话要加charset='utf8'
        # 创建游标
        self.cursor = self.conn.cursor()
        sql = "SELECT * FROM funnytable WHERE isTran = 0"
        self.conn.ping(reconnect=True)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for result in results:
            original_text = json.loads(result[4])
            tran_text = json.loads(result[5])
            if tran_text['title'] == '翻译失败':
                tran_text['title']  = self.translate_to_es(original_text['title'],result[3])
            if tran_text['summary'] == '翻译失败':
                tran_text['summary'] = self.translate_to_es(original_text['summary'], result[3])
            original_content = original_text['content']
            tran_content = tran_text['content']
            i = 0
            print(i)
            print("-",result[0],result[1],result[2],result[3])
            for item in tran_content:
                if item['subtitle'] == '翻译失败':
                    item['subtitle'] = self.translate_to_es(original_content[i]['subtitle'], result[3])
                original_element = original_content[i]['element']
                tran_element = item['element']
                sub_i = 0
                for sub_item in tran_element:
                    if sub_item['text'] == '翻译失败':
                        sub_item['text'] = self.translate_to_es(original_element[sub_i]['text'], result[3])
                    sub_i += 1
                i += 1
            tran_text_new = json.dumps(tran_text)
            if '翻译失败' not in tran_text_new:
                update = "update funnytable set traText = '" + pymysql.escape_string(tran_text_new) +  "',istran = 1 where id = " + str(result[0])
                self.cursor.execute(update)
                self.conn.commit()
            else:
                istran = 0
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    utils = Utils("../baidu.jpg")
    utils.updateTran();
    # utils.wipe_lm("../img/image.jpg","../img/image_new.jpg")
    # print(utils.translate_to_es("冬寒菜 500克",''))
