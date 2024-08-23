import json
import utils
from translate import Translator as t

class Item:
  rItems = json.load(open(utils.getFileLocation("/json/items.json"), "r"))

  @staticmethod
  def GetAllItems():
    return Item.rItems.keys()
  
  def __init__(self, type, count=1):
    self.type = type
    self.count = count

  def getFood(self, zeroNulliesStats=True):
    if zeroNulliesStats and self.count <= 0:  return 0
    return Item.rItems[self.type].get("food", 0)

  def getWater(self, zeroNulliesStats=True):
    if zeroNulliesStats and self.count <= 0:  return 0
    return Item.rItems[self.type].get("water", 0)

  def getFlammibility(self, zeroNulliesStats=True):
    if zeroNulliesStats and self.count <= 0:  return 0
    return Item.rItems[self.type].get("flammability", 0)

  def getDamage(self, zeroNulliesStats=True):
    if zeroNulliesStats and self.count <= 0:  return 0
    return Item.rItems[self.type].get("damage", 0)

  def getEquipable(self, zeroNulliesStats=True):
    if zeroNulliesStats and self.count <= 0:  return False
    return Item.rItems[self.type].get("equipable", False)

  def getTemperature(self, zeroNulliesStats=True):
    if zeroNulliesStats and self.count <= 0:  return 0
    return Item.rItems[self.type].get("temperature", 0)
   
  def getDrinkString(self, zeroNulliesStats=True):
    if zeroNulliesStats and self.count <= 0:  return ""
    return Item.rItems[self.type].get("drink_alt_text", self.type)


  def __repr__(self):
    if self.count == 1:  t.getString(self.type)
    return t.getString(self.type) + " × " + str(self.count)
