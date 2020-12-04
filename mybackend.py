import csv
import sqlite3
import model

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

    def getRecommendations(self, loc, time, k):
        raw = self.cur.execute("select * from BikeShare "
                               "where StartStationName like '" + loc +
                               "' and TripDurationinmin <= " + str(time)).fetchall()
        return self.ranker(self, raw, time, k)

    
    def ranker(self, raw, time, k):
        response = {}
        return sorted(response.items(), key=lambda item: item[1], reverse=True)


def model(k=29):
    from sklearn.neighbors import KNeighborsClassifier
    import pandas as pd
    from sklearn import preprocessing

    df = pd.read_csv('assets/BikeShare.csv')
    df.index = [x for x in range(1, len(df.values)+1)]

    X = df[['TripDuration', 'StartStationID',
            'StartStationLatitude', 'StartStationLongitude', 'TripDurationinmin']].values

    y = df['EndStationID'].values

    X = preprocessing.StandardScaler().fit(X).transform(X.astype(float))
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.1, random_state=4)

    #Train Model and Predict
    knn = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)

    ypred = knn.predict(X_test)

    from sklearn import metrics

    print("Test set Accuracy: ", metrics.accuracy_score(y_test, ypred))
    

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


if __name__ == "__main__":
    model()

