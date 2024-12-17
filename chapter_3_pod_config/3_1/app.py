from flask import Flask, request, json
app = Flask(__name__)

import os
pod_name = os.getenv('POD_NAME')
app_name = os.getenv('APP_NAME')

@app.route('/sum', methods=['POST'])
def sum():
    global status
    data = request.get_json()
    sum = int(data['a']) + int(data['b'])
    return json.dumps({"status": 200, "msg": f"[{app_name}-{pod_name}] sum = {sum}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)