from flask import Flask, flash,  render_template, redirect, url_for, request
import requests
import json
import unicodedata
from merkle import merkleTree
from alicia import alicia_encrypt
from doctor import doctor_decrypt
from validation import validate_values

app = Flask(__name__)
app.config['SECRET_KEY'] = '3141592653589793238462643383279502884197169399'

@app.route('/menu')
def menu():
  return render_template('menu.html')

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
       info= {}
       for topics in data:
           if topics=='$class':
               continue
           else:
               info[topics] = data[topics]
       r = requests.post(url = endpoint, data = data)
       mt=merkleTree()
       merkle_data=mt.merkle_tree(info)
       m_data=[]
       import os
       exists = os.path.isfile('Merkle_json.json')
       if exists:
           with open("Merkle_json.json","r") as read_file:
               m_data=json.load(read_file)
       m_data.append(merkle_data)
       with open("Merkle_json.json", "w") as write_file:
                           json.dump(m_data, write_file)
       mt.post_data(merkle_data[1]["Merkle_root"],result['email'])
       return redirect(url_for('merkle', pid=result['email']))

@app.route('/merkle')
def merkle():
    pid = request.args['pid']
    #info = requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Patient/'+pid)
    #info = info.json()
    #data={}
    #for topics in info:
    #    if topics=='$class':
    #       continue
    #    else:
    #        data[topics] = info[topics]
    #mt = merkleTree()
    #merkle_data = mt.merkle_tree(data)
    #m_data = []
    #import os
    #exists = os.path.isfile('Merkle_json.json')
    #if exists:
    #    with open("Merkle_json.json","r") as read_file:
    #        m_data=json.load(read_file)
    #m_data.append(merkle_data)
    #with open("Merkle_json.json", "w") as write_file:
    #                    json.dump(m_data, write_file)
    #mt.post_data(merkle_data[1]["Merkle_root"],pid)
    with open("Merkle_json.json","r") as read_file:
            data=json.load(read_file)
    for selected_data in data:
        if selected_data[0]['pid']['Value']==pid:
            process_data=selected_data
    return render_template('showMerkle.html', info=process_data)

@app.route('/share')
def share():
    with open("Merkle_json.json","r") as read_file:
            m_data=json.load(read_file)
    x=[]
    for data in m_data:
        x.append(data[0]['pid'])

    return render_template('fields.html', info=x)

@app.route('/doctorview', methods=['POST', 'GET'])
def alicia():
  if request.method == 'POST':
       result = request.form
       for_alicia=[]
       for values in result:
           if(values!='username'):
               for_alicia.append(values)
       print(result['username'])
       res=alicia_encrypt(for_alicia, result['username'])
       hash=res['Hash']
       response=requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Ipfshash/'+result['username'])
       print("get"+str(type(response)))
       if str(response) =='<Response [200]>':
           response=requests.put('http://23.99.231.16:3000/api/org.acme.nucypher.Ipfshash/'+result['username'], data = { "$class": "org.acme.nucypher.Ipfshash", "hash": hash,"pid": result['username']})
           print("put"+str(response))
       else:
           response=requests.post('http://23.99.231.16:3000/api/org.acme.nucypher.Ipfshash', data = { "$class": "org.acme.nucypher.Ipfshash", "hash": hash,"pid": result['username']})
           print("POST"+str(response))
       #return redirect(url_for('search', pid=result['username']))
       flash('Data Shared Successfully! Doctors can view it in Doctor View.')
       return redirect(url_for('menu'))

@app.route('/viewdoc')
def select_data():
    info = requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Ipfshash/')
    info = info.json()
    #info = info['hash']
    print(info)
    return render_template('select_pid.html', info=info)

@app.route('/doctor', methods=['POST', 'GET'])
def search():
    if request.method=='POST':
        form = request.form
        pid = form['pid']
        print("===============> pid"+ str(pid))
        info = requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Ipfshash/'+pid)
        info = info.json()
        print("==========================> info   " + str(info))
        info = info['hash']
        data = doctor_decrypt(info)
        print("to show data ======================> "+ str(data))
        root_hash=requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Roothash/'+pid.rstrip())
        root_hash=root_hash.json()
        root_hash=root_hash['hash']
        validated_data=validate_values(data,root_hash,pid)
        #print("++++++++++++++++++++=====================" + str(validated_data))
        #requests.post('http://23.99.231.16:3000/api/org.acme.nucypher.Proofrecord', data={"$class":"org.acme.nucypher.Proofrecord", "pid": pid,"value":
        return render_template('docview.html', info=data, validation=validated_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
