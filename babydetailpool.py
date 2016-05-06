# coding: utf-8
import copy_reg
import types
import sys
import multiprocessing
import requests
from pyquery import PyQuery as pq
import json
import re

reload(sys)
sys.setdefaultencoding("utf-8")


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)


class babydetailpool():

    def __init__(self, baby_queue):
        self.baby_queue = baby_queue
        self.beginMultiProcess()

    # todo:处理最后数据 完成明细抓取
    # todo:处理最后数据 对队列数据总量进行取模分析 产生多个异步进程
    # 处理相应数据后生成到es
    def beginMultiProcess(self):
        pool_process_num = len(self.baby_queue) % 10
        baby_item_pool = multiprocessing.Pool(processes=pool_process_num)
        for baby_item in self.baby_queue:
            baby_item_pool.apply_async(
                self.get_item_text,
                args=(baby_item, ))
        baby_item_pool.close()
        baby_item_pool.join()

    # todo:处理队列里的数据明细
    def get_item_text(self, baby_item):
        r = requests.get(baby_item.target_link)
        if r.status_code == 200:
            html = pq(r.text)
            item_content = html(
                'div.clearfix>div.bd-left>div.page>div.info').html()
            regex_html_item_link = self.regex_parse_a(item_content)
            regex_html_item_link = self.regex_parse_img(regex_html_item_link)
            k = regex_html_item_link.rfind("<p")
            start_offset = regex_html_item_link.find("<")
            if k == -1:
                new_item_link = regex_html_item_link[start_offset:]
            else:
                new_item_link = regex_html_item_link[start_offset:k]
            item_es_content = {
                "agerecommended_title": baby_item.target_text,
                "agerecommended_content": new_item_link,
                "agerecommended_ages": baby_item.target_ages,
                "agerecommended_link": baby_item.target_link}
            es_agestant_data = json.dumps(item_es_content)
            es_url = "http://23.244.68.121:9200/babygrowthassistant/agerecommended/"
            baby_respone = requests.post(es_url, data=es_agestant_data)
            results = json.loads(baby_respone.text)
            print(results)

    def regex_parse_a(self, data):
        p = re.compile(r'<a.*?/a>')
        return p.sub('', data)

    def regex_parse_img(self, data):
        p = re.compile(r'<img.*/>')
        return p.sub('', data)
