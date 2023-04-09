import os
import time
import uiautomator


# input keyevent
# https://mkblog.co.kr/android-adb-input-command/
class Device:
    def __init__(self, _id: str, model: str, product: str):
        self.id = _id
        self.model = model
        self.product = product

        # command for press button
        self.home = "adb -s " + self.id + " shell input keyevent KEYCODE_HOME"
        self.recent_app = "adb -s " + self.id + " shell input keyevent KEYCODE_APP_SWITCH"

        # command for get memory information from device
        self.proc_meminfo = "adb -s " + self.id + " shell cat /proc/meminfo"
        self.meminfo_extra = "adb -s " + self.id + " shell cat /proc/meminfo_extra"
        self.dumpsys_meminfo = "adb -s " + self.id + " shell dumpsys meminfo"

        # command for get full time information
        self.logcat_log = "adb -s " + self.id + " logcat"
        self.event_log = "adb -s " + self.id + " logcat -b events -v time"

        # command for get bugreport log
        self.bugreport = "adb -s " + self.id + " bugreport"

        # physical display resolution of device
        # example 1080 * 1920
        self.display_size = {"x": 0, "y": 0}

        # home screen ui information
        self.ui_info = {}

    def press_home(self):
        os.popen(self.home)

    def press_recent_app(self):
        os.popen(self.recent_app)

    def reboot(self):
        os.popen("adb -s {id} reboot".format(id=self.id))
        print("reboot {id}({model}) device.".format(id=self.id, model=self.model))

    def set_resolution(self):
        cmd = "adb -s " + self.id + " shell dumpsys window displays | findstr cur="
        ret = os.popen(cmd).read().splitlines()[0]
        self.display_size["x"] = int(ret.split("cur=")[1].split()[0].split("x")[0])
        self.display_size["y"] = int(ret.split("cur=")[1].split()[0].split("x")[1])

    def swipe(self, dir_: str):
        if self.display_size["x"] == 0 or self.display_size["y"] == 0:
            self.set_resolution()
        x = self.display_size["x"]
        y = self.display_size["y"]

        position = {
            "left": {
                "from_x": str(x * 0.2),
                "from_y": str(y * 0.5),
                "to_x": str(x * 0.8),
                "to_y": str(y * 0.5)
            },
            "right": {
                "from_x": str(x * 0.8),
                "from_y": str(y * 0.5),
                "to_x": str(x * 0.2),
                "to_y": str(y * 0.5)
            },
            "up": {
                "from_x": str(x * 0.5),
                "from_y": str(y * 0.2),
                "to_x": str(x * 0.5),
                "to_y": str(y * 0.8)
            },
            "down": {
                "from_x": str(x * 0.5),
                "from_y": str(y * 0.8),
                "to_x": str(x * 0.5),
                "to_y": str(y * 0.2)
            }
        }
        cmd = "adb -s " + self.id + " shell input swipe " + \
              position[dir_]["from_x"] + " " + position[dir_]["from_y"] + " " + \
              position[dir_]["to_x"] + " " + position[dir_]["to_y"]
        os.popen(cmd)

    def get_uidump(self) -> str:
        cmd = "adb -s " + self.id + " shell uiautomator dump"
        while True:
            ret = os.popen(cmd).read().splitlines()[0]
            if "UI hierchary dumped to:" in ret:
                path = ret.split("UI hierchary dumped to:")[-1].strip()
                return path

    def read_uidump(self) -> str:
        path = self.get_uidump()
        cmd = "adb -s " + self.id + " pull " + path

        """
         # dump = os.popen(cmd).read()
         # UnicodeDecodeError: 'cp949' codec can't decode byte 0x9c in position 9089: illegal multibyte sequence
         # occurred above error, so can not read directly with os.popen().read()
        """
        os.system(cmd)
        file = open("window_dump.xml", "r", encoding="UTF-8")
        xml = file.readlines()
        file.close()
        return xml[0]

    def compute_uidump(self) -> dict:
        self.ui_info = uiautomator.compute_xml(self.read_uidump())
        return self.ui_info

    def unlock(self):
        self.swipe("left")
        time.sleep(2)
        os.popen(self.home)

    def get_uptime(self) -> int:
        cmd = "adb -s " + self.id + " shell uptime"
        ret = os.popen(cmd).read().splitlines()[0]
        uptime = int(ret.split(" min")[0].split()[-1])
        return uptime

    def screen_capture(self):
        os.system(f"adb -s {self.id} shell screencap -p /sdcard/temp.png")
        time.sleep(1)
        os.system(f"adb -s {self.id} pull /sdcard/temp.png")
