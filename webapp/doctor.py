import json
import os
import shutil
import msgpack
import maya
import traceback
from timeit import default_timer as timer

from twisted.logger import globalLogPublisher

from nucypher.characters.lawful import Bob, Ursula
from nucypher.crypto.kits import UmbralMessageKit
from nucypher.crypto.powers import DecryptingPower, SigningPower
from nucypher.data_sources import DataSource
from nucypher.keystore.keypairs import DecryptingKeypair, SigningKeypair
from nucypher.network.middleware import RestMiddleware

from umbral.keys import UmbralPublicKey

from nucypher.utilities.logging import SimpleObserver
import ipfsapi
import os

def doctor_decrypt(hash_key):
    globalLogPublisher.addObserver(SimpleObserver())
    SEEDNODE_URL = 'localhost:11501'

    TEMP_DOCTOR_DIR = "{}/doctor-files".format(os.path.dirname(os.path.abspath(__file__)))
    shutil.rmtree(TEMP_DOCTOR_DIR, ignore_errors=True)

    ursula = Ursula.from_seed_and_stake_info(seed_uri=SEEDNODE_URL,
                                            federated_only=True,
                                            minimum_stake=0)

    from doctor_keys import get_doctor_privkeys

    doctor_keys = get_doctor_privkeys()

    bob_enc_keypair = DecryptingKeypair(private_key=doctor_keys["enc"])
    bob_sig_keypair = SigningKeypair(private_key=doctor_keys["sig"])
    enc_power = DecryptingPower(keypair=bob_enc_keypair)
    sig_power = SigningPower(keypair=bob_sig_keypair)
    power_ups = [enc_power, sig_power]

    print("Creating the Doctor ...")

    doctor = Bob(
        is_me=True,
        federated_only=True,
        crypto_power_ups=power_ups,
        start_learning_now=True,
        abort_on_learning_error=True,
        known_nodes=[ursula],
        save_metadata=False,
        network_middleware=RestMiddleware(),
    )

    print("Doctor = ", doctor)

    with open("policy-metadata.json", 'r') as f:
        policy_data = json.load(f)

    policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_data["policy_pubkey"]))
    alices_sig_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_data["alice_sig_pubkey"]))
    label = policy_data["label"].encode()

    print("The Doctor joins policy for label '{}'".format(label.decode("utf-8")))
    doctor.join_policy(label, alices_sig_pubkey)

    ipfs_api = ipfsapi.connect()
    file = ipfs_api.get(hash_key)
    print(file)
    os.rename(hash_key, 'patient_details.msgpack')
    data = msgpack.load(open("patient_details.msgpack", "rb"), raw=False)
    message_kits = (UmbralMessageKit.from_bytes(k) for k in data['kits'])

    data_source = DataSource.from_public_keys(
        policy_public_key=policy_pubkey,
        datasource_public_key=data['data_source'],
        label=label
    )
    complete_message=[]
    for message_kit in message_kits:
        print(message_kit)
        try:
            start = timer()
            retrieved_plaintexts = doctor.retrieve(
                message_kit=message_kit,
                data_source=data_source,
                alice_verifying_key=alices_sig_pubkey
            )
            end = timer()
            plaintext = msgpack.loads(retrieved_plaintexts[0], raw=False)
            complete_message.append(plaintext)
            print(plaintext)
            #with open("details.json", "w") as write_file:
             #               json.dump(plaintext, write_file)
        except Exception as e:
            traceback.print_exc()
    with open("details.json", "w") as write_file:
                            json.dump(complete_message, write_file)
    return complete_message
