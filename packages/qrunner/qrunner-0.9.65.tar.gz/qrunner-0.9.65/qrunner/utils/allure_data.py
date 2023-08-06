import json
import os.path


# 从allure数据中获取用例执行情况
def get_allure_data(allure_path):
    # 从json文件中获取执行结果列表
    data_list = []
    for filename in os.listdir(allure_path):
        if filename.endswith('result.json'):
            # 读result.json
            print(os.path.join(allure_path, filename))
            with open(os.path.join(allure_path, filename), 'r', encoding='UTF-8') as f:
                content = json.load(f)

            # 获取需要的字段
            full_name = content.get('fullName')
            status = content.get('status')
            data = {'full_name': full_name, 'status': status}

            # 去重，失败重试后会有重复执行结果（这里可能会有一个bug，重试成功后会同时显示失败和成功的用例）
            for item in data_list:
                if full_name == item.get('full_name'):
                    break
            else:
                data_list.append(data)

    # 根据执行结果进行数据统计
    print(data_list)
    total_num = len(data_list)
    pass_list = [data for data in data_list if data.get('status') == 'passed']
    pass_num = len(pass_list)
    fail_num = total_num - pass_num
    rate = round((pass_num / total_num) * 100, 2)
    data = {
        'total': total_num,
        'passed': pass_num,
        'fail': fail_num,
        'rate': rate
    }
    return data


if __name__ == '__main__':
    print(get_allure_data('/Users/UI/PycharmProjects/qrunner_new_gitee/allure-results'))



