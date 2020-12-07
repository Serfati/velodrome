import math
import pickle
import csv
import sqlite3
import pandas as pd

from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


class Database:

    def __init__(self):
        import os
        files = os.listdir("./")
        if "database.db" in files:
            self.conn = sqlite3.connect("database.db")
            self.cur = self.conn.cursor()
            if not self.shape()[0]:
                self.insert_values()
        else:
            data = pd.read_csv("BikeShare.csv")
            self.conn = sqlite3.connect("database.db")
            data.to_sql("BikeShare", self.conn, if_exists="replace")
            self.cur = self.conn.cursor()
            # self.cur.execute("CREATE TABLE IF NOT EXISTS BikeShare ("
            #             "TripDuration INT,"
            #             "StartTime DATE,"
            #             "StopTime DATE,"
            #             "StartStationID INT,"
            #             "StartStationName TEXT,"
            #             "StartStationLatitude FLOAT,"
            #             "StartStationLongitude FLOAT,"
            #             "EndStationID INT,"
            #             "EndStationName TEXT,"
            #             "EndStationLatitude FLOAT,"
            #             "EndStationLongitude FLOAT,"
            #             "BikeID INT,"
            #             "UserType TEXT,"
            #             "BirthYear INT,"
            #             "Gender INT,"
            #             "TripDurationinmin INT)")

    def shape(self):
        return self.cur.execute("SELECT count(*) FROM BikeShare").fetchone()

    def insert_values(self):
        with open('BikeShare.csv', 'r') as f:
            reader = csv.reader(f)
            data = next(reader)
            query = 'INSERT into BikeShare({0}) VALUES ({1})'
            query = query.format(','.join(data), ','.join('?' * len(data)))
            for data in reader:
                self.cur.execute(query, data)
            self.conn.commit()

    def get_recommendations(self, loc, time, k):
        raw = self.cur.execute("SELECT * FROM BikeShare "
                               "WHERE StartStationName like '" + loc +
                               "' AND TripDurationinmin <= " + str(time)).fetchall()

        return self.ranker(raw, loc, time)[:k]

    def score(self, item, pred, distance_weight=0.3, time_weight=0.3, day_light_weight=0.4):
        # score distance by euclidean distance (with min distance of 1 km)
        distance = math.sqrt(
            (item[6] - item[10]) ** 2 + (item[7] - item[10]) ** 2)/1000  # convert to km
        distance = distance if distance > 1 else 1
        distance_score = 1/(1 + distance)
        # score to starting time by its distance from current time
        t1 = datetime.now().strftime("%H:%M")
        t2 = item[2].split(sep=" ")[1]
        diff_minutes = datetime.strptime(
            t1, '%H:%M') - datetime.strptime(t2, '%H:%M')
        hours_from_now = diff_minutes.seconds / 60 / 60
        time_from_start_score = 1/hours_from_now if hours_from_now > 1 else 1
        # score the starting time by daylight
        is_daytime = 1 if datetime.strptime(
            t2, '%H:%M') < datetime.strptime('18:00', '%H:%M') else 0.5
        # weighted score sum
        score = 0.1 + distance_weight*distance_score + \
            time_from_start_score*time_weight + is_daytime*day_light_weight
        if item[5] == pred:
            score += 0.15
        return score

    def ranker(self, raw, loc, time):
        # 0 TripDuration 1 StartTime 2 StopTime 3 StartStationID 4 StartStationName	5 StartStationLatitude
        # 6 StartStationLongitude 7 EndStationID 8 EndStationName 9 EndStationLatitude 10 EndStationLongitude
        # 11 BikeID 12 UserType 13 BirthYear 14 Gender 15 TripDuration in min
        pred = self.predict(loc=loc, time=time)
        ranked_recommendations = sorted(raw,
                                        key=lambda item: self.score(
                                            item, pred),
                                        reverse=True)
        ranked_recommendations = [e[9]
                                  for e in ranked_recommendations if e[9] != loc]

        recommendations = []
        # remove duplicate and keep the order
        for location in ranked_recommendations:
            if location not in recommendations:
                recommendations.append(location)
        return recommendations

    def predict(self, loc, time):
        rec = self.cur.execute(
            "SELECT StartStationID,StartStationLatitude, StartStationLongitude FROM BikeShare WHERE StartStationName like '" + loc + "' LIMIT 1").fetchone()
        if not rec:
            return -1
        sample = [time*60, rec[0], rec[1], rec[2], time]
        from numpy import asarray
        df = pd.read_csv('BikeShare.csv')
        df.index = [x for x in range(1, len(df.values)+1)]
        X = df[['TripDuration', 'StartStationID',
                'StartStationLatitude', 'StartStationLongitude', 'TripDurationinmin']].values
        record = asarray(sample).reshape(1, -1)
        record = StandardScaler().fit(X).transform(record.astype(float))
        knn = pickle.load(open('knnpickle_file', 'rb'))
        pred = knn.predict(record)
        return pred[0]


def create_model(k=29):
    df = pd.read_csv('BikeShare.csv')
    df.index = [x for x in range(1, len(df.values)+1)]

    X = df[['TripDuration', 'StartStationID',
            'StartStationLatitude', 'StartStationLongitude', 'TripDurationinmin']].values

    y = df['EndStationName'].values

    X = StandardScaler().fit(X).transform(X.astype(float))
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=4)

    # Train Model and Predict
    knn = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)

    knnPickle = open('knnpickle_file', 'wb')

    pickle.dump(knn, knnPickle)


def validation(location, duration, k):
    if location == "" or location == None:
        return "Start location is mandatory."
    if location.isdigit():
        return "Location not found"
    if duration == "" or duration == None:
        return "Time Range is mandatory."
    if k == "" or k == None:
        return "Results size is mandatory."
    try:
        duration = int(duration)
    except ValueError:
        return "Only numbers acceptable for riding time."
    try:
        k = int(k)
    except ValueError:
        return "Only numbers acceptable for results size."
    if(duration < 1):
        return "Negative riding time."
    if (k < 1):
        return "Negative results size."
    return True
