## Ceph monitor.
- Các Ceph monitors lưu một "master copy" của cluster map, có nghĩa là một ceph client có thể xác định vị trí của tất cả Ceph monitors, Ceph OSD Daemons và Ceph metadata servers mà chỉ cần kết nối tới một Ceph monitor và lấy về một bản cluster map. Trước khi ceph client có thể đọc ghi vào Ceph OSD Daemon hoặc Ceph Metadata Servers, nó phải kết nối với Ceph Monitor trước. Với một bản sao cluster map và thuật toán CRUSH, ceph client có thể tính ra vị trí của bất kỳ object nào. Khả năng tính vị trí object này cho phép ceph client nói chuyện trực tiếp với OSD daemon, điều này rất quan trọng cho hiệu năng của ceph.
- Vai trò chính của Ceph Monitor là duy trì một bản copy của cluster map. Ceph Monitor cũng cung cấp dịch vụ xác thực và ghi log. Ceph monitor ghi tất cả những thay đổi trong dịch vụ monitor vào Paxos, Paxos ghi thay đổi này vào `key/store`

	![](../../images/ceph_paxos.png)
	
- Các monitors chịu tránh nhiệm giám sát trạng thái của toàn bộ hệ thống. Có các daemons giữ trạng thái của các thành viên trong cluster bằng cách lưu thông tin của cluster, trạng thái của mỗi node, thông tin cấu hình cluster. Ceph monitor giữ một bản sao master của cluster. Cluster map bao gồm monitor, OSD, PG, CRUSH, và MDS maps. Tập hợp các map này được gọi là cluster map. Chức năng cơ bản của mỗi map:
	- Monitor map: Lưu thông tin về các monitor node. Thông tin bao gồm ID cluster, hostname, IP và port. Monitor cũng lưu thông tin như lúc khởi tạo và lần cuối thay đổi.
	- OSD map: Lưu các thông tin như là ID cluster, epoch tạo OSD map và lần cuối cùng thay đổi; và các thông tin liên quan đến pools như là pool name, pool ID, type, số lượng replication, và PG (placement groups). Các thông tin về osd như là count, state, weight, last clean interval, và osd host.
	- PG map: map này lưu giữ các phiên bản của PG (thành phần quản lý các object trong ceph), timestamp, bản OSD map cuối cùng, tỉ lệ đầy và gần đầy dung lượng. Nó cũng lưu các ID của PG, object count, tình trạng hoạt động và srub (hoạt động kiểm tra tính nhất quán của dữ liệu lưu trữ).
	- CRUSH map: lưu các thông tin của các thiết bị lưu trữ trong Cluster, các rule cho từng vùng lưu trữ.
	- MDS map: lưu thông tin về thời gian tạo và chỉnh sửa, dữ liệu và metadata pool ID, cluster MDS count, tình trạng hoạt động của MDS, epoch của MDS map hiện tại.
	

## 1 Monitor map.
- Monitor map cho chúng ta biết thông tin về toàn bộ monitors trên cluster
- Một số lệnh sau để xem monitor map

```sh
root@cephaio:~# ceph mon stat
e1: 1 mons at {cephaio=10.10.10.11:6789/0}, election epoch 6, quorum 0 cephaio

root@cephaio:~# ceph mon dump
dumped monmap epoch 1
epoch 1
fsid fe7cd007-6da4-4ea6-b04b-754b0e3c64de
last_changed 2017-12-22 09:43:45.690505
created 2017-12-22 09:43:45.690505
0: 10.10.10.11:6789/0 mon.cephaio
```

## 2. MDS map
<Cập nhật sau>

## 3. OSD map
-  OSD map: Lưu các thông tin như là ID cluster, epoch tạo OSD map và lần cuối cùng thay đổi; và các thông tin liên quan đến pools như là pool name, pool ID, type, số lượng replication, và PG (placement groups). Các thông tin về osd như là count, state, weight, last clean interval, và osd host.
- Trạng thái của OSD là `in` hoặc `out` và `up` đang running hoặc `down` không running. Nếu OSD là up, nó có thể là in (có thể đọc ghi dữ liệu) hoặc là out. Nếu osd đã in, sau đó out, ceph sẽ chuyển PG tới các osds khác. Nếu osd là out, crush sẽ không gán PG lên osd đó. Nếu osd là down, nó cũng là out.

