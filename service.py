import threading, queue, time, random, os
from rpi_ws281x import Color, PixelStrip, ws
from flask import Flask

# LED strip configuration:
LED_COUNT = 500        # Number of LED pixels.
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

def tree():
    global run
    while run:
        global mode
        for i in range(strip.numPixels()):
            if mode == 0:
                strip.setPixelColor(i, Color(255, 175, 75))
            if mode == 1:
                strip.setPixelColor(i, Color(255, 255, 255))
            if mode == 2:
                strip.setPixelColor(i, Color(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        strip.show()
        time.sleep(1)

def worker():
    global run
    while run:
        try:
            global mode
            item = q.get(True, 1)
            print(f'recived on {item}')
            mode = item
            print(f'completed {item}')
            q.task_done()
        except queue.Empty:
            continue # nothing

@app.route("/")
def root():
    q.put(1)
    return "OK"

@app.route("/update")
def update():
    global run
    os.system("git pull")
    run = False
    raise RuntimeError('Stopping Server')
    return "OK"

@app.route("/0")
def one():
    q.put(0)
    return "OK"

@app.route("/2")
def two():
    q.put(2)
    return "OK"

if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=tree, daemon=True).start()
    q.put(0)
    app.run(host='0.0.0.0', port=8811)
