import csv
import sqlite3

class Database:
    
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cur = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS BikeShare ("
                         "TripDuration INT,"
                         "StartTime DATE,"
                         "StopTime DATE,"
                         "StartStationID INT,"
                         "StartStationName TEXT,"
                         "StartStationLatitude FLOAT,"
                         "StartStationLongitude FLOAT,"
                         "EndStationID INT,"
                         "EndStationName TEXT,"
                         "EndStationLatitude FLOAT,"
                         "EndStationLongitude FLOAT,"
                         "BikeID INT,"
                         "UserType TEXT,"
                         "BirthYear INT,"
                         "Gender INT,"
                         "TripDurationinmin INT)")
        self.conn.commit()
        shape = self.shape()[0] != 0
        if not shape:
            self.insert_values()

    def shape(self):
        return self.cur.execute("select count(*) from BikeShare").fetchone()

    def insert_values(self):
        with open('assets/BikeShare.csv', 'r') as f:
            reader = csv.reader(f)
            data = next(reader)
            query = 'INSERT into BikeShare({0}) values ({1})'
            query = query.format(','.join(data), ','.join('?' * len(data)))
            for data in reader:
                self.cur.execute(query, data)
            self.conn.commit()

    def getRecommendations(self, currentLocation, spendTime, numRecommendations):
        res = self.cur.execute("select * from BikeShare "
                               "where StartStationName like '" + currentLocation +
                               "' and TripDurationinmin <= " + str(spendTime)).fetchall()
        return 'start Ranking function', res


    
def validation(userStart, userTime, userAmount):
    if userStart == "" or userStart == None:
        return "Start location is mandatory."
    if userTime == "" or userTime == None:
        return "Time Range is mandatory."
    if userAmount == "" or userAmount == None:
        return "Results size is mandatory."
    try:
        userTime = int(userTime)
    except ValueError:
        return "Only numbers acceptable for riding time." 
    try:
        userAmount = int(userAmount)
    except ValueError:
        return "Only numbers acceptable for results size."        
    if(userTime < 1):
        return "Negative riding time."
    if (userAmount < 1):
        return "Negative results size."
    return True
