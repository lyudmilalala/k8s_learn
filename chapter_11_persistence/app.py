from flask import Flask, request, jsonify
import os
import traceback

app = Flask(__name__)

import os
pod_name = os.getenv('POD_NAME')
storage_prefix = os.getenv('STORAGE_PREFIX')

@app.route('/write', methods=['POST'])
def write_file():
    data = request.json
    filename = data.get('filename')
    content = data.get('content')
    
    if not filename or not content:
        return jsonify({"error": "filename and content are required"}), 400
    
    file_path = os.path.join(storage_prefix, filename)
    
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return jsonify({"message": f"File {filename} written successfully"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/read', methods=['GET'])
def read_file():
    filename = request.args.get('filename')
    
    if not filename:
        return jsonify({"error": "filename is required"}), 400
    
    file_path = os.path.join(storage_prefix, filename)
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return jsonify({"filepath": file_path, "content": content}), 200
    except FileNotFoundError:
        return jsonify({"error": f"File {file_path} not found"}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/list', methods=['GET'])
def list_files():
    try:
        files = os.listdir(storage_prefix)
        return jsonify({"files": files}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)