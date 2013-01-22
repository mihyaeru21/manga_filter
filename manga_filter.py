# -*- coding: utf-8 -*-
import os
from PIL import Image
from PIL import ImageFilter

class MangaFilter:
    """漫画カメラっぽい画像に変換する機能を提供"""

    OUTPUT_TYPE = "png"  # 面倒なのでPNG一択で
    GRAY_COLOR = 128     # 灰色の定義(0 < x < 255ならなんでもいい)
    MAX_SIZE = 640       # 縦横ともに最大640px

    def __init__(self, name):
        self.img = Image.open(name)
        self.gray_img = self.img.convert("L")
        self.converted = None
        self.naname_img = None
        self.black_gray = 75   # 適当な初期値
        self.white_gray = 115  # 同じく
        self.rinkaku_noise  = 176
        self._create_naname_image()
        self._analyze_histogram()

    def _analyze_histogram(self):
        """ヒストグラムから、3色の境目を補正する"""
        # 関数長い分割せねばﾒﾝﾄﾞｸｾ
        hist = self.gray_img.histogram()
        max_pixel = self.gray_img.size[0] * self.gray_img.size[1]
        # 明るさ強度を4分割し、黒、2灰、白としてカウント
        black_count = 0
        gray_count = 0
        white_count = 0
        for brightness, pixel in enumerate(hist):
            if brightness < 64:
                black_count += pixel
            elif brightness < 192:
                gray_count += pixel
            else:
                white_count += pixel
        # 白黒の平均と灰を比較して灰部分の幅を決める
        avg = (black_count + white_count) / 2
        if gray_count > avg * 2:
            gray_range = 20
        elif gray_count < avg / 10:  # 極端に白か黒が多いパターン
            gray_range = 60
        elif gray_count < avg / 6:
            gray_range = 40
        elif gray_count < avg / 2:
            gray_range = 30
        else:
            gray_range = 25

        # 全体の1/5のピクセル数が出てくる所を基準点として
        # 灰領域を、上で求めた幅分白黒側にとる
        black_gray = 0
        white_gray = 0
        count = 0
        for brightness, pixel in enumerate(hist):
            count += pixel
            if count >= max_pixel  / 5:
                black_gray = brightness - gray_range
                white_gray = brightness + gray_range
                break
        offset = abs(black_gray - white_gray)
        if black_gray < gray_range:
            black_gray += offset
            white_gray += offset
        if white_gray > 255 - gray_range:
            black_gray -= offset
            white_gray -= offset
        self.black_gray = black_gray
        self.white_gray = white_gray

    def _create_small_image(self, image):
        """大きい画像なら画像を小さくして返す"""
        size = image.size
        if size[0] > size[1]:
            large_index = 0
        else:
            large_index = 1
        if size[large_index] <= self.MAX_SIZE:
            return image
        if large_index == 0:
            x = self.MAX_SIZE
            y = int(1.0 * x * size[1] / size[0])
        else:
            y = self.MAX_SIZE
            x = int(1.0 * y * size[0] / size[1])
        return image.resize((x, y), Image.ANTIALIAS)

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

    def _stretch_naname_image(self, size):
        """マスク用の画像を入力画像のサイズまで拡大する"""
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
        # 画像サイズを小さくする
        small_img = self._create_small_image(self.gray_img)
        # 元画像を3値変換
        img = small_img.point(self._create_3colors_image)
        # 斜め線のmask処理 グレー部分を透明にしてマスク画像と重ねる
        self._stretch_naname_image(img.size)
        naname_mask = img.point(self._create_naname_mask)
        img = Image.composite(img, self.naname_img, naname_mask)
        # 輪郭線のmask処理 PILの輪郭フィルタ->グレースケール->適当な値で2値化して真っ黒画像と重ねる
        rinkaku = Image.new(mode="L", size=img.size, color=0)
        rinkaku_mask = small_img.filter(ImageFilter.CONTOUR).convert("L").point(self._create_rinkaku_mask)
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


if __name__ == "__main__":
    #convert_image("t.png", "test_conved.png")
    convert_image("kai.jpg", "test_conved.png")

