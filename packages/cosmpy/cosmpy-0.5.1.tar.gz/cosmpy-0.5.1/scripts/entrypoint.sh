#!/usr/bin/env bash

# variables
export VALIDATOR_KEY_NAME=validator
export BOB_KEY_NAME=bob
export VALIDATOR_MNEMONIC="erase weekend bid boss knee vintage goat syrup use tumble device album fortune water sweet maple kind degree toss owner crane half useless sleep"
export BOB_MNEMONIC="account snack twist chef razor sing gain birth check identify unable vendor model utility fragile stadium turtle sun sail enemy violin either keep fiction"
export PASSWORD="12345678"
export CHAIN_ID=testing
export DENOM_1=stake
export DENOM_2=atestfet
export MONIKER=some-moniker


# Add keys
( echo "$VALIDATOR_MNEMONIC"; echo "$PASSWORD"; echo "$PASSWORD"; ) |fetchd keys add $VALIDATOR_KEY_NAME --recover
( echo "$BOB_MNEMONIC"; echo "$PASSWORD"; ) |fetchd keys add $BOB_KEY_NAME --recover

# Configure node
fetchd init --chain-id=$CHAIN_ID $MONIKER
echo "$PASSWORD" |fetchd add-genesis-account $(fetchd keys show $VALIDATOR_KEY_NAME -a) 100000000000000000000000$DENOM_1
echo "$PASSWORD" |fetchd add-genesis-account $(fetchd keys show $BOB_KEY_NAME -a) 100000000000000000000000$DENOM_2
echo "$PASSWORD" |fetchd gentx $VALIDATOR_KEY_NAME 10000000000000000000000$DENOM_1 --chain-id $CHAIN_ID
fetchd collect-gentxs

# Enable rest-api
sed -i '/^\[api\]$/,/^\[/ s/^enable = false/enable = true/' ~/.fetchd/config/app.toml
sed -i '/^\[api\]$/,/^\[/ s/^swagger = false/swagger = true/' ~/.fetchd/config/app.toml
fetchd start
