# Hướng dẫn cấu hình ceph object

## 1. Mô hình

## 2. IP Planning

## 3. Các bước cấu hình

Cài đặt CEPH theo tài liệu (./ceph-deploy install --rgw ceph01 ceph02 ceph03.md)

#### 3.1. Cấu hình CEPH RGW

Đăng nhập vào node `ceph1` và thực hiện cấu hình thêm `RGW` cho CEPH.

- Chuyển sang user `cephuser`

```
su - cephuser
```

- Khai báo `RGW` cho CEPH cluster

```
ceph-deploy install --rgw ceph1 ceph2 ceph3
```