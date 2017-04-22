# Hướng dẫn cài đặt CEPH sử dụng `ceph-deploy` trên 1 máy duy nhất (CEPH AIO)

## 1. Mục tiêu LAB
- Mô hình này sẽ cài tất cả các thành phần của CEPH lên một máy duy nhất, bao gồm:
  - ceph-deploy
  - ceph-admin
  - mon
  - OSD
- LAB này chỉ phù hợp với việc nghiên cức các tính năng và demo thử nghiệm, không áp dụng được trong thực tế.
- Việc dựng CEPH-AIO có thể chạy theo đúng mô hình này hoặc theo mô hình để tích hợp cùng OpenStack tại tài liệu này [link tài liệu]

## 2. Mô hình 
- Sử dụng mô hình dưới để cài đặt CEPH AIO, nếu chỉ dựng CEPH AIO thì chỉ cần một máy chủ để cài đặt CEPH. 
![img](../images/topology_CEPH_AIO_CentOS7.2.png)

## 3. IP Planning
- Phân hoạch IP cho các máy chủ trong mô hình trên, nếu chỉ dựng CEPH-AIO thì chỉ cần quan tâm tới node CEPH-AIO
![img](../images/ip-Planning-CEPH_AIO_CentOS7.2.png)

## 4. Chuẩn bị và môi trường LAB
 
- OS
  - CentOS Server 7.2 64 bit
  - 05: HDD, trong đó:
    - `sda`: sử dụng để cài OS
    - `sdb`: sử dụng làm `journal` (Journal là một lớp cache khi client ghi dữ liệu, thực tế thường dùng ổ SSD để làm cache)
    - `sdc, sdd, sde`: sử dụng làm OSD (nơi chứa dữ liệu của client)
  - 02 NICs: 
    - `eno16777728`: dùng client (các máy trong OpenStack) sử dụng, sử dụng dải 10.10.10.0/24
    - `eno33554952`: dùng để ssh và tải gói cho máy chủ CEPH AIO, sử dụng dải172.16.69.0/24
    - `eno50332176`: dùng để replicate cho CEPH, dải 10.10.30.0/24
  
- CEPH Jewel

## 5. Cài đặt CEPH trên máy chủ CEPH
- Nếu chưa login vào máy chủ CEPH-AIO bằng quyền `root` thì thực hiện chuyển sang quyền `root`
  ```sh
  su -
  ```

- Update các gói cho máy chủ 
  ```sh
  yum update -y
  ```

- Đặt hostname cho máy cài AIO
  ```sh
  hostnamectl set-hostname cephaio  
  ```
- Thiết lập IP cho máy CEPH AIO
  ```sh
  echo "Setup IP  eno16777728"
  nmcli c modify eno16777728 ipv4.addresses 10.10.10.71/24
  nmcli c modify eno16777728 ipv4.method manual
  nmcli con mod eno16777728 connection.autoconnect yes

  echo "Setup IP  eno33554952"
  nmcli c modify eno33554952 ipv4.addresses 172.16.69.71/24
  nmcli c modify eno33554952 ipv4.gateway 172.16.69.1
  nmcli c modify eno33554952 ipv4.dns 8.8.8.8
  nmcli c modify eno33554952 ipv4.method manual
  nmcli con mod eno33554952 connection.autoconnect yes

  echo "Setup IP  eno50332176"
  nmcli c modify eno50332176 ipv4.addresses 10.10.30.71/24
  nmcli c modify eno50332176 ipv4.method manual
  nmcli con mod eno50332176 connection.autoconnect yes
  ```
  
- Cấu hình các thành phần mạng cơ bản
  ```sh
  sudo systemctl disable firewalld
  sudo systemctl stop firewalld
  sudo systemctl disable NetworkManager
  sudo systemctl stop NetworkManager
  sudo systemctl enable network
  sudo systemctl start network
  ```

- Vô hiệu hóa Selinux
  ```sh
  sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
  ```

- Sửa file host 
  ```sh
  echo "10.10.10.71 cephaio" >> /etc/hosts
  ```

- Khởi động lại máy chủ sau khi cấu hình cơ bản.
  ```sh
  init 6
  ```
 
- Đăng nhập lại bằng quyền `root` sau khi máy chủ reboot xong.

