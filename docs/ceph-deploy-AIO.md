## Hướng dẫn cài đặt CEPH sử dụng `ceph-deploy` trên 1 máy duy nhất (CEPH AIO)

### Mục tiêu LAB
- Mô hình này sẽ cài tất cả các thành phần của CEPH lên một máy duy nhất, bao gồm:
  - ceph-deploy
  - ceph-admin
  - mon
  - OSD
- Máy CEPH AIO được cài đặt để sẵn sàng tích hợp với hệ thống OpenStack

## Mô hình 
` cập nhật mô hình`

## IP Planning
` cập nhật ip planning`

## Chuẩn bị và môi trường LAB
 
- OS
  - Ubuntu Server 14.04 - 64 bit
  - 04: HDD, trong đó:
    - sda: sử dụng để cài OS
    - sdb: sử dụng làm `journal` (Journal là một lớp cache khi client ghi dữ liệu, thực tế thường dùng ổ SSD để làm cache)
    - sdc, sdd: sử dụng làm OSD (nơi chứa dữ liệu của client)
  - 02 NICs: 
    - eth0 dùng để replicate cho CEPH. 10.10.10.231/24
    - eth1 dùng để ssh và client sử dụng. 172.16.69.247/24
  
- CEPH Jewel

## Cài đặt CEPH

- Thực hiện bằng quyền root
  ```sh
  su -
  ```
  
- Đặt hostname cho máy cài AIO
  ```sh
  echo "cephAIO" > /etc/hostname
  hostname -F /etc/hostname
  ```

- Sửa file host 
  ```sh
  echo "172.16.69.247 cephAIO" >> /ect/hosts
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

- Copy ssh key để sử dụng, trong quá trình copy lựa chọn theo hướng dẫn và nhập mật khẩu của user `ceph-deploy`. Thay `cephAIO` bằng tên hostname của máy bạn nếu có thay đổi.
  ```sh
  ssh-copy-id ceph-deploy@cephAIO
  ```

- Tạo các thư mục để công cụ `ceph-deploy` sử dụng để cài đặt CEPH
  ```sh
  cd ~
  mkdir my-cluster
  cd my-cluster
  ```

- Thiết lập các file cấu hình cho CEPH.
  ```sh
  ceph-deploy new cephAIO
  ```

- Thêm các dòng dưới vào file `ceph.conf` vừa được tạo ra ở trên
  ```sh
  echo "osd pool default size = 2" >> ceph.conf
  echo "osd crush chooseleaf type = 0" >> ceph.conf
  echo "osd journal size = 8000" >> ceph.conf
  echo "public network = 172.16.69.0/24" >> ceph.conf
  echo "cluster network = 10.10.10.0/24" >> ceph.conf
  ```
  
- Cài đặt CEPH, thay `cephAIO` bằng tên hostname của máy bạn nếu có thay đổi.
  ```sh
  ceph-deploy install cephAIO
  ```

- Cấu hình `MON` (một thành phần của CEPH)
  ```sh
  ceph-deploy mon create-initial
  ```

- Tạo các OSD cho CEPH, thay `cephAIO` bằng tên hostname của máy bạn 
  ```sh
  ceph-deploy osd prepare cephAIO:sdc:/dev/sdb
  ceph-deploy osd prepare cephAIO:sdd:/dev/sdb
  ```

- Active các OSD vừa tạo ở trên
  ```sh
  ceph-deploy osd activate cephAIO:/dev/sdc1:/dev/sdb1
  ceph-deploy osd activate cephAIO:/dev/sdd1:/dev/sdb2
  ```
  
- Tạo file config và key
  ```sh
  ceph-deploy admin cephAIO
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
