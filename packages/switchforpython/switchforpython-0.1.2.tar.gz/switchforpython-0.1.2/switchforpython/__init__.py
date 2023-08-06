__version__ = '0.1.2'

class Switch:
  def __init__(self, val):
    self.val = val
    self.cases = {}
    self.defaultFunc = None
  def updateValue(self, val):
    self.val = val
  def default(self, func):
    self.defaultFunc = func
  def case(self, val):
    def case_decorator(func):
      self.cases[val] = func
    return case_decorator
  def run(self):
    if self.val in self.cases.keys():
      for k in self.cases.keys():
        if self.val == k:
          self.cases[k]()
          break
    else:
      if self.defaultFunc != None:
        self.defaultFunc()