- Khai báo repos cho CEPH 
  ```sh
  sudo yum install -y yum-utils
  sudo yum-config-manager --add-repo https://dl.fedoraproject.org/pub/epel/7/x86_64/ 
  sudo yum install --nogpgcheck -y epel-release 
  sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 
  sudo rm /etc/yum.repos.d/dl.fedoraproject.org*
  ```
   
  ```sh
  cat << EOF > /etc/yum.repos.d/ceph-deploy.repo
  [Ceph-noarch]
  name=Ceph noarch packages
  baseurl=http://download.ceph.com/rpm-jewel/el7/noarch
  enabled=1
  gpgcheck=1
  type=rpm-md
  gpgkey=https://download.ceph.com/keys/release.asc
  priority=1
  EOF
  ```

- Update sau khi khai báo repo
  ```sh
  sudo yum -y update
  ```
  
- Tạo user `ceph-deploy`
  ```sh
  sudo useradd -d /home/ceph-deploy -m ceph-deploy
  ```  
  
- Đặt mật khẩu cho user `ceph-deploy`
  ```sh
  sudo passwd ceph-deploy
  ```
  
- Phân quyền cho user `ceph`
  ```sh
  echo "ceph-deploy ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ceph-deploy
  chmod 0440 /etc/sudoers.d/ceph-deploy

  sed -i s'/Defaults requiretty/#Defaults requiretty'/g /etc/sudoers
  ```

- Chuyển sang user `ceph-deploy`
  ```sh
  su - ceph-deploy
  ```

- Tạo ssh key cho user `ceph-deploy`
  ```sh
  ssh-keygen -t rsa
  ```

- Thực hiện copy ssh key, nhập yes và mật khẩu của user `ceph-deploy` ở bước trước.
  ```sh
  ssh-copy-id ceph-deploy@cephaio
  ```

- Cài đặt `ceph-deploy` 
  ```sh
  sudo yum install -y ceph-deploy
  ```

- Tạo thư mục để chứa các file cần thiết cho việc cài đặt CEPH 
  ```sh
  mkdir cluster-ceph
  cd cluster-ceph
  ```

- Thiết lập các file cấu hình cho CEPH.
  ```sh
  ceph-deploy new cephaio
  ```

