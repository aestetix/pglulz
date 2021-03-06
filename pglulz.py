#!/usr/bin/env python
"""
Pretty Good Lulz, aka PGLulz
prepared by aestetix for berlinsides 2016

Make sure you run pip install -r requirements.txt before running
"""

import subprocess
import yaml

# Open config file
with open('pglulz.yaml', 'r') as stream:
    try:
        yaml_data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print exc

# Fixing up the gnupg library a little bit

# total hack because it's unclear how to change the default keyserver
if 'keyserver' in yaml_data:
    subprocess.call('for x in $(find src/ -type f); \
        do perl -p -i -e \'s/subkeys.pgp.net/' + yaml_data['keyserver'] \
        + '/g\' $x; done', shell=True)
# remove log level unless otherwise noted
if not 'logging' in yaml_data:
    subprocess.call('perl -p -i -e \'s/create_logger\\(10/create_logger\\(0/g\' \
    src/gnupg/gnupg/_util.py', shell=True)
    subprocess.call('mkdir -p gnupg/test', shell=True)

import gnupg

# Check flag to wipe out pre-existing keys
if 'hard_reset' in yaml_data and yaml_data['hard_reset']:
    subprocess.call('rm -rf ' + yaml_data['keys_directory'] + '/*', shell=True)

# Create new key for signing
gpg = gnupg.GPG(
    binary='/usr/bin/gpg' if not 'binary' in yaml_data \
        else yaml_data['binary'],
    homedir='~/pgplulz' if not 'keys_directory' in yaml_data \
        else yaml_data['keys_directory'],
    keyring='pubring.gpg' if not 'keyring' in yaml_data \
        else yaml_data['keyring'],
    secring='secring.gpg' if not 'secring' in yaml_data \
        else yaml_data['secring'])

input_data = gpg.gen_key_input(
    key_type='RSA',
    key_length=2048,
    name_real=yaml_data['signing_key']['name'],
    name_email=yaml_data['signing_key']['email'])

key = gpg.gen_key(input_data)

print 'Created key', str(key)[-8:], 'for', yaml_data['signing_key']['name'], \
    yaml_data['signing_key']['email'], 'now to prepare keys to be signed'

# This lets us fetch keys with minimal interference
gpg.options = ['--batch', '--with-colons']

# Upload our key
if yaml_data['real_run'] is True:
    print 'Uploading the new key to the keyserver'
    subprocess.call('gpg --keyserver ' + yaml_data['keyserver'] +
                    ' --send-keys ' + str(key), shell=True)
else:
    print 'This is where we upload our new key to the keyserver'

# This loop is the meat of the project:
# 1. We iterate through each group, getting the name (for display) and
#    the value to match. Usually part of a name or email address.
# 2. Then we search the keysever (MIT is default) for matches.
# 3. We fetch the matches, and then pull in each key into our local db.
# 4. Then we sign each new key with our custom key signer.
# 5. Finally, upload the new trust relationship to the key server :)

for x in yaml_data['groups_to_sign']:

    # Fetch key matches
    key_list = gpg.search_keys(yaml_data['groups_to_sign'][x]['matching'])
    print 'Found', len(key_list), 'keys for ', \
        yaml_data['groups_to_sign'][x]['name']
    print 'Fetching keys from', yaml_data['groups_to_sign'][x]['name']

    # Loop through keys and sign them
    for y in key_list:
        gpg.recv_keys(y['keyid'])
        print 'Signing key', key_list.index(y)+1, 'of', len(key_list)
        # This is rather hackish, but the lib doesn't offer another way
        subprocess.call('gpg --yes --batch -u ' + str(key) + \
            ' --sign-key ' + str(y['keyid']), shell=True, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # All done here, let's ship it!
        if yaml_data['real_run'] is True:
            print 'Uploading our new trust relationship :)'
            subprocess.call('gpg --keyserver ' + yaml_data['keyserver'] \
            + ' --send-key ' + str(y['keyid']), shell=True)
