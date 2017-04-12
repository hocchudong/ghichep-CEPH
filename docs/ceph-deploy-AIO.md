## Hướng dẫn cài đặt CEPH sử dụng `ceph-deploy` trên 1 máy duy nhất (CEPH AIO)

### Mục tiêu LAB
- Mô hình này sẽ cài tất cả các thành phần của CEPH lên một máy duy nhất, bao gồm:
  - ceph-deploy
  - ceph-admin
  - mon
  - OSD
- Máy CEPH AIO được cài đặt để tích hợp với hệ thống OpenStack
- LAB này chỉ phù hợp với việc nghiên cức các tính năng và demo thử nghiệm, không áp dụng được trong thực tế.

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
  echo "172.16.69.247 cephAIO" >> /etc/hosts
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

- Copy ssh key để sử dụng, thay `cephAIO` bằng tên hostname của máy bạn nếu có thay đổi.
  ```sh
  ssh-copy-id ceph-deploy@cephAIO
  ```

  - Nhập `Yes` và mật khẩu của user `ceph-deploy` đã tạo ở trước, kết quả như bên dưới
    ```sh
    ceph-deploy@cephAIO:~$ ssh-copy-id ceph-deploy@cephAIO
    The authenticity of host 'cephaio (172.16.69.247)' can't be established.
    ECDSA key fingerprint is f2:38:1e:50:44:94:6f:0a:32:a3:23:63:90:7b:53:27.
    Are you sure you want to continue connecting (yes/no)? yes
    /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
    /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
    ceph-deploy@cephaio's password:

    Number of key(s) added: 1

    Now try logging into the machine, with:   "ssh 'ceph-deploy@cephAIO'"
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
  ceph-deploy new cephAIO
  ```

- Sau khi thực hiện lệnh trên xong, sẽ thu được 03 file ở dưới (sử dụng lệnh `ll -alh` để xem). Trong đó cần cập nhật file `ceph.conf` để cài đặt CEPH được hoàn chỉnh.
  ```sh
  ceph-deploy@cephAIO:~/my-cluster$ ls -alh
  total 20K
  drwxrwxr-x 2 ceph-deploy ceph-deploy 4.0K Apr 12 17:11 .
  drwxr-xr-x 5 ceph-deploy ceph-deploy 4.0K Apr 12 17:11 ..
  -rw-rw-r-- 1 ceph-deploy ceph-deploy  198 Apr 12 17:11 ceph.conf
  -rw-rw-r-- 1 ceph-deploy ceph-deploy 3.2K Apr 12 17:11 ceph-deploy-ceph.log
  -rw------- 1 ceph-deploy ceph-deploy   73 Apr 12 17:11 ceph.mon.keyring
  ceph-deploy@cephAIO:~/my-cluster$
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
