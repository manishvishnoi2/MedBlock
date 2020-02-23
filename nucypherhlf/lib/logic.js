'use strict';
/**
 * Write your transction processor functions here
 */

/**
 * Sample transaction
 * @param {org.acme.nucypher.SampleTransaction} sampleTransaction
 * @transaction
 */
/*
async function sampleTransaction(tx) {
    // Save the old value of the asset.
    const oldValue = tx.asset.value;

    // Update the asset with the new value.
    tx.asset.value = tx.newValue;

    // Get the asset registry for the asset.
    const assetRegistry = await getAssetRegistry('org.acme.nucypher.SampleAsset');
    // Update the asset in the asset registry.
    await assetRegistry.update(tx.asset);

    // Emit an event for the modified asset.
    let event = getFactory().newEvent('org.acme.nucypher', 'SampleEvent');
    event.asset = tx.asset;
    event.oldValue = oldValue;
    event.newValue = tx.newValue;
    emit(event);
}
*/

/**
 * Storehash transaction
 * @param {org.acme.nucypher.storehash} input - the input to the transaction
 * @transaction
 */

 function storehash(input){
     var factory=getFactory();
     var newhash;
     return getAssetRegistry('org.acme.nucypher.Roothash')
        .then(function(assetRegistry)
    {
        newhash=factory.newResource('org.acme.nucypher.Roothash',input.pid);
        newhash.hash=input.hash;
        return assetRegistry.add(newhash);
    });
 }



