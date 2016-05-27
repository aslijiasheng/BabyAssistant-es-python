# coding: utf-8


class itempagezone(object):

    def __init__(self, target_ages, target_link, target_text, type_classify_id):
        self.target_ages = target_ages
        self.target_link = target_link
        self.target_text = target_text
        self.target_type_classify_id = type_classify_id
        return

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)
