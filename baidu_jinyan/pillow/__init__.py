from PIL import Image

imageA = Image.open('../img/123.jpg')
imageA = imageA.convert('RGBA')
widthA , heightA = imageA.size

imageB = Image.open('../img/sign.png')
imageB = imageB.convert('RGBA')
widthB , heightB = imageB.size

#新建透明底图
resultPicture = Image.new('RGB', imageA.size, (0, 0, 0, 0))   #RGB->.JPG  RGBA->.PNG
resultPicture.paste(imageA,(0,0))

right_bottom = (widthA - widthB -28, heightA - heightB - 3)
resultPicture.paste(imageB, right_bottom, imageB)

resultPicture.save('../img/new.jpg')