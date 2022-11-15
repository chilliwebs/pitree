import threading, queue, time, random, os, subprocess
from rpi_ws281x import Color, PixelStrip, ws
from flask import Flask, request, current_app

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
    

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def tree():
    global run
    while run:
        global mode
        if mode == 0:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(255, 175, 75))

            strip.show()
            time.sleep(1)

        if mode == 1:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(255, 255, 255))

            strip.show()
            time.sleep(1)
            
        if mode == 2:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(random.randint(0,255), random.randint(0,255), random.randint(0,255)))

            strip.show()
            time.sleep(1)

        if mode == 3:
            colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255), Color(255, 255, 0), Color(0, 255, 255), Color(255, 0, 255)]
            for c in colors:
                if mode != 3:
                        break
                for n in range(int(strip.numPixels()/4)):
                    if mode != 3:
                        break
                    strip.setPixelColor(n*4, c)
                    strip.setPixelColor((n*4)+1, c)
                    strip.setPixelColor((n*4)+2, c)
                    strip.setPixelColor((n*4)+3, c)

                    time.sleep(0.1)
                    strip.show()

        if mode == 4:
            colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255), Color(255, 255, 0), Color(0, 255, 255), Color(255, 0, 255)]
            for c in colors:
                if mode != 4:
                        break
                for r in range(11):
                    if mode != 4:
                            break
                    for n in range(int(strip.numPixels()/3)):
                        if mode != 4:
                            break
                        if (r % 3) == 0:
                            strip.setPixelColor(n*3, c)
                            strip.setPixelColor((n*3)+1, Color(0, 0, 0))
                            strip.setPixelColor((n*3)+2, Color(0, 0, 0))
                        if (r % 3) == 1:
                            strip.setPixelColor(n*3, Color(0, 0, 0))
                            strip.setPixelColor((n*3)+1, c)
                            strip.setPixelColor((n*3)+2, Color(0, 0, 0))
                        if (r % 3) == 2:
                            strip.setPixelColor(n*3, Color(0, 0, 0))
                            strip.setPixelColor((n*3)+1, Color(0, 0, 0))
                            strip.setPixelColor((n*3)+2, c)

                    time.sleep(0.1)
                    strip.show()
        
        if mode == 5:
            colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255), Color(255, 255, 0), Color(0, 255, 255), Color(255, 0, 255)]
            for c in colors:
                if mode != 5:
                    break
                for i in range(int(strip.numPixels()/4)):
                    if mode != 5:
                        break
                    strip.setPixelColor((i*4), Color(0, 0, 0))
                    strip.setPixelColor((i*4)+1, Color(0, 0, 0))
                    strip.setPixelColor((i*4)+2, Color(0, 0, 0))
                    strip.setPixelColor((i*4)+3, Color(0, 0, 0))

                    strip.setPixelColor(((i+1)*4), c)
                    strip.setPixelColor(((i+1)*4)+1, c)
                    strip.setPixelColor(((i+1)*4)+2, c)
                    strip.setPixelColor(((i+1)*4)+3, c)

                    time.sleep(0.1)
                    strip.show()

        if mode == 6:
            for j in range(0, 255, 5):
                if mode != 6:
                        break
                for i in range(strip.numPixels()):
                    if mode != 6:
                        break
                    pixel_index = (i * 256 // strip.numPixels()) + j*4
                    r, g, b = wheel(pixel_index & 255)
                    strip.setPixelColor(i, Color(r, g, b) )
                
                time.sleep(0.1)
                strip.show()

        if mode == 7:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(random.randint(0,255), random.randint(0,255), random.randint(0,255)))

            time.sleep(0.1)
            strip.show()

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
def index():
    return current_app.send_static_file('index.html')

@app.route("/update.png")
def update_img():
    return current_app.send_static_file('update.png')

@app.route("/ver")
def ver():
    return '0.0.28'

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
