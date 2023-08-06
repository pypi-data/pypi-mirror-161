#!/usr/bin/env xonsh

domain = $ARG1
out=$(openssl s_client -servername @(domain) -connect @(domain):443 | openssl x509 -noout -dates)
out

