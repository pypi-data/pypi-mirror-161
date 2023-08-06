# Gongge

九宫格图片分割，最简单的Python图像分割工具。


## 特点

- 默认九宫格分割模式
  - 支持自定义设置分割数量
- 支持分割图像预览
- 默认保存到本地文件夹，包括预览图像

## 安装说明

```Python
pip install Gongge
```

## 调用说明

默认生成九格

```Python
import Gongge

Gongge.split("test.jpg")
```

![test-9.jpg](https://s2.loli.net/2022/08/03/JhDGuSTo925gM71.jpg)

设置参数size修改生成格数

```Python
import Gongge

Gongge.split("test.jpg", size=2)
```

![test-4.jpg](https://s2.loli.net/2022/08/03/xCQMSonrXlivG1I.jpg)


## 效果展示


![test-16.jpg](https://s2.loli.net/2022/08/03/cj58NqzXaFGCIBf.jpg)


![test-25.jpg](https://s2.loli.net/2022/08/03/yYeLb61BfEdhVTR.jpg)


![test-36.jpg](https://s2.loli.net/2022/08/03/HyfAbcSZXDUM9n3.jpg)


![test-49.jpg](https://s2.loli.net/2022/08/03/uSJbemQs8LN5YI4.jpg)


![test-64.jpg](https://s2.loli.net/2022/08/03/YjBSAHNeoXL4Euf.jpg)