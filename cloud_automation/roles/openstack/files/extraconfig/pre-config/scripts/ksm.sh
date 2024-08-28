#!/bin/bash

cat > /etc/ksmtuned.conf << EOF
# Configuration file for ksmtuned.

# How long ksmtuned should sleep between tuning adjustments
# KSM_MONITOR_INTERVAL=60

# Millisecond sleep between ksm scans for 16Gb server.
# Smaller servers sleep more, bigger sleep less.
# KSM_SLEEP_MSEC=10

# KSM_NPAGES_BOOST=300
# KSM_NPAGES_DECAY=-50
# KSM_NPAGES_MIN=64
# KSM_NPAGES_MAX=1250

KSM_THRES_COEF=100
KSM_THRES_CONST=512000000

# uncomment the following if you want ksmtuned debug info

LOGFILE=/var/log/ksmtuned
DEBUG=1
EOF

systemctl restart ksmtuned.service

exit 0
