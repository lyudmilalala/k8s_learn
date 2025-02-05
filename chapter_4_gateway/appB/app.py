from flask import Flask, request, json
app = Flask(__name__)

@app.route('/subtract', methods=['POST'])
def subtract():
    global status
    data = request.get_json()
    diff = int(data['a']) - int(data['b'])
    return json.dumps({"status": 200, "msg": f"diff = {diff}"})

@app.route('/hello', methods=['GET'])
def hello():
    return json.dumps({"status": 200, "msg": "Hello from App B"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)