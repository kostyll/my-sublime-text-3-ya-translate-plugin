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
    def urllib3_HTTPResponse_stream_wrapper(func):
        return lambda self,amt=None,decode_content=None:func(self,None,decode_content)
    yandex_translate.requests.packages.urllib3.response.HTTPResponse.stream = urllib3_HTTPResponse_stream_wrapper(func)
    print ("Plugin RussianVariableTranslate is loaded")


class Translator(object):
    def __init__(self):
        self.cache = {}
        self.handler = YandexTranslate(os.environ['YA_TRANSLATE_KEY'])
        self.dict = {}
        self.loaddict()

    def loaddict(self):
        try:
            dictfile = open(local_storage,'rt')
        except:
            open(local_storage,'wt')
            self.loaddict()
            return
        for line in dictfile:
            word, translated_word = line.split('<===>')
            self.dict.update({word:translated_word})

    def savedict(self):
        with open(local_storage,'wt') as dictfile:
            for word,translated_word in self.dict.items():
                dictfile.write("{}<===>{}\n".format(word,translated_word))

    def add_translated_word(self,word,translated_word):
        self.dict[word] = translated_word
        self.savedict()

    def translate(self,text):
        if text not in self.cache.keys():
            print ("Query local dict ...")
            if text not in self.dict.keys():
                print ("Query API...")
                translated_text = self.handler.translate(text,'ru-en')
                if translated_text['code'] != 200:
                    return
                translated_word = translated_text['text'][0]
                self.add_translated_word(text, translated_word)
                self.savedict()
                self.cache.update({text:self.dict[text]})
            else:
                pass
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
