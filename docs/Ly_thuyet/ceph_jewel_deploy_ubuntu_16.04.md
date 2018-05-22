# Ceph-deploy Jewel trên ubuntu 16.04 - 64 bit

## 1. Mô hình cài đặt
- Sử dụng mô hình ceph 3 node được cài đặt trên Ubuntu 16.04

	![](../images/ceph_jewel_layout.png)
	
## 2. Ip Planning 
- Phân hoạch địa chỉ Ip và thông số phần cứng 

	![](../images/ceph_jewel_ip.png)
	
## 3. Cài đặt môi trường cho các server ceph
- OS:
	- Ubuntu Server 16.04 - 64 bit
	- 5: HDD, trong đó:
	- sda: sử dụng để cài OS
	- sdb: sử dụng làm journal (Journal là một lớp cache khi client ghi dữ liệu, thực tế thường dùng ổ SSD để làm cache)
	- sdc, sdd, sde: sử dụng làm OSD (nơi chứa dữ liệu của client)
- 2 NICs:
	- ens3: dùng để client sử dụng, dải 10.10.10.0/24
	- ens4: dùng để ssh và tải gói cài đặt cho máy chủ CEPH và ceph client , sử dụng dải 172.16.10.0/24
	- ens5: dùng để replicate cho CEPH sử dụng, dải 10.10.20.0/24
- CEPH Jewel

- Trên các server ceph đều thực hiện tương tự nhau.

### 3.1 Cấu hình route và ip
- 1. Đặt hostname: dùng vi sửa file `/etc/hostname`
	- ceph - 1 đặt: `ceph1`
	- ceph - 2 đặt: `ceph2`
	- ceph - 3 đặt: `ceph3`
	
- 2. Sửa file `/etc/hosts`

```sh
10.10.10.21	ceph1
10.10.10.22	ceph2
10.10.10.23	ceph3
```

- 3. Cấu hình card mạng. sửa file `/etc/network/interfaces`

```sh
auto ens3
iface ens3 inet static
	address 10.10.10.21
	netmask 255.255.255.0

auto ens4
iface ens4 inet static
	address 172.16.10.21
	netmask 255.255.255.0
	gateway 172.16.10.1
	dns-nameservers 8.8.8.8

auto ens5
iface ens5 inet static
	address 10.10.20.21
	netmask 255.255.255.0
```

	- Trên ceph2 đặt ip là 22, ceph 3 đặt 23

### 3.2 Cài đặt NTP
- 1. Cài gói chrony.

```sh
apt -y install chrony
```

- 2. Mở file `/etc/chrony/chrony.conf` bằng vi và thêm vào các dòng sau:

	- Trên ceph 1 thực hiện như sau:
		- commnet dòng sau:
		
		```sh
		#pool 2.debian.pool.ntp.org offline iburst
		```
		
		- Thêm các dòng sau:

		```sh
		server 1.vn.poo.ntp.org iburst
		server 0.asia.pool.ntp.org iburst 
		server 3.asia.pool.ntp.org iburst
		
		allow 10.10.10.0/24
		```
	
	- Trên ceph 2 và ceph 3:
		- commnet dòng sau:
		
		```sh
		#pool 2.debian.pool.ntp.org offline iburst
		```
		
		- Thêm các dòng sau:

		```sh
		server ceph1 iburst
		```
		
- Restart dịch vụ NTP

```sh 
service chrony restart
```

### 3.3 Cài đặt các gói ceph.
- 1. Khai báo Repo cho CEPH đối với Ubuntu Server 

```sh
wget -q -O- 'https://download.ceph.com/keys/release.asc' | sudo apt-key add -
echo deb https://download.ceph.com/debian-jewel/ $(lsb_release -sc) main | sudo tee /etc/apt/sources.list.d/ceph.list
apt update
apt install -y ceph
```

- 2. Cài đặt công cụ ceph-deploy. chỉ cài trên ceph1

```sh
apt -y install ceph-deploy
```

### 3.3 Tạo user `ceph-deploy` để sử dụng cho việc cài đặt cho CEPH.
- Tạo user

```sh
sudo useradd -m -s /bin/bash ceph-deploy
```

- Đặt mật mẩu cho user ceph-deploy

```sh
sudo passwd ceph-deploy
```

- Phân quyền cho user ceph-deploy

```sh
echo "ceph-deploy ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ceph-deploy
sudo chmod 0440 /etc/sudoers.d/ceph-deploy
```

- Chuyển sang tài khoản ceph-deploy để thực hiện cài đặt. Thực hiện trên ceph1

```sh
sudo su - ceph-deploy
```

- Tạo ssh key cho user `ceph-deploy`. Nhấn enter đối với các bước được hỏi trên màn hình.

```sh
ssh-keygen
```

- Copy ssh key để sử dụng:

```sh
ssh-copy-id ceph-deploy@ceph1
```

- Nhập Yes và mật khẩu của user ceph-deploy đã tạo ở trước, kết quả như bên dưới

```sh
ceph-deploy@ceph1:~$ ssh-copy-id ceph-deploy@ceph1
The authenticity of host 'ceph1 (172.16.10.21)' can't be established.
ECDSA key fingerprint is f2:38:1e:50:44:94:6f:0a:32:a3:23:63:90:7b:53:27.
Are you sure you want to continue connecting (yes/no)? yes
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
ceph-deploy@ceph1's password:

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'ceph-deploy@ceph1'"
and check to make sure that only the key(s) you wanted were added.
```

- Tiếp tục copy ssh key sang ceph 2 và ceph 3 bằng cách thay tên ceph1 ở trên lần lượt bằng ceph2 và ceph3

---
- Các bước sau thực hiện trên ceph1

