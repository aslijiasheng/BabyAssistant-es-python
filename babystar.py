# coding: utf-8


class babystar(object):

    def __init__(self, target_ages, target_link, target_path):
        self.target_ages = target_ages
        self.target_link = target_link
        self.target_path = target_path
        return

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)