- Sau khi thực hiện lệnh trên xong, sẽ thu được 03 file ở dưới (sử dụng lệnh `ll -alh` để xem). Trong đó cần cập nhật file `ceph.conf` để cài đặt CEPH được hoàn chỉnh.
  ```sh
  [ceph-deploy@cephaio cluster-ceph]$ ls -alh
  total 16K
  drwxrwxr-x. 2 ceph-deploy ceph-deploy   72 Apr 14 09:36 .
  drwx------. 4 ceph-deploy ceph-deploy 4.0K Apr 14 09:36 ..
  -rw-rw-r--. 1 ceph-deploy ceph-deploy  196 Apr 14 09:36 ceph.conf
  -rw-rw-r--. 1 ceph-deploy ceph-deploy 3.0K Apr 14 09:36 ceph-deploy-ceph.log
  -rw-------. 1 ceph-deploy ceph-deploy   73 Apr 14 09:36 ceph.mon.keyring
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
  
  - Sau khi cài xong, nếu thành công sẽ có kết quả như sau.
    ```sh
    [cephaio][DEBUG ] Complete!
    [cephaio][INFO  ] Running command: sudo ceph --version
    [cephaio][DEBUG ] ceph version 10.2.7 (50e863e0f4bc8f4b9e31156de690d765af245185
    ```

- Cấu hình `MON` (một thành phần của CEPH)
  ```sh
  ceph-deploy mon create-initial
  ```

- Sau khi thực hiện lệnh để cấu hình `MON` xong, sẽ sinh thêm ra 04 file : 
  - `ceph.bootstrap-mds.keyring`
  - `ceph.bootstrap-osd.keyring` 
  - `ceph.bootstrap-rgw.keyring`
  - `ceph.client.admin.keyring`

- Quan sát bằng lệnh `ll -alh`
  ```sh
  [ceph-deploy@cephaio cluster-ceph]$ ls -lah
  total 160K
  drwxrwxr-x. 2 ceph-deploy ceph-deploy 4.0K Apr 14 10:28 .
  drwx------. 4 ceph-deploy ceph-deploy 4.0K Apr 14 10:18 ..
  -rw-------. 1 ceph-deploy ceph-deploy  113 Apr 14 10:28 ceph.bootstrap-mds.keyring
  -rw-------. 1 ceph-deploy ceph-deploy  113 Apr 14 10:28 ceph.bootstrap-osd.keyring
  -rw-------. 1 ceph-deploy ceph-deploy  113 Apr 14 10:28 ceph.bootstrap-rgw.keyring
  -rw-------. 1 ceph-deploy ceph-deploy  129 Apr 14 10:28 ceph.client.admin.keyring
  -rw-rw-r--. 1 ceph-deploy ceph-deploy  339 Apr 14 10:18 ceph.conf
  -rw-rw-r--. 1 ceph-deploy ceph-deploy  66K Apr 14 10:28 ceph-deploy-ceph.log
  -rw-------. 1 ceph-deploy ceph-deploy   73 Apr 14 10:18 ceph.mon.keyring
  ```

- Tạo các OSD cho CEPH, thay `cephaio` bằng tên hostname của máy bạn 
  ```sh
  ceph-deploy osd prepare cephaio:sdc:/dev/sdb
  ceph-deploy osd prepare cephaio:sdd:/dev/sdb
  ceph-deploy osd prepare cephaio:sde:/dev/sdb
  ```

- Active các OSD vừa tạo ở trên
  ```sh
  ceph-deploy osd activate cephaio:/dev/sdc1:/dev/sdb1
  ceph-deploy osd activate cephaio:/dev/sdd1:/dev/sdb2
  ceph-deploy osd activate cephaio:/dev/sde1:/dev/sdb3
  ```

- Sau khi cấu hình các OSD xong, kiểm tra xem các phân vùng bằng lệnh `sudo lsblk`, nếu thành công, kết quả như sau
  ```sh
  [ceph-deploy@cephaio cluster-ceph]$ lsblk
  NAME            MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
  sda               8:0    0   60G  0 disk
  ├─sda1            8:1    0  500M  0 part /boot
  └─sda2            8:2    0 59.5G  0 part
    ├─centos-root 253:0    0 35.9G  0 lvm  /
    ├─centos-swap 253:1    0    6G  0 lvm  [SWAP]
    └─centos-home 253:2    0 17.5G  0 lvm  /home
  sdb               8:16   0   50G  0 disk
  ├─sdb1            8:17   0  7.8G  0 part
  ├─sdb2            8:18   0  7.8G  0 part
  └─sdb3            8:19   0  7.8G  0 part
  sdc               8:32   0   50G  0 disk
  └─sdc1            8:33   0   50G  0 part /var/lib/ceph/osd/ceph-0
  sdd               8:48   0   50G  0 disk
  └─sdd1            8:49   0   50G  0 part /var/lib/ceph/osd/ceph-1
  sde               8:64   0   50G  0 disk
  └─sde1            8:65   0   50G  0 part /var/lib/ceph/osd/ceph-2
  sr0              11:0    1  603M  0 rom
  [ceph-deploy@cephaio cluster-ceph]$
  ```

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
  
  - Kết của lệnh `ceph -s`
    ```sh
    [ceph-deploy@cephaio cluster-ceph]$   ceph -s
      cluster ae46be36-dee3-4bb9-9448-91aa148b301e
       health HEALTH_OK
       monmap e1: 1 mons at {cephaio=10.10.10.71:6789/0}
              election epoch 3, quorum 0 cephaio
       osdmap e15: 3 osds: 3 up, 3 in
              flags sortbitwise,require_jewel_osds
        pgmap v34: 64 pgs, 1 pools, 0 bytes data, 0 objects
              100 MB used, 149 GB / 149 GB avail
                    64 active+clean
  ```
  
- Kiểm tra các OSD bằng lệnh `ceph osd tree`, kết quả như sau:
  ```sh
  [ceph-deploy@cephaio cluster-ceph]$ ceph osd tree
  ID WEIGHT  TYPE NAME        UP/DOWN REWEIGHT PRIMARY-AFFINITY
  -1 0.14639 root default
  -2 0.14639     host cephaio
   0 0.04880         osd.0         up  1.00000          1.00000
   1 0.04880         osd.1         up  1.00000          1.00000
   2 0.04880         osd.2         up  1.00000          1.00000
  ```
  
- Kiểm tra bằng lệnh `ceph health`, kết quả như sau là ok.
  ```sh
  [ceph-deploy@cephaio cluster-ceph]$ ceph health
  HEALTH_OK
  ```

## 6. Cấu hình ceph để client sử dụng
### 6.1. Cấu hình client -  CentOS 7.x 64 bit
- Thực hiện map và mount các rbd cho client là CentOS 7.x

#### Bước 1: Chuẩn bị trên client 
- Login vào máy chủ và chuyển sang quyền `root`
  ```sh
  su -
  ```

- Update các gói cho máy chủ 
  ```sh
  yum update -y
  ```

- Đặt hostname cho máy cài CentOS Client1
  ```sh
  hostnamectl set-hostname centos7client1  
  ```
- Thiết lập IP cho máy CEPH AIO
  ```sh
  echo "Setup IP  eno16777728"
  nmcli c modify eno16777728 ipv4.addresses 10.10.10.51/24
  nmcli c modify eno16777728 ipv4.method manual
  nmcli con mod eno16777728 connection.autoconnect yes


  echo "Setup IP  eno33554952"
  nmcli c modify eno33554952 ipv4.addresses 172.16.69.51/24
  nmcli c modify eno33554952 ipv4.gateway 172.16.69.1
  nmcli c modify eno33554952 ipv4.dns 8.8.8.8
  nmcli c modify eno33554952 ipv4.method manual
  nmcli con mod eno16777728 connection.autoconnect yes
  ```
  
- Cấu hình các thành phần mạng cơ bản
  ```sh
  sudo systemctl disable firewalld
  sudo systemctl stop firewalld
  sudo systemctl disable NetworkManager
  sudo systemctl stop NetworkManager
  sudo systemctl enable network
  sudo systemctl start network
  ```

- Vô hiệu hóa Selinux
  ```sh
  sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
  ```

- Sửa file host 
  ```sh
  echo "10.10.10.71 cephaio" >> /etc/hosts
  echo "10.10.10.51 centos7client1" >> /etc/hosts
  ```

- Khởi động lại máy chủ sau khi cấu hình cơ bản.
  ```sh
  init 6
  ```
 
- Đăng nhập lại bằng quyền `root` sau khi máy chủ reboot xong.

- Khai báo repos cho CEPH 
  ```sh
  sudo yum install -y yum-utils
  sudo yum-config-manager --add-repo https://dl.fedoraproject.org/pub/epel/7/x86_64/ 
  sudo yum install --nogpgcheck -y epel-release 
  sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 
  sudo rm /etc/yum.repos.d/dl.fedoraproject.org*
  ```
   
  ```sh
  cat << EOF > /etc/yum.repos.d/ceph-deploy.repo
  [Ceph-noarch]
  name=Ceph noarch packages
  baseurl=http://download.ceph.com/rpm-jewel/el7/noarch
  enabled=1
  gpgcheck=1
  type=rpm-md
  gpgkey=https://download.ceph.com/keys/release.asc
  priority=1
  EOF
  ```

- Update sau khi khai báo repo
  ```sh
  sudo yum -y update
  ```
  
- Tạo user `ceph-deploy`
  ```sh
  sudo useradd -d /home/ceph-deploy -m ceph-deploy
  ```  
  
- Đặt mật khẩu cho user `ceph-deploy`
  ```sh
  sudo passwd ceph-deploy
  ```
  
- Phân quyền cho user `ceph`
  ```sh
  echo "ceph-deploy ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ceph-deploy
  chmod 0440 /etc/sudoers.d/ceph-deploy

  sed -i s'/Defaults requiretty/#Defaults requiretty'/g /etc/sudoers
  ```

#### Bước 2: Đứng trên node CEPH-AIO thực hiện các lệnh dưới.
- Login vào máy chủ CEPH AIO và thực hiện các lệnh dưới
  - Chuyển sang tài khoản `root`
    ```sh
    su -
    ```
  - Khai báo thêm host của client 
    ```sh
    echo "10.10.10.51 centos7client1" >> /etc/hosts
    ```
    
  - Chuyển sang tài khoản `ceph-deploy` để thực hiện cài đặt
    ```sh
    sudo su - ceph-deploy
    
    cd cluster-ceph
    ```
    
  - Copy ssh key đã tạo trước đó sang client, gõ `yes` và nhập mật khẩu của user `ceph-deploy` phía client đã tạo trước đó.
    ```sh
    ssh-copy-id ceph-deploy@centos7client1
    ```
  
- Thực hiện copy file config cho ceph và key sang client
  ```sh
  ceph-deploy install centos7client1 
  ```
  
  - Sau khi kết thúc quá trình cài đặt cho client, nếu thành công sẽ có báo kết quả như sau ở màn hình.
    ```sh
    [centos7client1][DEBUG ] Complete!
    [centos7client1][INFO  ] Running command: sudo ceph --version
    [centos7client1][DEBUG ] ceph version 10.2.7 (50e863e0f4bc8f4b9e31156de690d765af245185)
    ```
  - Tiếp tục thực hiện lệnh để copy các file cần thiết từ node CEPH-AIO sang client
    ```sh
    ceph-deploy admin centos7client1
    ```   
  - Thực hiện xong lệnh trên, ceph-deploy sẽ copy các file cần thiết vào thư mục `/etc/ceph` của client. Chuyển sang client để thực hiện tiếp các thao tác. 
  
#### Bước 3: Thực hiện các thao tác để sử dụng rbd trên Client.
- Đăng nhập vào tài khoản `root` của client (Trong phần này client là CentOS 7)
- Thực hiện việc kiểm tra các gói `ceph` đã được cài bằng lệnh `rpm -qa | grep ceph`
  ```sh
  [root@centos7client1 yum.repos.d]# rpm -qa | grep ceph
  python-cephfs-10.2.7-0.el7.x86_64
  ceph-base-10.2.7-0.el7.x86_64
  ceph-selinux-10.2.7-0.el7.x86_64
  ceph-osd-10.2.7-0.el7.x86_64
  ceph-mds-10.2.7-0.el7.x86_64
  ceph-radosgw-10.2.7-0.el7.x86_64
  libcephfs1-10.2.7-0.el7.x86_64
  ceph-common-10.2.7-0.el7.x86_64
  ceph-mon-10.2.7-0.el7.x86_64
  ceph-10.2.7-0.el7.x86_64
  ceph-release-1-1.el7.noarch
  ```

- Kích hoạt rbdmap để khởi động cùng OS.
  ```sh
  [root@centos7client1 ceph]# systemctl enable rbdmap
  Created symlink from /etc/systemd/system/multi-user.target.wants/rbdmap.service to /usr/lib/systemd/system/rbdmap.service.
  ```
  
- Tạo 1 RBD có dung lượng 10Gb
  ```sh
  rbd create disk02 --size 10240
  ```
  - Có thể kiểm tra lại kết quả tạo bằng lệnh
    ```sh
    rbd ls -l
    ```
 
- Chạy lệnh dưới để fix lỗi `RBD image feature set mismatch. You can disable features unsupported by the kernel with "rbd feature disable".` ở bản  CEPH Jewel. Lưu ý từ khóa `disk01` trong lệnh, nó là tên image của rbd được tạo.
  ```sh
  rbd feature disable rbd/disk01 fast-diff,object-map,exclusive-lock,deep-flatten
  ```

  
- Thực hiện map rbd vừa tạo 
  ```sh
  sudo rbd map disk01
  ```
  - Kiểm tra lại kết quả map bằng lệnh dưới
    ```sh
    rbd showmapped 
    ```
  
- Thực hiện format disk vừa được map
  ```sh
  sudo mkfs.xfs /dev/rbd0
  ```
  
- Thực hiện mount disk vừa được format để sử dụng (mount vào thư mục `mnt` của client)
  ```sh
  sudo mount /dev/rbd0 /mnt
  ```

- Kiểm tra lại việc mount đã thành công hay chưa bằng một trong các lệnh dưới
  ```sh
  df -hT
  ```

  ```sh
  lsblk
  ```
- Tạo thử 1 file 5GB vào thư mục `/mnt` bằng lệnh `dd`. Lệnh này thực hiện trên client.
  ```sh
  cd /mnt 
  
  dd if=/dev/zero of=test bs=1M count=5000
  ```
  - Nếu muốn quan sát quá trình ghi đọc trên server CEPH-AIO thì thực hiện lệnh `ceph -w` 

- Mặc định khi khởi động lại thì việc map rbd sẽ bị mất, xử lý như sau:
  - Mở file /etc/ceph/rbdmap và thêm dòng dưới
    ```sh
    rbd/disk01   id=admin,keyring=/etc/ceph/ceph.client.admin.keyring
    ```
    - Lưu ý cần khai báo pool `rbd` và tên images là `disk01` đã được khai báo ở bên trên.
    
  - Sửa file `/etc/fstab` để việc mount được thực hiện mỗi khi khởi động lại OS, thêm dòng
    ```sh
    /dev/rbd0   /mnt  xfs defaults,noatime,_netdev        0       0
    ```
    
  - Trong quá trình lab với client là ubuntu và centos tôi gặp hiện tượng khởi động lại Client 2 lần thì mới đăng nhập được, chưa hiểu tại sao lại bị tình trạng như vậy.

### 6.2. Cấu hình client - Ubuntu Server 14.04 64 bit
- Bước này sẽ hướng dẫn sử dụng RBD của CEPH để cung cấp cho các Client

#### Bước 1: Chuẩn bị trên Client 

- Login vào máy chủ client và chuyển sang quyền `root`
  ```sh
  su -
  ```

- Cấu hình IP cho các NICs theo IP Planning
  ```sh
  cp /etc/network/interfaces  /etc/network/interfaces.orig
  
  
  cat << EOF > /etc/network/interfaces
  # This file describes the network interfaces available on your system
  # and how to activate them. For more information, see interfaces(5).

  # The loopback network interface
  auto lo
  iface lo inet loopback

  # The primary network interface
  auto eth0
  iface eth0 inet static
  address 10.10.10.52
  netmask 255.255.255.0

  auto eth1
  iface eth1 inet static
  address 172.16.69.52
  gateway 172.16.69.1
  netmask 255.255.255.0
  dns-nameservers 8.8.8.8
  EOF
  ```

- Thiết lập hostname
  ```sh
  echo "ubuntuclient2" > /etc/hostname
  hostname -F /etc/hostname
  ```
- Sửa file host 
  ```sh
  echo "10.10.10.71 cephaio" >> /etc/hosts
  echo "10.10.10.52 ubuntuclient2" >> /etc/hosts
  ```
- Khai báo Repo cho CEPH đối với Ubuntu Server 14.04
  ```sh
  wget -q -O- 'https://download.ceph.com/keys/release.asc' | sudo apt-key add -
  echo deb http://download.ceph.com/debian-jewel/ trusty main | sudo tee /etc/apt/sources.list.d/ceph.list
  ```
- Thực hiện update sau khi khai báo repos và khởi động lại
  ```sh
  apt-get update -y && apt-get upgrade -y && apt-get dist-upgrade -y && init 6
  ```

- Cài đặt các gói ceph phía client
  ```sh
  sudo apt-get install -y python-rbd ceph-common
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

#### Bước 2: Chuẩn bị trên Server CEPH 

- Login vào máy chủ CEPH AIO và thực hiện các lệnh dưới
  - Khai báo thêm host của client 
    ```sh
    echo "10.10.10.52 ubuntuclient2" >> /etc/hosts
    ```
    
  - Chuyển sang tài khoản `ceph-deploy` để thực hiện cài đặt
    ```sh
    sudo su - ceph-deploy
    
    cd cluster-ceph
    ```
    
  - Copy ssh key đã tạo trước đó sang client, gõ `yes` và nhập mật khẩu của user `ceph-deploy` phía client đã tạo trước đó.
    ```sh
    ssh-copy-id ceph-deploy@ubuntuclient2
    ```
  
- Thực hiện copy file config cho ceph và key sang client
```sh
ceph-deploy admin ubuntuclient2
```

#### Bước 3: Tạo các RBD trên client 
- Login vào mà hình của máy client để thực hiện các bước tiếp theo như sau:
- Chuyển sang quyền `root`
  ```sh
  su -
  ```
- Phân quyền cho file `/etc/ceph/ceph.client.admin.keyring` vừa được copy sang ở trên
  ```sh
  sudo chmod +r /etc/ceph/ceph.client.admin.keyring
  ```

- Kiểm tra trạng thái của CEPH từ client
  ```sh
  ceph -s
  ```
  - Kết quả là:
    ```sh
    root@ubuntuclient2:/etc/ceph# ceph -s
        cluster 2406781c-afdf-40c5-83a4-3ae49b2a3dea
         health HEALTH_OK
         monmap e1: 1 mons at {cephaio=10.10.10.71:6789/0}
                election epoch 4, quorum 0 cephaio
         osdmap e24: 3 osds: 3 up, 3 in
                flags sortbitwise,require_jewel_osds
          pgmap v3484: 64 pgs, 1 pools, 0 bytes data, 1 objects
                101 MB used, 149 GB / 149 GB avail
                      64 active+clean
    ```

- Khởi động rbdmap cùng OS
  ```sh
  sudo update-rc.d rbdmap defaults
  ```

- Cài đặt thêm gói `xfsprogs` để có thể sử dụng lệnh `mkfs.xfs`
  ```sh
  sudo apt-get install xfsprogs
  ```
- Tạo 1 RBD có dung lượng 10Gb
  ```sh
  rbd create disk02 --size 10240
  ```
  - Có thể kiểm tra lại kết quả tạo bằng lệnh
    ```sh
    rbd ls -l
    ```
 
- Chạy lệnh dưới để fix lỗi `RBD image feature set mismatch. You can disable features unsupported by the kernel with "rbd feature disable".` ở bản  CEPH Jewel. Lưu ý từ khóa `disk02` trong lệnh, nó là tên image của rbd được tạo.
  ```sh
  rbd feature disable rbd/disk02 fast-diff,object-map,exclusive-lock,deep-flatten
  ```

  
- Thực hiện map rbd vừa tạo 
  ```sh
  sudo rbd map disk02 
  ```
  - Kiểm tra lại kết quả map bằng lệnh dưới
    ```sh
    rbd showmapped 
    ```
  
- Thực hiện format disk vừa được map
  ```sh
  sudo mkfs.xfs /dev/rbd1
  ```
  
- Thực hiện mount disk vừa được format để sử dụng (mount vào thư mục `mnt` của client)
  ```sh
  sudo mount /dev/rbd1 /mnt
  ```

- Kiểm tra lại việc mount đã thành công hay chưa bằng một trong các lệnh dưới
  ```sh
  df -hT
  ```

  ```sh
  lsblk
  ```
- Tạo thử 1 file 5GB vào thư mục `/mnt` bằng lệnh `dd`. Lệnh này thực hiện trên client.
  ```sh
  cd /mnt 
  
  dd if=/dev/zero of=test bs=1M count=5000
  ```
  - Nếu muốn quan sát quá trình ghi đọc trên server CEPH-AIO thì thực hiện lệnh `ceph -w` 

- Mặc định khi khởi động lại thì việc map rbd sẽ bị mất, xử lý như sau:
  - Mở file /etc/ceph/rbdmap và thêm dòng dưới
    ```sh
    rbd/disk02   id=admin,keyring=/etc/ceph/ceph.client.admin.keyring
    ```
    - Lưu ý cần khai báo pool `rbd` và tên images là `disk01` đã được khai báo ở bên trên.
    
  - Sửa file `/etc/fstab` để việc mount được thực hiện mỗi khi khởi động lại OS, thêm dòng
    ```sh
    /dev/rbd1   /mnt  xfs defaults,noatime,_netdev        0       0
    ```
    
  - Trong quá trình lab với client là ubuntu tôi gặp hiện tượng khởi động lại Client 2 lần thì mới đăng nhập được, chưa hiểu tại sao lại bị tình trạng như vậy.

  
### 7. Các ghi chú cấu hình client sử dụng CEPH 

- File lỗi khi thực hiện `map` các rbd, nếu chạy xuất hiện lỗi dưới
  ```sh
  ceph-deploy@client:~$ sudo rbd map disk01
  rbd: sysfs write failed
  RBD image feature set mismatch. You can disable features unsupported by the kernel with "rbd feature disable".
  In some cases useful info is found in syslog - try "dmesg | tail" or so.
  rbd: map failed: (6) No such device or address
  ```
  
  - Thì thực hiện
    ```sh
    rbd feature disable rbd/disk01 fast-diff,object-map,exclusive-lock,deep-flatten
    ```
    - Lưu ý từ khóa `disk02` trong lệnh, nó là tên image của rbd được tạo.
    
- Nếu khi thực hiện format phân vùng RBD trên client`sudo: mkfs.xfs: command not found`, thì cần cài đặt gói để sử dụng lệnh `mkfs.xfs`
  ```sh
  sudo apt-get install xfsprogs
  ```  

- Lệnh để xem thuộc tính của các loại disk trong linux
  ```sh
  blkid
  ```
  
- Lệnh xem các pool trong CEPH
  ``` 
  root@ubuntuclient2:~# ceph osd lspools
  0 rbd,
  ```  

