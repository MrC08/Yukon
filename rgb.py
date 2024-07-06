class RGB:
  def __init__(self, r, g=None, b=None):
    if g == None:
      self.r = r[0]
      self.g = r[1]
      self.b = r[2]
      return
      
    self.r = r
    self.b = b
    self.g = g
    
    
  def toANSI(self, background=False):
    return f"\033[{48 if background else 38};2;{self.r};{self.g};{self.b}m"


  def isFullyBlack(self):
    return self.r == 0 and self.g == 0 and self.b == 0