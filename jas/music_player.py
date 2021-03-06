import dbus
import dbus.mainloop.glib
import sys
from gi.repository import GLib
import argparse
import requests
import bs4
import json
import subprocess

URL = 'https://www.google.com/search?tbm=isch&q='
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
viewer = None

class MusicScript:

    def __init__(self, app):
        self.app = app.root
        print("App: ", self.app)

    songTitle = ""
    songArtist = ""
    songGenre = ""
    songAlbum = ""
    songDuration = 0
    songTime = 0
    trackNum = "0"
    totalTracks = "0"
    currentTime = 0
    imageURL = ""
    isPlaying = False
    changingSong = 0
    player_iface = dbus.Interface

    def on_property_changed(self, interface, changed, invalidated):

        if interface != 'org.bluez.MediaPlayer1' and interface != 'org.bluez.MediaItem1':
            return
        if interface == 'org.bluez.MediaItem1':
            self.changingSong += 1
        for prop, value in changed.items():
            if prop == 'Position':
                self.currentTime = value
            if prop == 'Status':
                if value == "playing":
                    self.isPlaying = True
                else:
                    self.isPlaying = False
            if prop == 'Track' or prop == 'Metadata':
                for prop2, value2 in value.items():
                    if prop2 == "Title":
                        if len(value2) > 20:
                            self.songTitle = value2[0:20]
                        else:
                            self.songTitle = value2
                    if prop2 == "Artist":
                        if len(value2) > 20:
                            self.songArtist = value2[0:20]
                        else:
                            self.songArtist = value2
                    if prop2 == "Album":
                        self.songAlbum = value2
                    if prop2 == "Genre":
                        self.songGenre = value2
                    if prop2 == "Duration":
                        self.songDuration = value2
                    if prop2 == "TrackNumber":
                        self.trackNum = str(value2)
                    if prop2 == "NumberOfTracks":
                        self.totalTracks = str(value2)
                # self.show_album_art(self.songArtist, self.songAlbum)

    def on_playback_control(self, fd, condition):
        str = fd.readline()
        if str.startswith('play'):
            self.player_iface.Play()
        elif str.startswith('pause'):
            self.player_iface.Pause()
        elif str.startswith('next'):
            self.player_iface.Next()
        elif str.startswith('prev'):
            self.player_iface.Previous()
        return True

    def show_album_art(self, artist, album):
        if artist == '' or album == '':
            return

        artist = '"' + '+'.join(artist.split()) + '"'
        album = '"' + '+'.join(album.split()) + '"'
        res = requests.get(URL + '+'.join((artist, album)), headers=HEADER)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        meta_elements = soup.find_all("div", {"class": "rg_meta"})
        meta_dicts = (json.loads(e.text) for e in meta_elements)

        for d in meta_dicts:
            print(d)
            if d['oh'] == d['ow']:
                image_url = d['ou']
                self.imageURL = image_url
                print(image_url)
                break

        # with open('album_art', 'wb') as f:
        #     f.write(res.content)
        #
        # viewer = subprocess.Popen(['feh', '-g', '220x220', 'album_art'])

    def getSongTitle(self):
        return self.songTitle

    def getSongArtist(self):
        return self.songArtist

    def listen(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        obj = bus.get_object('org.bluez', "/")
        mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
        for path, ifaces in mgr.GetManagedObjects().items():
            adapter = ifaces.get('org.bluez.MediaPlayer1')
            if not adapter:
                continue
            player = bus.get_object('org.bluez', path)
            self.player_iface = dbus.Interface(player, dbus_interface='org.bluez.MediaPlayer1')
            break
        if not adapter:
            sys.exit('Error: Media Player not found.')

        bus.add_signal_receiver(
            self.on_property_changed,
            bus_name='org.bluez',
            signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties')
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_playback_control)
        GLib.MainLoop().run()
