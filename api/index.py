from flask import Flask, jsonify, render_template, redirect, make_response
import json
import os
import re
import requests
app = Flask(__name__)


def get_video_json(vimeo_id, video_id):
    """
    输入vimeo_id, video_id
    输出并保存vimeo json
    """
    # vimeo_id = str(vimeo_id)
    # video_id = str(video_id)
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Language': 'ja,zh-CN;q=0.9,zh;q=0.7,zh-TW;q=0.6,zh-HK;q=0.4,en-US;q=0.3,en;q=0.1',
               # 'Origin': 'https://player.vimeo.com',
               'Referer': 'https://idol-on-demand.com/',
               'DNT': '1',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
    url = 'https://player.vimeo.com/video/' + vimeo_id

    r = requests.get(url, headers=headers, verify=True)
    pattern = re.compile(r'(?<=var config = ).+(?=; if \(!config.request)')
    result = pattern.findall(r.text)
    if len(result) == 0:
        return None
    else:
        # 写入vimeo json
        # vimeo_json = json.loads(result[0])
        # f = open(video_id + '_vimeo.json', "w+", encoding='utf-8')
        # f.write(json.dumps(vimeo_json, ensure_ascii=False, indent=4))
        # f.close()
        return result[0]


def act_video_json(video_json):
    """
    没有做异常处理，默认vimeo json无误
    输入vimeo json
    输出视频下载URL
    """
    load_dict = json.loads(video_json)
    # 自动选择最佳分辨率，根据视频宽度决定；自动选择最佳帧率
    best_resolution = load_dict['request']['files']['progressive'][0]['height']
    best_resolution_url = load_dict['request']['files']['progressive'][0]['url']
    best_fps = load_dict['request']['files']['progressive'][0]['fps']
    for i in range(len(load_dict['request']['files']['progressive'])):
        resolution = load_dict['request']['files']['progressive'][i]['height']
        fps = load_dict['request']['files']['progressive'][i]['fps']
        if resolution > best_resolution:  # 分辨率更大
            best_resolution = resolution
            best_fps = fps
            best_resolution_url = load_dict['request']['files']['progressive'][i]['url']
        if resolution == best_resolution and fps > best_fps:  # 分辨率同，fps更大
            best_resolution = resolution
            best_fps = fps
            best_resolution_url = load_dict['request']['files']['progressive'][i]['url']
    # print('自动选择最佳分辨率：' + str(best_resolution) + 'p ' + str(best_fps + 1) + 'fps')
    return best_resolution_url


def get_html_json_and_vimeo_id(video_id):
    """
    输入视频id
    保存html和格式化的json
    返回vimeo id
    ※网页404，匹配不到json返回None
    """
    video_id = str(video_id)
    url = "https://idol-on-demand.com/movies/" + video_id

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en;q=0.9,en-US;q=0.7',
        'Origin': 'https://idol-on-demand.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://idol-on-demand.com/',
        'TE': 'Trailers'
    }

    r = requests.request("GET", url, headers=headers, verify=True)  # 获取视频信息

    if r.status_code != 200:  # 404
        return None
    else:
        # 写入html
        # f = open(video_id + '.html', "w+", encoding='utf-8')
        # f.write(r.text)
        # f.close()
        # 提取json
        pattern = re.compile(r'(?<=var getMovieDetail = ).+(?=;)')
        result = pattern.findall(r.text)
        if len(result) == 0:
            return None  # 匹配不到json
        else:
            # 写入json
            html_json = json.loads(result[0])
            # f = open(video_id + '_html.json', "w+", encoding='utf-8')
            # f.write(json.dumps(html_json, ensure_ascii=False, indent=4))
            # f.close()

            # 读取vimeo id并返回
            if 'vimeo_link' in html_json:
                return html_json['vimeo_link'].split('com/')[1].split('/')[0]
            else:
                return None


def act_html_json(html_json):
    """
    输入网页json
    输出vimeo id
    """
    if html_json['vimeo_link'] in html_json:
        return html_json['vimeo_link'].split('com/')[1].split('/')[0]
    else:
        return None


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/test')
def test():
    return 'Test'


@app.route('/api/iv/<video_id>/')
def get_url(video_id):
    if not video_id.isdigit():
        return '404 Not Found', 404
    vimeo_id = get_html_json_and_vimeo_id(video_id)
    if vimeo_id is None:
        return '404 Not Found', 404
    else:
        # print(vimeo_id)
        video_json = get_video_json(vimeo_id, video_id)
        if video_json is None:
            return '404 Not Found', 404
        else:
            dl_url = act_video_json(video_json)
            res = make_response(redirect(dl_url, 301))
            video_title = video_json['video']['title']
            res.headers['content-disposition'] = 'attachment; filename="%s"' % video_title
            res.headers['Content-Type'] = 'video/mp4'
            return res


if __name__ == '__main__':
    #app.after_request(after_request)
    app.run(host='0.0.0.0')
