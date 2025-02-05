from flask import Flask, request, json
app = Flask(__name__)

@app.route('/sum', methods=['POST'])
def sum():
    global status
    data = request.get_json()
    sum = int(data['a']) + int(data['b'])
    return json.dumps({"status": 200, "msg": f"sum = {sum}"})

@app.route('/hello', methods=['GET'])
def hello():
    return json.dumps({"status": 200, "msg": "Hello from App A"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)