from doctest import DocFileSuite, ELLIPSIS

class DummyConnection(object):
    def __init__(self):
        self.w = ''
        self.response = []
        self.timeout = .5
        
    # serial.Serial methods
        
    def write(self, text):
        self.w += text

    def read(self):
        timeout = self.timeout
        if timeout is None:
            timeout = 'no'
        print 'reading with %s timeout' % timeout
        return ''
        
    def readlines(self):
        return self.response

    def close(self):
        pass

    # test methods
    
    def sent(self):
        v = self.w
        self.w = ''
        return v

    def reset(self):
        self.w = ''
        
def test_suite():
    return DocFileSuite('README.txt',
                        globs={'DummyConnection':DummyConnection}, 
                        optionflags = ELLIPSIS)
