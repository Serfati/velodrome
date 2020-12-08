from flask import Flask, request, jsonify, send_file
import mybackend as backend


'''
this class represents a web-server for biking route information using the business logic in the backend. 
We receive parameters in GET requests and send them on to be analyzed by the backend. The answers will
be sent back.
'''

app = Flask(__name__)


@app.route('/', methods=['GET'])
def querySearch():
    db = backend.Database()
    if request.args:
        loc = request.args.get('startlocation')
        time = request.args.get('timeduration')
        k = request.args.get('k')
        validation = backend.validation(loc, time, k)
        if validation == True:
            resultList = db.get_recommendations(str(loc), int(time), int(k))
            return jsonify("Nothing to Show!") if len(resultList) == 0 else jsonify(resultList)
        else: return jsonify(['Error %s' % (validation)])
    return send_file('assets/logo.png', mimetype='image/gif')

'''
runs flask server on port 5000
'''
if __name__ == '__main__':
    print("server runs on port 5000")
    app.run(port=int("5000"))
