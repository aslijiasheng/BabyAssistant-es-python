# coding: utf-8
# 对三个不同年龄段的URL进行采集  开启三个进程采集出主URL里的信息 再从进程中开启多线程进行子URL的采集 最后将采集下来的信息存入ES里
import multiprocessing
import copy_reg
import types
import requests
from pyquery import PyQuery as pq
import sys
import os
from itemthreading import itemthreading
from itemjob import itemjob
import Queue
from threading import Thread
from itempagezone import itempagezone
from babydetailpool import babydetailpool

reload(sys)
sys.setdefaultencoding("utf-8")


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)


class Crawl():

    def __init__(self, ages_num, ages_url):
        self.start_urls = ages_url
        self.pool_num = ages_num
        self.__result = []
        self.map_urlsfunc = {
            'one': 'one',
            'two': 'two',
            'three': 'three'}
        self.beginMultiProcess()

    def resultCollector(self, result):
        self.__result.append(result)

    def BarcodeSearcher(self, start_url):
        return start_url

    def beginMultiProcess(self):
        pool = multiprocessing.Pool(processes=self.pool_num)
        m = multiprocessing.Manager()
        q = m.Queue()
        for url_key, url_value in self.start_urls.items():
            pool.apply(
                self.getCrawl,
                args=(self.map_urlsfunc[url_key], url_value, ))
            pool.apply(
                self.getPageBar,
                args=(self.map_urlsfunc[url_key], q, ))
        pool.apply_async(
            self.itemstopic, args=(q, ),
            callback=self.result_item_link)

        pool.close()
        # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        pool.join()
        #  print(self.__result)

    def result_item_link(self, result):
        babydetailpool(result)

# todo: 页码URL全部找到  下一步对页码进行扒取然后处理扒取后的URL
    def itemstopic(self, q):
        print os.getpid(), "itemstopic working"
        item_link_queue = Queue.Queue()
        threads = []
        while not q.empty():
            target = q.get_nowait()
            t = Thread(
                target=self.get_item_link, args=(
                    target, item_link_queue))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return [item_link_queue.get() for _ in xrange(item_link_queue.qsize())]

    # 分页列表链接获取
    def get_item_link(self, target, item_link_queue):
        try:
            r = requests.get(target.target_link)
            if r.status_code == 200:
                html = pq(r.text)
                item_links = html('div.knowledge>ul.knowledge-lists')
                for ullist in item_links:
                    for i in range(len(ullist)):
                        # 产生多个线程来处理类目的Url
                        target_link = pq(ullist[i])('li > a').attr('href')
                        target_text = pq(ullist[i])('li > a').text()
                        item_link_queue.put(
                            itempagezone(
                                target.target_ages, target_link, target_text))
        except requests.exceptions.RequestException as e:
            print('\n' + str(e))

    def getPageBar(self, ages, q):
        print os.getpid(), "getpagebar working"
        with open(ages + '.txt') as fp:
            for line in fp:
                q.put_nowait(itemjob(ages, line))

    def getCrawl(self, ages,  url):
        print os.getpid(), "working"
        r = requests.get(url)
        threadBox = []
        if r.status_code == 200:
            html = pq(r.text)
            rightContainer = html('div.bd-right>div.clearfix>ul.clearfix')
            for ullist in rightContainer:
                for i in range(len(ullist)):
                    # 产生多个线程来处理类目的Url
                    target_link = pq(ullist[i])('li > a').attr('href')
                    target_text = pq(ullist[i])('li > a').text()
                    t = itemthreading(
                        i, ages, target_link, target_text)
                    threadBox.append(t)
                    t.start()
        if len(threadBox) > 0:
            for i in threadBox:
                i.join()

if __name__ == "__main__":
    start_urls = {
        'one': 'http://www.ci123.com/category.php/8029/848',
        'two': 'http://www.ci123.com/category.php/8029/849',
        'three': 'http://www.ci123.com/category.php/8029/918'}
    Crawl(10, start_urls)
