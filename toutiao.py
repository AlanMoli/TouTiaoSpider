from urllib.parse import urlencode
import requests
import os
from hashlib import md5
from multiprocessing.pool import Pool


def get_page(offset):
    headers = {
        'Host': 'www.toutiao.com',
        'Referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    base_url = 'https://www.toutiao.com/search_content/?'
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }
    url = base_url + urlencode(params)

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def get_image(json):
    if json:
        for item in json.get('data'):
            if item.get('open_url') is not None:
                for image in item.get('image_list'):
                    yield {
                        'title': item.get('title'),
                        'image': 'https://' + image.get('url')[2:]
                    }


def save_image(item):
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            # 格式化图片路径
            file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to Save Image')


def main(offset):
    json = get_page(offset)
    print(offset)
    for result in get_image(json):
        print(result)
        save_image(result)


GROUP_START = 0
GROUP_END = 4


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    # 多进程下载
    pool.map(main, groups)
    pool.close()
    pool.join()
