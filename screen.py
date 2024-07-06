from rgb import RGB


class Screen:

  def __init__(self):
    self.content = []
    self.height = 30
    self.width = 50
    self.cache = {}

    for i in range(self.width):
      self.content.append([])
      for _ in range(self.height):
        self.content[i].append(RGB(0, 0, 0))

  def display(self):
    print("\033[0;0H\033[2J")
    for y in range(self.height // 2):
      for x in range(self.width):
        print(self.content[x][y * 2].toANSI(True) +
              self.content[x][y * 2 + 1].toANSI() + "▄",
              end="")
      print("")
    print("\033[38;2;0;0;0m\033[48;2;255;255;255m")


  def set(self, x, y, rgb):
    self.content[x][y] = rgb

  def blit(self, x, y, img):
    for dx in range(x, x + len(img)):
      for dy in range(y, y + len(img[dx - x])):
        if not RGB(img[dx - x][dy - y]).isFullyBlack():
          self.content[dx][dy] = RGB(img[dx - x][dy - y])

  def clear(self):
    self.content = []

    for i in range(self.width):
      self.content.append([])
      for _ in range(self.height):
        self.content[i].append(RGB(0, 0, 0))

  def delete(self):
    print("\033[0;0H\033[2J")