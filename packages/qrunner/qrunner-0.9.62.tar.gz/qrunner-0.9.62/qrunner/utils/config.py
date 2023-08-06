import os
import json
import yaml


local_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(local_path)


class Config:
    def __init__(self):
        self.file_path = os.path.join(root_path, 'running', 'conf.yml')
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.yaml_data = yaml.load(f.read(), Loader=yaml.FullLoader)

    def get_all(self):
        return self.yaml_data

    def get_item(self, module, key):
        return self.yaml_data[module][key]

    def set_item(self, module, key, value):
        self.yaml_data[module][key] = value
        with open(self.file_path, 'w', encoding="utf-8") as f:
            yaml.dump(self.yaml_data, f)

    def set_android_alerts(self, alerts: list):
        """设置安卓异常弹窗列表"""
        self.set_item('app', 'android_alert', alerts)

    def set_ios_alerts(self, alerts: list):
        """设置ios异常弹窗列表"""
        self.set_item('app', 'ios_alert', alerts)

    def set_report_path(self, report_path):
        """设置报告路径"""
        self.set_item('common', 'report_path', report_path)


conf = Config()


if __name__ == '__main__':
    conf.get_all()
    conf.set_item('common', 'platform', 'android')
    conf.set_item('common', 'platform', 'ios')
    print(conf.get_item('app', 'android_alert'))
    print(conf.get_item('common', 'platform'))



