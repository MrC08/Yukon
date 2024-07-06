import json


class Translator:
  lang = None

  @staticmethod
  def setLanguage(languageCode):
    Translator.lang = languageCode

  @staticmethod
  def getAllLanguages():
    return {"English": "en", "Español": "es"}

  @staticmethod
  def getString(id):
    dir = __file__.replace("\\", "/")
    s = json.load(open(dir.removesuffix(dir.split("/")[-1]) + "/json/translate.json", "r", encoding="utf-8"))
    for i in id.split(":"):
      s = s.get(i)

      if s == None:  return "ID-NOT-FOUND: " + id

    s = s.get(Translator.lang)

    if s == None: return "TRANSLATION-NOT-FOUND: " + Translator.lang + ":" + id

    return s