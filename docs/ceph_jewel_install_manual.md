# Hướng dẫn cài đặt Ceph Jewel
******

<a name="I."> </a> 
# I. Cài đặt cơ bản
******
<a name="1"> </a> 
## 1. Chuẩn bị môi trường
<a name="1.1"> </a> 
### 1.1 Mô hình mạng
- Mô hình đầy đủ

![Ceph Jewel Topo](../../images/ceph_jewel_manual/Jewel_topo.jpg)

<a name="1.2"> </a> 
### 1.2 Các tham số phần cứng đối với các node

![Ceph hardware](../../images/ceph_jewel_manual/Cauhinh_phancung.jpg)

### Chú ý khi lựa chọn OS và lựa chọn dải mạng

```
- OS: Ubuntu Server 14.04.5 64 bit, kernel >= 4.4.0-31-generic
- Các dải mạng: 
	- Management Network: sử dụng để quản lý (ssh) các máy chủ và để các máy chủ tải các gói cài đặt từ Internet.
	- Data Network: sử dụng để các máy client có thể truy cập và sử dụng tài nguyên lưu trữ trên Ceph.
	- Replication Network: Sử dụng để nhân bản dữ liệu giữa các node Ceph.
- Ổ cứng:
	- Label của các ổ cứng trong hướng dẫn này là sda, sdb,sdc,sdd. Tùy từng môi trường thực hiện label này có thể thay đổi (vda, vdb)
```

<a name="2"> </a> 
## 2. Cài đặt các thành phần chung trên tất cả các node
===
- Lưu ý:
 - Đăng nhập với quyền root trên tất cả các bước cài đặt.
 - Các thao tác sửa file trong hướng dẫn này sử dụng lệnh `vi` hoặc `vim`
 - Thực hiện trên tất cả các node

### 2.1. Thiết lập và cài đặt các gói cơ bản

- Chạy lệnh để cập nhật các gói phần mềm và đưa lên kernel mới nhất

	```sh
	apt-get update && apt-get -y upgrade && apt-get -y dist-upgrade
	```

- Thiết lập địa chỉ IP cho từng node
- Dùng lệnh `vi` để sửa file `/etc/network/interfaces` với nội dung như sau.

	```sh
	# Interface MGNT
		auto eth0
		iface eth0 inet static
		address 172.16.69.77
		gateway 172.16.69.1
		netmask 255.255.255.0
		dns-nameservers 8.8.8.8

	# Interface PUB
		auto eth1
		iface eth1 inet static
		address 10.10.20.77
		netmask 255.255.255.0

	# Interface REP
		auto eth2
		iface eth2 inet static
		address 10.10.30.77
		netmask 255.255.255.0
	```

- Khởi động lại card mạng sau khi thiết lập IP tĩnh

	```sh
	ifdown -a && ifup -a
	```
- Đăng nhập lại máy `Ceph1` với quyền `root` và thực hiện kiểm tra kết nối. 
- Kiểm tra kết nối tới gateway và internet sau khi thiết lập xong.

	```sh
	ping 172.16.69.1 -c 4
	PING 172.16.69.1 (172.16.69.1) 56(84) bytes of data.
	64 bytes from 172.16.69.1: icmp_seq=1 ttl=64 time=0.253 ms
	64 bytes from 172.16.69.1: icmp_seq=2 ttl=64 time=0.305 ms
	64 bytes from 172.16.69.1: icmp_seq=3 ttl=64 time=0.306 ms
	64 bytes from 172.16.69.1: icmp_seq=4 ttl=64 time=0.414 ms
	```
	
	```sh
	ping google.com -c 4
	PING google.com (74.125.204.113) 56(84) bytes of data.
	64 bytes from ti-in-f113.1e100.net (74.125.204.113): icmp_seq=1 ttl=41 time=58.3 ms
	64 bytes from ti-in-f113.1e100.net (74.125.204.113): icmp_seq=2 ttl=41 time=58.3 ms
	64 bytes from ti-in-f113.1e100.net (74.125.204.113): icmp_seq=3 ttl=41 time=58.3 ms
	64 bytes from ti-in-f113.1e100.net (74.125.204.113): icmp_seq=4 ttl=41 time=58.3 ms
	```
