# -*- coding:utf-8 -*-
import os
import Image
import ImageFilter

class MangaFilter:
    """漫画カメラっぽい画像に変換する機能を提供"""

    OUTPUT_TYPE = "png"  # 面倒なのでPNG一択で

    def __init__(self, name):
        self.img = Image.open(name)
        self.converted = None
        self.black = 75
        self.white = 115
        self.gray  = 0xaa
        self.digi  = 0xb0

    def to3colors(self, brightness):
        """画素の値を3値化する"""
        if brightness < self.black:
            return 0x00
        elif brightness < self.white:
            return self.gray
        else:
            return 0xff

    def to2colors(self, brightness):
        """画素の値を2値化する(輪郭フィルター後に使う)"""
        if brightness < self.digi:
            return 0x00
        else:
            return 0xff

    def make_mask(self, brightness):
        """GRAYな部分だけα値を0に"""
        if brightness == self.gray:
            return 0x00
        else:
            return 0xff

    def create_mask_image(self):
        """斜め線の画像(5*5px)を作成"""
        img = Image.new(mode="L", size=(5, 5), color=0xff)
        pixel = img.load()
        mask = [[  0, 255, 255, 255, 255],
                [255, 255, 255, 255,   0],
                [255, 255, 255,   0, 255],
                [255, 255,   0, 255, 255],
                [255,   0, 255, 255, 255]]
        for x in range(5):
            for y in range(5):
                pixel[x, y] = mask[x][y]
        return img

    def stretch_mask_image(self):
        """マスク用の画像を入力画像のサイズまで拡大する"""
        size = self.img.size
        img = Image.new(mode="L", size=size, color=0)
        mono = self.create_mask_image()
        x = 0
        while x < size[0]:
            y = 0
            while y < size[1]:
                img.paste(mono, (x,y))
                y += mono.size[1]
            x += mono.size[0]
        return img

    def convert(self):
        """変換処理"""
        # 3値変換
        img = self.img.convert("L").point(self.to3colors)
        # 塗りつぶし線のmask処理
        sen = self.stretch_mask_image()
        sen_mask = img.point(self.make_mask)
        img = Image.composite(img, sen, sen_mask)
        # 輪郭線のmask処理
        rin = Image.new(mode="L", size=img.size, color=0)
        rin_mask = self.img.filter(ImageFilter.CONTOUR).convert("L").point(self.to2colors)
        img = Image.composite(img, rin, rin_mask)
        self.converted = img

    def save(self, output_path):
        root, ext = os.path.splitext(output_path)
        path = root + "." + self.OUTPUT_TYPE
        self.converted.save(path, self.OUTPUT_TYPE)


def convert_image(input_path, output_path):
    """入力パス名の画像を変換して出力"""
    mf = MangaFilter(input_path)
    mf.convert()
    mf.save(output_path)
    mf.converted.show()


if __name__ == "__main__":
    convert_image("test.jpg", "test_conved.png")

