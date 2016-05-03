# coding: utf-8


class itemjob(object):

    def __init__(self, target_ages, target_link):
        self.target_ages = target_ages
        self.target_link = target_link
        return

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)
