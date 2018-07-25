#Command

[1. Pool]

[2. RBD]

[5. Replacing a failed disk drive]

[6. Crush map]



PGs status:

```sh
Peering: Các OSD kết nối với nhau để replica dữ liệu, đồng bộ trạng thái của Object, metadata.
Active: Peering is complete, Ceph makes the PG active. Data in PG is available on primary OSD and replica. 
Clean: Các OSD peered chính xác, các PG ở đúng vị trí và replica đúng số lần.
Degraded: Khi OSD down hoặc Object của PG bị lỗi, số replica chưa đúng
Recovering: 
Backflling: Khi OSD mới đc thêm vào cluster. Hệ thống sẽ tái cân bằng lưu trữ. 
Remapped: Khi có sự thay đổi của các PG.
State: Khi primary OSD ko báo về trạng thái của nó. 
```


###1. Pool

- List pool
```sh
ceph osd lspools
ceph osd dump | grep "^pool"
rados df
```
- Create pool
```sh
ceph osd pool create {pool-name} {pg-num} [{pgp-num}] [replicated] \
     [crush-ruleset-name] [expected-num-objects]
ceph osd pool create {pool-name} {pg-num}  {pgp-num}   erasure \
     [erasure-code-profile] [crush-ruleset-name] [expected_num_objects]
```

- Rename poll

`ceph osd pool rename {current-pool-name} {new-pool-name}`

- Set number of replica

`ceph osd pool set {poolname} size {num-replicas}`

- Get replica

`ceph osd dump | grep 'replicated size'`

- Set quotas

`ceph osd pool set-quota {pool-name} [max_objects {obj-count}] [max_bytes {bytes}]`

- Snapshot pool
```sh
ceph osd pool mksnap <pool-name> <snap>
ceph osd pool rmsnap <pool-name> <snap>
```


####2. RBD

- Create rbd
```sh
rbd create --size {megabytes} {pool-name}/{image-name}
rbd create --size {megabytes} {image-name}
```
- List
```sh
rbd list
rbd -p {pool-name} list
```
-  Info rbd
```sh
rbd info {image-name}
rbd info {pool-name}/{image-name}
```
-  RESIZING A BLOCK DEVICE IMAGE
```sh
rbd resize --size ... {image-name}
rbd resize -p {pool-name} --image {image-name}  --size ... --allow-shrink
```
-  Remove block device image
```sh
rbd rm {image-name}
rbd rm {pool-name}/{image-name}
```
-  MAP A BLOCK DEVICE

`check - modprobe rbd`

vim /etc/ceph/ceph.conf

```sh
[global]
rbd_default_features = 3
```
```sh
rbd map {image-name}
rbd map {pool-name}/{image-name}
```
`rbd showmapped`

`rbd unmap /dev/rbd/{poolname}/{imagename}`

```sh
# fdisk -l /dev/rbd0
# mkfs.xfs /dev/rbd0
# mkdir /mnt/ceph-vol1
# mount /dev/rbd0 /mnt/ceph-vol1
```

-  Snapshot RBD
```sh
rbd snap create,rm,rollback {pool-name}/{image-name}@{snap-name}
rbd snap ls {pool-name}/{image-name}
```

- Delete all sanpshot

`rbd snap purge {pool-name}/{image-name}`

- CLONE RBD 

Create snapshot

Protect snapshot: `rbd snap protect {image-name}@{snap-name}`

`# rbd clone {pool-name}/{image-name}@{snap-name} {pool-name}/{image-New}}`

make clone independent partent 

`# rbd flatten`

- Put object vào pool

```sh
rados -p sata put sata.pool.object sata.pool
ceph osd map sata sata.pool.object
```

###3. QEMU AND BLOCK DEVICES

- Create

`qemu-img create -f raw rbd:{pool-name}/{image-name} {size}`

- RESIZING IMAGES 

`qemu-img resize rbd:{pool-name}/{image-name} {size}`

- RUNNING QEMU WITH RBD
```sh
qemu-img convert -f qcow2 -O raw debian_squeeze.qcow2 rbd:data/squeeze
qemu -m 1024 -drive format=raw,file=rbd:data/squeeze
qemu -m 1024 -drive format=rbd,file=rbd:data/squeeze,cache=writeback
```

###4. USING LIBVIRT WITH CEPH RBD
```sh
ceph osd pool create libvirt-pool 128 128
ceph auth get-or-create client.libvirt mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=libvirt-pool'
qemu-img create -f rbd rbd:libvirt-pool/new-libvirt-image 2G
apt-get install virt-manager (https://help.ubuntu.com/community/KVM/VirtManager)
virt-manager
```

- CREATE VM 

http://docs.ceph.com/docs/master/rbd/libvirt/


###5. Replacing a failed disk drive

- MAKE OSD FAILED
```sh
ceph osd out
ceph osd down osd.0
ceph osd tree
```
Remove the failed OSD from the CRUSH map:

`ceph osd crush rm osd.0`

Delete Ceph authentication keys for the OSD:

`ceph auth del osd.0`

Remove the OSD from the Ceph cluster

`ceph osd rm osd.0`


- REPLAYCING OSD

Before adding the disk to the Ceph cluster, perform disk zap:

`ceph-deploy disk zap ceph-node1:sdb`

Finally, create an OSD on the disk, and Ceph will add it as osd.0:

`ceph-deploy --overwrite-conf osd create ceph-node1:sdb`

###6. CRUSH MAP

```sh
ceph osd crush dump
ceph osd crush rule list
ceph osd crush rule dump <crush_rule_name>
ceph osd find 1
```

Edit:
```sh
ceph osd getcrushmap -o crushmap_compiled_file
crushtool -d crushmap_compiled_file -o crushmap_decompiled_file
crushtool -c crushmap_decompiled_file -o newcrushmap
ceph osd setcrushmap -i newcrushmap
```

7. FileSystem

- Create FileSystem Pool

```sh
ceph osd pool create cephfs_data <pg_num>
ceph osd pool create cephfs_metadata <pg_num>
```

- Create FileSystem
```sh
ceph fs new <fs_name> <metadata> <data>
ceph fs ls
```




























