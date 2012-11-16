# -*- coding:utf-8 -*-
import Image
import ImageFilter

class MangaFilter:
    """漫画カメラっぽい画像に変換する機能を提供"""
    def __init__(self, name):
        self.img = Image.open(name)
        # 予定ではヒストグラム解析して閾値を決める
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
        mask = [[0x00, 0xff, 0xff, 0xff, 0xff],
                [0xff, 0xff, 0xff, 0xff, 0x00],
                [0xff, 0xff, 0xff, 0x00, 0xff],
                [0xff, 0xff, 0x00, 0xff, 0xff],
                [0xff, 0x00, 0xff, 0xff, 0xff]]
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
        return img

if __name__ == "__main__":
    img = MangaFilter("baby.jpg").convert()
    # 出力
    out_name = "conv.png"
    img.save(out_name, "png")
    img.show()

