import threading, queue, time, random, os, subprocess
from rpi_ws281x import Color, PixelStrip, ws
from flask import Flask, request, current_app
#import sympy as sp
#import numpy as np

# LED strip configuration:
LED_COUNT = 750        # Number of LED pixels.
LED_PIN = 12          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.WS2811_STRIP_RGB

q = queue.Queue()
app = Flask(__name__)
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()
mode = 0
run = True
needsupdate = False

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)

# Color Palates
BRIGHT_WHITE = [[Color(255, 255, 255)]]
WARM_WHITE = [[Color(255, 175, 75)]]
RGBYAV = [[Color(255, 0, 0)], [Color(0, 255, 0)], [Color(0, 0, 255)], [Color(255, 255, 0)], [Color(0, 255, 255)], [Color(255, 0, 255)]]

RANDOM = [[Color(0, 0, 0)]] * LED_COUNT
for i in range(0, LED_COUNT):
    RANDOM[i] = [Color(random.randint(0,255), random.randint(0,255), random.randint(0,255))]

RAINBOW = [[Color(0, 0, 0)]] * LED_COUNT
for j in range(0, 255, 1):
    for i in range(LED_COUNT):
        pixel_index = (i * 256 // LED_COUNT) + j * 4
        r, g, b = wheel(pixel_index & 255)
        RAINBOW[i] = [Color(r, g, b)]

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

# led buffer
BUFF = [Color(0, 0, 0)] * LED_COUNT

AVG_SLEEP = 0.0
PALATE = RGBYAV
SPEED = 1 #120

def tree():
    global run
    while run:
        # global mode
        global AVG_SLEEP
        global PALATE
        global SPEED

        t = time.time() # time
        y = 0           # y
        s = SPEED       # speed
        l = len(PALATE) # length
        for x in range(LED_COUNT):
            BUFF[x] = PALATE[int((x + (t * s)) % l) % l][y]

        for i in range(LED_COUNT):
            strip.setPixelColor(i, BUFF[i])
        
        strip.show()
        slp = max(0.05-(time.time()-t), 0)
        AVG_SLEEP = (AVG_SLEEP + slp)/2.0
        time.sleep(slp)

        # # Warm White
        # if mode == 0:
        #     for i in range(strip.numPixels()):
        #         strip.setPixelColor(i, WARM_WHITE[i%1])

        #     strip.show()
        #     time.sleep(1)

        # # Bright White
        # if mode == 1:
        #     for i in range(strip.numPixels()):
        #         strip.setPixelColor(i, BRIGHT_WHITE[i%1])

        #     strip.show()
        #     time.sleep(1)

        # # Random
        # if mode == 2:
        #     for i in range(strip.numPixels()):
        #         strip.setPixelColor(i, RANDOM[random.randint(0,strip.numPixels()-1)])

        #     strip.show()
        #     time.sleep(1)

        # # Wipe
        # if mode == 3:
        #     width = 15
        #     for c in RGBYAV:
        #         if mode != 3:
        #             break
        #         for n in range(int(strip.numPixels()/width)+1):
        #             if mode != 3:
        #                 break
        #             for i in range(0,width):
        #                 if ((n*width)+i) < strip.numPixels():
        #                     strip.setPixelColor((n*width)+i, c)

        #             strip.show()
        #             time.sleep(0.05)

        # # Fanfare
        # if mode == 4:
        #     for c in RGBYAV:
        #         if mode != 4:
        #                 break
        #         for r in range(11):
        #             if mode != 4:
        #                     break
        #             for n in range(int(strip.numPixels()/3)):
        #                 if mode != 4:
        #                     break
        #                 if (r % 3) == 0:
        #                     strip.setPixelColor(n*3, c)
        #                     strip.setPixelColor((n*3)+1, Color(0, 0, 0))
        #                     strip.setPixelColor((n*3)+2, Color(0, 0, 0))
        #                 if (r % 3) == 1:
        #                     strip.setPixelColor(n*3, Color(0, 0, 0))
        #                     strip.setPixelColor((n*3)+1, c)
        #                     strip.setPixelColor((n*3)+2, Color(0, 0, 0))
        #                 if (r % 3) == 2:
        #                     strip.setPixelColor(n*3, Color(0, 0, 0))
        #                     strip.setPixelColor((n*3)+1, Color(0, 0, 0))
        #                     strip.setPixelColor((n*3)+2, c)

        #             strip.show()
        #             time.sleep(0.05)

        # # Chase
        # if mode == 5:
        #     for c in RGBYAV:
        #         if mode != 5:
        #             break
        #         for i in range(int(strip.numPixels()/4)):
        #             if mode != 5:
        #                 break
        #             strip.setPixelColor((i*4), Color(0, 0, 0))
        #             strip.setPixelColor((i*4)+1, Color(0, 0, 0))
        #             strip.setPixelColor((i*4)+2, Color(0, 0, 0))
        #             strip.setPixelColor((i*4)+3, Color(0, 0, 0))

        #             strip.setPixelColor(((i+1)*4), c)
        #             strip.setPixelColor(((i+1)*4)+1, c)
        #             strip.setPixelColor(((i+1)*4)+2, c)
        #             strip.setPixelColor(((i+1)*4)+3, c)

        #             strip.show()
        #             time.sleep(0.05)

        # # Rainbow
        # if mode == 6:
        #     for j in range(0, strip.numPixels(), 10):
        #         if mode != 6:
        #             break
        #         for i in range(strip.numPixels()):
        #             strip.setPixelColor(i, RAINBOW[(i+j)%strip.numPixels()] )

        #         strip.show()
        #         time.sleep(0.05)

        # # Fast Random
        # if mode == 7:
        #     for i in range(strip.numPixels()):
        #         strip.setPixelColor(i, RANDOM[random.randint(0,strip.numPixels()-1)])

        #    strip.show()
        #    time.sleep(0.05)
            

def worker():
    global run
    while run:
        try:
            global PALATE
            # global mode
            item = q.get(True, 1)
            # mode = item
            q.task_done()

            if mode == 0:
                PALATE = WARM_WHITE
            if mode == 1:
                PALATE = WARM_WHITE
            if mode == 2:
                PALATE = RANDOM
            if mode == 6:
                PALATE = RAINBOW
        except queue.Empty:
            continue # nothing

@app.route("/")
def index():
    return current_app.send_static_file('index.html')

@app.route("/update.png")
def update_img():
    return current_app.send_static_file('update.png')

@app.route("/bg.jpg")
def bg_img():
    return current_app.send_static_file('bg.jpg')

@app.route("/ver")
def ver():
    return '0.0.30'

@app.route("/AVG_SLEEP")
def avg_slp():
    global AVG_SLEEP
    return str(AVG_SLEEP)

@app.route("/hasupdate")
def hasupdate():
    global needsupdate
    if not needsupdate:
        localvers = subprocess.check_output('git -C /home/pi/pitree rev-parse --verify HEAD', shell=True, stderr=subprocess.STDOUT)
        remote = subprocess.check_output('git -C /home/pi/pitree ls-remote -q | grep HEAD | cut -c1-40', shell=True, stderr=subprocess.STDOUT)
        needsupdate = localvers != remote
    return str(needsupdate)

@app.route("/update")
def update():
    global run
    os.system("git -C /home/pi/pitree pull")
    run = False
    shutdown_server()
    return "RESTARTING"

@app.route("/mode")
def setMode():
    no = request.args.get('no', default = None, type = int)
    if no != None:
        q.put(no)
    return "OK"

if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=tree, daemon=True).start()
    q.put(0)
    app.run(host='0.0.0.0', port=8811)
