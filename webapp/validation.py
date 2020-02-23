import merkletools
import json
import requests
mt=merkletools.MerkleTools()
def validate_values(data, root, pid):
    validated_data = {}
    for i in data:
        proof = i['proof']
        value = i['hash']
        #print(proof)
        #print(value)
        #print(root)
        is_valid = mt.validate_proof(proof, value, root)
        response=requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Ipfshash/'+pid)
        print("get"+str(type(response)))
        if str(response) =='<Response [200]>':
            response=requests.put('http://23.99.231.16:3000/api/org.acme.nucypher.Ipfshash/'+pid, data={"$class":"org.acme.nucypher.Proofrecord", "pid": pid,"value":value,"proof":str(proof),"valid":is_valid})
        else:
            requests.post('http://23.99.231.16:3000/api/org.acme.nucypher.Proofrecord', data={"$class":"org.acme.nucypher.Proofrecord", "pid": pid,"value":value,"proof":str(proof),"valid":is_valid})
        validated_data[i['resourceType']]=is_valid
    return validated_data
