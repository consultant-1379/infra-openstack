#!/bin/bash
openssl req -new -newkey rsa:2048 -nodes -out cloudenv4.athtem.eei.ericsson.se.csr -keyout cloudenv4.athtem.eei.ericsson.se.key -config ssl_config.conf
