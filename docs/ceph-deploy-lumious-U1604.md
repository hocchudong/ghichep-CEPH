## Hướng dẫn cài đặt CEPH sử dụng `ceph-deploy`

### Mục tiêu LAB
- Mô hình này sử dụng 2 server, trong đó:
  - Host Ceph1 cài đặt ceph-deploy, ceph-mon, ceph-osd, ceph-mgr
  - Host Ceph2 cài đặt ceph-osd, ceph-mgr
- LAB này chỉ phù hợp với việc nghiên cứu các tính năng và demo thử nghiệm, không áp dụng được trong thực tế.

## Mô hình 
- Sử dụng mô hình dưới để cài đặt
![img](../images/topology_OPS_CEPH-AIO_Ubuntu14.04.png)

## IP Planning
- Phân hoạch IP cho các máy chủ trong mô hình trên, nếu chỉ dựng CEPH-AIO thì chỉ cần quan tâm tới node CEPH-AIO
![img](../images/ip-planning-OPS-CEPH-AIO-Ubuntu14.04.png)

## Chuẩn bị và môi trường LAB
 
- OS
  - Ubuntu Server 16.04 - 64 bit
  - 05: HDD, trong đó:
    - `vda`: sử dụng để cài OS
    - `vdb`: sử dụng làm OSD (nơi chứa dữ liệu của client)
  - 02 NICs: 
    - `eth0`: dùng để ssh và tải gói cài đặt cho máy chủ CEPH AIO, sử dụng dải 172.16.69.0/24
    - `eth1`: dùng để replicate cho CEPH sử dụng, dải 10.10.20.0/24
    - `eth2`: dùng để client (các máy chủ trong OpenStack) sử dụng, dải 10.10.10.0/24
  
- CEPH Luminous

## Thực hiện trên từng host 

- Thực hiện bằng quyền root
  ```sh
  su -
  ```
  
- Đặt hostname
  ```sh
  echo "ceph1" > /etc/hostname
  hostname -F /etc/hostname
  ```

- Sửa file host 
  ```sh
  echo "10.10.10.70 ceph1" >> /etc/hosts
  echo "10.10.10.71 ceph2" >> /etc/hosts
  ```

- Update OS 
  ```sh
  sudo apt-get update 
  ```

- Tạo user `ceph-deploy` để sử dụng cho việc cài đặt cho CEPH.
  ```sh
  sudo useradd -m -s /bin/bash ceph-deploy
  ```

- Đặt mật mẩu cho user `ceph-deploy`  
  ```sh
  sudo passwd ceph-deploy
  ```

- Phân quyền cho user `ceph-deploy`
  ```sh
  echo "ceph-deploy ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ceph-deploy
  sudo chmod 0440 /etc/sudoers.d/ceph-deploy
  ```

  
## Cài đặt CEPH
Thực hiện trên host ceph1 

- Cài đặt công cụ `ceph-deploy`
  ```sh
  sudo apt-get -y install ceph-deploy
  ```
- Chuyển sang tài khoản `ceph-deploy` để thực hiện cài đặt
  ```sh
  sudo su - ceph-deploy
  ```
