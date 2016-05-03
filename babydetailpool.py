# coding: utf-8
import copy_reg
import types
import sys
import multiprocessing
import requests
from pyquery import PyQuery as pq
import re
import json

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
        print r.status_code
        if r.status_code == 200:
            html = pq(r.text)
            item_content = html(
                'div.clearfix>div.bd-left>div.page>div.info').text()
            item_content = re.sub('www.ci123.com', '#', item_content)
            item_es_content = {
                "agerecommended_title": baby_item.target_text,
                "agerecommended_content": item_content,
                "agerecommended_ages": baby_item.target_ages}
            es_agestant_data = json.dumps(item_es_content)
            es_url = "http://172.28.128.3:9200/babygrowthassistant/agerecommended/"
            baby_respone = requests.post(es_url, data=es_agestant_data)
            results = json.loads(baby_respone.text)
            print(results)
