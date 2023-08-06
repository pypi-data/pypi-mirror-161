from .runner import Runner

class Suite(object):
    def __init__(self, tests=[]):
        self.runner = Runner(tests)
    
    def add_tests(self, tests):
        self.runner.add_tests(tests)
    
    def start(self):
        self.runner.run()