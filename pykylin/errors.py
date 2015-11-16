from __future__ import absolute_import

class Error(Exception):

    def __init__(self, msg):
        super(Error, self).__init__(msg)
        self.msg = msg
