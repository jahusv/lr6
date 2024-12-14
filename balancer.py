from flask import Flask, jsonify, request
import requests
import threading
import time

app = Flask(__name__)

instances = []

index = 0

def health_check():
    while True:
        for instance in instances:
            try:
                url = f"http://{instance['ip']}:{instance['port']}/health"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    instance['status'] = 'healthy'
                else:
                    instance['status'] = 'not healthy'
            except:
                instance['status'] = 'not healthy'
        time.sleep(5)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"instances": instances})

@app.route('/process')
def process():
    global index
    active_instances = [instance for instance in instances if instance['status'] == 'healthy']

    if len(active_instances) == 0:
        return jsonify({"error": "no apps"}), 503

    instance = active_instances[index]
    index = (index + 1) % len(active_instances)

    try:
        response = requests.get(f'http://{instance["ip"]}:{instance["port"]}/process')
        return jsonify(response.json())
    except:
        return jsonify({"error": "not got it"}), 503

# добавление
@app.route('/add_instance', methods=['POST'])
def add_instance():
    ip = request.form.get('ip')
    port = request.form.get('port')
    if ip and port:
        instances.append({"ip": ip, "port": port, "status": "healthy"})
        return jsonify({"message": "added", "instances": instances})
    return jsonify({"error": "something wrong"}), 400

# удаление
@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    index = request.form.get("index")
    if index and 0 <= int(index) < len(instances):
        removed = instances.pop(int(index))
        return jsonify({"message": "removed", "removed": removed, "instances": instances})
    return jsonify({"error": "something wrong"}), 400

# перенаправление запросов
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    global index
    active_instances = [inst for inst in instances if inst['status'] == 'healthy']
    if not active_instances:
        return jsonify({"error": "not connected"}), 503

    instance = active_instances[index % len(active_instances)]
    index += 1
    target_url = f"http://{instance['ip']}:{instance['port']}/{path}"

    try:
        if request.method == 'GET':
            response = requests.get(target_url, params=request.args)
        elif request.method == 'POST':
            response = requests.post(target_url, json=request.json)

        return (response.content, response.status_code, response.headers.items())
    except:
        return jsonify({"error": "not connected"}), 503

if __name__ == '__main__':
    app.run(port=5000, debug=True)