```sh
root@cephaio:~# ceph osd dump
epoch 46
fsid fe7cd007-6da4-4ea6-b04b-754b0e3c64de
created 2017-12-22 09:43:46.279410
modified 2018-01-11 07:56:09.082962
flags sortbitwise,require_jewel_osds
pool 0 'rbd' replicated size 2 min_size 1 crush_ruleset 0 object_hash rjenkins pg_num 64 pgp_num 64 last_change 1 flags hashpspool stripe_width 0
max_osd 2
osd.0 up   in  weight 1 up_from 42 up_thru 45 down_at 40 last_clean_interval [37,39) 10.10.10.11:6800/2050 10.10.20.11:6800/2050 10.10.20.11:6801/2050 10.10.10.11:6801/2050 exists,up a53c360b-ca92-4a9b-8105-44621a25c90b
osd.1 up   in  weight 1 up_from 44 up_thru 45 down_at 40 last_clean_interval [35,39) 10.10.10.11:6802/2298 10.10.20.11:6802/2298 10.10.20.11:6803/2298 10.10.10.11:6803/2298 exists,up 33b4b1ae-be78-4be6-8abd-fad9126cdb13
```

## 4. PG map
- Lệnh tạo mới một pool

```sh
ceph osd pool create {pool-name} pg_num
```

- Khi tạo pool cần chỉ rõ tham số `pg_num`. Ở đây có một vài giá trị thường dùng:
	- Ít hơn 5 OSDs đặt pg_num = 128
	- Từ 5 đến 10 OSDs đặt pg_num = 512
	- Từ 10 đến 50 OSDs đặt pg_num = 1024
	- Nếu nhiều hơn 50 OSDs thì phải tính toán phù hợp theo yêu cầu.
	
- Khi mà số lượng OSDs tăng lên, việc đặt giá trị pg_num chính xác là rất quan trọng vì nó ảnh hưởng lớn đến việc xử lý của cluster cũng như đảm bảo dữ liệu an toàn khi có lỗi gì đó xảy ra.

### Placement group được sử dụng như thế nào?
- Placement group (PG) tập hợp các objects trong một pool
	
	![](../../images/ceph_pg.png)

- Ceph client sẽ tính PG mà object sẽ thuộc vào. Việc tính toán này được thực hiện bằng cách băm object ID và áp dụng cho một tác vụ dựa trên số lượng PGs được định nghĩa trong pool và Id của pool.
- Nội dung trên trong một PG được lưu trong một bộ OSDs. Ví dụ, một pool có số replicate là 2, mỗi PG sẽ lưu các object trên 2 OSDs.

	![](../../images/ceph_pgstore.png)
	
- Khi số lượng PG tăng lên, các PG mới sẽ được gán vào các OSDs. CRUSH cũng sẽ thay đổi và một số object từ PGs cũ sẽ được sao chép tới PG mới và xóa từ PG cũ.
- Sau khi một OSD gặp sự cố, nguy cơ mất dữ liệu tăng lên cho đến khi dữ được chứa trong osd đó được khôi phục lại toàn bộ. Một số kịch bản gây ra mất dữ liệu vĩnh viễn trong một PG:
	- OSD hư hỏng và toàn bộ bản sao của object mà osd chứa bị mất. Với tất cả các object có bản sao ở trong osd đều bị giảm từ 3 xuống 2.
	- Ceph bắt đầu khôi phục OSD này bằng cách chọn một osd mới để tạo lại bản copy thứ 3 của tất cả các object đó.
	- Một OSD khác, trong cùng PG đó, hỏng trước khi OSD mới sao chép toàn bộ copy thứ 3. Một số object chỉ còn lại một bản sao.
	- Ceph chọn một OSD khác và giữ các đối tượng sao chép để khôi phục số lượng bản sao mong muốn
	- Một OSD thứ 3, trong cùng PG này, hỏng trước khi khôi phục hoàn thành. Nếu OSD này chứa bản sao duy nhất còn lại của object thì object đó bị mất hoàn toàn.
	
