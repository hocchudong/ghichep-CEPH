# CEPH RADOS
 RADOS (Reliable Autonomic Distributed Object Store) là trái tim của hệ thống lưu trữ CEPH,. RADOS cung cấp tất cả các tính năng của Ceph, gồm lưu trữ object phân tán, sẵn sàng cao, tin cậy, kkhông có SPOF, tự sửa lỗi, tự quản lý,... lớp RADOS giữ vai trò đặc biệt quan trọng trong kiến trúc Ceph. Các phương thức truy xuất Ceph, như RBD, CephFS, RADOSGW và librados, đều hoạt động trên lớp RADOS.
 Khi Ceph cluster nhận một yêu cầu ghi từ người dùng, thuật toán CRUSH tính toán vị trí và thiết bị mà dữ liệu sẽ được ghi vào. Các thông tin này được đưa lên lớp RADOS để xử lý. Dựa vào quy tắc của CRUSH, RADOS phân tán dữ liệu lên tất cả các node dưới dạng câc object. Cuối cùng ,các object này được lưu tại các OSD.

 RADOS, khi cấu hình với số nhân bản nhiều hơn hai, sẽ chịu trách nhiệm về độ tin cậy của dữ liệu. Nó sao chép object, tạo các bản sao và lưu trữ tại các zone khác nhau, do đó các bản ghi giống nhau không nằm trên cùng 1 zone. RADOS đảm bảo có nhiều hơn một bản copy của object trong RADOS cluster.
 RADOS cũng đảm bảo object luôn nhất quán. Trong trường hợp object không nhất quán, tiến trình khôi phục sẽ chạy. Tiến trình này chạy tự động và trong suốt với người dùng, do đó mang lại khả năng tự sửa lỗi và tự quẩn lý cho Ceph. RADOS có 2 phần: phần thấp không tương tác trực tiếp với giao diện người dùng, và phần cao hơn có tất cả giao diện người dùng.

 RADOS lưu dữ liệu dưới trạng thái các object trong pool. 
 Để liệt kê danh sách các pool:
 ```
 rados lspools
 ```

 Để liệt kê các object trong pool:
 ```
  rados -p [pool] ls
  ```

 Để kiểm tra tài nguyên sử dụng:
 ```
 rados df
 ```

 RADOS có 2 thành phần lõi: OSD và monitor

 