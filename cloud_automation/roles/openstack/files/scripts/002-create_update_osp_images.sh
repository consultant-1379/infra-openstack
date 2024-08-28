#!/bin/bash
# source common functions
. common.bsh

info "#### Removing old image directory content"
rm -rf ~/images
mkdir ~/images

info "#### Checking RHOSP version"
if (grep -q '16.2' ../../containers-prepare-parameter.yaml); then
    rhosp_version='16.2'
    sudo dnf install -y rhosp-director-images rhosp-director-images-ipa-x86_64 || abort "Error installing rhosp-director-images rhosp-director-images-ipa packages."
    info "#### Extract new overcloud images"
    for i in /usr/share/rhosp-director-images/overcloud-full-latest-${rhosp_version}.tar /usr/share/rhosp-director-images/ironic-python-agent-latest-${rhosp_version}.tar
    do
      info "Extracting ${i} to  ~/images"
      tar -xvf $i -C  ~/images || abort "Error extracting ${i} to  ~/images.Tar exited with return code ${PIPESTATUS[0]}"
    done

elif (grep -q '16.1' ../../containers-prepare-parameter.yaml)
then
    rhosp_version='16.1'
    sudo dnf install -y rhosp-director-images rhosp-director-images-ipa-x86_64 || abort "Error installing rhosp-director-images rhosp-director-images-ipa packages."
    info "#### Extract new overcloud images"
    for i in /usr/share/rhosp-director-images/overcloud-full-latest-${rhosp_version}.tar /usr/share/rhosp-director-images/ironic-python-agent-latest-${rhosp_version}.tar
    do
      info "Extracting ${i} to  ~/images"
      tar -xvf $i -C  ~/images || abort "Error extracting ${i} to  ~/images.Tar exited with return code ${PIPESTATUS[0]}"
    done

elif (grep -q '17.1' ../../containers-prepare-parameter.yaml)
then
    rhosp_version='17.1'
    sudo dnf install -y rhosp-director-images-uefi-x86_64 rhosp-director-images-ipa-x86_64 || abort "Error installing rhosp-director-images-uefi rhosp-director-images-ipa packages."
    info "#### Extract new overcloud images"
    for i in /usr/share/rhosp-director-images/ironic-python-agent-latest.tar /usr/share/rhosp-director-images/overcloud-hardened-uefi-full-latest.tar
    do
      info "Extracting ${i} to  ~/images"
      tar -xvf $i -C  ~/images || abort "Error extracting ${i} to  ~/images.Tar exited with return code ${PIPESTATUS[0]}"

    done

else
    echo "Compatible RHOSP version not found"
    exit 0
fi

info "#### Uploading updated overcloud image to the Undercloud's Glance Registry"
source ~/stackrc
openstack overcloud image upload --image-path ~/images/ --update-existing || abort "Error uploading images to Glance."

exit ${PIPESTATUS[0]}