- Trong cluster chứa 10 OSDs với 512 PG và 3 bản sao, CRUSH sẽ cho mỗi PG 3 OSDs. Như vậy mỗi OSD sẽ phải chứa lên đến (512*3)/10 = ~150 PGs. Khi OSD đầu tiên hỏng, ceph sẽ phải khôi phục tất cả 150 PG cùng lúc.
- 150 PGs được phục hồi có thể lan ra 9 OSD còn lại. Mỗi OSD còn lại gửi bản sao của objects tới tất cả OSD khác và cũng nhận các objects mới bởi vì chúng trở thành một phần của PG mới.
- Lượng thời gian để khôi phục hoàn toàn phụ thuộc vào kiến trúc của cluster.

### Cách tính số PG.
- PG là rất quan trọng, ảnh hưởng đến hiệu năng cũng như độ an toàn của dữ liệu.
- Công thức tính số PG cho mỗi pool như sau

	![](../../images/ceph_total_pg.png)
	
- `pool size` là số lượng replicate cho pool hoặc K + M cho erasure coded pools.
- Ví dụ về một PG map

```
~# ceph pg dump
dumped all in format plain
version 378
stamp 2018-01-16 09:05:02.505632
last_osdmap_epoch 69
last_pg_scan 69
full_ratio 0.95
nearfull_ratio 0.85
pg_stat objects mip     degr    misp    unf     bytes   log     disklog state   state_stamp     v       reported        up      up_primary      acting  acting_primary     last_scrub      scrub_stamp     last_deep_scrub deep_scrub_stamp
1.e     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.557715      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453495      0'0     2018-01-11 10:51:03.453495
0.f     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.620672      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 10:16:12.611201      0'0     2018-01-09 10:48:19.413307
1.f     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.554232      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453498      0'0     2018-01-11 10:51:03.453498
0.e     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.606054      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:58.729559      0'0     2018-01-09 10:49:14.498889
1.c     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.558109      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453489      0'0     2018-01-11 10:51:03.453489
0.d     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.620816      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:32.710388      0'0     2018-01-09 10:48:59.463102
1.d     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.557410      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453491      0'0     2018-01-11 10:51:03.453491
0.c     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.580751      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:51.728760      0'0     2018-01-09 10:48:57.182386
1.a     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.553640      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453484      0'0     2018-01-11 10:51:03.453484
0.b     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.605291      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:44.720342      0'0     2018-01-09 10:48:03.386157
1.b     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.539976      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453487      0'0     2018-01-11 10:51:03.453487
0.a     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.675761      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:35:21.786784      0'0     2018-01-09 10:48:43.172624
1.8     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.520763      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453479      0'0     2018-01-11 10:51:03.453479
0.9     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.521390      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:53.746911      0'0     2018-01-10 23:10:01.300851
1.9     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.553093      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453480      0'0     2018-01-11 10:51:03.453480
0.8     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.604543      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:04.734573      0'0     2018-01-09 10:49:18.504020
1.6     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.620887      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453474      0'0     2018-01-11 10:51:03.453474
0.7     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.619655      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:34.709746      0'0     2018-01-09 10:48:27.429901
1.7     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.413536      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453476      0'0     2018-01-11 10:51:03.453476
0.6     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.642020      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:05.692876      0'0     2018-01-09 10:48:37.167018
1.4     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.507018      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453469      0'0     2018-01-11 10:51:03.453469
0.5     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.641567      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:01.759140      0'0     2018-01-12 08:19:01.759140
1.5     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.507070      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453472      0'0     2018-01-11 10:51:03.453472
0.4     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.637459      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:02.684721      0'0     2018-01-09 10:48:07.124722
0.3f    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.579730      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:20:06.757178      0'0     2018-01-09 10:48:41.169491
0.3e    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.584692      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:56:36.691018      0'0     2018-01-10 23:09:57.973020
0.3d    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.606473      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:57:54.763828      0'0     2018-01-09 10:48:56.464663
0.3c    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.584956      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 10:14:44.550817      0'0     2018-01-12 10:14:44.550817
0.3b    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.619347      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:19.743888      0'0     2018-01-09 10:48:24.424490
0.3a    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.605601      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:05.683944      0'0     2018-01-09 10:48:25.430764
0.22    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.572857      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:03.677726      0'0     2018-01-09 10:48:16.419492
0.21    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.644305      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:20:17.797408      0'0     2018-01-09 10:49:02.187247
0.20    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.566683      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:17.739597      0'0     2018-01-09 10:49:23.509486
1.1e    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.507150      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453545      0'0     2018-01-11 10:51:03.453545
0.1f    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.642298      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:46.723315      0'0     2018-01-09 10:48:52.176550
1.1f    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.513967      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453547      0'0     2018-01-11 10:51:03.453547
0.1e    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.577933      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 09:53:59.996487      0'0     2018-01-09 10:47:59.103603
1.1c    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.513913      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453541      0'0     2018-01-11 10:51:03.453541
0.1d    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514875      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:20:16.796682      0'0     2018-01-09 10:48:50.175636
1.1d    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.552337      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453543      0'0     2018-01-11 10:51:03.453543
0.1c    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514784      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 10:38:38.395126      0'0     2018-01-10 23:09:55.966583
1.1a    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.529337      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453537      0'0     2018-01-11 10:51:03.453537
0.1b    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.566310      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 10:13:11.439876      0'0     2018-01-10 23:10:57.407110
1.1b    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.513829      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453539      0'0     2018-01-11 10:51:03.453539
0.1a    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514728      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:20:09.790310      0'0     2018-01-09 10:48:12.145303
1.3     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.507109      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453466      0'0     2018-01-11 10:51:03.453466
0.2     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.586211      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:30.710793      0'0     2018-01-09 10:48:13.134284
0.31    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.521193      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:35.712897      0'0     2018-01-09 10:49:29.518504
1.18    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.552903      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453532      0'0     2018-01-11 10:51:03.453532
0.19    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514629      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 09:29:08.614719      0'0     2018-01-09 10:48:58.186722
1.10    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.672954      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453500      0'0     2018-01-11 10:51:03.453500
0.11    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.676030      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:07.696565      0'0     2018-01-10 23:09:45.946286
1.11    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.674898      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453502      0'0     2018-01-11 10:51:03.453502
0.10    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.676135      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:20:04.754035      0'0     2018-01-09 10:47:52.087627
1.19    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.529141      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453535      0'0     2018-01-11 10:51:03.453535
0.18    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.559775      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:45.720955      0'0     2018-01-09 10:49:10.487190
1.0     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.520684      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453421      0'0     2018-01-11 10:51:03.453421
0.1     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.521246      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:41.717803      0'0     2018-01-12 08:19:41.717803
0.30    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.521338      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:18.700512      0'0     2018-01-09 10:49:27.515470
1.16    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.540008      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453514      0'0     2018-01-11 10:51:03.453514
0.17    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.675922      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:56.750304      0'0     2018-01-09 10:48:53.180178
1.1     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.524101      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453458      0'0     2018-01-11 10:51:03.453458
0.0     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.592204      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 09:06:55.301339      0'0     2018-01-09 10:48:45.173255
0.2f    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.620625      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:06.735932      0'0     2018-01-09 10:48:53.458910
1.17    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.672238      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453516      0'0     2018-01-11 10:51:03.453516
0.16    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.675876      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:17.705254      0'0     2018-01-09 10:49:00.184005
1.13    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.557204      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453506      0'0     2018-01-11 10:51:03.453506
0.12    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.620501      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:14.698578      0'0     2018-01-09 10:47:52.356352
1.12    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.514265      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453505      0'0     2018-01-11 10:51:03.453505
0.13    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.507733      0'0     69:88   [1,0]   1       [1,0]   1 0'0      2018-01-12 16:01:09.410774      0'0     2018-01-09 10:48:48.447673
1.15    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.520513      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453510      0'0     2018-01-11 10:51:03.453510
0.14    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.520932      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:13.737870      0'0     2018-01-09 10:48:14.407106
1.14    0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.520596      0'0     69:43   [1,0]   1 [1,0]    1       0'0     2018-01-11 10:51:03.453509      0'0     2018-01-11 10:51:03.453509
0.15    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.521035      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:27.752125      0'0     2018-01-10 23:09:16.202468
0.23    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.644440      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:49.727184      0'0     2018-01-10 23:09:20.969565
0.24    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.573032      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:01.731600      0'0     2018-01-09 10:48:57.464069
0.25    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.573305      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 09:18:24.991944      0'0     2018-01-09 10:48:43.442802
0.26    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.572235      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:08.734725      0'0     2018-01-09 10:49:22.508123
0.27    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.558988      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:25.745496      0'0     2018-01-12 08:20:25.745496
0.28    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.559328      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:39.713381      0'0     2018-01-12 08:19:39.713381
0.29    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.669782      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:20:14.793199      0'0     2018-01-10 23:09:29.921034
0.2a    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514416      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 10:24:05.541193      0'0     2018-01-12 10:24:05.541193
0.2b    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514483      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 16:01:04.999288      0'0     2018-01-12 16:01:04.999288
0.2c    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514533      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:20:21.801728      0'0     2018-01-12 08:20:21.801728
0.2d    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.514584      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:55.749441      0'0     2018-01-09 10:47:55.090330
0.2e    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.521095      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:16.699462      0'0     2018-01-09 10:47:59.373414
1.2     0       0       0       0       0       0       0       0       active+undersized+degraded      2018-01-16 09:04:53.524017      0'0     69:38   [0,1]   0 [0,1]    0       0'0     2018-01-11 10:51:03.453463      0'0     2018-01-11 10:51:03.453463
0.3     0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.586157      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:54.748620      0'0     2018-01-09 10:48:28.159522
0.32    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.620767      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 09:13:43.721110      0'0     2018-01-09 10:49:28.516720
0.33    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.675708      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:29.712009      0'0     2018-01-12 08:19:29.712009
0.34    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.620288      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:31:45.695977      0'0     2018-01-09 10:48:10.400834
0.35    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.619933      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:20:15.741413      0'0     2018-01-12 08:20:15.741413
0.36    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.586016      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:06.695305      0'0     2018-01-12 08:19:06.695305
0.37    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.604749      0'0     69:86   [1,0]   1       [1,0]   1 0'0      2018-01-12 08:19:31.707592      0'0     2018-01-09 10:47:49.344771
0.38    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.585959      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 10:13:25.471893      0'0     2018-01-09 10:49:04.193629
0.39    0       0       0       0       0       0       0       0       active+clean    2018-01-16 09:04:53.580234      0'0     69:100  [0,1]   0       [0,1]   0 0'0      2018-01-12 08:19:19.707230      0'0     2018-01-10 23:09:51.958248
pool 1  0       0       0       0       0       0       0       0
pool 0  0       0       0       0       0       0       0       0
 sum    0       0       0       0       0       0       0       0
osdstat kbused  kbavail kb      hb in   hb out
1       35460   20924776        20960236        [0]     []
0       36000   20924236        20960236        [1]     []
 sum    71460   41849012        41920472
```
 