### 3.4 Tạo các thư mục để công cụ ceph-deploy sử dụng để cài đặt CEPH
- 1. Tạo thư mục

```sh
cd ~
mkdir my-cluster
cd my-cluster
```

- 2. Thiết lập các file cấu hình cho CEPH.

```sh
ceph-deploy new ceph1
```

- Sau khi thực hiện lệnh trên xong, sẽ thu được 03 file ở dưới (sử dụng lệnh ll -alh để xem). Trong đó cần cập nhật file ceph.conf để cài đặt CEPH được hoàn chỉnh.

```sh
ceph-deploy@ceph1:~/my-cluster$ ll -alh
total 20K
drwxrwxr-x 2 ceph-deploy ceph-deploy 4.0K Jan 29 10:03 ./
drwxr-xr-x 5 ceph-deploy ceph-deploy 4.0K Jan 29 10:01 ../
-rw-rw-r-- 1 ceph-deploy ceph-deploy  194 Jan 29 10:03 ceph.conf
-rw-rw-r-- 1 ceph-deploy ceph-deploy 3.0K Jan 29 10:03 ceph-deploy-ceph.log
-rw------- 1 ceph-deploy ceph-deploy   73 Jan 29 10:03 ceph.mon.keyring
```

- 3. Sửa file ceph.conf có nội dung như sau:

```sh
[global]
fsid = ff191f7b-5e50-4a21-b0ee-388b769d13e4
mon_initial_members = ceph1, ceph2, ceph3
mon_host = 10.10.10.21, 10.10.10.22, 10.10.10.23
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx

osd pool default size = 2
osd crush chooseleaf type = 0
osd journal size = 1024
public network = 10.10.10.0/24
cluster network = 10.10.20.0/24

[mon]
mon host = ceph1, ceph2, ceph3
mon initial members = ceph1, ceph2, ceph3

[mon.ceph1]
host = ceph1
mon addr = 10.10.10.21
[mon.ceph2]
host = ceph2
mon addr = 10.10.10.22
[mon.ceph3]
host = ceph3
mon addr = 10.10.10.23
```

- 3. Cài đặt CEPH

```sh
ceph-deploy install ceph1 ceph2 ceph3
```

- 4. Cấu hình `MON` (một thành phần của CEPH)

```sh
ceph-deploy mon create-initial
```

- 5. Tạo các OSD cho CEPH
- Các OSD trên ceph1

```sh
ceph-deploy osd prepare ceph1:sdc:/dev/sdb
ceph-deploy osd prepare ceph1:sdd:/dev/sdb
```

- Active các OSD vừa tạo ở trên

```sh
ceph-deploy osd activate ceph1:/dev/sdc1:/dev/sdb1
ceph-deploy osd activate ceph1:/dev/sdd1:/dev/sdb2
```

- Các OSD trên ceph2

```sh
ceph-deploy osd prepare ceph2:sdc:/dev/sdb
ceph-deploy osd prepare ceph2:sdd:/dev/sdb
```

- Active các OSD vừa tạo ở trên

```sh
ceph-deploy osd activate ceph2:/dev/sdc1:/dev/sdb1
ceph-deploy osd activate ceph2:/dev/sdd1:/dev/sdb2
```

- Các OSD trên ceph3

```sh
ceph-deploy osd prepare ceph3:sdc:/dev/sdb
ceph-deploy osd prepare ceph3:sdd:/dev/sdb
```

- Active các OSD vừa tạo ở trên

```sh
ceph-deploy osd activate ceph3:/dev/sdc1:/dev/sdb1
ceph-deploy osd activate ceph3:/dev/sdd1:/dev/sdb2
```

- Kiểm tra các phân vùng được tạo ra bằng lệnh `sudo lsblk` (nhớ phải có lệnh sudo vì đang dùng user ceph-deploy)

```sh
ceph-deploy@ceph1:~/my-cluster$ sudo lsblk
NAME                  MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda                     8:0    0   20G  0 disk
├─sda1                  8:1    0  487M  0 part /boot
├─sda2                  8:2    0    1K  0 part
└─sda5                  8:5    0 19.5G  0 part
  ├─ubuntu--vg-root   252:0    0 18.5G  0 lvm  /
  └─ubuntu--vg-swap_1 252:1    0    1G  0 lvm  [SWAP]
sdb                     8:16   0   10G  0 disk
├─sdb1                  8:17   0    1G  0 part
└─sdb2                  8:18   0    1G  0 part
sdc                     8:32   0   10G  0 disk
└─sdc1                  8:33   0   10G  0 part /var/lib/ceph/osd/ceph-0
sdd                     8:48   0   10G  0 disk
└─sdd1                  8:49   0   10G  0 part /var/lib/ceph/osd/ceph-1
sr0                    11:0    1  825M  0 rom
```

### 3.5 Tạo admin key
- Tạo key

```sh
ceph-deploy admin ceph1
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
ceph-deploy@ceph1:~/my-cluster$ ceph -s
    cluster ff191f7b-5e50-4a21-b0ee-388b769d13e4
     health HEALTH_WARN
            too few PGs per OSD (21 < min 30)
     monmap e1: 3 mons at {ceph1=10.10.10.21:6789/0,ceph2=10.10.10.22:6789/0,ceph3=10.10.10.23:6789/0}
            election epoch 4, quorum 0,1,2 ceph1,ceph2,ceph3
     osdmap e33: 6 osds: 6 up, 6 in
            flags sortbitwise,require_jewel_osds
      pgmap v86: 64 pgs, 1 pools, 0 bytes data, 0 objects
            202 MB used, 61171 MB / 61373 MB avail
                  64 active+clean
```

- Có cảnh báo do quá ít PG trên mỗi osd. Như vậy cluster đã được cài đặt thành công.