var updateIntervalTime = 0;
var colorIncrement = 0;
var colors = {};

function updateColors() {
    const sortedColors = new Array(...Object.entries(colors).sort((a, b) => a[1].pos - b[1].pos));
    if (sortedColors.length == 1) {
        sortedColors.push(sortedColors[0]);
    }

    console.log(sortedColors);

    var cssGradient = "linear-gradient(to right, ";
    cssGradient += sortedColors.map((c) => c[1].color + " " + Math.floor(c[1].pos / 8) + "%").join(", ")
    cssGradient += ");";

    console.log(cssGradient);

    document.getElementById('colorbar').setAttribute("style", "background: " + cssGradient)
}

function checkUpdates() {
    fetch('/hasupdate').then((g) => g.text()).then((v) => {
        if (v === "True") {
            document.getElementById('update').style.display = 'inline';
            clearInterval(window.updateInterval);
        } else {
            updateIntervalTime = Math.min(updateIntervalTime + 5000, 30000);
            // setTimeout(() => {
            //     checkUpdates();
            // }, updateIntervalTime);
        }
    });
}

window.onload = async function () {
    document.getElementById('update').onclick = function () {
        fetch('/update').then((resp) => {
            setTimeout(() => {
                window.location.reload();
            }, 20000);
        });
    }

    for (var btn of document.getElementsByClassName('mode')) {
        (function (b) {
            b.addEventListener('click', function (event) {
                fetch('/mode?no=' + b.id.replace('mode', ''));
            }, false);
        })(btn);
    }

    document.getElementById('addColor').addEventListener('click', function (event) {
        var controll = document.createElement('div');
        controll.setAttribute('id', 'colorControll' + colorIncrement);

        var slider = document.createElement('input');
        slider.setAttribute('type', 'range');
        slider.setAttribute('min', '0');
        slider.setAttribute('max', '800');
        slider.setAttribute('value', '0');
        slider.setAttribute('class', 'positionSlider');
        slider.setAttribute('id', 'positionSlider' + colorIncrement);
        controll.append(slider);

        var colorchooser = document.createElement('input');
        colorchooser.setAttribute('type', 'color');
        colorchooser.setAttribute('value', '#ff0000');
        colorchooser.setAttribute('class', 'colorChooser');
        colorchooser.setAttribute('id', 'colorChooser' + colorIncrement);
        controll.append(colorchooser);

        document.getElementById('colorControlls').append(controll);

        var indicator = document.createElement('div');
        indicator.setAttribute('id', 'posIndicator' + colorIncrement);
        indicator.setAttribute('class', 'posIndicator');
        document.getElementById('colorbar').append(indicator);

        (function (n) {
            slider.addEventListener('change', function (event) {
                indicator.style.left = (event.target.value - 10) + 'px';
                colors[n].pos = event.target.value;
                updateColors();
            }, false);
        })(colorIncrement);

        (function (n) {
            colorchooser.addEventListener('change', function (event) {
                indicator.style.background = event.target.value;
                colors[n].color = event.target.value;
                updateColors();
            }, false);
        })(colorIncrement);

        colors[colorIncrement] = { "color": "#ff0000", "pos": 0 };

        colorIncrement++;
    });

    // <div id="colorControll0"></div>

    // document.getElementById('positionSlider0').addEventListener('change', function (event) {
    //     document.getElementById('posIndicator0').style.left = (event.target.value-10)+'px';
    // }, false);

    fetch('/ver').then(async (ver) => {
        var version = await ver.text();
        document.getElementById('ver').innerText = version;
        document.title = "PiTree v" + version;
    });

    checkUpdates();
}