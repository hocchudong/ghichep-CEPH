# Hướng dẫn cài đặt CEPH Luminous

### Mô Hình

![topo_ceph3node.png](./images/topo_ceph3node.png)


### IP Planning

![ip_planning_ceph03node.png](./images/ip_planning_ceph03node.png)


#1. Thiết lập IP, hostname

##1.1 Thiết lập IP, hostname cho ceph1

-  Đăng nhập với tài khoản root

```
su -
```

- Khai báo repos nếu có

```sh
echo "proxy=http://192.168.70.111:3142;" >> /etc/yum.conf
```

- Update OS

```sh
yum update -y
```

- Đặt hostname

```sh
hostnamectl set-hostname ceph1
```

- Đặt IP cho máy cài CEPH

```sh
echo "Setup IP  ens160"
nmcli c modify ens160 ipv4.addresses 192.168.70.131/24
nmcli c modify ens160 ipv4.gateway 192.168.70.1
nmcli c modify ens160 ipv4.dns 8.8.8.8
nmcli c modify ens160 ipv4.method manual
nmcli con mod ens160 connection.autoconnect yes

echo "Setup IP  ens192"
nmcli c modify ens192 ipv4.addresses 192.168.82.131/24
nmcli c modify ens192 ipv4.method manual
nmcli con mod ens192 connection.autoconnect yes

echo "Setup IP  ens224"
nmcli c modify ens224 ipv4.addresses 192.168.83.131/24
nmcli c modify ens224 ipv4.method manual
nmcli con mod ens224 connection.autoconnect yes
```

#### Cấu hình các thành phần cơ bản

```sh
sudo systemctl disable firewalld
sudo systemctl stop firewalld
sudo systemctl disable NetworkManager
sudo systemctl stop NetworkManager
sudo systemctl enable network
sudo systemctl start network

sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
```

- Khai báo file  /etc/hosts

```sh
echo "192.168.82.131 ceph1" >> /etc/hosts
echo "192.168.82.132 ceph2" >> /etc/hosts
echo "192.168.82.133 ceph3" >> /etc/hosts

echo "192.168.70.131 ceph1" >> /etc/hosts
echo "192.168.70.132 ceph2" >> /etc/hosts
echo "192.168.70.133 ceph3" >> /etc/hosts
```

- Khởi động lại

```
init 6
```

##1.2 Thiết lập IP, hostname cho ceph2

- Đăng nhập với tài khoản root

```
su -
```

- Khai báo repos nếu có

	```sh
	echo "proxy=http://192.168.70.111:3142;" >> /etc/yum.conf
	```


- Update OS

```sh 
yum update -y
````

- Đặt hostname

```sh
hostnamectl set-hostname ceph2
```

- Đặt IP cho máy cài CEPH

```sh
echo "Setup IP  ens160"
nmcli c modify ens160 ipv4.addresses 192.168.70.132/24
nmcli c modify ens160 ipv4.gateway 192.168.70.1
nmcli c modify ens160 ipv4.dns 8.8.8.8
nmcli c modify ens160 ipv4.method manual
nmcli con mod ens160 connection.autoconnect yes

echo "Setup IP  ens192"
nmcli c modify ens192 ipv4.addresses 192.168.82.132/24
nmcli c modify ens192 ipv4.method manual
nmcli con mod ens192 connection.autoconnect yes

echo "Setup IP  ens224"
nmcli c modify ens224 ipv4.addresses 192.168.83.132/24
nmcli c modify ens224 ipv4.method manual
nmcli con mod ens224 connection.autoconnect yes
```

- Cấu hình các thành phần cơ bản


```sh
sudo systemctl disable firewalld
sudo systemctl stop firewalld
sudo systemctl disable NetworkManager
sudo systemctl stop NetworkManager
sudo systemctl enable network
sudo systemctl start network

sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
```


- Khai báo file  /etc/hosts

```sh
echo "192.168.82.131 ceph1" >> /etc/hosts
echo "192.168.82.132 ceph2" >> /etc/hosts
echo "192.168.82.133 ceph3" >> /etc/hosts

