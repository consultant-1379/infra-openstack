#!/bin/bash

cat > /etc/multipath.conf <<EOF
blacklist {
    # Skip the files uner /dev that are definitely not FC/iSCSI devices
    # Different system may need different customization
    devnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"
    devnode "^hd[a-z][0-9]*"
    devnode "^cciss!c[0-9]d[0-9]*[p[0-9]*]"

    # Skip LUNZ device from VNX/Unity
    device {
        vendor "DGC"
        product "LUNZ"
    }
}

defaults {
    # Adding kpartx yes for https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/ITTEI-5356 and https://access.redhat.com/support/cases/#/case/02653971
    skip_kpartx yes
    user_friendly_names no
    flush_on_last_del yes
}

devices {
    # Device attributed for EMC CLARiiON and VNX/Unity series ALUA
    device {
        vendor "DGC"
        product ".*"
        product_blacklist "LUNZ"
        path_grouping_policy group_by_prio
        path_selector "round-robin 0"
        path_checker emc_clariion
        features "0"
        no_path_retry 12
        hardware_handler "1 alua"
        prio alua
        failback immediate
    }
}
EOF

systemctl is-active multipathd
if [[ "$?" != "0" ]]; then
  systemctl restart multipathd
  systemctl enable multipathd
fi

exit 0
