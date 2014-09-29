import sublime
import sublime_plugin

import os
import sys

root_location = os.path.dirname(__file__)
local_storage = os.path.join(root_location,'local.db')

yandex_translate_path = os.path.join(root_location,'python-yandex-translate')
requests_path = os.path.join(root_location,'requests')
sublimessl = os.path.join(root_location,'sublimessl')

sys.path.insert(0, yandex_translate_path)
sys.path.insert(0, requests_path)
sys.path.insert(0, sublimessl)

import yandex_translate
from yandex_translate import YandexTranslate

from SSL import ssl

def plugin_loaded():
    from imp import reload
    reload(yandex_translate)
    reload(yandex_translate.requests)
    reload(yandex_translate.requests.packages.urllib3.connection)
    yandex_translate.requests.packages.urllib3.connection.ssl = ssl

    func = yandex_translate.requests.packages.urllib3.response.HTTPResponse.stream
    def urllib3_HTTPResponse_stream_wrapper():
        return lambda self,amt=None,decode_content=None:func(self,None,decode_content)
    yandex_translate.requests.packages.urllib3.response.HTTPResponse.stream = urllib3_HTTPResponse_stream_wrapper()
    print ("Plugin RussianVariableTranslate is loaded")


class Translator(object):
    def __init__(self):
        self.cache = {}
        self.handler = YandexTranslate(os.environ['YA_TRANSLATE_KEY'])

    def translate(self,text):
        if text not in self.cache.keys():
            print ("Query API...")
            translated_text = self.handler.translate(text,'ru-en')
            if translated_text['code'] != 200:
                return
            self.cache.update({text:translated_text['text'][0]})
        else:
            print ("From cache...")
        return self.cache[text]

translator = Translator()

class RussianVariableTranslateCommand(sublime_plugin.TextCommand):
    """
    Translates russian variables to English via yandex translate api + localstore db(text file).
    """

    def run(self,edit,**kwargs):
        if len(kwargs.keys())>0:
            print ("kwargs =",kwargs)
            print (translator.translate(kwargs['text']))
            return None
        print ("running command")
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
        print("translated_text=",translated_text)
        self.insert_translated_text(translated_text)

    def insert_translated_text(self,translated_text):
        self.view.run_command("insert",{"characters":translated_text})
