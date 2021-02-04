#!/usr/bin/python
import os
import sys
import signal
import logging
import logging.handlers
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GObject, GLib

LOG_LEVEL = logging.INFO
#LOG_LEVEL = logging.DEBUG
LOG_FILE = "/dev/log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
BLUEZ_DEV = "org.bluez.Device1"
isPaired = 0

def device_property_changed_cb(property_name, value, path, interface, device_path):
    global bus
    if property_name != BLUEZ_DEV:
        return

    device = dbus.Interface(bus.get_object("org.bluez", device_path), "org.freedesktop.DBus.Properties")
    properties = device.GetAll(BLUEZ_DEV)

    #logger.info("Getting dbus interface for device: %s interface: %s property_name: %s" % (device_path, interface, property_name))
    if properties["Connected"]:
        bt_addr = "_".join(device_path.split('/')[-1].split('_')[1:])
        if bt_addr == "F8_87_F1_DB_B7_D9":
            cmd = "./playNolanPaired"
        else:
            cmd = "./playOtherPhonePaired"
    else:
        bt_addr = "_".join(device_path.split('/')[-1].split('_')[1:])
        if bt_addr == "F8_87_F1_DB_B7_D9":
            cmd = "./playNolanDisconnected"
        else:
            cmd = "./playWaiting"

        logger.info("Device: %s has disconnected" % bt_addr)
#        cmd = "for i in $(pactl list short modules | grep module-loopback | grep source=bluez_source.%s | cut -f 1); do pactl unload-module $i; done" % bt_addr
#        logger.info("Running cmd: %s" % cmd)
#        os.system(cmd)
    os.system(cmd)

def shutdown(signum, frame):
    mainloop.quit()

if __name__ == "__main__":
    # shut down on a TERM signal
    signal.signal(signal.SIGTERM, shutdown)

    # start logging
    logger = logging.getLogger("bt_auto_loader")
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(logging.handlers.SysLogHandler(address = "/dev/log"))
    logger.info("Starting to monitor Bluetooth connections")

    # Get the system bus
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
    except Exception as ex:
        logger.error("Unable to get the system dbus: '{0}'. Exiting. Is dbus running?".format(ex.message))
        sys.exit(1)

    # listen for signals on the Bluez bus
    bus.add_signal_receiver(device_property_changed_cb, bus_name="org.bluez", signal_name="PropertiesChanged", path_keyword="device_path", interface_keyword="interface")

    try:
        mainloop = GLib.MainLoop.new(None, False)
        mainloop.run()
    except KeyboardInterrupt:
        pass
    except:
        logger.error("Unable to run the gobject main loop")
        sys.exit(1)

    logger.info("Shutting down")
    sys.exit(0)
# SERVICE_NAME = "org.bluez"
# OBJECT_IFACE =  "org.freedesktop.DBus.ObjectManager"
# ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
# DEVICE_IFACE = SERVICE_NAME + ".Device1"
# PROPERTIES_IFACE = "org.freedesktop.DBus.Properties"
# adap = ""
# bus = dbus.SystemBus()
# manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
# objects = manager.GetManagedObjects()
# for path, ifaces in objects.items():
#     adapter = ifaces.get(ADAPTER_IFACE)
#     if adapter is None:
#         continue
#     obj = bus.get_object(SERVICE_NAME, path)
#     adap = dbus.Interface(obj, ADAPTER_IFACE)
#
# def cb(iface=None, mbr=None, path=None):
#
#     print(iface)
#     if ("org.bluez" == iface and path.find(DEV_ID) > -1):
#         print('iface: %s' % iface)
#         print('mbr: %s' % mbr)
#         print('path: %s' % path)
#         print("\n")
#         print("matched")
#
#         if mbr == "Connected":
#             subprocess.call(["playNolanPaired"])
#             print('conn')
#
#         elif mbr == "Disconnected":
#             subprocess.call(["playNolanDisconnected"])
#             print('dconn')
#
# adap.connect_to_signal("Connected", cb, interface_keyword='iface', member_keyword='mbr', path_keyword='path')
# adap.connect_to_signal("Disconnected", cb, interface_keyword='iface', member_keyword='mbr', path_keyword='path')
#
# loop = gobject.MainLoop()
# loop.run()
