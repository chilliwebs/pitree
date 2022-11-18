import threading, queue, time, random, os, subprocess, math
from rpi_ws281x import Color, PixelStrip, ws
from flask import Flask, request, current_app
import compiler

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
RGBYAV = [[Color(255, 0, 0)], [Color(255, 255, 0)], [Color(0, 255, 0)], [Color(0, 255, 255)], [Color(0, 0, 255)], [Color(255, 0, 255)]]

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
PALATE = WARM_WHITE
SPEED = 1
FPS = 1/15
EXPR = False

allowed_globals = {"__builtins__": {}, "t": 0, "s": 0, "l": 0, "c": 0, "sin": math.sin}
allowed_locals = {"range": range}

def build_expr(x_expr, y_expr):
    global EXPR
    EXPR = False
    expr_str = "[[(%s), (%s)] for i in range(c)]" % (x_expr, y_expr)
    EXPR = compile(expr_str, '<string>', 'eval')
    for name in EXPR.co_names:
        if name not in allowed_globals and name not in allowed_locals:
            raise NameError(f"Use of {name} not allowed")

def eval_expr(t, s, l, c):
    global EXPR
    if EXPR:
        allowed_globals["t"] = t
        allowed_globals["s"] = s
        allowed_globals["l"] = l
        allowed_globals["c"] = c
        return eval(EXPR, allowed_globals, allowed_locals)
    else:
        return [[0,0] for i in range(LED_COUNT)]

def tree():
    global run
    while run:
        # global mode
        global AVG_SLEEP
        global PALATE
        global SPEED

        current_palate = PALATE

        t = time.time() # time
        s = SPEED
        l = len(current_palate)
        c = LED_COUNT
        f = eval_expr(t, s, l, c)

        for i in range(LED_COUNT):
            if f[i][0] < 0 or f[i][1] < 0:
                strip.setPixelColor(i, Color(0, 0, 0))
            else:
                strip.setPixelColor(i, current_palate[int(f[i][0])%l][int(f[i][1])%l])
        
        strip.show()
        fps = FPS #(1/SPEED) if SPEED < (1/FPS) else FPS
        slp = max(min(fps-(time.time()-t), 0.25), 0)
        AVG_SLEEP = (AVG_SLEEP + slp)/2.0
        time.sleep(slp)

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

            

def worker():
    global run
    while run:
        try:
            global PALATE
            global SPEED
            item = q.get(True, 1)
            if item == 0:
                PALATE = WARM_WHITE
            if item == 1:
                PALATE = BRIGHT_WHITE
            if item == 2:
                PALATE = RANDOM
            if item == 3:
                PALATE = RGBYAV
            if item == 4:
                PALATE = RAINBOW


            # https://www.desmos.com/calculator
            if item == 50: # Solid
                x_expr = "i * 0"
                y_expr = "i * 0"
                build_expr(x_expr, y_expr)
            if item == 51: # Cycle
                x_expr = "(t * s)"
                y_expr = "i * 0"
                build_expr(x_expr, y_expr)
            if item == 52: # crawl
                x_expr = "i + (t * s)"
                y_expr = "i * 0"
                build_expr(x_expr, y_expr)
            if item == 53: # Ungulate 
                x_expr = "(i if i % 2 == 0 else -2*i) + (t * s)"
                y_expr = "i * 0"
                build_expr(x_expr, y_expr)
            if item == 54: # wipe
                x_expr = "(i + (t * s)) / c"
                y_expr = "i * 0"
                build_expr(x_expr, y_expr)
            
            if item == 55: # fanfare
                x_expr = "(i + (t * s * l)) / c"
                y_expr = "sin((2*i) - (t * s))"
                build_expr(x_expr, y_expr)
            if item == 56: # chase
                x_expr = "(i + (t * s * l * 2)) / c"
                y_expr = "2 * sin((i/2) + (t * s)) - 1"
                build_expr(x_expr, y_expr)
            if item == 57: # race
                x_expr = "(i + (t * s * l * 4)) / c"
                y_expr = "25 * sin((i/4) + (t * s)) - 24"
                build_expr(x_expr, y_expr)
            if item == 58: # race
                x_expr = "(i + (t * s * l * 6)) / c"
                y_expr = "200 * sin((i/20) + (t * s)) - 199"
                build_expr(x_expr, y_expr)


            if item == 100: # 1/4
                SPEED = 0.25
            if item == 101: # 1/2
                SPEED = 0.5
            if item == 102: # 1
                SPEED = 1
            if item == 103: # 1
                SPEED = 2
            if item == 104: # 1
                SPEED = 4
            if item == 105: # 1
                SPEED = 8
            if item == 106: # 30
                SPEED = 30
            if item == 107: # 60
                SPEED = 60
            if item == 108: # 120
                SPEED = 120
            if item == 109: # 240
                SPEED = 240
            if item == 110: # 750
                SPEED = 750
            if item == 111: # 2x
                SPEED = 750*2
            if item == 112: # 4x
                SPEED = 750*4

            q.task_done()
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
    q.put(50)
    q.put(100)
    app.run(host='0.0.0.0', port=8811)
