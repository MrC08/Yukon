from translate import Translator as t
import utils
import time


class GlobalChoiceSettings:
  screen = None
  

class Choices:
  GlobalContrastMode = 0


  def __init__(self, prompt, options):
    self.prompt = prompt
    self.options = options
    self.cache = None

  def _printPrompt(self):
    print("\033[0;0m" + utils.partitionString(self.prompt, GlobalChoiceSettings.screen.width),
          end="\n\n")

  def choose(self, key=True, exe=False, translate=True):
    self._printPrompt()
    
    for i in range(len(self.options)):
      tempOptions = self.options[i]
      if type(tempOptions) == str and translate:
        tempOptions = t.getString(tempOptions)

      tempOptions = str(tempOptions)
      
      if Choices.GlobalContrastMode == 0:
        bgColor = "\033[" + ("47" if (i % 2) else "100") + "m"
        fgColor = "\033[" + ("90" if (i % 2) else "37") + "m"
      
      elif Choices.GlobalContrastMode == 1:
        bgColor = "\033[38;2;" + ("50;50;50" if (i % 2) else "220;220;220") + "m"
        fgColor = "\033[48;2;" + ("220;220;220" if (i % 2) else "50;50;50") + "m"
      
      
      insert = f"[{i}]"
      secondSpacer = ("{0:" + str(GlobalChoiceSettings.screen.width - 5) + "}")
      print(bgColor + fgColor + "{0:5}".format(insert) +
            secondSpacer.format(tempOptions) + "\033[0")
    inp = None

    print("\033[0m\033[38;2;0;0;0m\033[48;2;255;255;255m")

    if len(self.options) == 1:
      time.sleep(0.1)
      input("\033[0m> ")
      inp = 0

    else:
      while type(inp) != int:
        inp = input("\033[0m> ")
        try:
          inp = int(inp)
          if inp >= len(self.options):
            inp = None
            print("\033[1A\033[K", end="\r")
        except:
          print("\033[1A\033[K", end="\r")
          if exe:
            return {"type": "code", "code": inp}

    self.cache = (inp if key else self.options[inp])
    return self.cache

  def clear(self):
    self.cache = None