- Link tham khảo: http://docs.ceph.com/docs/master/rados/operations/placement-groups/

## 5. CRUSH map
- Hệ thống lưu trữ sẽ phải lưu phần data và metadata của nó. Metadata, là dữ liệu của dữ liệu, lưu thông tin như nơi data được lưu trong chuỗi các node storage và các disk. Mỗi lần dữ liệu mới được thêm vào, metadata của nó sẽ được cập nhật trước khi dữ liệu được lưu. Việc quản lý metadata rất phức tạp và khó khăn khi dữ liệu lớn.
- Ceph sử dụng thuật toán `Controlled Replication Under Scalable Hashing (CRUSH)` để thực hiện lưu trữ và quản lý dữ liệu.
- Thuật toán CRUSH dùng để tính toán nơi dữ liệu sẽ được lưu hoặc nơi dữ liệu sẽ được đọc. Thay vì lưu trữ metadata, CRUSH tính metadata dự trên yêu cầu.
- CRUSH tính metadata chỉ khi có yêu cầu. Quá trình tính toán này được biết với tên gọi CRUSH lookup.
- Với yêu cầu đọc và ghi, đầu tiên client liên hệ với monitor và tìm một bản copy của cluster map. Cluster map giúp client biết trạng thái và cấu hình của cluster. Data sẽ được biến đổi thành các objects. Sau đó object sẽ được băm với số PG để sinh ra một PG không thay đổi trong ceph pool. Sau khi tính xong PG, CRUSH lookup xác định primary OSD để lưu và tìm kiếm data. ID của OSD primary được gửi cho client, client sẽ làm việc trực tiếp với OSD để lưu dữ liệu. Tất cả các thao tác tính toán đều được thực hiện bởi client, do đó không ảnh hưởng đến hiệu năng của cluster. 
- Một khi data dược ghi lên primary OSD, trên cùng node đó thực hiện một tác vụ CRUSH lookup và tính vị trí secondary PG và các OSD, nơi mà data sẽ được sao chép.

	![](../../images/ceph_crush_lookup.png)

