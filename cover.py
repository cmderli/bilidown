#coding:utf-8
# BiliMusic Cover Image
# Copyright (C) 2023 cmderli. This program is a free software.
from PIL import Image, ImageFilter
import os
# Correctly Gaussian Blur in PIL
# https://www.cnblogs.com/lurenjiashuo/p/python-pil-gaussianblur.html
class Blur(ImageFilter.Filter):
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
    coverImg = Image.open(f'{CACHE_DIR}/bilimusic.cache.coverImage.{bv}')
    coverImgBlurred = coverImg
    coverImgBlurred = coverImgBlurred.filter(Blur(blurRadius=100))
    coverImgBlurredHeight = coverImgBlurred.height
    coverImgBlurredWidth = coverImgBlurred.width
    coverImgBlurredX = (coverImgBlurredWidth-coverImgBlurredHeight) // 2
    coverImgBlurred = coverImgBlurred.crop((coverImgBlurredX, 0, coverImgBlurredX+coverImgBlurredHeight, coverImgBlurredHeight))
    coverImgBlurred = coverImgBlurred.resize((COVER_RES, COVER_RES))
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
    coverImage.save(f'{CACHE_DIR}/bilimusic.cache.cover.{bv}.jpg')