- Tạo ssh key cho user ceph-deploy`. Nhấn enter đối với các bước được hỏi trên màn hình.
  ```sh
  ssh-keygen
  ```

- Copy ssh key sang các máy ceph
  ```sh
  ssh-copy-id ceph-deploy@ceph1
  ssh-copy-id ceph-deploy@ceph2
  ```

  - Nhập `Yes` và mật khẩu của user `ceph-deploy` đã tạo ở trước, kết quả như bên dưới
    ```sh
    ceph-deploy@ceph1:~$ ssh-copy-id ceph-deploy@ceph1
    The authenticity of host 'ceph1 (172.16.69.247)' can't be established.
    ECDSA key fingerprint is f2:38:1e:50:44:94:6f:0a:32:a3:23:63:90:7b:53:27.
    Are you sure you want to continue connecting (yes/no)? yes
    /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
    /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
    ceph-deploy@ceph1's password:

    Number of key(s) added: 1

    Now try logging into the machine, with:   "ssh 'ceph-deploy@ceph1'"
    and check to make sure that only the key(s) you wanted were added.
    ```
  
- Tạo các thư mục để công cụ `ceph-deploy` sử dụng để cài đặt CEPH
  ```sh
  cd ~
  mkdir my-cluster
  cd my-cluster
  ```

- Thiết lập các file cấu hình cho CEPH.
  ```sh
  ceph-deploy new ceph1
  ```

- Sau khi thực hiện lệnh trên xong, sẽ thu được 03 file ở dưới (sử dụng lệnh `ll -alh` để xem). Trong đó cần cập nhật file `ceph.conf` để cài đặt CEPH được hoàn chỉnh.
  ```sh
  [ceph-deploy@ceph1 cluster-ceph]$ ls -al
  total 20
  drwxrwxr-x. 2 ceph-deploy ceph-deploy 4096 Sep 15 15:35 .
  drwx------. 4 ceph-deploy ceph-deploy 4096 Sep 15 15:35 ..
  -rw-rw-r--. 1 ceph-deploy ceph-deploy  194 Sep 15 15:35 ceph.conf
  -rw-rw-r--. 1 ceph-deploy ceph-deploy 3028 Sep 15 15:35 ceph-deploy-ceph.log
  -rw-------. 1 ceph-deploy ceph-deploy   73 Sep 15 15:35 ceph.mon.keyring
  ```

- Sửa file ceph.conf như sau:
  ```sh
  [global]
  fsid = 36bb6bc0-5f0d-4418-b403-2d4ca22779a2
  mon_initial_members = ceph1
  mon host = 10.10.10.70
  auth_cluster_required = cephx
  auth_service_required = cephx
  auth_client_required = cephx

  osd pool default size = 2
  osd pool default min size = 1
  osd crush chooseleaf type = 0
  public network = 10.10.10.0/24
  cluster network = 10.10.20.0/24
  bluestore block db size = 5737418240
  bluestore block wal size = 2737418240
  osd objectstore = bluestore
  mon_allow_pool_delete = true
  rbd_cache = false
  osd pool default pg num = 128
  osd pool default pgp num = 128

  [mon.ceph1]
  host = ceph1
  mon addr = 10.10.10.70
 
  [osd]
  osd crush update on start = false
  bluestore = true
  ```
  
- Cài đặt CEPH, thay `ceph1` bằng tên hostname của máy bạn nếu có thay đổi.
  ```sh
  ceph-deploy install --release luminous ceph1 ceph2
  ```

- Chuyển cấu hình ceph.conf sang các host ceph khác
  ```sh
  ceph-deploy --overwrite-conf config push ceph2
  ```

- Cấu hình `MON` (một thành phần của CEPH)
  ```sh
  ceph-deploy mon create-initial
  ```

- Sau khi thực hiện lệnh để cấu hình `MON` xong, sẽ sinh thêm ra 04 file : `ceph.bootstrap-mds.keyring`, `ceph.bootstrap-osd.keyring`, `ceph.client.admin.keyring` và `ceph.bootstrap-rgw.keyring`. Quan sát bằng lệnh `ll -alh`

  ```sh
  ceph-deploy@ceph1:~/my-cluster$ ls -alh
  total 576K
  drwxrwxr-x 2 ceph-deploy ceph-deploy 4.0K Sep 11 21:12 .
  drwxr-xr-x 6 ceph-deploy ceph-deploy 4.0K Sep 11 21:12 ..
  -rw------- 1 ceph-deploy ceph-deploy   71 Sep  7 18:40 ceph.bootstrap-mds.keyring
  -rw------- 1 ceph-deploy ceph-deploy   71 Sep  7 18:40 ceph.bootstrap-mgr.keyring
  -rw------- 1 ceph-deploy ceph-deploy   71 Sep  7 18:40 ceph.bootstrap-osd.keyring
  -rw------- 1 ceph-deploy ceph-deploy   71 Sep  7 18:40 ceph.bootstrap-rgw.keyring
  -rw------- 1 ceph-deploy ceph-deploy  71 Sep  12 17:20 ceph.client.admin.keyring
  -rw-rw-r-- 1 ceph-deploy ceph-deploy  849 Sep 11 20:58 ceph.conf
  -rw-rw-r-- 1 ceph-deploy ceph-deploy 530K Sep 11 20:58 ceph-deploy-ceph.log
  -rw------- 1 ceph-deploy ceph-deploy   73 Sep  7 18:34 ceph.mon.keyring
  -rw-r--r-- 1 root        root        1.7K Oct 15  2015 release.asc
  ```
- Tạo user admin để quản trị ceph cluster
  ```sh  
  ceph-deploy admin ceph1
  sudo chmod +r /etc/ceph/ceph.client.admin.keyring
  ```

- Copy `ceph.bootstrap-osd.keyring` sang tất cả các host ceph
  ```
  scp ceph.bootstrap-osd.keyring ceph1:/var/lib/ceph/bootstrap-osd/ceph.keyring
  scp ceph.bootstrap-osd.keyring ceph2:/var/lib/ceph/bootstrap-osd/ceph.keyring
  ```

Thực hiện trên từng host
- Tạo các OSD cho CEPH, thay `ceph1` bằng tên hostname của máy bạn 
  ```sh
  ceph-deploy disk zap ceph1:/dev/vdb
  ceph-deploy osd prepare ceph1:vdb
  ceph-disk prepare  --bluestore --block.db /dev/vdb  --block.wal /dev/vdb /dev/vdb
  ```
  
- Kiểm tra các phân vùng được tạo ra bằng lệnh `sudo lsblk` (nhớ phải có lệnh sudo vì đang dùng user `ceph-deploy`)
```sh
ceph-deploy@ceph1:~/my-cluster$ sudo lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sr0     11:0    1 1024M  0 rom  
vda    253:0    0   10G  0 disk 
└─vda1 253:1    0   10G  0 part /
vdb    253:16   0   40G  0 disk 
├─vdb1 253:17   0  100M  0 part /var/lib/ceph/osd/ceph-1
├─vdb2 253:18   0   32G  0 part 
├─vdb3 253:19   0  5.4G  0 part 
└─vdb4 253:20   0  2.6G  0 part 
```

Thực hiện trên ceph1
- Kiểm tra trạng thái của CEPH sau khi cài
  ```sh
  ceph -s
  ```

- Kết quả của lệnh trên như sau: 
  ```sh
  ceph-deploy@ceph1:~/my-cluster$ ceph -s
  cluster:
    id:     36bb6bc0-5f0d-4418-b403-2d4ca22779a2
    health: HEALTH_OK
 
  services:
    mon: 1 daemons, quorum ceph1
    mgr: ceph1(active), standbys: ceph2
    osd: 2 osds: 2 up, 2 in
 
  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0 bytes
    usage:   3180 MB used, 116 GB / 119 GB avail
    pgs:     
  ```

- Nếu có dòng `health HEALTH_OK` thì việc cài đặt đã ok.

Ceph-mgr là một thành phần mới của Ceph (xuất hiện từ bản Luminous), chịu trách nhiệm cho việc mirror dữ liệu giữa các ceph cluster và quản lý tài nguyên của Ceph Cluster. Có thể cài đặt Ceph-mgr daemon trên nhiều host, hoạt động theo cơ chế active-passive.

- Cài đặt ceph-mgr trên ceph1
```sh
ceph-deploy mgr create ceph1
```
- Kiểm tra trạng thái của ceph-mgr bằng `ceph -s`
```sh
ceph-deploy@ceph1:~$ ceph -s
  cluster:
    id:     36bb6bc0-5f0d-4418-b403-2d4ca22779a2
    health: HEALTH_OK
 
  services:
    mon: 3 daemons, quorum ceph1,ceph2,ceph3
    mgr: ceph1(active)
    osd: 3 osds: 2 up, 2 in
 
  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0 bytes
    usage:   2132 MB used, 79585 MB / 81717 MB avail
    pgs:     
```
Chú ý dòng `mgr: ceph1(active)`, ceph-mgr daemon trên host ceph1 đã active

- Ceph-mgr hỗ trợ dashboard để quan sát trạng thái của cluster, Enable mgr dashboard trên host ceph1
```sh
ceph mgr module enable dashboard
```

- Truy cập vào mgr dashboard để kiểm tra
![img](../images/ceph_luminous/ceph_mgr_1.jpg)
