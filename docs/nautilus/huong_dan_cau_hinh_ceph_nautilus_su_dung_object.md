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

- Khai báo đổi port của civetweb 

- Cập nhật lại file cấu hình cho ceph.

```
ceph-deploy --overwrite-conf config push ceph1 ceph2 ceph3
```

```
ceph-deploy rgw create ceph1 ceph2 ceph3
```

- Kiểm tra trạng thái của `radosgw`

```
systemctl status ceph-radosgw@rgw.ceph1
```

- Kiểm tra pool radosgw

```
ceph osd lspools
```

- Ta thấy danh sách các pool của rgw như bên dưới

```
[root@ceph1 ceph]# ceph osd lspools
1 .rgw.root
2 default.rgw.control
3 default.rgw.meta
4 default.rgw.log
```

- Kiểm tra xem `radosgw` đang chạy trên port nào. Nếu là port `80` là ok.

```
netstat -tunlp | grep radosgw
```


- Thực hiện test bằng cách vào trình duyệt với địa chỉ IP `http://192.168.98.85`, ta thấy kết quả

![](https://image.prntscr.com/image/6BtL5nhHRhK6FjZgyxbpuA.png)

