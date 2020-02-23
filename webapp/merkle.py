import merkletools
import json
import requests
mt=merkletools.MerkleTools()

class merkleTree:
        def merkle_tree(self, data):
                data_list=[]
                for x in data:
                        data_list.append(data[x])
                mt.reset_tree()
                mt.add_leaf(data_list, True)
                mt.make_tree()
                ans={}
                for x in data:
                        for i in range(len(data_list)):
                                if data[x]==data_list[i]:
                                        value=i
                        ans[x]={
                                "Value" : data[x],
                                "Hash": mt.get_leaf(value),
                                "Proof": mt.get_proof(value)
                        }
                mk={"Merkle_root" : mt.get_merkle_root()}
                return [ans,mk]
        
        def post_data(self, hash, pid):
                response=requests.get('http://23.99.231.16:3000/api/org.acme.nucypher.Roothash/'+pid)
                print("get"+str(type(response)))
                if str(response) =='<Response [200]>':
                    response=requests.put('http://23.99.231.16:3000/api/org.acme.nucypher.Roothash/'+pid, data = { "$class": "org.acme.nucypher.Ipfshash", "hash": hash,"pid": pid})
                    print("put"+str(response))
                else:
                    response=requests.post('http://23.99.231.16:3000/api/org.acme.nucypher.Roothash', data = { "$class": "org.acme.nucypher.Ipfshash", "hash": hash,"pid": pid})
                    print("POST"+str(response))
