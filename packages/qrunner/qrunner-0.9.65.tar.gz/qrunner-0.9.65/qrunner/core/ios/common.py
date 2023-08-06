import os


def get_device_list():
    cmd = 'tidevice list'
    output = os.popen(cmd).read()
    device_list = [item.split(' ')[0] for item in output.split('\n') if item]
    return device_list


if __name__ == '__main__':
    print(get_device_list())

