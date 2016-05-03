# coding: utf-8
import sys
import threading
import requests
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")


class itemthreading (threading.Thread):

    def __init__(
        self,
        threadID,
        target_ages,
        target_link,
        target_text
     ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.target_link = target_link
        self.target_text = target_text
        self.target_ages = target_ages

    def run(self):
        self.coreMulthreading()

    def coreMulthreading(self):
        try:
            r = requests.get(self.target_link)
            html = pq(r.text)
            pageonzieContainer = html('div.knowledge>div.page>div.page-list')
            for pageonzie in pageonzieContainer:
                for i in xrange(len(pageonzie)):
                    if pq(pageonzie)('a').eq(i).is_('.next-page'):
                        continue
                    else:
                        pageonzie_link = pq(pageonzie[i])('a').attr('href')
                        fo = open(self.target_ages + ".txt", "ab")
                        k = pageonzie_link.rfind("/")
                        new_pageonzie_link = pageonzie_link[
                            :k] + "?" + pageonzie_link[k+1:]
                        fo.write(new_pageonzie_link + "\r\n")
                        fo.close()
        except:
            pass
