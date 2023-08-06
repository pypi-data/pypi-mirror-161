# 全栈自动化测试框架

## 支持平台
* 支持安卓、IOS、H5、Web、接口、windows、mac

## 环境部署

* 安装allure：
    - 下载地址： https://github.com/allure-framework/allure2/releases
    - windows: 直接下载allure的zip包，解压到本地，然后配置到环境变量
    - mac：使用brew命令安装
      * 安装brew：/usr/bin/ruby -e "$(curl -fsSL https://cdn.jsdelivr.net/gh/ineo6/homebrew-install/install)"
      * brew install allure
* 安装python依赖库
    - 默认：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrunner
    - mac端：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrunner[mac]
    - windows端：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrunner[win]

## 更新内容
* 2022年5月
    - 支持allure报告数据获取
    - web测试支持配置默认域名
    - 支持报告生成目录可配置
    - 优化web测试相关代码
    - 增加测试步骤文案的设置
    - 增加截图标红当前控件的功能
    - 自动获取安装webview对应chrome版本，并自动下载安装对应版本chromedriver
    - 解决安卓端click方式有时候定位成功，但是实际没有点击成功的问题
    
* 2022年5月30日
    - api测试增加步骤描述
    - 把不常用的依赖包放到extras_require里面
  
* 2022年6月01日
    - 增加特征点-sift方式图像识别功能（支持安卓、ios）
  
* 2022年6月02日
    - 增加pc端自动化功能（支持windows和mac，需要单独安装附加的库）
  
* 2022年6月06日
    - 修改脚手架，调整目录结构
  
