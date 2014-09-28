import sublime
import sublime_plugin

import os
import sys

root_location = os.path.dirname(__file__)
local_storage = os.path.join(root_location,'local.db')

yandex_translate_path = os.path.join(root_location,'python-yandex-translate')
requests_path = os.path.join(root_location,'requests')
ssl_path = os.path.join(root_location,'backports.ssl')
six_path = os.path.join(root_location,'six')
OpenSSL_path = os.path.join(root_location,'pyopenssl')
cryptography_path = os.path.join(root_location,'cryptography')

sys.path.insert(0, yandex_translate_path)
sys.path.insert(0, requests_path)
sys.path.insert(0, ssl_path)
sys.path.insert(0, six_path)
sys.path.insert(0, OpenSSL_path)
sys.path.insert(0, cryptography_path)

# import ssl   

from yandex_translate import YandexTranslate

class Translator(object):
    def __init__(self):
        self.cache = {}
        self.handler = YandexTranslate(os.environ['YA_TRANSLATE_KEY'])
 
    def translate(self,text):
        if text not in self.cache.keys():
            print ("Query API...")
            translated_text = self.handler.translate(text,'ru-en')
            self.cache.update({text:translated_text})
        else:
            print ("From cache...")
            return self.cache[text]

translator = Translator()

class RussianVariableTranslateCommand(sublime_plugin.TextCommand):
    """
    Translates russian variables to English via yandex translate api + localstore db(text file).
    """

    def run(self,edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                self.translate(text)
            else:
                self.view.window().show_input_panel("Word to translate ...",'',self.on_input,None,None)

    def on_input(self,user_input):
        self.translate(user_input)

    def translate(self,text):
        translated_text = translator.translate(text)
        self.insert_translated_text(translated_text)

    def insert_translated_text(self,translated_text):
        self.view.run_command("insert",{"characters":translated_text})

