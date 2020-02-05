# Ceph Block Storage Gateway
![ceph RBD](http://image.prntscr.com/image/cb931be8c87f4fc190fe7c7e2e5f30eb.png)

 Block Storage là định dạng lưu trữ trong môi trường doanh nghiệp. Ceph Block Device có tên là RADOS block device (RBD); cung cấp block storage cho hypervisor và máy ảo. Ceph RBD driver được tích hợp với Linux kernel (từ bản 2.6.39) và hỗ trợ QEMU/KVM.

 Máy chủ Linux hỗ trợ Kernel RBD (KRBD), map block device dùng librados. RADOS lưu các object của Ceph block device phân tán trên cluster. Khi Ceph block device được map vào máy chủ Linux, nó có thể được sử dụng như một phân vùng RAW hoặc cố thể định dạng theo các loại filesystem phổ biến.

 Ceph đã được tích hợp chặt chẽ với các nền tảng Cloud như OpenStack. Ceph cung cấp backend là block device để lưu trữ volume máy ảo và OS image choCinder và Glance. Các volume và image này là thin provisioned, có nghĩa chỉ lưu trữ các dữ liệu object bị thay đổi, giúp tiết kiệm tài nguyên lưu trữ.

 Tính năng copy-on-write và cloning của Ceph giúp OpenStack tạo hàng trăm máy ảo trong thời gian ngắn. RBD cũng hỗ trợ snapshot, giúp lưu giữ trạng thái máy ảo, dùng để khôi phục máy ảo lại môt thời điểm hoặc để tạo ra một máy ảo khác tương tự. Ceph cũng là backend cho máy ảo, giúp di chuyển máy ảo giữa các node Compute bởi tất cả dữ liệu máy ảo đều nằm trên Ceph. Các hypervisor như QEMY, KVM, XEN có thể boot máy ảo từ volume nằm trên Ceph.

 RBD sử dụng thư viện librbd để tận dụng các tiện ích của RADOS và cung cấp tính tin cậy, phân tán và khả năng lưu trữ dựa trên object. Khi client ghi dữ liệu xuống RBD, thư viện librbd map data block vào các object để lưu xuống Ceph cluster, nhân bản chúng trên Cluster, tăng hiệu năng và độ tin cậy dữ liệu. RBD hỗ trợ update vào các object. Client có thể ghi, nối thêm, cắt xén vào các object đang có. Do đó RBD là giải pháp lưu trữ tối ưu cho volume máy ảo.

 Ceph RBD đang thay thế giải pháp lưu trữ SAN đắt tiền bằng cách cung cấp các tính năng cao câp như  thin provisioning, copy-on-write snapshot và clone, read-only snapshot, hỗ trợ các nền tảng cloud như OpenStack và CloudStack.