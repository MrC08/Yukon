import random
import math as m
import json
import time

import image
import screen as s
import utils
import choices
from item import Item
from choices import Choices
from translate import Translator as t


screen = None
gamestate = None


def environmentText(temperature, food, water, day, hour, fire, distance):
  a = "\033[0;4m"
  b = "\033[0;0m"
  
  if t.lang == "en":
    s = f"It feels {a}{utils.temperatureToString(temperature, color=True)}{b} outside. You feel {a}{utils.hungerToString(food, color=True)}{b} and {a}{utils.thirstToString(water, color=True)}{b}. It is the {a}{utils.intToOrdinal((day % 3) + 1)}{b} day of {a}{utils.getSeason(day)}{b}. Right now it is {a}{utils.hourToTime(hour, day, capitalization=False)}{b}."
    if innerTemp != temperature:
      s = s + f" You feel {a}{utils.temperatureToString(innerTemp, color=True, sound=True)}{b}."
    if fire > 0:
      s = s + f" Your fire is {a}{utils.fireToString(fire, color=True)}{b}."
    s += f" You have {distance} miles left."
    return s
  else:
    return "NO-ENVIRONMENT-TEXT-FOUND-FOR: " + t.lang


def choiceSpaceText():
  print("\033[0;0H" + "\n" * (1 + screen.height // 2) + "\033[J")


def init():
  global screen
  global gamestate
  global t

  screen = s.Screen()
  gamestate = "title"
  t.setLanguage("en")
  choices.GlobalChoiceSettings.screen = screen


food, water, temperature, day, hour, shelter, inventory, fire, fireHasExisted, grace, innerTemp, equip, distance, hasFrozen = [None] * 14

def main():
  global screen
  global gamestate

  global food
  global water
  global temperature
  global day
  global hour
  global shelter
  global inventory
  global fire
  global fireHasExisted
  global grace
  global innerTemp
  global equip
  global distance
  global hasFrozen
  
  while True:
    if gamestate == "title":
      screen.blit(0, 0, image.getImage("YukonDay.bin"))
      screen.display()
      c = Choices(
        #t.getString("text:title"),["text:play", "text:language"]
        t.getString("text:title"),["text:play"]
        ).choose()

      if c == 0:
        break

      if c == 1:
        screen.display()
        c = Choices(t.getString("text:language"),
                    list(t.getAllLanguages().keys())).choose(key=False, translate=False)
        t.setLanguage(t.getAllLanguages()[c])

  run = True

  food = 100
  water = 100
  temperature = 70
  day = 0
  hour = 5
  shelter = None
  fire = 0
  fireHasExisted = False
  grace = 3
  distance = 100
  trail = False
  trailProgress = 0
  nightTravel = False
  trailProgressCache = -1
  hasFrozen = False
  
  causeOfDeath = ""

  inventory = {}
  for i in Item.GetAllItems():
    inventory[i] = 0
  
  def buildGameChoices():
    arr = ["action:wait", "action:check_inventory", "action:craft"]

    if inventory["item:wood"] >= 20:
      arr.append("action:build_shelter")
    
    if (utils.hourToTime(hour, day, translate=False) != "time:night") or inventory["item:torch"] > 0:
      arr.append("action:explore_nearby")

    elif shelter != None:
      arr.append("action:sleep")

    if food <= 80:
      arr.append("action:eat")

    if water <= 80:
      arr.append("action:drink")

    if fire == 0 and inventory["item:fire_starter"] > 0:
      arr.append("action:build_fire")

    elif fire > 0 and fire < 100:
      arr.append("action:refuel_fire")

    if equip != None or bool(max([int(Item(i, inventory[i]).getEquipable()) for i in inventory])):
      arr.append("action:manage_equipment")

    if trail:
      arr.append("action:take_trail")
    
    return arr

  
  def decrementState(amt, hardWork=False):
    amtF = amt
    amtW = amt
    
    if temperature > 70:
      add = (70 - temperature) * -0.5
      amtW += m.ceil(add)

    if temperature < 50:
      add = -(temperature - 50) * -0.1
      amtF += m.ceil(add)

    if temperature <= 32:
      amtF *= 1.1
      amtW *= 1.05

      if temperature <= 0:
        amtF *= 1.2
        amtW *= 1.1

    if hardWork:
      amtF *= 2
      amtW *= 2.25

    global food
    global water
      
    food -= amtF
    water -= amtW

  
  tempMap = json.load(open(utils.getFileLocation("/json/temperature.json"), "r"))

  sleeping = False
  sleepTime = 0

  if random.randint(1, 50000) == 420:
    causeOfDeath = "appendicitis"
    run = False
  
  while run:
    temperature = tempMap["day"] \
      [utils.getSeason(day, translate=False).removeprefix("season:")] \
      [day % 3] \
      [utils.hourToTime(hour, day, integer=True)]
    
    if equip == None:
      innerTemp = temperature
    else:
      innerTemp = temperature + Item(equip).getTemperature()

    i = fire
    while innerTemp < 85 and i > 0:
      innerTemp += 1
      i -= 2

      
    if food <= 0 or water <= 0 or innerTemp <= 32:
      if sleeping:
        sleeping = False
        print("\033[0;0H\033[J" + t.getString("text:sleep:wake_up") + str(sleepTime), end="")
        Choices("", ["common:ok"]).choose()
        sleepTime = 0
      elif trailProgress >= 0:
        trail = True
        trailProgressCache = trailProgress
        trailProgress = -1
        fireHasExisted = False
        
      else:
        grace -= 1
    if grace <= -1:
      run = False
      if food <= 0:
        causeOfDeath = "starvation"
      elif water <= 0:
        causeOfDeath = "dehydration"
      elif innerTemp <= 32:
        causeOfDeath = "freezing"
      
      break
    
    if hour >= 24:
      day += 1
      hour -= 23

    if fire > 0:
      fire -= 3
    elif fire < 0:
      fire = 0

    season = utils.getSeason(day, translate=False)
    if temperature <= 32 and (season.endswith("fall") or season.endswith("winter")):
      hasFrozen = True
    elif temperature > 32 and (season.endswith("spring") or season.endswith("summer")):
      hasFrozen = False

    if (utils.hourToTime(hour, day, translate=False) != "time:night" or innerTemp <= 32) and sleeping:
      sleeping = False
      print("\033[0;0H\033[J" + t.getString("text:sleep:wake_up") + str(sleepTime), end="")
      Choices("", ["common:ok"]).choose()
      sleepTime = 0

    if (not sleeping) and (trailProgress <= 0):
      print(utils.getCorrectBackgroundImage(hour, day, hasFrozen))
      screen.blit(0, 0, image.getImage(utils.getCorrectBackgroundImage(hour, day, hasFrozen)))


      if fire != 0:
        screen.blit(24, 20, image.getImage("fire_on.bin"))
      elif fireHasExisted:
        screen.blit(24, 20, image.getImage("fire_off.bin"))

      if shelter == "shelter:lean-to":
        screen.blit(18, 19, image.getImage("tent.bin"))
      
      screen.display()

    proceed = False


    print(t.getString("text:explore:torch_burn_out") + "\n")

    while not proceed:
      c = None
      if (not sleeping) and (trailProgress <= 0):
        print("\033[0m", end="")
        cArray = buildGameChoices()
        choiceSpaceText()
        c = Choices(environmentText(temperature, food, water, day, hour, fire, distance), cArray).choose(key=False, exe=False)
      
        if type(c) == dict:
          if c["type"] == "code":
            exec(c["code"])

      
      elif sleeping:
        proceed = True
        sleepTime += 1

      
      elif trailProgress > 0:
        print("\033[0;0H\033[J", end="")
        proceed = True
        
        distance -= 1
        trailProgress -= 1
        hour += 1
        
        shelter = None
        fire = 0

        decrementState(0.5, hardWork=True)

        if distance <= 0:
          print("\033[0;0H\033[J\033[38;2;30;250;30m")
          print(t.getString("text:win"))
          return

        elif trailProgress <= 0:
          trailProgress = -1
          nightTravel = False
          print("\033[0;0H\033[J", end="")
          Choices(t.getString("text:trail:end"), ["common:ok"]).choose()
          
        
        elif utils.hourToTime(hour, day, translate=False) == "time:night" and not nightTravel:
          c = Choices(t.getString("text:trail:night"), ["common:no", "common:yes"]).choose()

          if c == 0:
            nightTravel = True
          else:
            trail = True
            trailProgressCache = trailProgress
            trailProgress = -1

        
        elif utils.hourToTime(hour, day, translate=False) == "time:night" and random.randint(1, 10) == 5:
          print("\a\033[0;0H\033[J", end=None)
          Choices(t.getString("text:trail:howls"), ["common:ok"]).choose()
          run = False
          causeOfDeath = "animal_attack"
          

      
      if c == "action:wait":
        proceed = True


      
      elif c == "action:check_inventory":
        choiceSpaceText()

        refinedList = []

        for i in inventory.keys():
          if inventory[i] != 0:
            refinedList.append((" {:<" + str(screen.width - 12) + "} {:<10}").format(t.getString(i), "× " + str(inventory[i]), ""))

        if len(refinedList) == 0:
          print(t.getString("text:inventory:empty"))
        else:  
        
          lineColor = True
          refinedList.sort()
          
          print(t.getString("text:inventory:you_have") + ":\n")

          for i in refinedList:
            lineColor = not lineColor
            
            bgColor = "\033[" + ("47" if lineColor else "100") + "m"
            fgColor = "\033[" + ("90" if lineColor else "37") + "m"
            
            print("\033[0;1m" + bgColor + fgColor + i)
        
        Choices("", ["common:ok"]).choose()

      
        
      elif c == "action:build_shelter":
        choiceSpaceText()
        shelter
        shelters = ["common:back"]
        if inventory["item:wood"] >= 10:
          shelters.append("shelter:lean-to")

        if len(shelters) == 1:
          Choices(t.getString("text:shelter:missing"), ["common:ok"]).choose()
        else:
          c = Choices(t.getString("text:shelter:choose"), shelters).choose(key=False)

          if c == "shelter:lean-to":
            shelter = "shelter:lean-to"
            inventory["item:wood"] -= 10
            choiceSpaceText()
            Choices(t.getString("text:shelter:built:" + c.removeprefix("shelter:")), ["common:ok"]).choose()
            proceed = True


      
      elif c == "action:explore_nearby":
        decrementState(3, hardWork=True)

        foundTrail = False
        foundDeer = [False, False]
        
        foundWater = [random.randint(1, 5) == 1, random.randint(1, 2) == 1]
        if not foundWater[0]:
          foundTrail = random.randint(1, 8) == 1
        if not foundTrail:
          foundDeer = [random.randint(1, 4) == 1, random.randint(1, 100) < (max([Item(i, inventory[i]).getDamage() for i in inventory]))]
        
        
        screen.blit(0, 0, image.getImage(utils.getCorrectBackgroundImage(hour, day, hasFrozen)))

        if foundWater[0]:
          if hasFrozen:
            screen.blit(22, 22, image.getImage("pond_frozen.bin"))
          else:
            screen.blit(22, 22, image.getImage("pond_thawed.bin"))
        elif foundDeer[0]:
          if random.random() > 0.5:
            screen.blit(random.randint(16, 32), random.randint(16, 20), image.getImage("deer_f.bin"))
          else:
            screen.blit(random.randint(16, 32), random.randint(16, 20), image.getImage("deer_m.bin"))
        
        screen.display()

        print("\033[0m", end="")
        choiceSpaceText()
        
        lootTables = json.load(open(utils.getFileLocation("/json/lootTables.json"), "r"))["exploreNearby"]

        lootTable = None
        
        if utils.getSeason(day, translate=False).endswith("spring"):
          lootTable = lootTables["spring"]
        elif utils.getSeason(day, translate=False).endswith("summer"):
          lootTable = lootTables["summer"]
        elif utils.getSeason(day, translate=False).endswith("fall"):
          lootTable = lootTables["fall"]
        else:
          lootTable = lootTables["winter"]

        items = []
        itemCounts = []
        
        for i in lootTable:
          items.append(random.choice(list(i.keys())))
          itemCounts.append(random.randint(1, i[items[-1]]))

        if random.randint(1, 100) == 1:
          rareItem = random.choice(lootTables["rare"])
          items.append(rareItem)
          itemCounts.append(1)

        if inventory["item:stone_hatchet"] > 0:
          for item in lootTables["hatchet"]:
            items.append(item)
            itemCounts.append(random.randint(0, 3))

        for i in range(len(items)):
          inventory[items[i]] += itemCounts[i]

        if utils.hourToTime(hour, day, translate=False) == "time:night":
          inventory["item:torch"] -= 1
          print(t.getString("text:explore:torch_burn_out") + "\n")
        
        print(t.getString("text:explore:found") + "\n")
        for i in range(len(items)):
          print(Item(items[i], itemCounts[i]))

        if foundWater[0]:
          print("\n" + t.getString("text:explore:water:found"))
          c = Choices("", ["common:no", "common:yes"]).choose(key=True)
          
          choiceSpaceText()

          if c == 1:
            if foundWater[1]:
              water = 100
              Choices(t.getString("text:explore:water:drank"), ["common:ok"]).choose()
              while inventory["item:empty_bottle"] > 0:
                inventory["item:empty_bottle"] -= 1
                inventory["item:water_bottle"] += 1
              hour += 1

            else:
              c = Choices(t.getString("text:explore:water:dirty"), ["common:no", "common:yes"]).choose()

              choiceSpaceText()

              if c == 1:
                if random.randint(1, 2) == 1:
                  run = False
                  causeOfDeath = "cholera"
                else:
                  water += 25
                  Choices(t.getString("text:explore:water:drank_anyways"), ["common:ok"]).choose()
        
        
        elif foundTrail:
          print("")
          Choices(t.getString("text:trail:find"), ["common:ok"]).choose()
          trail = True

        
        else:
          if foundDeer[0]:
            print("\n" + t.getString("text:explore:deer:found"))
            c = Choices("", ["common:no", "common:yes"]).choose(key=True)
            
            choiceSpaceText()
  
            if c == 1:
              if foundDeer[1]:
                water = 100
                Choices(t.getString("text:explore:deer:kill"), ["common:ok"]).choose()
                inventory["item:raw_venison"] += 1
                inventory["item:deer_pelt"] += 1
                decrementState(1, hardWork=True)
                hour += 1
  
              else:
                
                screen.blit(0, 0, image.getImage(utils.getCorrectBackgroundImage(hour, day, hasFrozen)))
                screen.display()
                print("\033[0m", end="")
                choiceSpaceText()
                
                Choices(t.getString("text:explore:deer:escape"), ["common:ok"]).choose()

          else:
          
            c = Choices("", ["common:ok"]).choose()
        
        proceed = True

      
      
      elif c == "action:eat":
        foods = []
        
        for i in inventory.keys():
          if inventory[i] > 0 and Item(i).getFood() > 0:
            foods.append(i)
        
        choiceSpaceText()

        if len(foods) == 0:
          Choices(t.getString("text:eat:missing"), ["common:ok"]).choose()

        else:
          c = Choices(t.getString("text:eat:choose"), ["common:back"] + foods).choose(key=True)
  
          if c != 0:
            c -= 1
            doWhile = True
            while doWhile:
              inventory[foods[c]] -= 1
              food += Item(foods[c]).getFood()
              water += Item(foods[c]).getWater()

              doWhile = inventory[foods[c]] > 0 and food < (100 - Item(foods[c]).getFood())

      
      
      elif c == "action:drink":
        drinks = []
        
        for i in inventory.keys():
          if inventory[i] > 0 and Item(i).getWater() > 0:
            drinks.append(i)
        
        choiceSpaceText()

        if len(drinks) == 0:
          Choices(t.getString("text:drink:missing"), ["common:ok"]).choose()

        else:
          c = Choices(t.getString("text:drink:choose"), ["common:back"] + drinks).choose(key=True)
  
          if c != 0:
            c -= 1
            doWhile = True
            while doWhile:
              inventory[drinks[c]] -= 1
              food += Item(drinks[c]).getFood()
              water += Item(drinks[c]).getWater()

              doWhile = inventory[drinks[c]] > 0 and water < (100 - Item(drinks[c]).getWater())

              
      
      elif c == "action:craft":
        crafting = json.load(open(utils.getFileLocation("/json/crafting.json")))

        recipes = []
        
        for i in crafting.keys():
          recipes.append(i)
          for j in crafting[i]["ingredients"].keys():
            if inventory[j] < crafting[i]["ingredients"][j] and (i in recipes):
              recipes.pop(-1)
            elif "fire" in crafting[i].get("req", []) and fire <= 0:
              recipes.pop(-1)

        choiceSpaceText()

        if len(recipes) == 0:
          Choices(t.getString("text:craft:missing"), ["common:ok"]).choose()

        else:

          c = Choices(t.getString("text:craft:choose"), ["common:back"] + recipes).choose(key=False)

          if c != "common:back":
            choiceSpaceText()

            print('"' + t.getString(c) + '" ', end="")
            print(t.getString("text:craft:requires") + ": \n")

            for i in crafting[c]["ingredients"].keys():
              print(t.getString(i) + " × " + str(crafting[c]["ingredients"][i]))
            
            c2 = Choices("", ["common:back", "action:craft"]).choose()

            if c2 == 1:
            
              for i in crafting[c]["ingredients"].keys():
                inventory[i] -= crafting[c]["ingredients"][i]

              inventory[c] += 1

              choiceSpaceText()
              Choices(t.getString("text:craft:crafted") + " " + t.getString(c) + "!", ["common:ok"]).choose()
              
              proceed = True
              decrementState(1, hardWork=True)


      
      elif c == "action:build_fire":
        items = []

        for i in inventory.keys():
          if inventory[i] and i != "item:fire_starter" and Item(i).getFlammibility() > 0:
            items.append(i)
            
        choiceSpaceText()
        
        if len(items) == 0:
          Choices(t.getString("text:fire:mising"), ["common:ok"]).choose()
        else:
          choiceSpaceText()
          c = Choices(t.getString("text:fire:feul"), ["common:back"] + [Item(i, inventory[i]) for i in items]).choose()
          c -= 1

          proceed = True
          
          if c != -1:
            item = items[c]
            while fire < 100 and inventory[item] > 0:
              fire += Item(item).getFlammibility()
              inventory[item] -= 1

            fireHasExisted = True



      elif c == "action:refuel_fire":
        flammables = []
        
        for i in inventory.keys():
          if inventory[i] > 0 and Item(i).getFlammibility() > 0:
            flammables.append(i)
        
        choiceSpaceText()

        if len(flammables) == 0:
          Choices(t.getString("text:refuel:missing"), ["common:ok"]).choose()

        else:
          c = Choices(t.getString("text:refuel:choose"), ["common:back"] + flammables).choose(key=True)
  
          if c != 0:
            c -= 1
            doWhile = True
            while doWhile:
              inventory[flammables[c]] -= 1
              fire += Item(flammables[c]).getFlammibility()

              doWhile = inventory[flammables[c]] > 0 and fire < (100 - Item(flammables[c]).getFlammibility())
        

      elif c == "action:manage_equipment":
        choiceSpaceText()
        if equip != None:
          print(t.getString("text:equipment:current") + Item(equip).__repr__(), end="\n\n")
          c = Choices(t.getString("text:equipment:unequip") + Item(equip).__repr__() + "?", ["common:no", "common:yes" ]).choose(key=False)
          if c == "common:yes":
            inventory[equip] += 1
            equip = None
        else:
          print(t.getString("text:equipment:missing"), end="\n\n")
        
          equipment = []
  
          for i in inventory:
            if inventory[i] > 0 and Item(i).getEquipable():
              equipment.append(i)

          c = Choices(t.getString("text:equipment:choose"), ["common:back"] + equipment).choose(key=False)

          if c != "common:back":
            equip = c
            inventory[c] -= 1

      
      elif c == "action:sleep":
        if innerTemp > 32:
          sleeping = True
          proceed = True
        else:
          Choices(t.getString("text:sleep:cold"), ["OK"]).choose()


      elif c == "action:take_trail":
        trail = False
        fireHasExisted = False

        if trailProgressCache == -1:
          trailProgress = random.randint(1, 10)
        else:
          trailProgress = trailProgressCache
          trailProgressCache = -1
          
    
    decrementState(0.5 if sleeping else 1)
    hour += random.randint(1, 2)
      
  screen.delete()

  print("\a\033[0m\033[38;2;200;0;0m" + t.getString("text:death:screen") + "\033[0m", end="\n\n\n")
  print(t.getString("text:death:cause:text") + t.getString("text:death:cause:" + causeOfDeath))

if __name__ == "__main__":
  while True:
    init()
    main()
    time.sleep(0.5)
    input()