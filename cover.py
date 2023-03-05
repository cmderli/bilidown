#coding:utf-8
# Bilidown Cover Image
# Copyright (C) 2023 cmderli. This program is a free software.
from PIL import Image, ImageFilter
import os
# BV1Vx4y1M7Pf
class Blur(ImageFilter.Filter):
    # https://www.cnblogs.com/lurenjiashuo/p/python-pil-gaussianblur.html
    name = "GaussianBlur"
    def __init__(self, blurRadius, bounds = None):
        self.blurRadius = blurRadius
        self.bounds = bounds
    def filter(self, image):
        if self.bounds:
            imageCilp = image.crop(self.bounds).gaussian_blur(self.blurRadius)
            image.paste(imageCilp, self.bounds)
            return image
        else:
            return image.gaussian_blur(self.blurRadius)
def cover(bv, COVER_RES, CACHE_DIR):
    coverImg = Image.open(f'{CACHE_DIR}/bilidown_CACHE_coverImage_{bv}')
    coverImgBlurred = coverImg
    coverImgBlurred = coverImgBlurred.filter(Blur(blurRadius=100))
    coverImgBlurredHeight = coverImgBlurred.height
    coverImgBlurredWidth = coverImgBlurred.width
    coverImgBlurredX = (coverImgBlurredWidth-coverImgBlurredHeight) // 2
    coverImgBlurred = coverImgBlurred.crop((coverImgBlurredX, 0, coverImgBlurredX+coverImgBlurredHeight, coverImgBlurredHeight))
    coverImgBlurred = coverImgBlurred.resize((COVER_RES, COVER_RES))
    # coverImgBlurred.show()
    # coverImgSmall = Image.open(f'{CACHE_DIR}/bilidown_CACHE_coverImage_{bv}')
    """
    coverImgSmall = coverImg.resize((50, 50))
    coverImgArray = coverImgSmall.load()
    coverWidth , coverHeight = coverImgSmall.size
    print(coverWidth , coverHeight)
    colors = []
    colorAvg = [0, 0, 0]
    for x in range(coverWidth):
        for y in range(coverHeight):
            coverColor = coverImgArray[x, y]
            colorAvg[0] += coverColor[0]
            colorAvg[1] += coverColor[1]
            colorAvg[2] += coverColor[2]
            # print(coverColor)
            colors.append(coverColor)
    # os._exit()
    colorAvg[0] = colorAvg[0] // (coverHeight * coverWidth)
    colorAvg[1] = colorAvg[1] // (coverHeight * coverWidth)
    colorAvg[2] = colorAvg[2] // (coverHeight * coverWidth)
    colorFinalTuple = max(colors, key=colors.count)
    colorFinal = list(colorFinalTuple)
    colorFinal[0] = (colorFinal[0] + colorAvg[0]*2) // 3
    colorFinal[1] = (colorFinal[1] + colorAvg[1]*2) // 3
    colorFinal[2] = (colorFinal[2] + colorAvg[2]*2) // 3"""
    coverImage = Image.new(mode='RGB', 
                           size=(COVER_RES, COVER_RES)) # color = (colorFinal[0], colorFinal[1], colorFinal[2])
    coverImage.paste(coverImgBlurred, (0, 0))
    width = COVER_RES
    wid = COVER_RES / float(coverImg.size[0])
    hei = int(float(coverImg.size[1]) * float(wid))
    coverImg = coverImg.resize((width, hei))
    # coverImg.show()
    y = (COVER_RES - hei) // 2 # Start paste y
    coverImage.paste(coverImg, (0, y))
    coverImage.save(f'{CACHE_DIR}/bilidown_CACHE_cover_{bv}.jpg')