## Hướng dẫn cài đặt CEPH sử dụng `ceph-deploy` trên 1 máy duy nhất (CEPH AIO)

### Mục tiêu LAB
- Mô hình này sẽ cài tất cả các thành phần của CEPH lên một máy duy nhất, bao gồm:
  - ceph-deploy
  - ceph-admin
  - mon
  - OSD
- Máy CEPH AIO được cài đặt để có thể sẵn sàng tích hợp với hệ thống OpenStack
- LAB này chỉ phù hợp với việc nghiên cức các tính năng và demo thử nghiệm, không áp dụng được trong thực tế.

## Mô hình 
- Sử dụng mô hình dưới để cài đặt CEPH AIO, nếu chỉ dựng CEPH AIO thì chỉ cần một máy chủ để cài đặt CEPH. 
![img](../images/topology_OPS_CEPH-AIO_Ubuntu14.04.png)

## IP Planning
- Phân hoạch IP cho các máy chủ trong mô hình trên, nếu chỉ dựng CEPH-AIO thì chỉ cần quan tâm tới node CEPH-AIO
![img](../images/ip-planning-OPS-CEPH-AIO-Ubuntu14.04.png)

## Chuẩn bị và môi trường LAB
 
- OS
  - Ubuntu Server 14.04 - 64 bit
  - 05: HDD, trong đó:
    - `sda`: sử dụng để cài OS
    - `sdb`: sử dụng làm `journal` (Journal là một lớp cache khi client ghi dữ liệu, thực tế thường dùng ổ SSD để làm cache)
    - `sdc, sdd, sde`: sử dụng làm OSD (nơi chứa dữ liệu của client)
  - 02 NICs: 
    - `eth0`: dùng để client (các máy chủ trong OpenStack) sử dụng, dải 10.10.10.0/24
    - `eth1`: dùng để ssh và tải gói cài đặt cho máy chủ CEPH AIO, sử dụng dải 172.16.69.0/24
    - `eth2`: dùng để replicate cho CEPH sử dụng, dải 10.10.30.0/24
  
- CEPH Jewel

## Cài đặt CEPH

- Thực hiện bằng quyền root
  ```sh
  su -
  ```
  
- Đặt hostname cho máy cài AIO
  ```sh
  echo "cephaio" > /etc/hostname
  hostname -F /etc/hostname
  ```

- Sửa file host 
  ```sh
  echo "10.10.10.71 cephaio" >> /etc/hosts
  ```

- Khai báo Repo cho CEPH đối với Ubuntu Server 14.04
  ```sh
  wget -q -O- 'https://download.ceph.com/keys/release.asc' | sudo apt-key add -
  
  echo deb http://download.ceph.com/debian-jewel/ trusty main | sudo tee /etc/apt/sources.list.d/ceph.list
  ```
  
  
- Update OS 
  ```sh
  sudo apt-get update 
  ```

- Cài đặt công cụ `ceph-deploy`
  ```sh
  sudo apt-get -y install ceph-deploy
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

- Chuyển sang tài khoản `ceph-deploy` để thực hiện cài đặt
  ```sh
  sudo su - ceph-deploy
  ```

- Tạo ssh key cho user ceph-deploy`. Nhấn enter đối với các bước được hỏi trên màn hình.
  ```sh
  ssh-keygen
  ```

- Copy ssh key để sử dụng, thay `cephaio` bằng tên hostname của máy bạn nếu có thay đổi.
  ```sh
  ssh-copy-id ceph-deploy@cephaio
  ```

  - Nhập `Yes` và mật khẩu của user `ceph-deploy` đã tạo ở trước, kết quả như bên dưới
    ```sh
    ceph-deploy@cephaio:~$ ssh-copy-id ceph-deploy@cephaio
    The authenticity of host 'cephaio (172.16.69.247)' can't be established.
    ECDSA key fingerprint is f2:38:1e:50:44:94:6f:0a:32:a3:23:63:90:7b:53:27.
    Are you sure you want to continue connecting (yes/no)? yes
    /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
    /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
    ceph-deploy@cephaio's password:

    Number of key(s) added: 1

    Now try logging into the machine, with:   "ssh 'ceph-deploy@cephaio'"
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
  ceph-deploy new cephaio
  ```

- Sau khi thực hiện lệnh trên xong, sẽ thu được 03 file ở dưới (sử dụng lệnh `ll -alh` để xem). Trong đó cần cập nhật file `ceph.conf` để cài đặt CEPH được hoàn chỉnh.
  ```sh
  ceph-deploy@cephaio:~/my-cluster$ ls -alh
  total 20K
  drwxrwxr-x 2 ceph-deploy ceph-deploy 4.0K Apr 12 17:11 .
  drwxr-xr-x 5 ceph-deploy ceph-deploy 4.0K Apr 12 17:11 ..
  -rw-rw-r-- 1 ceph-deploy ceph-deploy  198 Apr 12 17:11 ceph.conf
  -rw-rw-r-- 1 ceph-deploy ceph-deploy 3.2K Apr 12 17:11 ceph-deploy-ceph.log
  -rw------- 1 ceph-deploy ceph-deploy   73 Apr 12 17:11 ceph.mon.keyring
  ceph-deploy@cephaio:~/my-cluster$
  ```

