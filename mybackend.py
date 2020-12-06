from sklearn.preprocessing import MinMaxScaler
from numpy import asarray
import pickle
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
import timeit
import numpy as np
import pandas as pd
from sklearn import preprocessing
import csv
import sqlite3


class Database:

    def __init__(self):
        import os
        files = os.listdir("./")
        if "database.db" in files:
            self.conn = sqlite3.connect("database.db")
            self.cur = self.conn.cursor()
            if not self.shape()[0] :
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
        return self.cur.execute("select count(*) from BikeShare").fetchone()

    def insert_values(self):
        with open('BikeShare.csv', 'r') as f:
            reader = csv.reader(f)
            data = next(reader)
            query = 'INSERT into BikeShare({0}) values ({1})'
            query = query.format(','.join(data), ','.join('?' * len(data)))
            for data in reader:
                self.cur.execute(query, data)
            self.conn.commit()

    def getRecommendations(self, loc, time, k):
        raw = self.cur.execute("select * from BikeShare "
                               "where StartStationName like '" + loc +
                               "' and TripDurationinmin <= " + str(time)).fetchall()
        return self.ranker(self, raw, time, k)

    def ranker(self, raw, time, k):
        response = {}
        return sorted(response.items(), key=lambda item: item[1], reverse=True)


    def create_model(self, k=29):
        df = pd.read_csv('BikeShare.csv')
        df.index = [x for x in range(1, len(df.values)+1)]

        X = df[['TripDuration', 'StartStationID',
                'StartStationLatitude', 'StartStationLongitude', 'TripDurationinmin']].values

        y = df['EndStationID'].values

        X = preprocessing.StandardScaler().fit(X).transform(X.astype(float))
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.01, random_state=4)

        # Train Model and Predict
        knn = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)

        knnPickle = open('knnpickle_file', 'wb')

        pickle.dump(knn, knnPickle)


    def predict(self, record):
        from numpy import asarray
        df = pd.read_csv('BikeShare.csv')
        df.index = [x for x in range(1, len(df.values)+1)]
        X = df[['TripDuration', 'StartStationID',
                'StartStationLatitude', 'StartStationLongitude', 'TripDurationinmin']].values
        record = asarray(record).reshape(1, -1)
        record = preprocessing.StandardScaler().fit(X).transform(record.astype(float))
        knn = pickle.load(open('knnpickle_file', 'rb'))
        pred = knn.predict(record)
        return pred


def validation(location, duration, k):
    if location == "" or location == None:
        return "Start location is mandatory."
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

db = Database()

