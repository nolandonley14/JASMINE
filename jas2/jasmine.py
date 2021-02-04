import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.tabbedpanel import *
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.progressbar import ProgressBar
from kivy.config import Config
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.lang import Builder
from kivy.animation import Animation
from kivy_garden.mapview import MapView
from mapbox import Maps
from gi.repository import GLib
from music_player import *
from weather_script import *
from ForecastView import *
from ScrollingLabel import *
import math
import time
import datetime
from datetime import date
import googlemaps
import threading
import schedule
import config

# 0 being off 1 being on as in true/false
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

LabelBase.register(name="HeaderLight",
                   fn_regular="aileron/Aileron-UltraLight.otf")
LabelBase.register(name="HeaderMed", fn_regular="aileron/Aileron-Light.otf")

gmaps = googlemaps.Client(key=config.api_key)
weatherObject = WeatherScript()

class PPButton(ToggleButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(PPButton, self).__init__(**kwargs)
        self.source = 'iconFolder/png/011-pause.png'

    def on_state(self, widget, value):
        if value == 'down':
            self.source = 'iconFolder/png/011-pause.png'
        else:
            self.source = 'iconFolder/png/012-play.png'
        self.reload()

    def refresh(self):
        self.reload()

class ScrollLabel(ScrollView):
    text = StringProperty('')

class HomeTab(TabbedPanelItem):
    temp = ObjectProperty(Label)
    title = StringProperty()
    artist = StringProperty()
    weather = ObjectProperty(Label)
    wind = ObjectProperty(Label)
    uv = ObjectProperty(Label)
    city = ObjectProperty(Label)
    weatherIcon = ObjectProperty(AsyncImage)
    ppBut = StringProperty()

    def nextSong(self):
        musicObject.player_iface.Next()

    def prevSong(self):
        musicObject.player_iface.Previous()

    # def update(self, *args):
    #     try:
    #         self.temp.text = str(round(weatherObject.currentWeatherObj.temperature['temp']))
    #         self.weather.text = weatherObject.currentWeatherObj.weatherDescription.title()
    #         self.wind.text = str(weatherObject.currentWeatherObj.wind['speed'])
    #         self.city.text = weatherObject.currentWeatherObj.city
    #         self.uv.text = str(math.floor(weatherObject.currentWeatherObj.uv))
    #         self.weatherIcon.source = weatherObject.currentWeatherObj.weatherIconURL
    #     except Exception as e:
    #         print("Error: ", e)
    #         return

    def __init__(self, **kwargs):
        super(HomeTab, self).__init__(**kwargs)
        self.title = "Title"
        self.artist = "Artist"
        self.ppBut = "normal"
        # Clock.schedule_interval(self.update, 30)
        # Clock.schedule_interval(self.clockUpdate, 1)

class MusicTab(TabbedPanelItem):
    title = StringProperty()
    artist = StringProperty()
    songNum = StringProperty()
    songTime = StringProperty()
    songDuration = StringProperty()
    songProgress = ObjectProperty(ProgressBar)
    duration = NumericProperty(10)
    curTime = -2
    # change = musicObject.changingSong
    ppBut2 = ObjectProperty(PPButton)

    def timeRep(self, numSeconds):
        millis = int(numSeconds)
        seconds = (millis / 1000) % 60
        seconds = int(seconds)
        minutes = (millis / (1000 * 60)) % 60
        minutes = int(minutes)

        return("%d:%02d" % (minutes, seconds))

    # def nextSong(self):
    #     musicObject.player_iface.Next()
    #
    # def prevSong(self):
    #     musicObject.player_iface.Previous()
    #
    # def on_enter(self):
    #     self.curTime = musicObject.currentTime
    #     self.title.text = musicObject.songTitle
    #     self.artist.text = musicObject.songArtist
    #     self.songNum.text = musicObject.trackNum + " / " + musicObject.totalTracks
    #     self.songTime.text = self.timeRep(self.curTime)
    #     self.songDuration.text = self.timeRep(musicObject.songDuration)

    # def update(self, *args):
    #     if musicObject.changingSong != self.change:
    #         self.curTime = 0
    #         self.change = musicObject.changingSong
    #     self.songProgress.max = int(musicObject.songDuration)
    #     self.songProgress.value = self.curTime
    #     self.title.text = musicObject.songTitle
    #     self.artist.text = musicObject.songArtist
    #     self.songNum.text = musicObject.trackNum + " / " + musicObject.totalTracks
    #     if musicObject.isPlaying:
    #         self.curTime += 1000
    #         self.ppBut2.source = 'iconFolder/png/011-pause.png'
    #     else:
    #         self.ppBut2.source = 'iconFolder/png/012-play.png'
    #     self.songTime.text = self.timeRep(self.curTime)
    #     self.songDuration.text = self.timeRep(musicObject.songDuration)

    def __init__(self, **kwargs):
        super(MusicTab, self).__init__(**kwargs)
        # marquee = Animation(scroll_x = 1, duration=self.duration)
        # marquee.start(self.title)
        # Clock.schedule_interval(self.update, 1)

class MapsTab(TabbedPanelItem):
    # currentMap = ObjectProperty(MapView)

    def __init__(self, **kwargs):
        super(MapsTab, self).__init__(**kwargs)

class WeatherTab(TabbedPanelItem):
    temp = ObjectProperty(Label)
    weather = ObjectProperty(Label)
    wind = ObjectProperty(Label)
    uv = ObjectProperty(Label)
    city = ObjectProperty(Label)
    fLike = ObjectProperty(Label)
    sunSetTime = ObjectProperty(Label)
    sunRiseTime = ObjectProperty(Label)
    pressureLabel = ObjectProperty(Label)
    humidityLabel = ObjectProperty(Label)
    weatherIcon = ObjectProperty(AsyncImage)
    foreBox = ObjectProperty(BoxLayout)
    dailyBut = ObjectProperty(ToggleButton)

    def changeForecast(self):
        self.foreBox.clear_widgets()
        if self.dailyBut.state == 'down':
            for i in range(len(weatherObject.dailyWeatherObj)):
                dw = weatherObject.dailyWeatherObj[i]
                d = DailyForecast(dayName=dw.dayName,image = dw.weatherIconURL, description= dw.weatherDescription.title(), tempMax= str(math.floor(dw.maxTemp)), tempMin=str(math.floor(dw.minTemp)))
                self.foreBox.add_widget(d)
        else:
            for j in range(len(weatherObject.hourlyWeatherObj)):
                hw = weatherObject.hourlyWeatherObj[j]
                h = HourlyForecast(time=hw.time,image = hw.weatherIconURL, description= hw.weatherDescription.title(), temp=str(math.floor(hw.temperature['temp'])))
                self.foreBox.add_widget(h)

    def update(self, *args):
        try:
            self.temp.text = str(round(weatherObject.currentWeatherObj.temperature['temp']))
            self.weather.text = weatherObject.currentWeatherObj.weatherDescription.title()
            self.wind.text = str(weatherObject.currentWeatherObj.wind['speed']) + " mph"
            self.city.text = weatherObject.currentWeatherObj.city
            self.uv.text = str(math.floor(weatherObject.currentWeatherObj.uv))
            self.weatherIcon.source = weatherObject.currentWeatherObj.weatherIconURL
            self.fLike.text = "Feels Like: " + str(round(weatherObject.currentWeatherObj.temperature['feels_like'])) + " °F"
            self.sunSetTime.text = weatherObject.currentWeatherObj.sunset
            self.sunRiseTime.text = weatherObject.currentWeatherObj.sunrise
            self.pressureLabel.text = str(weatherObject.currentWeatherObj.pressure['press']) + " atm"
            self.humidityLabel.text = str(weatherObject.currentWeatherObj.humidity) + " %"
            self.changeForecast()
        except Exception as e:
            print("Error: ", e)
            return


    def __init__(self, **kwargs):
        super(WeatherTab, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 30)

class SettingsTab(TabbedPanelItem):
    pass

class BottomBar(GridLayout):
    time = ObjectProperty(Label)

    def clockUpdate(self, *args):
        date = datetime.datetime.now()
        self.time.text = date.strftime("%-I:%M %p")

    def __init__(self, **kwargs):
        super(BottomBar, self).__init__(**kwargs)
        Clock.schedule_interval(self.clockUpdate, 1)

class TabSection(TabbedPanel):
    pass

class AppLayout(FloatLayout):
    pass

#kv = Builder.load_file("jasmine.kv")
class JasmineApp(App):
    def build(self):
        return AppLayout()


if __name__ == "__main__":
    app = JasmineApp()
    musicObject = MusicScript(app)
    listener = threading.Thread(target=musicObject.listen).start()
    app.run()
