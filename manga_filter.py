# -*- coding:utf-8 -*-
import Image
import ImageFilter

BLACK_LINE = 75
GRAY_LINE  = 115
GRAY_COLOR = 0xaa

def to3colors(brightness):
    """画素の値を3値化する"""
    if brightness < BLACK_LINE:
        return 0x00
    elif brightness < GRAY_LINE:
        return GRAY_COLOR
    else:
        return 0xff

def to2colors(brightness):
    """画素の値を2値化する(輪郭フィルター後に使う)"""
    if brightness < 0xb0:
        return 0x00
    else:
        return 0xff

def make_mask(brightness):
    """GRAYな部分だけα値を0に"""
    if brightness == GRAY_COLOR:
        return 0x00
    else:
        return 0xff

def stretch_mask_image(size):
    """マスク用の画像を入力画像のサイズまで拡大する"""
    img = Image.new(mode="L", size=size, color=GRAY_COLOR)
    mono = Image.open("mask.png")
    x = 0
    while x < size[0]:
        y = 0
        while y < size[1]:
            img.paste(mono, (x,y))
            y += mono.size[1]
        x += mono.size[0]
    return img

def main():
    in_name = "baby.jpg"
    raw = Image.open(in_name)

    # 3値変換
    img = raw.convert("L").point(to3colors)

    # 塗りつぶし線のmask処理
    sen = stretch_mask_image(img.size)
    sen_mask = img.point(make_mask)
    img = Image.composite(img, sen, sen_mask)

    # 輪郭線のmask処理
    rin = Image.new(mode="L", size=img.size, color=0)
    rin_mask = raw.filter(ImageFilter.CONTOUR).convert("L").point(to2colors)
    img = Image.composite(img, rin, rin_mask)

    # 出力
    out_name = "conv.png"
    img.save(out_name, "png")
    img.show() # ついでに表示


if __name__ == "__main__":
    main()

