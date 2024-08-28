#!/bin/bash
cerfile=$(ls *.cer)
keyfile=$(ls *.key)
csrfile=$(ls *.csr)
fc=$( ls *.key *.cer *.csr|wc -w)
[ $fc -eq 3 ] || { echo "Number of Required files is incorrect - please check " ; exit 1 ; }
echo -e  "We will check the modulus of the following files \n"$cerfile"\n"$keyfile"\n"$csrfile
echo "We will decrypt $keyfile  prior to doing test . Decrypted file  will be deleted after test"
ansible-vault view $keyfile >/tmp/$keyfile
KEY=$(openssl rsa -modulus -noout -in /tmp/$keyfile | openssl md5 | awk '{print $NF}')
rm /tmp/$keyfile 2>/dev/null
CER=$(openssl x509 -modulus -noout -in $cerfile | openssl md5 | awk '{print $NF}')
CSR=$(openssl req -modulus -noout -in $csrfile | openssl md5 | awk '{print $NF}')
echo -e $CER"\n"$KEY"\n"$CSR
[ "$CER" = "$KEY" ] && [ "$KEY" = "$CSR" ]  && echo "Modulus of all SSL files match thus indicating SSL files are verified" || echo "Modulus of SSL files do not match - please check"