- Cấu hình hostname
- Dùng `vi` sửa file `/etc/hostname` với tên là `ceph1`

	```sh
	ceph1
	```
	
- Cập nhật file `/etc/hosts` để phân giải từ IP sang hostname và ngược lại, nội dung như sau

	```sh
	127.0.0.1      localhost ceph1
	10.10.20.77    ceph1
	10.10.20.78    ceph2
	10.10.20.79    ceph3
	```

### 2.2. Cài đặt NTP
- Cài gói `chrony`

	```sh
	apt-get -y install chrony
	```
	
- Mở file `/etc/chrony/chrony.conf` và tìm các dòng dưới

	```sh
	server 0.debian.pool.ntp.org offline minpoll 8
	server 1.debian.pool.ntp.org offline minpoll 8
	server 2.debian.pool.ntp.org offline minpoll 8
	server 3.debian.pool.ntp.org offline minpoll 8
	```

- Thay bằng các dòng sau 

	```sh
	server 1.vn.pool.ntp.org iburst
	server 0.asia.pool.ntp.org iburst
	server 3.asia.pool.ntp.org iburst
	```

- Khởi động lại dịch vụ NTP

	```sh
	service chrony restart
	```

- Kiểm tra lại hoạt động của NTP bằng lệnh dưới

	```sh
	root@ceph1:~# chronyc sources
	```
	
	- Kết quả như sau
	
		```sh
		210 Number of sources = 3
		MS Name/IP address         Stratum Poll Reach LastRx Last sample
		===============================================================================
		^+ 220.231.122.105               3   6    17    16    +12ms[+4642us] +/-  139ms
		^** 103.245.79.2                  2   6    17    17    -10ms[  -12ms] +/-  176ms
		^? routerida1.soprano-asm.ne     0   6     0   10y     +0ns[   +0ns] +/-    0ns
		```

### 2.3. Cài đặt package cho Ceph Jewel
- Cài đặt repo

	```sh
	wget -q -O- 'https://ceph.com/git/?p=ceph.git;a=blob_plain;f=keys/release.asc' | sudo apt-key add -
	```
	Kết quả: `OK`

	```sh
	echo deb http://download.ceph.com/debian-jewel/ trusty main | sudo tee /etc/apt/sources.list.d/ceph.list
	```
- Cập nhật các gói phần mềm

	```sh
	apt-get -y update
	```
- Cài đặt Ceph package

	```sh
	apt-get install ceph -y
	```
- Kiểm tra các gói sau khi cài

	```sh
	dpkg -l | egrep -i "ceph|rados|rbd"
	```
	Kết quả:

	```sh
	ii  ceph                                  10.2.5-1trusty                    amd64        distributed storage and file system
	ii  ceph-base                             10.2.5-1trusty                    amd64        common ceph daemon libraries and management tools
	ii  ceph-common                           10.2.5-1trusty                    amd64        common utilities to mount and interact with a ceph storage cluster
	ii  ceph-fs-common                        10.2.5-1trusty                    amd64        common utilities to mount and interact with a ceph file system
	ii  ceph-fuse                             10.2.5-1trusty                    amd64        FUSE-based client for the Ceph distributed file system
	ii  ceph-mds                              10.2.5-1trusty                    amd64        metadata server for the ceph distributed file system
	ii  ceph-mon                              10.2.5-1trusty                    amd64        monitor server for the ceph storage system
	ii  ceph-osd                              10.2.5-1trusty                    amd64        OSD server for the ceph storage system
	ii  libcephfs1                            10.2.5-1trusty                    amd64        Ceph distributed file system client library
	ii  librados2                             10.2.5-1trusty                    amd64        RADOS distributed object store client library
	ii  libradosstriper1                      10.2.5-1trusty                    amd64        RADOS striping interface
	ii  librbd1                               10.2.5-1trusty                    amd64        RADOS block device client library
	ii  librgw2                               10.2.5-1trusty                    amd64        RADOS Gateway client library
	ii  python-cephfs                         10.2.5-1trusty                    amd64        Python libraries for the Ceph libcephfs library
	ii  python-rados                          10.2.5-1trusty                    amd64        Python libraries for the Ceph librados library
	ii  python-rbd                            10.2.5-1trusty                    amd64        Python libraries for the Ceph librbd library

	```
