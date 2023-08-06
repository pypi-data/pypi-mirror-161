from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os


def split(img_path, size=3):
    # 读取图片
    im = Image.open(img_path)
    # 宽高各除 3，获取裁剪后的单张图片大小
    width, height = im.size[0] // size, im.size[1] // size
    # 裁剪图片的左上角坐标
    start_x, start_y = 0, 0
    # 用于给图片命名
    number = 1
    img_name = img_path.split(".")[0]+f"-{size*size}"
    # 创建目录
    if not os.path.exists(img_name):
        os.makedirs(img_name)
    # 循环裁剪图片
    for i in range(size):
        for n in range(size):
            # 裁剪图片并保存
            crop = im.crop((start_x, start_y, start_x + width, start_y + height))
            crop.save(os.path.join(img_name, f"{number}.jpg"))
            # 将左上角坐标的 x 轴向右移动
            start_x += width
            number += 1
        # 当第一行裁剪完后 x 继续从 0 开始裁剪
        start_x = 0
        # 裁剪第二行
        start_y += height
    """预览图"""
    np_img = np.array(im)
    np_img_height, np_img_width, np_size = np_img.shape
    h_stage, h_init = int(np_img_height / size), int(np_img_height / size)
    w_stage, w_init = int(np_img_width / size), int(np_img_width / size)
    for i in range(size):
        np_img[h_stage:h_stage + 10, :, :] = 255
        np_img[:, w_stage:w_stage + 10, :] = 255
        h_stage += h_init
        w_stage += w_init
    file = Image.fromarray(np_img)
    file.save(os.path.join(img_name, f"preview.jpg"))
    plt.imshow(np_img)
    plt.show()

