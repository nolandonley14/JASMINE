from datetime import datetime
from random import randint

import kivy

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import DictProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.button import Button

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

class Screen(BoxLayout):
    now = ObjectProperty(datetime.now(), rebind=True)
    background_image = ObjectProperty()

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)

        self.background_image = Image(source='BKOCH.jpg').texture
        self.background_image.wrap = 'repeat'
        self.background_image.uvsize = (1, -1)

        Clock.schedule_interval(self.update, 0.1)
        self.update()

    def update(self, *args):
        self.now = datetime.now()

    def on_page_changed(self, page):
        self.ids.camera_view.play = (page == 0)

class TestingApp(App):
    def build(self):
        return Screen()

if __name__ == '__main__':
    TestingApp().run()
