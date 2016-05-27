# coding: utf-8
import sys
import threading
import requests
from pyquery import PyQuery as pq
import MySQLdb

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
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def run(self):
        self.coreMulthreading()

    def coreMulthreading(self):
        try:
            db = MySQLdb.connect(user="root", passwd="871027", db="babystar")
            c = db.cursor()
            c.execute(
                "insert into tc_type(`type_name`) VALUES('%s')" %
                self.target_text)
            typeid = c.lastrowid
            if self.target_ages == 'one':
                ageid = 1
            if self.target_ages == 'two':
                ageid = 2
            if self.target_ages == 'three':
                ageid = 3
            c.execute("""insert into tc_type_classify(`type_classify_type_id`, `type_classify_classify_id`)
                        VALUES('%s', '%s')""", (typeid, ageid))
            type_classify_lastid = c.lastrowid
            db.commit()
            db.close()
            r = requests.get(self.target_link, headers=self.headers)
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
                        fo.write(new_pageonzie_link  + '|' + str(type_classify_lastid)+ "\r\n")
                        fo.close()
        except:
            pass
