from flask import Flask, render_template, redirect, url_for, request
import requests
import json
import unicodedata
from merkle import merkleTree

app = Flask(__name__)
app.config['SECRET_KEY'] = '3141592653589793238462643383279502884197169399'

@app.route('/doctor')
def search():
    info = requests.get('http://localhost:5000/doctor/mvishnoi')
    info = info.json()
    return render_template('show.html', info=info)

@app.route('/')
def student():
  return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
  if request.method == 'POST':
       result = request.form
       print(result)
       endpoint = 'http://23.99.231.16:3000/api/org.acme.nucypher.Patient'
       data = {
           "$class": "org.acme.nucypher.Patient",
           "pid": result['email'],
           "Name": result['name'],
           "gender": result['gender'],
           "claim_data": result['message']
           }
       r = requests.post(url = endpoint, data = data)
       print(r)
       return redirect(url_for('merkle', pid=result['email']))

@app.route('/merkle')
def merkle():
    pid = request.args['pid']
    info = requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Patient/'+pid)
    info = info.json()
    data={}
    for topics in info:
        if topics=='$class':
            continue
        else:
            data[topics] = info[topics]
    mt = merkleTree()
    merkle_data = mt.merkle_tree(data)
    with open("../rest_python/nucypher/Merkle_json.json", "w") as write_file:
                        json.dump(merkle_data, write_file)
    mt.post_data(merkle_data[1]["Merkle_root"],pid)
    return render_template('showMerkle.html', info=merkle_data)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
