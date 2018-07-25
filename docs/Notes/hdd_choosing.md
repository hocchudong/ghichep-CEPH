Bài viết sau tham khảo từ https://www.dreamhost.com/blog/2016/10/01/dreamhost-builds-cloud-selecting-hard-drives/

# 1. Hệ thống lưu trữ hiệu năng thấp
DreamHost trình bày về kinh nghiệm của họ khi hệ thống lưu trữ thử nghiệm của họ nhận được các phản hồi về throuput thấp và latency cao, mặc dù lượng dữ liệu lưu trữ không lớn như dự tính ban đầu. Có thể liệt kê ra 3 nguyên nhân sau:

## 1.1. Nguyên nhân đầu tiên: CPU và RAM
Họ sử dụng cùng một cấu hình với DreamObject, nơi lưu trữ dung lượng lớn nhưng lượng truy xuất không nhiều. Tuy nhiên, ở hệ thống beta thì ngược lại, họ lưu trữ lượng dữ liệu nhỏ với mật độ truy xuất thường xuyên.

## 1.2. Nguyên nhân thứ hai: mật độ lưu trữ
Hiệu năng của Ceph sẽ tốt hơn khi sử dụng càng ít ổ đĩa trên 1 host. Tiến trình Recovery (khôi phục dữ liệu) cũng nhanh hơn khi sử dụng các ổ đĩa dung lượng nhỏ.

## 1.3. Nguyên nhân thứ ba: SAS Expander. 
Họ sử dụng RAID Card với 4 kênh, tức có thể truy xuất 4 ổ đĩa một lúc, trong khi họ có 14 ổ đĩa (12 cho Ceph, 2 cho OS). Do đó, cần phải dùng một thiết bị là "SAS Expander", đứng giữa RAID Card và ổ đĩa. SAS Expander sử dụng chỉ hỗ trợ đủ bâng thông cho 2 lanes, do đó khi nhiều ổ đĩa hoạt động đồng thời, tốc độ sẽ bị giảm.

# 2. Kinh nghiệm lựa chọn SSD
Từ những phản hồi của người dùng, DreamHost biết fast IO và low latency là rất quan trọng, do đó họ lựa chọn SSD làm ổ lưu trữ.
Các tiêu chí khi lựa chọn SSD của họ gồm 3 tiêu chí:

## 2.1. Giao tiếp : 
SATA có max throughput là 6GB/s, SAS có max throughput là 12 GB/s, tuy nhiên nhược điểm của SAS là nó không được hỗ trực tiếp bởi các server chipset, có nghĩa bạn phải đặt các SAS driver sau RAID Card, kể cả khi không dùng đến RAID. NVMe là chuẩn giao tiếp được thiết kế riêng cho SSD, có tốc độ nhanh gấp đôi SATA, tuy nhiên giá thành quá cao so với SATA hay SAS, do đó SATA là lựa chọn tối ưu nhất.

## 2.2. Loại ổ: 
Hiện có 3 loại SSD phổ biến là SLC, MLC, TLC với tốc độ và độ bền giảm dần theo thứ tự, cùng với chỉ số giá/GB. Các ổ Enterprise SSD gần tương tự với các SSD dùng trong PC, điểm khác biệt lớn nhất là Enterprise SSD được tích hợp Supercapacitor, có tác dụng dự phòng khi nguồn điện gặp lỗi, sẽ hoàn thành tác vụ ghi, bảo vệ dữ liệu khỏi corrupt. Một điểm khác biệt nữa là Enterprise SSD sẽ có lượng cell dự phòng lớn hơn SSD phổ thông (do các cell sẽ bị hỏng trong quá trình sử dụng), nên dung lượng của Enterprise SSD thường thấp hơn so với SSD phổ thông.

## 2.3. Sử dụng RAID hay không: 
RAID Card cung cấp dự phòng cho ổ đĩa, điều không cần thiết với hệ thống Ceph đã có native HA, RAID Card cũng có nguồn dự phòng để bảo vệ dữ liệu trong trường hợp nguồn của host bị lỗi, đồng thời có RAID cache cho Driver.
