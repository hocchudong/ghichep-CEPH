#!/bin/bash -ex

cat << EOF > /etc/hosts
127.0.0.1 `hostname` localhost
192.168.62.84 client1
192.168.62.85 ceph1
192.168.62.86 ceph2
192.168.62.87 ceph3

192.168.98.84 client1
192.168.98.85 ceph1
192.168.98.86 ceph2
192.168.98.87 ceph3
EOF