# source common functions
. common.bsh
CONTAINER_VERSION=16.1.3-1
RH_DOCKER_REGISTRY=registry.connect.redhat.com
DOCKER_REGISTRY_IP=10.232.161.6
CONTAINER_NAME=dellemc/openstack-cinder-volume-dellemc-rhosp16

info "Logging in to ${RH_DOCKER_REGISTRY} using service account 6326810|lmi-athlone"
sudo podman login -u '6326810|lmi-athlone' -p 'eyJhbGciOiJSUzUxMiJ9.eyJzdWIiOiJlMTU2NWU1OTM2OGM0NzUyYTJlZjhmNzg5ODBjZTZhMyJ9.VQgOviLh5y7SApz_1QcokM3-ZsEqFsFgWMD2jKzH7gLULMNCdXj11r2LpzCNh7D4QAVO1B6DBfT_0f-OiXE3a0dDgEmQe2BKksfi9kLy1DqtLwXSy0FvxDbwcjRApkxYd6egLVs9nzKJya_R2wkkishcXm7xWVys4r_6PzHo1lS8ZsJOb0YnnJ4ghmKneTWc6VNUzU7eeeWyTW20I7Jz4x1KNH7OACTSn_Tv1zPRcufysyzjaoFYoUtuj9MSqnKIMwmbuBRAtxIWVJlbrP4WUL0Ldkz07TRTCL3m745mbc0gGfLNhIrLtC6KS88eQ-u7QpPefCpdOrZqHSlrj_75Gfl99pyCw2kD0aflYdruOmwrqCphlG2a9yQZKp3vkfwN8F8-ugBq5nJUZijM98G1Jlh-1-KeufGx-9_cG3ER3Ce2p9ga_bzTzXjqj-CuLcL2hyvT26UYJkHMGAAWtazxY8YcR8FOU8AG6Vclav2tanHTUHE1vCVV99WKIFlXyAndMWlROa9ivnrlvDaRo25jlJqQRD4w2DXkviQ2D00N8g5ZhLW03BWgb5fA856TpB5MCgGBKacuxkQmxU5NPQOxaaE2525seWM5F2uqkR5opInb_OQUC9z4WZM_A1ZE1QMig4nvnA4hXTnRutC_qKMBQPTsahjmDiH79Rq-nhLmQww' ${RH_DOCKER_REGISTRY}

info "Checking the PCS/Pacemaker version in ${CONTAINER_NAME}:${CONTAINER_VERSION} matches the deployment"
# nothing special about mariadb. container image used must be a container which is pacemaker controlled.
mariadb_image=$(sudo podman images | awk '/mariadb/{printf "%s:%s", $1,$2}')
cinder_image=$(sudo podman images |grep $CONTAINER_VERSION | awk '/cinder/{printf "%s:%s", $1,$2}')
pcs_version_mariadb=$(sudo podman run --rm --net=host -it ${mariadb_image} rpm -q pcs --queryformat='%{VERSION}' )
pcs_version_cinder=$(sudo podman run --rm --net=host -it ${cinder_image} rpm -q pcs --queryformat='%{VERSION}')
echo pcs_version_mariadb=$pcs_version_mariadb
echo pcs_version_cinder=$pcs_version_cinder
if [ "${pcs_version_cinder}" != "${pcs_version_mariadb}" ] ; then
    warn "The PCS version in ${CONTAINER_NAME}:${CONTAINER_VERSION} is ${pcs_version_cinder}. This does not match PCS version ${pcs_version_mariadb} in the rest of the deployment."
    warn "This can cause failures during the overcloud deployment in the step where cinder is added to the PCS configuration."
    warn "If this occurs, check ${RH_DOCKER_REGISTRY} for a newer version of the ${CONTAINER_NAME} image."
fi
