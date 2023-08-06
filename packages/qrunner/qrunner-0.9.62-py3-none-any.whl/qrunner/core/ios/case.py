import time
from qrunner.utils.log import logger
from qrunner.utils.config import conf
from qrunner.core.ios.driver import IosDriver
from qrunner.core.ios.element import Element


class TestCase(object):
    """
    测试用例基类，所有测试用例需要继承该类
    """

    # ---------------------初始化-------------------------------
    def start_class(self):
        """
        Hook method for setup_class fixture
        :return:
        """
        pass

    def end_class(self):
        """
        Hook method for teardown_class fixture
        :return:
        """
        pass

    @classmethod
    def setup_class(cls):
        # 从配置文件中获取浏览器相关配置（为了支持并发执行）
        serial_no = conf.get_item('app', 'serial_no')
        pkg_name = conf.get_item('app', 'pkg_name')
        cls.driver = IosDriver(serial_no, pkg_name)
        cls().start_class()

    @classmethod
    def teardown_class(cls):
        cls().end_class()

    def start(self):
        """
        Hook method for setup_method fixture
        :return:
        """
        self.start_time = time.time()
        logger.debug(f"[start_time]: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    def end(self):
        """
        Hook method for teardown_method fixture
        :return:
        """
        logger.debug(f"[end_time]: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        take_time = time.time() - self.start_time
        logger.debug("[run_time]: {:.2f} s".format(take_time))
        self.screenshot('用例执行完成截图')

    def setup_method(self):
        # 启动应用
        self.driver.force_start_app()
        self.start()

    def teardown_method(self):
        self.end()
        # 退出应用
        self.driver.stop_app()

    @staticmethod
    def sleep(n: int):
        logger.debug(f'等待: {n}s')
        time.sleep(n)

    def element(self, **kwargs):
        """
        定位元素
        :param kwargs: 元素定位方式
        :return: 根据平台返回对应的元素
        """
        return Element(self.driver, **kwargs)

    def screenshot(self, file_name):
        file_path = self.driver.screenshot(file_name)
        logger.debug(f'[截图并上传报告] {file_path}')

    def click(self, **kwargs):
        """点击"""
        self.element(**kwargs).click()

    def click_exists(self, **kwargs):
        """存在才点击"""
        self.element(**kwargs).click_exists()

    def input(self, text, **kwargs):
        """输入"""
        self.element(**kwargs).set_text(text)

    def input_clear(self, **kwargs):
        """清除输入框"""
        self.element(**kwargs).clear_text()

    def get_text(self, **kwargs):
        """获取文本属性"""
        return self.element(**kwargs).text

    def assertText(self, expect_value, timeout=5):
        """断言页面包含文本"""
        for _ in range(timeout + 1):
            try:
                page_source = self.driver.page_content
                assert expect_value in page_source, f'页面内容不包含 {expect_value}'
                break
            except AssertionError:
                time.sleep(1)
        else:
            page_source = self.driver.page_content
            assert expect_value in page_source, f'页面内容不包含 {expect_value}'

    def assertNotText(self, expect_value, timeout=5):
        """断言页面不包含文本"""
        for _ in range(timeout + 1):
            try:
                page_source = self.driver.page_content
                assert expect_value not in page_source, f'页面内容不包含 {expect_value}'
                break
            except AssertionError:
                time.sleep(1)
        else:
            page_source = self.driver.page_content
            assert expect_value not in page_source, f'页面内容仍然包含 {expect_value}'

    def assertElement(self, timeout=5, **kwargs):
        """断言元素存在"""
        for _ in range(timeout + 1):
            try:
                element = self.element(**kwargs)
                assert element.exists(), f'元素 {kwargs} 不存在'
                break
            except AssertionError:
                time.sleep(1)
        else:
            assert self.element(**kwargs).exists(), f'元素 {kwargs} 不存在'

    def assertNotElement(self, timeout=5, **kwargs):
        """断言元素不存在"""
        for _ in range(timeout + 1):
            try:
                assert not self.element(**kwargs).exists(), f'元素 {kwargs} 仍然存在'
                break
            except AssertionError:
                time.sleep(1)
        else:
            assert not self.element(**kwargs).exists(), f'元素 {kwargs} 仍然存在'