- Ở bản Jewel, khi khởi động lại các service của Ceph sẽ gặp lỗi phân quyền do 1 bug trong `/etc/init.d/ceph`, fix như sau

```sh
sed -i 's/do_cmd "mkdir -p "`dirname $pid_file`/do_cmd "mkdir -p -m 777 "`dirname $pid_file`/g' /etc/init.d/ceph
```
- Khởi động lại node ceph1

```sh
init 6
```

**Lặp lại các bước 2.1, 2.2, 2.3 trên các node ceph2 và ceph3** 

## 3. Cài đặt trên node Ceph1
### 3.1. Tạo cluster UUID cho Ceph cluster (sử dụng để xác thực giữa các ceph service nếu dùng ceph auth)

```sh
uuidgen
Kết quả:
31154d30-b0d3-4411-9178-0bbe367a5578
```

### 3.2. Tạo file cấu hình của Ceph cluster, đặt tại `/etc/ceph/ceph.conf`

```sh
[global]
# cluster UUID 
fsid = 31154d30-b0d3-4411-9178-0bbe367a5578
# Dải mạng để client kết nối tới Ceph Cluster
public network = 10.10.20.0/24
# Dải mạng để các node Ceph đồng bộ dữ liệu với nhau
cluster network = 10.10.30.0/24
# Khai báo cơ chế xác thực được sử dụng
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
filestore_xattr_use_omap = true
# Khai báo số nhân bản của dữ liệu mặc định cho từng pool khi cluster ở trạng thái degrade (hệ thống đang cảnh báo)
osd pool default min size = 1
# Khai báo số nhân bản của dữ liệu mặc định cho từng pool khi cluster ở trạng thái bình thường
osd pool default size = 3
# Khai báo số lượng pg và pgp mặc định cho từng pool khi khởi tạo
osd pool default pg num = 128
osd pool default pgp num = 128
# Khai báo kích thước mặc định của journal cho từng OSD (MB)
osd journal size = 10000
# Khai báo cấu hình chung cho các mon daemon
[mon]
mon host = ceph1, ceph2, ceph3
mon initial members = ceph1, ceph2, ceph3
# Khai báo cấu hình riêng cho từng mon daemon
[mon.ceph1]
host = ceph1
mon addr = 10.10.20.77
[mon.ceph2]
host = ceph2
mon addr = 10.10.20.78
[mon.ceph3]
host = ceph3
mon addr = 10.10.20.79
# Khai báo cấu hình chung cho các osd daemon
[osd]
# Khai báo số thread của CPU để xử lý OSD daemon
osd op threads = 8
# Để giữ cấu hình crush map không tự động update khi restart mon daemon
osd crush update on start = false
# Khai báo cấu hình riêng cho từng osd daemon
[osd.0]
host = ceph1
public addr = 10.10.20.77
cluster addr = 10.10.30.77
[osd.1]
host = ceph1
public addr = 10.10.20.77
cluster addr = 10.10.30.77
[osd.2]
host = ceph2
public addr = 10.10.20.78
cluster addr = 10.10.30.78
[osd.3]
host = ceph2
public addr = 10.10.20.78
cluster addr = 10.10.30.78
[osd.4]
host = ceph3
public addr = 10.10.20.79
cluster addr = 10.10.30.79
[osd.5]
host = ceph3
public addr = 10.10.20.79
cluster addr = 10.10.30.79
```

### 3.3. Khởi tạo mon trên ceph1
- Tạo thư mục chứa các file `monmap` và `ceph.client.admin.keyring` trên ceph1