### Cấu trúc phân cấp của CRUSH
- CRUSH là cơ sở để hiểu ceph và hoàn toàn có khả năng cấu hình; nó duy trì một phân cấp lồng nhau cho tất cả các thành phần của cơ sở hạ tầng của bạn. Danh sách các thiết bị CRUSH thường gồm có disk, node, rack, row, switch, dòng điện, room, data center, etc. Những thành phần này được gọi là failure zones hoặc CRUSH buckets.
- CRUSH map chứ danh sách các buckets để tập hợp các thiết bị vào trong vị trí vật lý. Và một danh sách các rule để cho CRUSH biết cách sao chép data cho các ceph pool khác nhau. Hình sau sẽ mô tả tổng quan về CRUSH map.

	![](../../images/ceph_crush.png)

- Lấy ra CRUSH  map bằng các lệnh sau

```sh
ceph osd getcrushmap -o crushmap.bin
crushtool -d crushmap.bin -o crushmap.txt
```

- `crushmap.bin` là tên file, file này chứa crush map ở dạng nhị phân. Để đọc được file này, crushtool chuyển từ nhị phân sang dạng file text.
- Ví dụ nội dung một crush map như sau:

```sh
# begin crush map
tunable choose_local_tries 0
tunable choose_local_fallback_tries 0
tunable choose_total_tries 50
tunable chooseleaf_descend_once 1
tunable chooseleaf_vary_r 1
tunable straw_calc_version 1

# devices
device 0 osd.0
device 1 osd.1

# types
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

# buckets
host cephaio {
        id -2           # do not change unnecessarily
        # weight 0.039
        alg straw
        hash 0  # rjenkins1
        item osd.0 weight 0.019
        item osd.1 weight 0.019
}
root default {
        id -1           # do not change unnecessarily
        # weight 0.039
        alg straw
        hash 0  # rjenkins1
        item cephaio weight 0.039
}

# rules
rule replicated_ruleset {
        ruleset 0
        type replicated
        min_size 1
        max_size 10
        step take default
        step choose firstn 0 type osd
        step emit
}

# end crush map
```

