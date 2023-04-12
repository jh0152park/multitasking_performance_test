import os
import signal
import time
import string
import subprocess
import compare
import scenario
from adb import ADB
from device import Device


def get_cur_time():
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))


# result log files list
event_logs = []
logcat_logs = []
proc_meminfo_logs = []
dumpsys_meminfo_logs = []

# get connected device information
adb = ADB()
device_ids = adb.get_device_ids()
model_names = adb.get_model_names()
product_names = adb.get_product_names()

# make result folder
HOME = os.getcwd()
RESULT_FOLDER = get_cur_time()
if RESULT_FOLDER not in os.listdir(os.getcwd()):
    os.mkdir(RESULT_FOLDER)
os.chdir(RESULT_FOLDER)

# main home screen check
models = []
for i in range(len(device_ids)):
    models.append(Device(device_ids[i], model_names[i], product_names[i]))
    models[-1].press_home()
    time.sleep(1)
    models[-1].compute_uidump()

# compute the position of every test application
for model in models:
    for app in scenario.SCENARIO:
        if app not in model.ui_info.keys():
            print("{app} not ready for test {id}/{product},please check it again...".format(app=app,
                                                                                            id=model.id,
                                                                                            product=model.product))
        else:
            print("{} is ready.".format(app))

# create result log files
for model in models:
    logcat_logs.append(
        open(model.id + "_" + model.product + "_full_time_logcat.txt", "a"))
    event_logs.append(
        open(model.id + "_" + model.product + "_full_time_eventlog.txt", "a"))
    proc_meminfo_logs.append(
        open(model.id + "_" + model.product + "_full_time_proc_meminfo.txt", "a"))
    dumpsys_meminfo_logs.append(
        open(model.id + "_" + model.product + "_full_time_dumpsys_meminfo.txt", "a"))

# start gathering full time logcat / event logs
logcat_pars = []
event_log_pars = []
for i in range(len(models)):
    model = models[i]
    logcat_pars.append(subprocess.Popen(model.logcat_log, stdout=logcat_logs[i], shell=False))
    event_log_pars.append(subprocess.Popen(model.event_log, stdout=event_logs[i], shell=False))

# test start!
sequence = 1
scenarios = scenario.SCENARIO * 5
videos = []
for app in scenarios:
    print("\nrun : {} [{}/{}] ".format(app, sequence, len(scenarios)))
    app_ = app.translate(str.maketrans("", "", string.punctuation)).replace(" ", "_")
    record_cmd = f"adb shell screenrecord --size 1440x2960 /sdcard/{sequence}_{app_}.mp4"
    videos.append(f"/sdcard/{sequence}_{app_}.mp4")
    record = subprocess.Popen(record_cmd, stdout=subprocess.PIPE, shell=False)
    time.sleep(1)

    for model in models:
        position = model.ui_info[app]
        x = position.split(",")[0]
        y = position.split(",")[1]
        cmd = "adb -s " + model.id + " shell input tap " + x + " " + y
        os.popen(cmd)
    time.sleep(1)

    while True:
        origin = HOME + f"\\images\\{app}.jpg"
        models[0].screen_capture()
        current = os.getcwd() + "\\temp.png"
        similarity = round(compare.compare(origin, current))
        th = 70.0 if app == "Etsy" else 85.0
        if similarity >= th:
            break

    cur_time = get_cur_time()
    for i in range(len(models)):
        model = models[i]
        proc_meminfo = os.popen(model.proc_meminfo).read()
        # meminfo_extra = os.popen(model.meminfo_extra).read()
        dumpsys_meminfo = os.popen(model.dumpsys_meminfo).read()

        proc_meminfo_logs[i].write("{time}\nrun this app : {app}\n\n{log1}\n{log2}\n\n".format(
            time=cur_time, app=app, log1=proc_meminfo, log2=""))
        dumpsys_meminfo_logs[i].write("{time}\nrun this app : {app}\n\n{log}\n\n".format(
            time=cur_time, app=app, log=dumpsys_meminfo))
        proc_meminfo_logs[i].flush()
        dumpsys_meminfo_logs[i].flush()

    record.send_signal(signal.SIGTERM)
    for model in models:
        model.press_home()
    time.sleep(3)
    sequence += 1

print("Test Done...!")
# close result log files
for i in range(len(models)):
    logcat_pars[i].terminate()
    event_log_pars[i].terminate()
    proc_meminfo_logs[i].close()
    dumpsys_meminfo_logs[i].close()

print("Start pulling bugreport log file.")
bugreports = []
for model in models:
    bugreports.append(subprocess.Popen(model.bugreport))

while True:
    done = 0
    for proc in bugreports:
        if proc.poll() is None:
            pass
            # still pulling bugreport log file
        else:
            done += 1
            if done == len(bugreports):
                print("pulled all bugreport log...!")

                os.system("mkdir videos")
                os.chdir("videos")
                for video in videos:
                    os.system("adb pull " + video)
                os.system("adb kill-server")
                os.system("adb start-server")
                exit(0)