```sh
mkdir /root/keyring
```

- Tạo cluster keyring cho mon daemon, keyring này sử dụng để add mon daemon vào quorum

```sh
ceph-authtool --create-keyring -n mon.  --gen-key /root/keyring/ceph.mon.keyring --cap mon 'allow **'
```

- Tạo file keyring cho user admin và phân quyền cho admin (có đầy đủ quyền với mon, osd, mds)

```sh
ceph-authtool --create-keyring  -n client.admin --gen-key /etc/ceph/ceph.client.admin.keyring --set-uid=0 --cap mon 'allow **' --cap osd 'allow **' --cap mds 'allow'
```

- Đưa nội dung của client.admin key vào ceph.mon.keyring

```sh
ceph-authtool /root/keyring/ceph.mon.keyring --import-keyring /etc/ceph/ceph.client.admin.keyring
```

- Tạo monitor map, bao gồm các thông tin của node Ceph1: hostname, IP Client và FSID của Ceph Cluster

  **Lưu ý: sử dụng hostname (ceph1), IP (10.10.20.77) và fsid(31154d30-b0d3-4411-9178-0bbe367a5578) tương ứng**

```sh
monmaptool --create --add ceph1 10.10.20.77 --fsid 31154d30-b0d3-4411-9178-0bbe367a5578 /root/keyring/monmap
```

- Tạo thư mục cho mon trên ceph1, đường dẫn mặc định nằm tại `/var/lib/ceph/mon`

**Lưu ý: thay thế hostname (ceph1) tương ứng**

```sh
ceph-mon --mkfs -i ceph1 --monmap /root/keyring/monmap --keyring /root/keyring/ceph.mon.keyring
chown -R ceph:ceph /var/lib/ceph/mon/
```

- Khởi chạy monitor daemon trên node ceph1

```sh
service ceph start mon
```

## 4. Cài đặt trên node Ceph2 (Ceph3 làm tương tự)
### 4.1. Copy file cấu hình và keyring
 - Tạo thư mục chứa các file `monmap` và `ceph.client.admin.keyring` trên ceph2

```sh
mkdir /root/keyring
```

 - Trên node Ceph1, copy các file `/root/keyring/monmap` và `/root/keyring/ceph.mon.keyring` sang ceph2 và ceph3, đặt tại thư mục `/root/keyring` trên từng node

 ```sh
 scp /root/keyring/monmap root@ceph2:/root/keyring
 scp /root/keyring/monmap root@ceph3:/root/keyring
 scp /root/keyring/ceph.mon.keyring root@ceph2:/root/keyring
 scp /root/keyring/ceph.mon.keyring root@ceph3:/root/keyring
 ```
 - Copy các file `ceph.conf`, `rbdmap`, `ceph.client.admin.keyring` trong thư mục `/etc/ceph` từ node ceph1 sang ceph2 và ceph3, đặt tại thư mục `/etc/ceph` tại từng node

 ```sh
 scp -r /etc/ceph/ root@ceph2:/etc/
 scp -r /etc/ceph/ root@ceph3:/etc/
 ```
 
### 4.2. Khởi tạo mon trên Ceph2

 - Tạo thư mục cho mon, đường dẫn mặc định nằm tại `/var/lib/ceph/mon`

 **Lưu ý: thay thế hostname (ceph2) tương ứng**

 ```sh
 ceph-mon --mkfs -i ceph2 --monmap /root/keyring/monmap --keyring /root/keyring/ceph.mon.keyring
 chown -R ceph:ceph /var/lib/ceph/mon/
 ```

 - Khởi chạy monitor daemon trên node ceph2

 ```sh
 service ceph start mon
 ```

 - Nếu gặp lỗi, thay đổi quyển cho thư mục `/var/run/ceph` và khởi động lại `mon`

 ```sh
 chown -R ceph:ceph /var/run/ceph
 service ceph start mon
 ```

 - Sau khi khởi chạy, ceph2 được add vào monmap.

  Kiểm tra

 ```sh
 ceph mon getmap -o /tmp/monmap
 monmaptool --print /tmp/monmap 
 ```

  Kết quả
  
 ```sh
 monmaptool: monmap file /tmp/monmap
 epoch 2
 fsid 31154d30-b0d3-4411-9178-0bbe367a5578
 last_changed 2017-04-11 13:05:53.691418
 created 2017-04-11 13:03:00.964314
 0: 10.10.20.77:6789/0 mon.ceph1
 1: 10.10.20.78:6789/0 mon.ceph2
 2: 10.10.20.79:6789/0 mon.ceph3
 ```

