import time
import allure
from qrunner.utils.log import logger
from qrunner.utils.config import conf
from qrunner.core.android.driver import AndroidDriver
from qrunner.core.android.element import Element


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
        # 初始化driver
        serial_no = conf.get_item('app', 'serial_no')
        cls.driver = AndroidDriver.get_instance(serial_no)
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
        # 退出应用cc
        self.driver.stop_app()

    def screenshot(self, file_name):
        # 截图保存本地
        file_path = self.driver.screenshot(file_name)
        # 上传allure报告
        allure.attach.file(file_path, attachment_type=allure.attachment_type.PNG, name=f'{file_name}.png')
        logger.debug(f'[截图并上传报告] {file_path}')

    def click_alerts(self, alert_list: list):
        """处理弹窗"""
        self.driver.click_alert(alert_list)

    @staticmethod
    def click(**kwargs):
        """点击"""
        Element(**kwargs).click()

    @staticmethod
    def click_exists(**kwargs):
        """存在才点击"""
        Element(**kwargs).click_exists(**kwargs)

    @staticmethod
    def input(text, **kwargs):
        """输入"""
        Element(**kwargs).set_text(text)

    def input_password(self, text, **kwargs):
        """输入密码，仅安卓使用"""
        Element(**kwargs).click()
        self.driver.set_password(text)

    @staticmethod
    def input_clear(**kwargs):
        """清除输入框"""
        Element(**kwargs).clear_text()

    @staticmethod
    def get_text(**kwargs):
        """获取文本属性"""
        return Element(**kwargs).text

    def assertText(self, expect_value, timeout=5):
        """断言页面包含文本"""
        for _ in range(timeout + 1):
            try:
                page_source = self.driver.get_page_content()
                assert expect_value in page_source, f'页面内容不包含 {expect_value}'
                break
            except AssertionError:
                time.sleep(1)
        else:
            page_source = self.driver.get_page_content()
            assert expect_value in page_source, f'页面内容不包含 {expect_value}'

    def assertNotText(self, expect_value, timeout=5):
        """断言页面不包含文本"""
        for _ in range(timeout + 1):
            try:
                page_source = self.driver.get_page_content()
                assert expect_value not in page_source, f'页面内容不包含 {expect_value}'
                break
            except AssertionError:
                time.sleep(1)
        else:
            page_source = self.driver.get_page_content()
            assert expect_value not in page_source, f'页面内容仍然包含 {expect_value}'

    @staticmethod
    def assertElement(timeout=5, **kwargs):
        """断言元素存在"""
        for _ in range(timeout + 1):
            try:
                element = Element(**kwargs)
                assert element.exists(), f'元素 {kwargs} 不存在'
                break
            except AssertionError:
                time.sleep(1)
        else:
            assert Element(**kwargs).exists(), f'元素 {kwargs} 不存在'

    @staticmethod
    def assertNotElement(timeout=5, **kwargs):
        """断言元素不存在"""
        for _ in range(timeout + 1):
            try:
                assert not Element(**kwargs).exists(), f'元素 {kwargs} 仍然存在'
                break
            except AssertionError:
                time.sleep(1)
        else:
            assert not Element(**kwargs).exists(), f'元素 {kwargs} 仍然存在'