- CRUSH map có các section như sau:
	- `tunables`: Cấu hình thuật toán CRUSH
	- `Devices`: là các OSD daemon riêng lẻ. Các thiết bị được định danh với ID là số nguyên không âm và tên có định dạng osd.N, N là id của osd. Device cũng có thể chứa một lớp các thiết bị liên quan (ví dụ hdd, ssd) thuận tiện cho đặt các rules.
	- `type và buckets`: buckets là thuật ngữ trong CRUSH để chỉ hệ thống phân cấp trong các node: hosts, racks, rows, etc. CRUSH map định nghĩa một loạt các `types` được sử dụng để miêu tả các node này. Mặc định có các type: osd (or device), host, chassis, rack, row, pdu, pod, room, datacenter, region, root. Đa số các cluster sử dụng các type này. Type có thể được định nghĩa nếu cần thiết. Hình dung bucket như cấu trúc cây. Các device là các osd ở nút lá, bắt đầu bằng root. ví dụ
	
		![](../../images/ceph_bucket.png)
		
	Mỗi node (device hoặc bucket) có một trọng số `weight `, chỉ ra tỉ lệ tương đối của tổng dữ liệu mà các device hoặc subtree sẽ lưu. weight được đặt ở lá, chỉ ra kích thước của device, và tự động tổng hợp cây từ đó, sao cho trọng lượng của nút mặc định sẽ là tổng của tất cả các thiết bị chứa bên dưới nó. Thông thường trọng lượng được tính bằng đơn vị terabyte (TB).
	- `rules`: Định nghĩa chính sách mà dữ liệu được phân tán trên các thiết bị. Trong ví dụ trên có một rule là replicated_ruleset. Các rule có thể xem được bằng CLI 
	
```
root@cephaio:~# ceph osd crush rule ls
[
		"replicated_ruleset"
]

root@cephaio:~# ceph osd crush rule dump
[
	{
		"rule_id": 0,
		"rule_name": "replicated_ruleset",
		"ruleset": 0,
		"type": 1,
		"min_size": 1,
		"max_size": 10,
		"steps": [
				{
					"op": "take",
					"item": -1,
						"item_name": "default"
				},
				{
					"op": "choose_firstn",
					"num": 0,
					"type": "osd"
				},
				{
					"op": "emit"
				}
		]
	}
]
```