## 5. Cài đặt OSD trên tất cả các node
### 5.1. Copy file cấu hình và keyring
 - Copy file `/var/lib/ceph/bootstrap-osd/ceph.keyring` từ ceph1 sang các node còn lại, đặt tại thư mục `/var/lib/ceph/bootstrap-osd/`. File này được sinh ra sau khi đã add thành công 3 mon vào quorum.

 ```sh
 scp /var/lib/ceph/bootstrap-osd/ceph.keyring root@ceph2:/var/lib/ceph/bootstrap-osd/
 scp /var/lib/ceph/bootstrap-osd/ceph.keyring root@ceph3:/var/lib/ceph/bootstrap-osd/
 ```
 - Copy các file `ceph.conf`, `rbdmap`, `ceph.client.admin.keyring` trong thư mục `/etc/ceph` từ node ceph1 sang ceph2 và ceph3, đặt tại thư mục `/etc/ceph` tại từng node

 ```sh
 scp -r /etc/ceph/ root@ceph2:/etc/
 scp -r /etc/ceph/ root@ceph3:/etc/
 ```

### 5.2. Triển khai OSD lần lượt trên từng node
 - Trong bài lab này, `/dev/sdb` trên từng node sẽ được dùng làm journal disk cho các OSD `/dev/sdc` và `/dev/sdd`.
 - Format các ổ `/dev/sdc` và `/dev/sdd` theo định dạng XFS, sử dụng GPT table

 ```sh
 parted /dev/sdc mklabel GPT
 parted /dev/sdd mklabel GPT
 ```

 - Tạo OSD trên từng ổ
 
 **Lưu ý: thay thế cluster(ceph), --cluster-uuid (31154d30-b0d3-4411-9178-0bbe367a5578) tương ứng**

 ```sh
 ceph-disk prepare --cluster ceph --cluster-uuid 31154d30-b0d3-4411-9178-0bbe367a5578 --fs-type xfs /dev/sdc /dev/sdb
 ceph-disk prepare --cluster ceph --cluster-uuid 31154d30-b0d3-4411-9178-0bbe367a5578 --fs-type xfs /dev/sdd /dev/sdb
 ```

### 5.3. Kiểm tra
 - Kiểm tra trạng thái Ceph Cluster

 ```sh
 ceph -s
 ```

 Kết quả:

 ```sh
 cluster 31154d30-b0d3-4411-9178-0bbe367a5578
     health HEALTH_OK
     monmap e2: 3 mons at {ceph1=10.10.20.77:6789/0,ceph2=10.10.20.78:6789/0,ceph3=10.10.20.79:6789/0}
            election epoch 6, quorum 0,1,2 ceph1,ceph2,ceph3
     osdmap e14: 6 osds: 6 up, 6 in
            flags sortbitwise,require_jewel_osds
      pgmap v57: 0 pgs, 0 pools, 0 bytes data, 0 objects
            196 MB used, 179 GB / 179 GB avail

 ```

 - Kiểm tra trạng thái các OSD

 ```sh
 ceph osd tree
 ```

 Kết quả:

 ```sh
 ID WEIGHT TYPE NAME    UP/DOWN REWEIGHT PRIMARY-AFFINITY
-1      0 root default
 0      0 osd.0             up  1.00000          1.00000
 1      0 osd.1             up  1.00000          1.00000
 2      0 osd.2             up  1.00000          1.00000
 3      0 osd.3             up  1.00000          1.00000
 4      0 osd.4             up  1.00000          1.00000
 5      0 osd.5             up  1.00000          1.00000
```

