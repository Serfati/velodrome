from flask import Flask, request, jsonify
from mybackend import Database as db

'''
this class represents a web-server for biking route information using the business logic in the backend. 
We receive parameters in GET requests and send them on to be analyzed by the backend. The answers will
be sent back.
'''

app = Flask(__name__)


@app.route('/', methods=['GET'])
def querySearch():
    startlocation = request.args.get('startlocation')
    timeduration = request.args.get('timeduration')
    k = request.args.get('k')
    validation = db.validation(startlocation, timeduration, k)
    if validation:
        resultList = db.Database().getRecommendations(startlocation, timeduration, k)
        res = [x[0] for x in resultList]
        return "no results found" if len(resultList) == 0 else jsonify(res)
    return jsonify('Error %s' % (validation))


'''
runs flask server on port 5000
'''
if __name__ == '__main__':
    print("server runs on port 5000")
    app.run(port=int("5000"))
