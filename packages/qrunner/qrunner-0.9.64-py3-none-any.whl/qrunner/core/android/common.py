import os


def get_device_list():
    cmd = 'adb devices'
    output = os.popen(cmd).read()
    device_list = [item.split('\t')[0] for item in output.split('\n') if item.endswith('device')]
    return device_list


if __name__ == '__main__':
    print(get_device_list())