- Thêm các dòng dưới vào file `ceph.conf` vừa được tạo ra ở trên
  ```sh
  echo "osd pool default size = 2" >> ceph.conf
  echo "osd crush chooseleaf type = 0" >> ceph.conf
  echo "osd journal size = 8000" >> ceph.conf
  echo "public network = 10.10.10.0/24" >> ceph.conf
  echo "cluster network = 10.10.30.0/24" >> ceph.conf
  ```
  
- Cài đặt CEPH, thay `cephaio` bằng tên hostname của máy bạn nếu có thay đổi.
  ```sh
  ceph-deploy install cephaio
  ```

- Cấu hình `MON` (một thành phần của CEPH)
  ```sh
  ceph-deploy mon create-initial
  ```
- Sau khi thực hiện lệnh để cấu hình `MON` xong, sẽ sinh thêm ra 03 file : `ceph.bootstrap-mds.keyring`, `ceph.bootstrap-osd.keyring` và `ceph.bootstrap-rgw.keyring`. Quan sát bằng lệnh `ll -alh`

  ```sh
  ceph-deploy@cephaio:~/my-cluster$ ls -alh
  total 96K
  drwxrwxr-x 2 ceph-deploy ceph-deploy 4.0K Apr 12 17:20 .
  drwxr-xr-x 5 ceph-deploy ceph-deploy 4.0K Apr 12 17:11 ..
  -rw------- 1 ceph-deploy ceph-deploy  113 Apr 12 17:20 ceph.bootstrap-mds.keyring
  -rw------- 1 ceph-deploy ceph-deploy  113 Apr 12 17:20 ceph.bootstrap-osd.keyring
  -rw------- 1 ceph-deploy ceph-deploy  113 Apr 12 17:20 ceph.bootstrap-rgw.keyring
  -rw------- 1 ceph-deploy ceph-deploy  129 Apr 12 17:20 ceph.client.admin.keyring
  -rw-rw-r-- 1 ceph-deploy ceph-deploy  342 Apr 12 17:14 ceph.conf
  -rw-rw-r-- 1 ceph-deploy ceph-deploy  54K Apr 12 17:20 ceph-deploy-ceph.log
  -rw------- 1 ceph-deploy ceph-deploy   73 Apr 12 17:11 ceph.mon.keyring
  -rw-r--r-- 1 root        root        1.7K Oct 16  2015 release.asc
  ```

- Tạo các OSD cho CEPH, thay `cephaio` bằng tên hostname của máy bạn 
  ```sh
  ceph-deploy osd prepare cephaio:sdc:/dev/sdb
  ceph-deploy osd prepare cephaio:sdd:/dev/sdb
  ```

- Active các OSD vừa tạo ở trên
  ```sh
  ceph-deploy osd activate cephaio:/dev/sdc1:/dev/sdb1
  ceph-deploy osd activate cephaio:/dev/sdd1:/dev/sdb2
  ```
  
- Kiểm tra các phân vùng được tạo ra bằng lệnh `sudo lsblk` (nhớ phải có lệnh sudo vì đang dùng user `ceph-deploy`)
```sh
ceph-deploy@cephaio:~/my-cluster$ sudo lsblk
NAME                            MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda                               8:0    0    50G  0 disk
├─sda1                            8:1    0   243M  0 part /boot
├─sda2                            8:2    0     1K  0 part
└─sda5                            8:5    0  49.8G  0 part
  ├─cephadmin--vg-root (dm-0)   252:0    0  45.7G  0 lvm  /
  └─cephadmin--vg-swap_1 (dm-1) 252:1    0     4G  0 lvm
sdb                               8:16   0    30G  0 disk
├─sdb1                            8:17   0   7.8G  0 part
└─sdb2                            8:18   0   7.8G  0 part
sdc                               8:32   0    30G  0 disk
└─sdc1                            8:33   0    30G  0 part /var/lib/ceph/osd/ceph-0
sdd                               8:48   0    30G  0 disk
└─sdd1                            8:49   0    30G  0 part /var/lib/ceph/osd/ceph-1
sr0                              11:0    1   574M  0 rom
ceph-deploy@cephaio:~/my-cluster$
````
- Tạo file config và key
  ```sh
  ceph-deploy admin cephaio
  ```

- Phân quyền cho file `/etc/ceph/ceph.client.admin.keyring`
  ```sh
  sudo chmod +r /etc/ceph/ceph.client.admin.keyring
  ```
  
- Kiểm tra trạng thái của CEPH sau khi cài
  ```sh
  ceph -s
  ```

- Kết quả của lệnh trên như sau: 
  ```sh
  ceph-deploy@cephaio:~/my-cluster$ ceph -s
      cluster 17321823-d3cc-4781-97c1-66228d12b007
       health HEALTH_OK
       monmap e1: 1 mons at {cephaio=172.16.69.247:6789/0}
              election epoch 3, quorum 0 cephaio
       osdmap e10: 2 osds: 2 up, 2 in
              flags sortbitwise,require_jewel_osds
        pgmap v17: 64 pgs, 1 pools, 0 bytes data, 0 objects
              68960 kB used, 61340 MB / 61407 MB avail
                    64 active+clean
  ceph-deploy@cephaio:~/my-cluster$
  ```

- Nếu có dòng `health HEALTH_OK` thì việc cài đặt đã ok.
