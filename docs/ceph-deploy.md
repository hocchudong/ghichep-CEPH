
### Khai bao file /etc/hosts tren ca ceph1
  ```sh
  127.0.0.1       localhost ceph1
  10.10.10.61     ceph1
  10.10.10.62     ceph2
  10.10.10.63     ceph3
  ```

### Khai bao file /etc/hosts tren ca ceph2
  ```sh
  127.0.0.1       localhost ceph2
  10.10.10.61     ceph1
  10.10.10.62     ceph2
  10.10.10.63     ceph3
  ```

### Khai bao file /etc/hosts tren ca ceph3
  ```sh
  127.0.0.1       localhost ceph3
  10.10.10.61     ceph1
  10.10.10.62     ceph2
  10.10.10.63     ceph3
  ```

### Tao user ten là cephuser tren tat ca cac node: ceph1, ceph2, ceph3
  ```sh
  useradd -d /home/cephuser -m cephuser
  passwd cephuser
  echo "cephuser ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/cephuser
  chmod 0440 /etc/sudoers.d/cephuser
  ```

### Tao ssh key 

- Dung tren ceph1 tao cap key
  ```sh
  su - cephuser
  ssh-keygen -t rsa
  ```

- Copy public key tu ceph1 sang ceph2 va ceph3
  ```sh
  ssh-copy-id cephuser@ceph2
  ssh-copy-id cephuser@ceph3
  ```

## Bat dau cai dat CEPH
- Dung tren ceph1 cai dat
  ```sh
  sudo wget -q -O- 'https://download.ceph.com/keys/release.asc' | sudo apt-key add -
  sudo echo deb http://download.ceph.com/debian-jewel/ $(lsb_release -sc) main | sudo tee /etc/apt/sources.list.d/ceph.list
  sudo apt-get update
  sudo apt-get -y update && sudo apt-get -y install ntp ceph-deploy
  ```

- Cai dat thanh pham MON tren CEPH1
  ```sh
  ceph-deploy new ceph1
  ```

- Mo file ceph.conf vua duoc tao ra o tren va them dong duoi
  ```
  osd pool default size = 2
  ```

- Cai dat CEPH
  ```sh
  ceph-deploy install --release jewel ceph1 ceph2 ceph3

  ceph-deploy mon create-initial
  ```

- Kiem tra cac disk tren cac node 
  ```sh
  ceph-deploy disk list ceph1
  ceph-deploy disk list ceph2
  ceph-deploy disk list ceph3
  ```


- Tao cac OSD tren cac node 
  ```sh
  ceph-deploy osd create ceph1:sdc ceph2:sdc ceph3:sdc
  ceph-deploy osd create ceph1:sdd ceph2:sdd ceph3:sdd
  ceph-deploy osd create ceph1:sde ceph2:sde ceph3:sde
  ```