### 5.4. Quy hoạch lại crushmap theo thứ tự ổ cứng trên từng node
 - Xuất file crushmap

 ```sh
 ceph osd getcrushmap -o crushmap-extract
 ```
 - Decompile lại crushmap theo định dạng text

 ```sh
 crushtool -d crushmap-extract -o crushmap-decompile
 ```
 - Chỉnh sửa lại crushmap như sau

    `vim crushmap-decompile`

 ```sh
 # begin crush map
 tunable choose_local_tries 0
 tunable choose_local_fallback_tries 0
 tunable choose_total_tries 50
 tunable chooseleaf_descend_once 1
 tunable chooseleaf_vary_r 1
 tunable straw_calc_version 1
 # devices (khai báo các OSD)
 device 0 osd.0
 device 1 osd.1
 device 2 osd.2
 device 3 osd.3
 device 4 osd.4
 device 5 osd.5
 # types (khai báo các loại item có thể sử dụng trong crushmap)
 type 0 osd
 type 1 host
 type 2 chassis
 type 3 rack
 type 4 row
 type 5 pdu
 type 6 pod
 type 7 room
 type 8 datacenter
 type 9 region
 type 10 root
 # buckets (khai báo các ceph host trong cluster)
 host ceph1{
    id -2           # do not change unnecessarily
    # weight 0.400
    alg straw
    hash 0  # rjenkins1
    item osd.0 weight 30 # tương ứng với 30GB
    item osd.1 weight 30
 }
 host ceph2{
    id -3           # do not change unnecessarily
    # weight 0.400
    alg straw
    hash 0  # rjenkins1
    item osd.2 weight 30
    item osd.3 weight 30
 }
 host ceph3{
    id -4          # do not change unnecessarily
    # weight 0.400
    alg straw
    hash 0  # rjenkins1
    item osd.4 weight 30
    item osd.5 weight 30
 }
 root default {
        id -1           # do not change unnecessarily
        # weight 0.000
        alg straw
        hash 0  # rjenkins1
        item ceph1 weight 20 # tương ứng với dung lượng khả dụng trên 1 host (vì replicate là 3)
        item ceph2 weight 20
        item ceph3 weight 20
 }
 # rules
 rule replicated_ruleset {
        ruleset 0
        type replicated
        min_size 1
        max_size 10
        step take default
        step chooseleaf firstn 0 type host
        step emit
 }
 # end crush map
 ```
 - Decompile lại file `crushmap-decompile`
 ```sh
 crushtool -c crushmap-decompile -o crushmap
 ```

 - Set lại crushmap
 ```sh
 ceph osd setcrushmap -i crushmap
 ```

 - Kiểm tra lại trạng thái các OSD
 ```sh
 ceph osd tree
 ```

 Kết quả:
 ```sh
 ID WEIGHT  TYPE NAME      UP/DOWN REWEIGHT PRIMARY-AFFINITY
 -1 9.59999 root default
 -2 3.20000     host ceph1
  0 4.00000         osd.0       up  1.00000          1.00000
  1 4.00000         osd.1       up  1.00000          1.00000
 -3 3.20000     host ceph2
  2 4.00000         osd.2       up  1.00000          1.00000
  3 4.00000         osd.3       up  1.00000          1.00000
 -4 3.20000     host ceph3
  4 4.00000         osd.4       up  1.00000          1.00000
  5 4.00000         osd.5       up  1.00000          1.00000
 ```

### 5.5. Thử tạo rbd object để kiểm tra

- Lệnh để list các pool đang có trong Ceph cluster

```sh
ceph osd lspools
```

Kết quả:
```sh
0 rbd,
```

- Lệnh để tạo 1 object trong pool rbd

```sh
rbd create ceph-client --size 256 --image-format 2 --pool rbd
```

- Liệt kê các object trong pool rbd

```sh
rbd -p rbd ls
```

Kết quả:
```sh
ceph-client
```

## Done