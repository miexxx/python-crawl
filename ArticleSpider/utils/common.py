# -*- coding: utf-8 -*-
import hashlib
def get_md5(url):
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()