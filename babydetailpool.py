# coding: utf-8
import copy_reg
import types
import sys
import multiprocessing
import requests
from pyquery import PyQuery as pq
import re
import MySQLdb
import babystar
from threading import Thread

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
        self.headers = {
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.beginMultiProcess()

    # todo:处理最后数据 完成明细抓取
    # todo:处理最后数据 对队列数据总量进行取模分析 产生多个异步进程
    # 处理相应数据后生成到es
    def beginMultiProcess(self):

        pool_process_num = len(self.baby_queue) % 10
        baby_item_pool = multiprocessing.Pool(processes=pool_process_num)
        # db = MySQLdb.connect(
            # host="localhost",
            # user="root",
            # passwd="871027",
            # db="babystar")
        for baby_item in self.baby_queue:
            baby_item_pool.apply_async(
                self.get_item_text,
                args=(baby_item, ),)
        baby_item_pool.close()
        baby_item_pool.join()
        #  db.close()

    # todo:处理队列里的数据明细
    def get_item_text(self, baby_item):
        r = requests.get(baby_item.target_link, headers=self.headers)
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
            if baby_item.target_ages == 'one':
                ageid = 1
            if baby_item.target_ages == 'two':
                ageid = 2
            if baby_item.target_ages == 'three':
                ageid = 3
            path = "./website/templete/baby/" + \
                str(ageid)+"/"+re.sub('[\s+]', '', baby_item.target_text) + ".html"
            fo = open(path, "ab")
            fo.write(new_item_link)
            fo.close()
            #  type_classify_id = baby_item.type_classify_id
            print path
            tmp = baby_item.target_type_classify_id
            target_type_classify_id = tmp.replace("\r\n", "")
            print 'start db'
            db = MySQLdb.connect(
                host="localhost",
                user="root",
                passwd="871027",
                db="babystar")
            c = db.cursor()
            c.execute(
                "insert into tc_news(`news_title`, `news_status`, `news_source_type`, `news_url`, `news_user_id`, `news_content_path`) values('" +
                baby_item.target_text +
                "', 0, 1, '" +
                baby_item.target_link +
                "', 2, '" +
                path +
                "')")
            new_lastedid = c.lastrowid
            print 'lasted id'
            print new_lastedid
            print "insert into tc_news_type(`news_type_news_id`, `news_type_classify_id`) VALUES('"+str(new_lastedid)+"', '"+target_type_classify_id+"')"
            print 'lasted id'
            c.execute(
                "insert into tc_news_type(`news_type_news_id`, `news_type_classify_id`) VALUES('" +
                str(new_lastedid) +
                "', '" +
                target_type_classify_id +
                "')")
            db.commit()
            db.close()
            print 'end db'
            #  es_agestant_data = json.dumps(item_es_content)
            #  es_url = "http://23.244.68.121:9200/babygrowthassistant/agerecommended/"
            #  baby_respone = requests.post(es_url, data=es_agestant_data)
            #  results = json.loads(baby_respone.text)
            #  print(results)

    def regex_parse_a(self, data):
        p = re.compile(r'<a.*?/a>')
        return p.sub('', data)

    def regex_parse_img(self, data):
        p = re.compile(r'<img.*/>')
        return p.sub('', data)
