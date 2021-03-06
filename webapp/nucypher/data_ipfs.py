import random
import time
import msgpack
import json
import ipfsapi

from nucypher.data_sources import DataSource


PATIENT_DETAIL = 'patient_details.msgpack'

# Alicia defined a label to categorize all her heart-related data ❤️
# All DataSources that produce this type of data will use this label.
DEFAULT_LABEL = b"Patient data"


def encrypt_patient_data(policy_pubkey, data_fields,
                                label: bytes = DEFAULT_LABEL,
                                save_as_file: bool = False):
    data_source = DataSource(policy_pubkey_enc=policy_pubkey,
                             label=label)

    data_source_public_key = bytes(data_source.stamp)
    ipfs_api = ipfsapi.connect()

    kits = list()
    with open("Merkle_json.json", "r") as read_file:
            data = json.load(read_file)
    share=data_fields
    share_data = {}
    for i in share:
        share_data[i] = {'Value' : data[0][i]['Value'], 'Hash' : data[0][i]['Hash']}

    plaintext = msgpack.dumps(share_data, use_bin_type=True)
    message_kit, _signature = data_source.encrypt_message(plaintext)

    kit_bytes = message_kit.to_bytes()
    kits.append(kit_bytes)

    data = {
        'data_source': data_source_public_key,
        'kits': kits,
    }

    if save_as_file:
        with open(PATIENT_DETAIL, "wb") as file:
            msgpack.dump(data, file, use_bin_type=True)
    res = ipfs_api.add(PATIENT_DETAIL)
    return res
