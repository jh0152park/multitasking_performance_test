# xml file read doc
# https://docs.python.org/ko/3/library/xml.etree.elementtree.html

"""
index="0" text="SoundCloud" resource-id="com.sec.android.app.launcher:id/home_icon" class="android.widget.TextView"
package="com.sec.android.app.launcher" content-desc="SoundCloud" checkable="false" checked="false" clickable="true"
enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="true" password="false"
selected="false" bounds="[40,181][281,553]" />
"""


def get_name(line):
    try:
        return line.split('content-desc="')[-1].split('"')[0]
    except Exception as err:
        print("occurred error from get_name of uiautomator.py : {}".format(err))
        return "None"


def get_position(line):
    try:
        bounds = line.split("bounds=")[-1].split()[0][2:-3].replace("][", ",").split(",")
        x = int((int(bounds[0]) + int(bounds[2])) * 0.5)
        y = int((int(bounds[1]) + int(bounds[3])) * 0.5)
        return str(x) + "," + str(y)
    except Exception as err:
        print("occurred error from get_position of uiautomator.py : {}".format(err))
        return "0,0"


def read_xml(file) -> dict:
    apps = {}
    for line in file.split("<node"):
        if 'focusable="true"' in line:
            name = get_name(line)
            position = get_position(line)
            if name not in apps.keys():
                apps[name] = ""
            apps[name] = position
    return apps


def compute_xml(file):
    return read_xml(file)
