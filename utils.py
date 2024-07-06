import math
from translate import Translator as t
from textwrap import wrap

def temperatureToString(temperature, capitalization=False, color=False, sound=False):
  def inner():
    if temperature > 80:
      return "temperature:hot"
    if temperature > 60:
      return "temperature:nice"
    if temperature > 45:
      return "temperature:cool"
    if temperature > 32:
      return "temperature:cold:1"
    if temperature > 16:
      return "temperature:cold:2"
    if temperature > 0:
      return "temperature:cold:3"
    if temperature > -16:
      return "temperature:cold:4"
    if temperature > -32:
      return "temperature:cold:5"
    if temperature > -64:
      return "temperature:cold:6"
    return "temperature:cold:7"

  out = t.getString(inner()) if capitalization else t.getString(inner()).lower()
  if color and temperature < 0:
    out = "\033[38;2;0;0;255m" + out
    if sound:  out = "\a" + out
  elif color and temperature < 32:
    out = "\033[38;2;180;180;255m" + out
    if sound:  out = "\a" + out
  elif color and temperature >= 80:
    out = "\033[38;2;255;30;30m" + out
    if sound:  out = "\a" + out
  return out


def hungerToString(h, capitalization=False, color=False):
  def inner():
    if h > 80:
      return "hunger:0"
    if h > 60:
      return "hunger:1"
    if h > 40:
      return "hunger:2"
    if h > 20:
      return "hunger:3"
    if h > 0:
      return "hunger:4"
    return "hunger:5"

  out = t.getString(inner()) if capitalization else t.getString(inner()).lower()
  if color and h <= 20:
    out = "\a\033[38;2;255;0;0m" + out
  elif color and h <= 40:
    out = "\a\033[38;2;255;200;0m" + out
  return out


def thirstToString(thirst, capitalization=False, color=False):
  def inner():
    if thirst > 80:
      return "thirst:0"
    if thirst > 60:
      return "thirst:1"
    if thirst > 40:
      return "thirst:2"
    if thirst > 20:
      return "thirst:3"
    if thirst > 0:
      return "thirst:4"
    return "thirst:5"

  out = t.getString(inner()) if capitalization else t.getString(inner()).lower()
  if color and thirst <= 20:
    out = "\a\033[38;2;255;0;0m" + out
  elif color and thirst <= 40:
    out = "\a\033[38;2;255;200;0m" + out
  return out


def getSeason(d, capitalization=True, translate=True, offset=3):
  s = ""
  if math.floor(d / 3) + offset == 0:
    s = "season:early_spring"
  elif math.floor(d / 3) + offset == 1:
    s = "season:mid_spring"
  elif math.floor(d / 3) + offset == 2:
    s = "season:late_spring"
  elif math.floor(d / 3) + offset == 3:
    s = "season:early_summer"
  elif math.floor(d / 3) + offset == 4:
    s = "season:mid_summer"
  elif math.floor(d / 3) + offset == 5:
    s = "season:late_summer"
  elif math.floor(d / 3) + offset == 6:
    s = "season:early_fall"
  elif math.floor(d / 3) + offset == 7:
    s = "season:mid_fall"
  elif math.floor(d / 3) + offset == 8:
    s = "season:late_fall"
  elif math.floor(d / 3) + offset == 9:
    s = "season:early_winter"
  elif math.floor(d / 3) + offset == 10:
    s = "season:mid_winter"
  elif math.floor(d / 3) + offset == 11:
    s = "season:late_winter"
  else:
    s = "BRO_YOURE_SCREWED_IDK_WHAT_YOU_DID_BUT_SOMEHOW_YOU_MADE_THE_YEAR_LITERALLY_GET_LONGER"

  if translate:
    return t.getString(s) if capitalization else t.getString(s).lower()
  return s if capitalization else s.lower()


def intToOrdinal(n, capitalization=False):
  s = "ordinal:" + str(n)

  return t.getString(s) if capitalization else t.getString(s).lower()


def hourToTime(h, day, capitalization=True, translate=True, integer=False):
  season = getSeason(day, translate=False).removeprefix("season:")
  time = "time:night"
  if season.lower() == "early_spring" or season.lower() == "late_fall":
    if h == 8:  time = "time:morning"
    elif h == 16:  time = "time:evening"
    elif h > 8 and h < 16:  time = "time:day"
  if season.lower() == "mid_spring" or season.lower() == "mid_fall":
    if h == 7:  time = "time:morning"
    elif h == 17:  time = "time:evening"
    elif h > 7 and h < 17:  time = "time:day"
  if season.lower() == "late_spring" or season.lower() == "early_fall":
    if h == 6:  time = "time:morning"
    elif h == 18:  time = "time:evening"
    elif h > 6 and h < 18:  time = "time:day"
  if season.lower() == "early_summer" or season.lower() == "late_summer":
    if h == 5:  time = "time:morning"
    elif h == 19:  time = "time:evening"
    elif h > 5 and h < 19:  time = "time:day"
  if season.lower() == "mid_summer":
    if h == 4:  time = "time:morning"
    elif h == 20:  time = "time:evening"
    elif h > 4 and h < 20:  time = "time:day"
  if season.lower() == "early_winter" or season.lower() == "late_winter":
    if h == 9:  time = "time:morning"
    elif h == 15:  time = "time:evening"
    elif h > 9 and h < 15:  time = "time:day"
  if season.lower() == "mid_winter":
    if h == 10:  time = "time:morning"
    elif h == 14:  time = "time:evening"
    elif h > 10 and h < 14:  time = "time:day"

  if integer:
    return 0 if time == "time:day" else \
    1 if time == "time:morning" or time == "time:evening" else 2
  
  if translate:
    return t.getString(time) if capitalization else t.getString(time).lower()
  return time if capitalization else time.lower()


def partitionString(s, width):
  arr = wrap(s, width)
  arr = [i.strip() + "\n" for i in arr]
  return "".join(arr)


def fireToString(fire, capitalization=False, color=False):
  def inner():
    if fire > 90:
      return "fire:4"
    if fire > 60:
      return "fire:3"
    if fire > 30:
      return "fire:2"
    if fire > 0:
      return "fire:1"
    return "fire:0"

  out = t.getString(inner()) if capitalization else t.getString(inner()).lower()
  if color and fire <= 30:
    out = "\a\033[38;2;255;0;0m" + out
  elif color and fire <= 60:
    out = "\a\033[38;2;255;255;0m" + out
  return out


def getCorrectBackgroundImage(hour, day, hasFrozen):
  s = ""
  if hourToTime(hour, day, translate=False) == "time:day":
    s = "YukonDay"
  elif hourToTime(hour, day, translate=False) == "time:night":
    s = "YukonNight"
  else:
    s = "YukonTwilight"

  if hasFrozen:
    s += "_snowy"
    
  s += ".bin"
  return s


def getFileLocation(dir):
  f = __file__.replace("\\", "/")
  return f.removesuffix(f.split("/")[-1]) + dir