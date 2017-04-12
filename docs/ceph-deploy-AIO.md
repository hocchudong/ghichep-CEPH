## Hướng dẫn cài đặt CEPH sử dụng `ceph-deploy` trên 1 máy duy nhất (CEPH AIO)

## Chuẩn bị và môi trường LAB

- OS
  - Ubuntu Server 14.04 - 64 bit
  - 01 HDD: dùng để cài OS (sda)
  - 03 HDD: dùng làm OSD (sdb, sdc, sdd)
  - 02 NICs: eth0 dùng để ssh và client sử dụng, eth1 dùng để replicate cho CEPH
  
- CEPH Jewel

## Cài đặt CEPH

- Thực hiện bằng quyền root
  ```sh
  su -
  ```

- Sửa file host 

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


- Tạo user cài đặt cho CEPH, đặt mật mẩu cho user `ceph-deploy`
  ```sh
  sudo useradd -m -s /bin/bash ceph-deploy
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

- Copy ssh key để sử dụng, trong quá trình copy lựa chọn theo hướng dẫn và nhập mật khẩu của user `ceph-deploy`. Thay `hostname_cua_may_ceph` bằng tên hostname của máy bạn 
  ```sh
  ssh-copy-id ceph-deploy@hostname_cua_may_ceph
  ```

- Tạo các thư mục để công cụ `ceph-deploy` sử dụng để cài đặt CEPH
  ```sh
  cd ~
  mkdir my-cluster
  cd my-cluster
  ```

- Thiết lập các file cấu hình cho CEPH, thay `hostname_cua_may_ceph` bằng tên hostname của máy bạn 
  ```sh
  ceph-deploy new hostname_cua_may_ceph
  ```

- Thêm các dòng dưới vào file `ceph.conf` vừa được tạo ra ở trên
  ```sh
  osd pool default size = 2
  osd crush chooseleaf type = 0
  ```
  
- Cài đặt CEPH, thay `hostname_cua_may_ceph` bằng tên hostname của máy bạn 
  ````sh
  ceph-deploy install hostname_cua_may_ceph
  ```

- Cấu hình `MON` (một thành phần của CEPH)
  ```sh
  ceph-deploy mon create-initial
  ```

- Tạo các OSD cho CEPH, thay `hostname_cua_may_ceph` bằng tên hostname của máy bạn 
  ```sh
  ceph-deploy osd prepare hostname_cua_may_ceph:sdb
  ceph-deploy osd prepare hostname_cua_may_ceph:sdc
  ceph-deploy osd prepare hostname_cua_may_ceph:sdd
  ```

- Active các OSD vừa tạo ở trên
  ```sh
  ceph-deploy osd activate hostname_cua_may_ceph:/dev/sdb1
  ceph-deploy osd activate hostname_cua_may_ceph:/dev/sdc1
  ceph-deploy osd activate hostname_cua_may_ceph:/dev/sdd1
  ```
  
- Tạo file config và key
  ```sh
  ceph-deploy admin hostname_cua_may_ceph
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
