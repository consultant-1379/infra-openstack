#!/bin/bash
keyname="cloud15a.athtem.eei.ericsson.se.key"
csrname="cloud15a.athtem.eei.ericsson.se.csr"
existing_key=$(find . -type f -name "*.key")
existing_csr=$(find . -type f -name "*.csr")

echo "Checking if there is an existing CSR"
if [[ -n ${existing_csr} && -s ${existing_csr} ]];then
   renamed_csr="${existing_csr##./}.$(date -Iseconds |sed 's/:/./g')"
   echo "Backing up existing CSR ${existing_csr##./} to ${renamed_csr}"
   mv ${existing_csr##./} ${renamed_csr}
fi

echo "Checking if there is an existing key"
csr_creation_exit_code=0
if [[ -n ${existing_key} && -s ${existing_key} ]]; then
   echo "Not creating a new key. Generating CSR with existing key: ${existing_key##./}"
   keyname="${existing_key##./}"
   openssl req -new -nodes -out ${csrname} -key ${keyname} -config ssl_config.conf
   csr_creation_exit_code=$?
else
   echo "No existing key. Generating CSR with new key ${keyname}"
   openssl req -new -newkey rsa:2048 -nodes -out ${csrname} -keyout ${keyname} -config ssl_config.conf
   csr_creation_exit_code=$?
fi
if [ ${csr_creation_exit_code} -eq 0 ]; then
   echo "CSR generated successfully"
else
   echo "There was a problem generating the CSR"
fi
exit ${csr_creation_exit_code}