echo "192.168.70.131 ceph1" >> /etc/hosts
echo "192.168.70.132 ceph2" >> /etc/hosts
echo "192.168.70.133 ceph3" >> /etc/hosts
```

#### Khởi động lại

```sh
init 6
```

##1.3 Thiết lập IP, hostname cho ceph3

-  Đăng nhập với tài khoản root

```sh
su -
```
-  Khai báo repos nếu có

```sh
echo "proxy=http://192.168.70.111:3142;" >> /etc/yum.conf
```

#### Update OS

```sh
yum update -y
```


- Đặt hostname

```sh
hostnamectl set-hostname ceph3
```

- Đặt IP cho máy cài CEPH

```sh
echo "Setup IP  ens160"
nmcli c modify ens160 ipv4.addresses 192.168.70.133/24
nmcli c modify ens160 ipv4.gateway 192.168.70.1
nmcli c modify ens160 ipv4.dns 8.8.8.8
nmcli c modify ens160 ipv4.method manual
nmcli con mod ens160 connection.autoconnect yes

echo "Setup IP  ens192"
nmcli c modify ens192 ipv4.addresses 192.168.82.133/24
nmcli c modify ens192 ipv4.method manual
nmcli con mod ens192 connection.autoconnect yes

echo "Setup IP  ens224"
nmcli c modify ens224 ipv4.addresses 192.168.83.133/24
nmcli c modify ens224 ipv4.method manual
nmcli con mod ens224 connection.autoconnect yes
```

- Cấu hình các thành phần cơ bản

```sh
sudo systemctl disable firewalld
sudo systemctl stop firewalld
sudo systemctl disable NetworkManager
sudo systemctl stop NetworkManager
sudo systemctl enable network
sudo systemctl start network

sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
```

-  Khai báo file  /etc/hosts

```sh
echo "192.168.82.131 ceph1" >> /etc/hosts
echo "192.168.82.132 ceph2" >> /etc/hosts
echo "192.168.82.133 ceph3" >> /etc/hosts

echo "192.168.70.131 ceph1" >> /etc/hosts
echo "192.168.70.132 ceph2" >> /etc/hosts
echo "192.168.70.133 ceph3" >> /etc/hosts
```

-  Khởi động lại

```sh
init 6
```

## 2. Cài đặt các gói cơ bản và cấu hình chuẩn bị
## 2.1. Cài đặt gói cơ bản trên cả 03 node CEPH1, CEPH2 và CEPH3

```sh
yum update -y

yum install epel-release -y

yum install wget bybo curl git -y

yum install python-setuptools -y

yum install python-virtualenv -y

yum update -y
```

- Cấu hình NTP

```sh
yum install -y ntp ntpdate ntp-doc

ntpdate 0.us.pool.ntp.org

hwclock --systohc

systemctl enable ntpd.service
systemctl start ntpd.service
```

Lưu ý: trường hợp máy chủ tại Nhân Hòa thì cần khai báo IP về NTP server, liên hệ đội RD để được hướng dẫn.

### 2.2 Tạo user cài đặt ceph

- Tạo user `cephuser` trên node `ceph1, ceph2, ceph3`

```sh
useradd -d /home/cephuser -m cephuser
```

- Đặt password cho user `cephuser`

```sh
passwd cephuser
```

- Cấp quyền sudo cho tài khoản cephuser

```sh
echo "cephuser ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/cephuser

chmod 0440 /etc/sudoers.d/cephuser
# sed -i s'/Defaults requiretty/#Defaults requiretty'/g /etc/sudoers
```


### 2.3. Tạo repos để cài đặt CEPH bằng cách tạo file
#### Tạo repos trên tất cả các host  

```sh
cat << EOF > /etc/yum.repos.d/ceph.repo
[Ceph]
name=Ceph packages for \$basearch
baseurl=http://download.ceph.com/rpm-luminous/el7/\$basearch
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://download.ceph.com/keys/release.asc
priority=1


