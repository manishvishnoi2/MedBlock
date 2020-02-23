from nucypher.characters.lawful import Bob, Ursula
from nucypher.config.characters import AliceConfiguration
from nucypher.config.storages import LocalFileBasedNodeStorage
from nucypher.crypto.powers import DecryptingPower, SigningPower
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import SimpleObserver

import datetime
import os
import shutil
import maya
import json
import sys
from twisted.logger import globalLogPublisher




def alicia_encrypt(data_fields):
    POLICY_FILENAME = "policy-metadata.json"
    globalLogPublisher.addObserver(SimpleObserver())
    TEMP_ALICE_DIR = "alicia-files".format(os.path.dirname(os.path.abspath(__file__)))
    SEEDNODE_URL = '40.122.164.26:9151'

    passphrase = "TEST_ALICIA_INSECURE_DEVELOPMENT_PASSWORD"
    try:
        alice_config_file = os.path.join(TEMP_ALICE_DIR, "alice.config")
        new_alice_config = AliceConfiguration.from_configuration_file(
                filepath=alice_config_file,
                network_middleware=RestMiddleware(),
                start_learning_now=False,
                save_metadata=False,
            )
        alicia = new_alice_config(passphrase=passphrase)

    except:
        shutil.rmtree(TEMP_ALICE_DIR, ignore_errors=True)
        ursula = Ursula.from_seed_and_stake_info(seed_uri=SEEDNODE_URL,
                                                federated_only=True,
                                                minimum_stake=0)
        alice_config = AliceConfiguration(
            config_root=os.path.join(TEMP_ALICE_DIR),
            is_me=True,
            known_nodes={ursula},
            start_learning_now=False,
            federated_only=True,
            learn_on_same_thread=True,
        )

        alice_config.initialize(password=passphrase)

        alice_config.keyring.unlock(password=passphrase)
        alicia = alice_config.produce()
        alice_config_file = alice_config.to_configuration_file()

    alicia.start_learning_loop(now=True)
    label = "doctor"
    label = label.encode()
    policy_pubkey = alicia.get_policy_pubkey_from_label(label)

    print("The policy public key for "
        "label '{}' is {}".format(label.decode("utf-8"), policy_pubkey.to_bytes().hex()))

    import data_ipfs
    res = data_ipfs.encrypt_patient_data(policy_pubkey , data_fields, label=label,save_as_file=True)
    print(res)

    from doctor_keys import get_doctor_pubkeys
    doctor_pubkeys = get_doctor_pubkeys()

    powers_and_material = {
        DecryptingPower: doctor_pubkeys['enc'],
        SigningPower: doctor_pubkeys['sig']
    }

    doctor_strange = Bob.from_public_keys(powers_and_material=powers_and_material,
                                        federated_only=True)


    policy_end_datetime = maya.now() + datetime.timedelta(days=5)

    m, n = 2, 3
    print("Creating access policy for the Doctor...")
    policy = alicia.grant(bob=doctor_strange,
                        label=label,
                        m=m,
                        n=n,
                        expiration=policy_end_datetime)
    print("Done!")


    policy_info = {
        "policy_pubkey": policy.public_key.to_bytes().hex(),
        "alice_sig_pubkey": bytes(alicia.stamp).hex(),
        "label": label.decode("utf-8"),
    }

    filename = POLICY_FILENAME
    with open(filename, 'w') as f:
        json.dump(policy_info, f)
    
    return res

