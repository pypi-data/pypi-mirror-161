import os
import subprocess
import time
import wda

from core.ios.common import get_device_list
from qrunner.utils.log import logger
from qrunner.utils.config import conf
from utils.exceptions import DeviceNotFoundException


class IosDriver(object):
    _instance = {}

    def __new__(cls, serial_no=None, bundle_id=None):
        if not serial_no:
            serial_no = conf.get_item('app', 'serial_no')
        if serial_no not in cls._instance:
            cls._instance[serial_no] = super().__new__(cls)
        return cls._instance[serial_no]

    def __init__(self, serial_no=None):
        self.serial_no = serial_no if serial_no else conf.get_item('app', 'serial_no')
        if serial_no in get_device_list():
            self.serial_no = serial_no
        else:
            raise DeviceNotFoundException(msg=f'设备 {serial_no} 未连接')
        self.bundle_id = conf.get_item('app', 'pkg_name')
        logger.info(f'启动 ios driver for {self.serial_no}')
        self.d = wda.USBClient(self.serial_no, port=8100)

    @classmethod
    def get_instance(cls, serial_no=None):
        if serial_no not in cls._instance:
            logger.info(f'{serial_no} Create ios driver singleton')
            return IosDriver(serial_no)
        return IosDriver._instance[serial_no]

    def install_app(self, ipa_url):
        cmd = f'tidevice -u {self.serial_no} install {ipa_url}'
        logger.info(f'安装应用: {ipa_url}')
        output = subprocess.getoutput(cmd)
        if 'Complete' in output.split()[-1]:
            logger.info(f'{self.serial_no} 安装应用{ipa_url} 成功')
            return
        else:
            logger.info(f'{self.serial_no} 安装应用{ipa_url}失败，因为{output}')

    def new_install_app(self, ipa_url, bundle_id=None):
        pkg_name = bundle_id if bundle_id else self.bundle_id
        self.uninstall_app(pkg_name)
        cmd = f'tidevice -u {self.serial_no} install {ipa_url}'
        logger.info(f'安装应用: {ipa_url}')
        output = subprocess.getoutput(cmd)
        if 'Complete' in output.split()[-1]:
            logger.info(f'{self.serial_no} 安装应用{ipa_url} 成功')
            return
        else:
            logger.info(f'{self.serial_no} 安装应用{ipa_url}失败，因为{output}')

    def uninstall_app(self, bundle_id=None):
        pkg_name = bundle_id if bundle_id else self.bundle_id
        cmd = f'tidevice -u {self.serial_no} uninstall {pkg_name}'
        logger.info(f'卸载应用: {pkg_name}')
        output = subprocess.getoutput(cmd)
        if 'Complete' in output.split()[-1]:
            logger.info(f'{self.serial_no} 卸载应用{pkg_name} 成功')
            return
        else:
            logger.info(f'{self.serial_no} 卸载应用{pkg_name}失败，因为{output}')

    def start_app(self, bundle_id=None):
        if not bundle_id:
            bundle_id = self.bundle_id
        logger.info(f'启动应用: {bundle_id}')
        self.d.app_start(bundle_id)

    def force_start_app(self, bundle_id=None):
        if not bundle_id:
            bundle_id = self.bundle_id
        logger.info(f'强制启动应用: {bundle_id}')
        self.d.app_terminate(bundle_id)
        self.start_app(bundle_id)

    def stop_app(self, bundle_id=None):
        if not bundle_id:
            bundle_id = self.bundle_id
        logger.info(f'停止应用: {bundle_id}')
        self.d.app_terminate(bundle_id)

    def app_current(self):
        cur_apps = self.d.app_current()
        logger.info(f'获取运行中的app列表: {cur_apps}')
        return cur_apps

    def app_launch(self, bundle_id=None):
        if not bundle_id:
            bundle_id = self.bundle_id
        logger.info(f'将应用切到前台: {bundle_id}')
        self.d.app_launch(bundle_id)

    def back(self):
        logger.info('返回上一页')
        time.sleep(1)
        self.d.swipe(0, 100, 100, 100)

    def go_home(self):
        logger.info('返回手机主页')
        self.d.home()

    def send_keys(self, value):
        logger.info(f'输入: {value}')
        self.d.send_keys(value)

    def screenshot(self, file_name):
        """
        截图并保存到预定路径
        @param file_name: foo.png or fool
        @return:
        """
        # 把文件名处理成test.png的样式
        if '.' in file_name:
            file_name = file_name.split(r'.')[0]
        # 截图并保存到当前目录的images文件夹中
        img_dir = os.path.join(os.getcwd(), 'images')
        if os.path.exists(img_dir) is False:
            os.mkdir(img_dir)
        time_str = time.strftime('%Y年%m月%d日 %H时%M分%S秒')
        file_path = os.path.join(img_dir, f'{time_str}-{file_name}.png')
        self.d.screenshot(file_path)
        # # 上传allure报告
        # allure.attach.file(file_path, attachment_type=allure.attachment_type.PNG, name=f'{file_name}.png')
        return file_path

    # def screenshot_and_mark(self, file_name, rect):
    #     """给图片指定范围画上红框
    #     rect: [x, y, width, height]
    #     x: 左上坐标x
    #     y：左上角坐标y
    #     width：矩形宽度
    #     height：矩形高度
    #     """
    #     # 把文件名处理成test.png的样式
    #     if '.' in file_name:
    #         file_name = file_name.split(r'.')[0]
    #     # 截图并保存到当前目录的images文件夹中
    #     img_dir = os.path.join(os.getcwd(), 'images')
    #     if os.path.exists(img_dir) is False:
    #         os.mkdir(img_dir)
    #     time_str = time.strftime('%Y年%m月%d日 %H时%M分%S秒')
    #     file_path = os.path.join(img_dir, f'{time_str}-{file_name}.png')
    #     self.d.screenshot(file_path)
    #     # 画框
    #     ImageRecognition.mark(file_path, rect)
    #     # 上传allure报告
    #     allure.attach.file(file_path, attachment_type=allure.attachment_type.PNG, name=f'{file_name}.png')
    #     return file_path

    @property
    def page_content(self):
        page_source = self.d.source(accessible=False)
        logger.info(f'获取页面内容: \n{page_source}')
        return page_source

    def get_window_size(self):
        size = self.d.window_size()
        logger.info(f'获取屏幕尺寸: {size}')
        return size

    def click(self, x, y):
        logger.info(f'点击坐标: ({x}, {y})')
        logger.info(f'{self.serial_no} Tap point ({x}, {y})')
        self.d.appium_settings({"snapshotMaxDepth": 0})
        self.d.tap(x, y)
        self.d.appium_settings({"snapshotMaxDepth": 50})
        time.sleep(1)

    def double_click(self, x, y):
        logger.info(f'双击坐标: {x},{y}')
        self.d.double_tap(x, y)

    def tap_hold(self, x, y):
        logger.info(f'长按: {x},{y}')
        self.d.tap_hold(x, y, 1.0)

    def click_alert(self, alert_list: list):
        try:
            self.d.alert.click(alert_list)
        except:
            pass

    def swipe(self, start_x, start_y, end_x, end_y, duration=0):
        logger.info(f'从坐标({start_x}, {start_y})滑动到({end_x}, {end_y})')
        logger.info(f'{self.serial_no} swipe from point ({start_x}, {start_y}) to ({end_x}, {end_y})')
        self.d.appium_settings({"snapshotMaxDepth": 2})
        self.d.swipe(int(start_x), int(start_y), int(end_x), int(end_y), duration)
        self.d.appium_settings({"snapshotMaxDepth": 50})
        time.sleep(2)

    def swipe_by_screen_percent(self, start_x_percent, start_y_percent, end_x_percent, end_y_percent, duration=0):
        logger.info(f'根据屏幕百分比进行滑动')
        w, h = self.d.window_size()
        start_x = w * start_x_percent
        start_y = h * start_y_percent
        end_x = w * end_x_percent
        end_y = h * end_y_percent
        self.swipe(start_x, start_y, end_x, end_y, duration=duration)

    def swipe_left(self, start_percent=1, end_percent=0.5):
        logger.info('往左边滑动')
        w, h = self.d.window_size()
        self.swipe(start_percent * (w - 1), h/2, end_percent * w, h/2)

    def swipe_right(self, start_percent=0.5, end_percent=1):
        logger.info('往右边滑动')
        w, h = self.d.window_size()
        self.swipe(start_percent * w, h / 2, end_percent * (w - 1), h / 2)

    def swipe_up(self, start_percent=0.8, end_percent=0.2):
        logger.info('往上边滑动')
        w, h = self.d.window_size()
        self.swipe(w / 2, start_percent * h, w / 2, end_percent * h)

    def swipe_down(self, start_percent=0.2, end_percent=0.8):
        logger.info('往下面滑动')
        w, h = self.d.window_size()
        self.swipe(w / 2, start_percent * h, w / 2, end_percent * h)

    def check(self):
        logger.info('健康检查')
        self.d.healthcheck()

    def locked(self):
        logger.info('是否锁屏')
        status = self.d.locked()
        logger.info(status)
        return status

    def lock(self):
        logger.info('锁住屏幕')
        self.d.lock()

    def unlock(self):
        logger.info('解锁屏幕')
        self.d.unlock()

    def open_url(self, url):
        """
        打开schema
        @param: url，schema链接，taobao://m.taobao.com/index.htm
        @return:
        """
        logger.info(f'打开url: {url}')
        self.d.open_url(url)

    @property
    def battery_info(self):
        info = self.d.battery_info()
        logger.info(f'电池信息: {info}')
        return info

    @property
    def device_info(self):
        info = self.d.device_info()
        logger.info(f'设备信息: {info}')
        return info

    @property
    def scale(self):
        scale = self.d.scale
        logger.info(f'设备分辨率: {scale}')
        return scale






