ceph-deploy --overwrite-conf mds create ceph2

systemctl status ceph-mds@ceph2.service

ceph osd pool create cephfs_data 64 64
ceph osd pool create cephfs_metadata 64 64

ceph fs new cephfs cephfs_metadata cephfs_data
new fs with metadata pool 10 and data pool 9

[root@ceph1 cluster-ceph]# ceph mds stat
cephfs-1/1/1 up  {0=ceph2=up:active}

[root@ceph1 cluster-ceph]# ceph fs ls
name: cephfs, metadata pool: cephfs_metadata, data pools: [cephfs_data ]

ceph auth get-or-create client.cephfs mon 'allow r' osd 'allow rwx pool=cephfs_metadata,allow rwx pool=cephfs_data' -o /etc/ceph/client.cephfs.keyring

ceph-authtool -p -n client.cephfs /etc/ceph/client.cephfs.keyring > /etc/ceph/client.cephfs
cat /etc/ceph/client.cephfs
AQDB3QValI+YDxAAOkQ7O1BXgS06dG7w6QIMXQ==

De khac phuc loi client khong mount duoc cephfs, bao loi: missing required protocol features trong syslog client


disable option trong crushmap
tunable chooseleaf_stable 1*

#### 4.2. Mount CephFS
Client có 2 cách để mount CephFS
 - Mount bằng kernel driver: hỗ trợ từ Linux kernel 2.6.34
 - Mount bằng Ceph Fuse: với Linux kernel < 2.6.34
#### 4.3. Mount file system sử dụng kernel driver
 - Trên Ceph1, chuyển file /etc/ceph/client.user1 sang client
 	```
 	scp /etc/ceph/client.user1 root@client:/etc/ceph
 	```
 - Mount FS
 	```sh
 	mount -t ceph 10.10.10.75:6789:/ /mnt/cephfs -o name=cephfs,secretfile=/etc/ceph/client.cephfs
 	```
 - Để mount FS khi reboot client, sửa /etc/fstab, thêm dòng sau ở cuối file
 	```sh
 	10.10.10.75:6789:/     /mnt/cephfs    ceph    name=cephfs,secretfile=/etc/ceph/client.cephfs,noatime,_netdev    0       2
 	```
#### 4.4. Mount file system sử dụng Ceph Fuse
 - Trên Ceph1, chuyển file /etc/ceph/client.cephfs.keyring sang client
 	```
 	scp /etc/ceph/client.cephfs.keyring root@client:/etc/ceph
 	```
 - Cài đặt Ceph Fuse trên Client
 	```
 	apt-get install ceph-fuse -y
 	```
 - Mount FS sử dụng ceph-fuse
 	```
 	ceph-fuse --keyring=/etc/ceph/client.cephfs.keyring -n client.cephfs -m 10.10.10.75:6789  /mnt/cephfs
 - Umount
 	fusermount -u /mnt/cephfs
 - Mount /etc/fstab
 	```none  /mnt/cephfs  fuse.ceph  ceph.id=cephfs,ceph.client_mountpoint=/,defaults,_netdev 0  0```

fstab
mount -t fuse.ceph id=admin,conf=/etc/ceph/ceph.conf /mnt/ceph/


