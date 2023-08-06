import inspect
import time
import typing
from multiprocessing.dummy import Pool as ThreadPool
# from typing import Union
from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector
from qrunner.utils.log import logger
from qrunner.utils.config import conf
from qrunner.core.android.driver import AndroidDriver
from qrunner.utils.exceptions import NoSuchElementException, ElementNameEmptyException


class Element(object):
    """
    安卓元素定义
    """
    def __init__(self, *args, **kwargs):
        # 从kwargs中删掉并返回index
        self._index = kwargs.pop('index', 0)
        self.desc = kwargs.pop('desc', '')
        if not self.desc:
            raise ElementNameEmptyException('请设置控件名称')
        self._xpath = kwargs.get('xpath', '')
        self._kwargs = kwargs
        _serial_no = conf.get_item('app', 'serial_no')
        self._driver = AndroidDriver.get_instance(_serial_no)
        self._pkg_name = conf.get_item('app', 'pkg_name')
        self._resourceId = kwargs.pop('resourceId', '')
        if self._resourceId:
            kwargs['resourceId'] = f'{self._pkg_name}:{self._resourceId}'
        self._d = self._driver.d

    def handle_alert(self, alert_list):
        """
        根据不同定位方式进行点击
        @return:
        """
        def click_alert(loc):
            if 'id/' in loc:
                element = self._d(resourceId=f'{self._pkg_name}:{loc}')
            elif '//' in loc:
                element = self._d.xpath(loc)
            else:
                element = self._d(text=loc)
            element.click_exists(timeout=1)

        # 多线程执行点击过程
        # alert_list = conf.get_item('app', 'android_alert')
        # pool = ThreadPool(len(alert_list))
        # if alert_list:
        #     pool.map(click_alert, alert_list)
        if alert_list:
            print(f'处理弹窗: {alert_list}')
            for alert in alert_list:
                click_alert(alert)
            logger.debug('处理异常弹窗完成')

    # def find_element(self, retry=3, timeout=3):
    #     """
    #     循环查找元素，查找失败先处理弹窗后重试，后面再考虑xpath要不要用.all()改造一下
    #     @param retry: 重试次数
    #     @param timeout: 每次查找超时时间
    #     @param alert_check: 是否监控弹窗
    #     @return: 找到的元素列表
    #     """
    #     logger.info(f'查找元素: {self._kwargs},{self._index}')
    #     _element = self._d.xpath(self._xpath) if \
    #         self._xpath else self._d(**self._kwargs)[self._index]
    #     while not _element.wait(timeout=timeout):
    #         if retry > 0:
    #             retry -= 1
    #             logger.warning(f'重试 查找元素： {self._kwargs},{self._index}')
    #         else:
    #             frame = inspect.currentframe().f_back
    #             caller = inspect.getframeinfo(frame)
    #             logger.warning(f'【{caller.function}:{caller.lineno}】未找到元素 {self._kwargs}')
    #             return None
    #     return _element

    def find_element(self, retry=3, timeout=3, alert_list=None):
        """
        循环查找元素，查找失败先处理弹窗后重试，后面再考虑xpath要不要用.all()改造一下
        @param retry: 重试次数
        @param timeout: 每次查找超时时间
        @param alert_list
        @return: 找到的元素列表
        """
        logger.info(f'查找元素: {self._kwargs},{self._index}')
        _element = self._d.xpath(self._xpath) if \
            self._xpath else self._d(**self._kwargs)[self._index]
        self.handle_alert(alert_list)  # 处理异常弹窗
        cur_retry = retry
        while not _element.wait(timeout=timeout):
            if cur_retry > 0:
                logger.warning(f'第{retry-cur_retry+1}次重试，查找元素： {self._kwargs},{self._index}')
                cur_retry -= 1
                self.handle_alert(alert_list)  # 处理异常弹窗
            else:
                frame = inspect.currentframe().f_back
                caller = inspect.getframeinfo(frame)
                logger.warning(f'【{caller.function}:{caller.lineno}】未找到元素 {self._kwargs}')
                return None
        return _element

    def get_element(self, retry=3, timeout=3, alert_list=None):
        """
        针对元素定位失败的情况，抛出NoSuchElementException异常
        @param retry:
        @param timeout:
        @param alert_list
        @return:
        """
        element = self.find_element(retry=retry, timeout=timeout, alert_list=alert_list)
        if element is None:
            self._driver.screenshot(f'[控件 {self.desc} 定位失败]')
            raise NoSuchElementException(f'[控件 {self.desc} 定位失败]')
        return element

    @property
    def info(self):
        logger.info(f'获取元素: {self._kwargs} 的所有信息')
        return self.get_element().info

    @property
    def text(self):
        logger.info(f'获取元素: {self._kwargs} 的文本')
        return self.get_element().info.get('text')

    @property
    def bounds(self):
        logger.info(f'获取元素: {self._kwargs} 的坐标')
        return self.get_element().info.get('bounds')

    @property
    def rect(self):
        logger.info(f'获取元素: {self._kwargs} 左上角的坐标以及宽高')
        bounds = self.get_element().info.get('bounds')
        x = bounds['left']
        y = bounds['top']
        width = bounds['right'] - x
        height = bounds['bottom'] - y
        return [x, y, width, height]

    @property
    def visibleBounds(self):
        logger.info(f'获取元素: {self._kwargs} 的可见坐标')
        return self.get_element().info.get('visibleBounds')

    @property
    def focusable(self):
        logger.info(f'获取元素: {self._kwargs} 是否聚焦')
        return self.get_element().info.get('focusable')

    @property
    def selected(self):
        logger.info(f'获取元素: {self._kwargs} 是否选中')
        return self.get_element().info.get('selected')

    def child(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的子元素{kwargs}')
        return self.get_element().child(*args, **kwargs)

    def brother(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的兄弟元素{kwargs}')
        return self.get_element().sibling(*args, **kwargs)

    def left(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 左边的元素 {kwargs}')
        return self.get_element().left(*args, **kwargs)

    def right(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 右边的元素 {kwargs}')
        return self.get_element().right(*args, **kwargs)

    def up(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 上边的元素 {kwargs}')
        return self.get_element().up(*args, **kwargs)

    def down(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 下边的元素 {kwargs}')
        return self.get_element().down(*args, **kwargs)

    def exists(self, timeout=1):
        logger.info(f'判断元素是否存在: {self._kwargs},{self._index}')
        element = self.find_element(retry=0, timeout=timeout)
        if element is None:
            # self._driver.screenshot(f'元素定位失败')
            return False
        return True

    @staticmethod
    def _adapt_center(e: typing.Union[UiObject, XPathSelector], offset=(0.5, 0.5)):
        if isinstance(e, UiObject):
            return e.center(offset=offset)
        else:
            return e.offset(offset[0], offset[1])

    def click(self, retry=3, timeout=3, alert_list=None):
        """
        @param: retry，重试次数
        @param: timeout，每次重试超时时间
        @param: alert_list，异常弹窗列表
        """
        logger.info(f'点击元素: {self._kwargs},{self._index}')
        element = self.get_element(retry=retry, timeout=timeout, alert_list=alert_list)
        # 这种方式经常点击不成功，感觉是页面刷新有影响
        # element.click()
        x, y = self._adapt_center(element)
        self._d.click(x, y)
        logger.debug('点击成功')

    # def click_no_retry(self, offset=(0.5, 0.5), timeout=1):
    #     logger.info(f'点击元素: {self._kwargs},{self._index}')
    #     element = self.get_element(timeout=timeout)
    #     x, y = self._adapt_center(element, offset=offset)
    #     self._d.click(x, y)
    #     logger.debug('点击成功')

    def click_exists(self, timeout=3):
        logger.info(f'存在才点击元素: {self._kwargs},{self._index}')
        if self.exists(timeout=timeout):
            self.click()

    def click_gone(self):
        logger.info(f'等元素 {self._kwargs} 消失后再点击')
        flag = self.get_element().click_gone()
        logger.info(flag)
        return flag

    def wait_gone(self, timeout=3):
        logger.info(f'等元素 {self._kwargs} 消失')
        flag = self.get_element().wait_gone(timeout=timeout)
        logger.info(flag)
        return flag

    def long_click(self):
        logger.info(f'长按元素 {self._kwargs}')
        self.get_element().long_click()

    def set_text(self, text):
        logger.info(f'输入文本: {text}')
        self.get_element().set_text(text)

    def clear_text(self):
        logger.info('清除文本')
        self.get_element().clear_text()

    def drag_to(self, *args, **kwargs):
        logger.info(f'从当前元素{self._kwargs},{self._index}, 拖动到元素: {kwargs}')
        self.get_element().drag_to(*args, **kwargs)

    def swipe_left(self):
        logger.info(f'往左滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("left")

    def swipe_right(self):
        logger.info(f'往右滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("right")

    def swipe_up(self):
        logger.info(f'往上滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("up")

    def swipe_down(self):
        logger.info(f'往下滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("down")



