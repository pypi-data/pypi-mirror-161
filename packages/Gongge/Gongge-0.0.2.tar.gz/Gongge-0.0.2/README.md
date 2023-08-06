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

![](img/test-9.jpg)

设置参数size修改生成格数

```Python
import Gongge

Gongge.split("test.jpg", size=2)
```

![](img/test-4.jpg)


## 效果展示


![](img/test-16.jpg)

![](img/test-25.jpg)

![](img/test-36.jpg)

![](img/test-49.jpg)

![](img/test-64.jpg)