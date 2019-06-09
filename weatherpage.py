from flask import Flask, render_template, send_file, make_response, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import pymysql

app = Flask(__name__)

connection = pymysql.connect(host='localhost', user='XYZ',
                             passwd='XYZ', database='XYZ',
                             autocommit=True)

cursor = connection.cursor()

def getData():
    cursor.execute("""SELECT date, time, temperature, humidity, pressure
                   FROM weather_data ORDER BY id DESC LIMIT 1;""")
    result = cursor.fetchall()
    
    for row in result:
        return row

def getHistory(numSamples):
    cursor.execute("""SELECT date, time, temperature, humidity, pressure
                   FROM weather_data ORDER BY id DESC LIMIT """+str(numSamples))
    data = cursor.fetchall()
    dates = []
    times = []
    temps = []
    hums = []
    press = []

    for row in reversed(data):
        dates.append(row[0])
        times.append(row[1])
        temps.append(row[2])
        hums.append(row[3])
        press.append(row[4])
    return dates, times, temps, hums, press

def maxRows():
    cursor.execute("SELECT COUNT(temperature) FROM weather_data")
    result = cursor.fetchall()
    for row in result:
        maxNumberRows = row[0]
    return maxNumberRows

global numSamples
numSamples = maxRows()
if (numSamples > 101):
    numSamples = 100
    
@app.route("/")
def home():
    row = getData()
    return render_template('index.html', date=row[0], time=row[1],
                           temperature=row[2], humidity=row[3], pressure=row[4])

@app.route("/", methods=['POST'])
def my_form_post():
    global numSamples
    numSamples = int(request.form['numSamples'])
    numMaxSamples = maxRows()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples - 1)
    row = getData()
    return render_template('index.html', date=row[0], time=row[1], temperature=row[2],
                           humidity=row[3], pressure=row[4], numSamples=numSamples)

def plot(kat, axis_title):
    dates, times, temps, hums, press = getHistory(numSamples)
    if kat == "temp":
        ys = temps
    elif kat == "hum":
        ys = hums
    else:
        ys = press
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    axis.set_title(axis_title)
    axis.set_xlabel("Samples")
    axis.grid(True)
    xs = range(numSamples)
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/temp')
def plot_temp():
    return plot("temp", "Temperature [C]")

@app.route('/plot/hum')
def plot_hum():
    return plot("hum", "Humidity [%]")

@app.route('/plot/press')
def plot_press():
    return plot("press", "Pressure [mbar]")

if __name__ == "__main__":
    app.run()