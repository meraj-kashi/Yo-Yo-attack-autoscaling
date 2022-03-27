from flask import Flask
import requests
app = Flask(__name__)
@app.route('/')
def hello_world():
    instance_id = requests.get("http://169.254.169.254/latest/meta-data/instance-id").content
    return instance_id
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')