[Ceph-noarch]
name=Ceph noarch packages
baseurl=http://download.ceph.com/rpm-luminous/el7/noarch
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://download.ceph.com/keys/release.asc
priority=1


[ceph-source]
name=Ceph source packages
baseurl=http://download.ceph.com/rpm-luminous/el7/SRPMS
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://download.ceph.com/keys/release.asc
priority=1
EOF
```

#### Thực hiện update sau khi khai báo repos 

	```sh
	yum update -y
	```

### 3. Cài đặt CEPH

#### 3.1. Thực hiện trên node ceph1

- Cài đặt ceph-deploy

	```sh
	yum install -y ceph-deploy
	```

- Kiểm tra lại phiên bản của ceph-deploy, chính xác là phiên bản 2.0.1

	```sh
	ceph-deploy --version
	```

- Kết quả: 

	```sh
	[cephuser@ceph1 ~]$ ceph-deploy --version
	2.0.1
	```

- Chuyển sang tài khoản `cephuser`

	```sh
	su - cephuser
	```

- Tạo keypair trên node ceph1

	```sh
	ssh-keygen
	```

-  Copy keypair sang các node để ceph-deploy sử dụng. Nhập yes và mật khẩu của từng node khi được hỏi.

	```sh
	ssh-copy-id cephuser@ceph1

	ssh-copy-id cephuser@ceph2

	ssh-copy-id cephuser@ceph3
	```


-  Tạo thư mục để chứa file cài đặt ceph

	```sh
	cd ~
	mkdir my-cluster
	cd my-cluster
	```

- Thiết lập cấu hình MON cho CEPH

	```sh
	ceph-deploy new ceph1 ceph2 ceph3
	```

-  Chỉ định các dải mạng cho CEPH

```sh
echo "public network = 192.168.82.0/24" >> ceph.conf
echo "cluster network = 192.168.83.0/24" >> ceph.conf
```

-  Cài đặt các gói của CEPH

```sh
ceph-deploy install --release luminous ceph1 ceph2 ceph3
```

-  Cấu hình MON 

```sh
ceph-deploy mon create-initial
```

-  Phân quyền cho  các node có thể quản trị được Cụm CEPH

- Đứng trên node CEPH 1 thực hiện lệnh dưới.

```sh
ceph-deploy admin ceph1 ceph2 ceph3
sudo chmod +r /etc/ceph/ceph.client.admin.keyring
```


Lệnh trên sẽ sinh ra file /etc/ceph/ceph.client.admin.keyring trên cả 03 node. Tiếp tục ssh vào các node ceph2 và ceph3 còn lại để thực hiện lệnh phân quyền thực thi cho file /etc/ceph/ceph.client.admin.keyring

```sh
sudo chmod +r /etc/ceph/ceph.client.admin.keyring
```

Việc trên có ý nghĩa là để có thể thực hiện lệnh quản trị của CEPH trên các 03 node trong cụm Cluster.

### Tạo OSD cho cụm cluster 

Add các OSD 

```sh

ceph-deploy osd create --data /dev/sdb ceph1

ceph-deploy osd create --data /dev/sdc ceph1

ceph-deploy osd create --data /dev/sdd ceph1


ceph-deploy osd create --data /dev/sdb ceph2

ceph-deploy osd create --data /dev/sdc ceph2

ceph-deploy osd create --data /dev/sdd ceph2


ceph-deploy osd create --data /dev/sdb ceph3

ceph-deploy osd create --data /dev/sdc ceph3

ceph-deploy osd create --data /dev/sdd ceph3
```


#### Cấu hình dashboad cho CEPH

- Thực hiện trên node ceph1

ceph-deploy mgr create ceph1:ceph-mgr-1

ceph mgr module enable dashboard

Kiểm tra xem địa chỉ IP của ceph dashboard là bao nhiêu

ceph mgr dump

Kết quả: http://prntscr.com/l58wm7

Truy cập vào địa chỉ IP với port mặc định là 7000 như ảnh: http://ip_address_ceph1:7000


##### Kiểm tra lại hoạt động của CEPH

ceph -s 
hoặc 
ceph health


