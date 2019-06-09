from sense_hat import SenseHat
import time
import datetime
import pymysql

connection = pymysql.connect(host='localhost', port=3306,
                             user='XYZ', password='XYZ',
                             autocommit=True)

cursor = connection.cursor()

sense = SenseHat()
sense.clear()

try:
    while True:
        print("%c[?25l" % (27))
        print("%c[%d;%dH" % (27,1,1), end='') # ^[1,1H
        print("%-60s" % (' '))
        
        t = round(sense.get_temperature(), 1)
        p = round(sense.get_pressure(), 1)
        h = round(sense.get_humidity(), 1)
        
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        clock = datetime.datetime.now().strftime("%H:%M:%S")
        
        mod = "%20s %5s %-4s"
        
        upload = ('INSERT INTO weather_data (date, time, temperature, pressure, humidity)'
                 'VALUES (\'%s\', \'%s\', %s, %s, %s);' % (date, clock, t, p, h))
        
        print("Last updated:", date, clock, "\n")
        print(mod % ("Temperature:", t, "°C"))
        print(mod % ("Pressure:", p, "mbar"))
        print(mod % ("Humidity:", h, "%"))
        
        try:
            cursor.execute("USE weather_station")
            cursor.execute(upload)
            print("\n%-60s" % ("The weather data was successfully sent to the database."))
        
        except:
            print("\n%-60s" % ("Data insertion failed."))

        time.sleep(600)
        
except KeyboardInterrupt:
    print("%c[?25h" % (27))
    pass
