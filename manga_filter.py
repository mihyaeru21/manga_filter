# -*- coding:utf-8 -*-
import os
import Image
import ImageFilter

class MangaFilter:
    """漫画カメラっぽい画像に変換する機能を提供"""

    OUTPUT_TYPE = "png"  # 面倒なのでPNG一択で
    GRAY_COLOR = 128     # 灰色の定義(0 < x < 255ならなんでもいい)

    def __init__(self, name):
        self.img = Image.open(name)
        self.converted = None
        self.naname_img = None
        self.black_gray = 75
        self.white_gray = 115
        self.rinkaku_noise  = 176
        # マスク画像を生成
        self._create_naname_image()
        self._stretch_naname_image()

    def _create_3colors_image(self, brightness):
        """
        3つの値だけで表現された画像を作る
        Image#point()から使う
        """
        if brightness < self.black_gray:
            return 0
        elif brightness < self.white_gray:
            return self.GRAY_COLOR
        else:
            return 255

    def _create_rinkaku_mask(self, brightness):
        """
        輪郭フィルタ後の画像を2値化した画像を作る
        Image#point()から使う
        """
        if brightness < self.rinkaku_noise:
            return 0
        else:
            return 255

    def _create_naname_mask(self, brightness):
        """
        斜め線用のマスク
        Image#point()から使う
        """
        if brightness == self.GRAY_COLOR:
            return 0
        else:
            return 255

    def _create_naname_image(self):
        """斜め線の画像(5*5px)を作成"""
        img = Image.new(mode="L", size=(5, 5), color=255)
        pixel = img.load()
        mask = [[  0, 255, 255, 255, 255],
                [255, 255, 255, 255,   0],
                [255, 255, 255,   0, 255],
                [255, 255,   0, 255, 255],
                [255,   0, 255, 255, 255]]
        for x in range(5):
            for y in range(5):
                pixel[x, y] = mask[x][y]
        self.naname_img = img

    def _stretch_naname_image(self):
        """マスク用の画像を入力画像のサイズまで拡大する"""
        size = self.img.size
        img = Image.new(mode="L", size=size, color=0)
        x = 0
        while x < size[0]:
            y = 0
            while y < size[1]:
                img.paste(self.naname_img, (x,y))
                y += self.naname_img.size[1]
            x += self.naname_img.size[0]
        self.naname_img = img

    def convert(self):
        """変換処理"""
        # 元画像を3値変換
        img = self.img.convert("L")
        img = img.point(self._create_3colors_image)
        # 斜め線のmask処理 グレー部分を透明にしてマスク画像と重ねる
        naname_mask = img.point(self._create_naname_mask)
        img = Image.composite(img, self.naname_img, naname_mask)
        # 輪郭線のmask処理 PILの輪郭フィルタ->グレースケール->適当な値で2値化して真っ黒画像と重ねる
        rinkaku = Image.new(mode="L", size=img.size, color=0)
        rinkaku_mask = self.img.filter(ImageFilter.CONTOUR).convert("L").point(self._create_rinkaku_mask)
        img = Image.composite(img, rinkaku, rinkaku_mask)
        self.converted = img

    def save(self, output_path):
        """ファイル出力"""
        root, ext = os.path.splitext(output_path)
        path = root + "." + self.OUTPUT_TYPE
        self.converted.save(path, self.OUTPUT_TYPE)


def convert_image(input_path, output_path):
    """入力パス名の画像を変換して出力"""
    mf = MangaFilter(input_path)
    mf.convert()
    mf.save(output_path)
    #mf.converted.show()


if __name__ == "__main__":
    convert_image("test.jpg", "test_conved.png")

