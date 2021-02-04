import kivy
import googlemaps

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.button import Button

class DirectionsSummary(BoxLayout):

    begin = StringProperty()
    to = StringProperty()
    timeText = StringProperty()
    distanceText = StringProperty()
    summaryText = StringProperty()

    def __init__(self, **kwargs):
        super(DirectionsSummary, self).__init__(**kwargs)
