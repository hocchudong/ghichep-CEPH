# Hướng dẫn fix lỗi incremental backup volume sử dụng cinder-backup

*Chú ý:*
 - Thực hiện trên phiên bản Mitaka và Ceph jewel

## 1. Vấn đề
Đối với phiên bản OpenStack Mitaka khi tích hợp với Ceph (jewel), chức năng backup up volume sử dụng cinder-backup gặp vấn đề: không thể thực hiện backup incremental, tất cả các bản backup đều là full backup, điều này gây lãng phí dung lượng lưu trữ.

## 2. Giải quyết
Trên phiên bản OpenStack Newton, bug này đã được khắc phục, ta sẽ sử dụng các bản patch cho cinder-backup trên Newton để vá cho phiên bản Mitaka.

## 2.1. Ở trên các node controller có service `cinder-backup`, thực hiện download và patch các bản vá
```
root@controller1:~# wget https://raw.githubusercontent.com/longsube/ghichep-Ceph/master/scripts/cinder_backup_patch_OpsMitaka_CephJewel/connector.patch -O /root/connector.patch
root@controller1:~# cd /usr/lib/python2.7/dist-packages/os_brick/initiator/
root@controller1:~# patch -p5 -b < /root/connector.patch
```

```
root@controller1:~# wget https://raw.githubusercontent.com/longsube/ghichep-Ceph/master/scripts/cinder_backup_patch_OpsMitaka_CephJewel/ceph.patch -O /root/ceph.patch
root@controller1:~# cd /usr/lib/python2.7/dist-packages/cinder/backup/drivers/
root@controller1:~# patch -p8 -b < /root/ceph.patch
```

```
root@controller1:~# wget https://raw.githubusercontent.com/longsube/ghichep-Ceph/master/scripts/cinder_backup_patch_OpsMitaka_CephJewel/linuxrbd.patch -O /root/linuxrbd.patch
root@controller1:~# cd /usr/lib/python2.7/dist-packages/os_brick/initiator/
root@controller1:~# patch -p5 -b < /root/linuxrbd.patch
```

```
root@controller1:~# wget https://raw.githubusercontent.com/longsube/ghichep-Ceph/master/scripts/cinder_backup_patch_OpsMitaka_CephJewel/rbd.patch -O /root/rbd.patch
root@controller1:~# cd /usr/lib/python2.7/dist-packages/cinder/volume/drivers/
root@controller1:~# patch -p8 -b < /root/rbd.patch
```

## 2.2. Để horizon hiển thị tab volume backup
`vim /etc/openstack-dashboard/local_settings.py`

Sửa `enable_backup` từ `False` sang `True`

```
OPENSTACK_CINDER_FEATURES = {
    'enable_backup': True,
}
```

Khởi động lại apache và memcached
`service apache2 restart && service memcached restart`

Kiểm tra lại trên Horizon
![Horizon volume backup](/images/cinder_backup_patch_OpsMitaka_CephJewel/volume_backup_1.jpg)

## 2.3. Test việc tạo volume backup
### 2.3.1. Kiểm tra các volume đang có:
`root@controller1:~# cinder --insecure list`

Kết quả:
```
+--------------------------------------+-----------+------+------+-------------+----------+-------------+
|                  ID                  |   Status  | Name | Size | Volume Type | Bootable | Attached to |
+--------------------------------------+-----------+------+------+-------------+----------+-------------+
| 3a4dab6c-e5d1-4ec8-b39c-ef70f6045cb5 | available | test |  1   |   ceph_hdd  |  false   |             |
| bf7855ad-15bf-41de-9262-8d2ca19483a9 | available | long |  1   |   ceph_hdd  |  false   |             |
+--------------------------------------+-----------+------+------+-------------+----------+-------------+
```

### 2.3.2. Tạo volume backup cho volume `test`
```
root@controller1:~# cinder --insecure backup-create --name test-backup2 3a4dab6c-e5d1-4ec8-b39c-ef70f6045cb5

3a4dab6c-e5d1-4ec8-b39c-ef70f6045cb5: id volume long
```

Kết quả:
```
+-----------+--------------------------------------+
|  Property |                Value                 |
+-----------+--------------------------------------+
|     id    | de8f1d24-c8ad-4b5d-b1a5-a68152543129 |
|    name   |             test-backup2             |
| volume_id | 3a4dab6c-e5d1-4ec8-b39c-ef70f6045cb5 |
+-----------+--------------------------------------+
```

### 2.3.3. Trên Ceph mon, kiểm tra RBD Image của bản backup vừa tạo
```
root@ceph:~# rbd -p backups ls

backups: pool chứa các bản backup
```

Kết quả:

```
volume-3a4dab6c-e5d1-4ec8-b39c-ef70f6045cb5.backup.base

3a4dab6c-e5d1-4ec8-b39c-ef70f6045cb5: ID của volume
```

### 2.3.4. List ra các snapshot của bản backup
```
root@ceph:~# rbd snap ls backups/volume-3a4dab6c-e5d1-4ec8-b39c-ef70f6045cb5.backup.base
```

Kết quả:
```
SNAPID NAME                                                              SIZE     
    40 backup.217fc49b-c584-483c-b0da-c9aa5b55e9a3.snap.1494564816.77 1024 MB 
    41 backup.de8f1d24-c8ad-4b5d-b1a5-a68152543129.snap.1494565404.87 1024 MB 
```

Như vậy, Volume này đã có 2 bản backup, bản `backup.de8f1d24-c8ad-4b5d-b1a5-a68152543129.snap.1494565404.87` là backup vừa tạo ở trên.




*Lưu ý:*
 - Khi patch bản vá sẽ sinh ra bản backup của file cấu hình gốc, đặt cùng thư mục. VD: `/usr/lib/python2.7/dist-packages/cinder/volume/drivers/rbd.patch.orig`
 - Muốn quay lại (reverse) file cấu hình gốc, chạy lệnh `patch -R`. VD:  `patch -p8 -R < /root/rbd.patch`

 Tham khảo:

 [1] - http://inter6.tistory.com/8

 [2] - https://bugs.launchpad.net/cinder/+bug/1578036

