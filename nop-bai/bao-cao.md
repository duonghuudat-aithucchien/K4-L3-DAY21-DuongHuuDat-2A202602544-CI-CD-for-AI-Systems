# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Dương Hữu Đạt |
| MSSV | 2A202602544 |
| Lớp / Khóa | K4-L3-2026 |
| Repo GitHub | https://github.com/duonghuudat-aithucchien/K4-L3-DAY21-DuongHuuDat-2A202602544-CI-CD-for-AI-Systems |
| Ngày nộp | 07/10/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:**
Dựa vào kết quả trên MLflow, bộ siêu tham số thứ 3 mang lại f1_score cao nhất (0.7149) nên được chọn. Đáng chú ý, lần chạy 1 có accuracy cao hơn (0.8780 so với 0.8740) nhưng f1_score lại thấp hơn. Điều này chỉ ra rằng ở tập dữ liệu mất cân bằng, accuracy không phản ánh đúng khả năng nhận diện lớp thiểu số. Bên cạnh đó, ta thấy rõ sự đánh đổi giữa các siêu tham số: tăng độ sâu của cây và số lượng cây cần đi kèm với một tốc độ học đủ lớn (0.1) để tối ưu mô hình, trong khi tốc độ học nhỏ kết hợp độ sâu nông khiến mô hình kém đi đáng kể.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Vì tập dữ liệu có sự mất cân bằng lớp (tỷ lệ người thu nhập >50K chỉ khoảng 24.8%). Nếu dùng Accuracy, một mô hình cực đoan chỉ đoán "thu nhập thấp" cho tất cả mọi người cũng có thể dễ dàng đạt Accuracy khoảng 75%, gây ảo tưởng về sức mạnh của mô hình. Ngược lại, F1-score (đối với lớp thiểu số thu nhập cao) đo lường sự cân bằng giữa Precision và Recall. Nó phản ánh chính xác khả năng mô hình phát hiện ra được lớp dương mà không bắt nhầm quá nhiều. Do đó F1-score là độ đo đáng tin cậy hơn để đặt ngưỡng chất lượng (Quality Gate). Ta KHÔNG dùng `average="weighted"` hay `average="macro"` vì chúng làm mờ đi hiệu suất thực sự trên lớp thiểu số bằng cách lấy trung bình với lớp đa số.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Lỗi `MissingConfigException` trong GitHub Actions | Máy ảo runner không tìm thấy thư mục `mlruns/` do không đẩy lên Git | Đưa thư mục `mlruns/` vào `.gitignore`, xóa khỏi cache git để tự sinh khi chạy mới |
| Lỗi Command Not Found (Exit code 127) ở pipeline | Lệnh `aws` và `dvc` không được nhận diện tự động trong môi trường `$PATH` của runner | Sửa file `cicd.yml` để gọi qua python: `python -m dvc` và dùng script `boto3` để upload model |
| Bị nuốt dấu ngoặc kép khi test API bằng `curl.exe` | Do cơ chế escape string của PowerShell trên môi trường Windows | Chuyển sang dùng native `Invoke-RestMethod` của PowerShell với tham số `-Body` |

---

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2`) | 0.7354 | 0.8820 |

**Nhận xét:**
Việc bổ sung thêm 22.361 mẫu dữ liệu mới có cùng phân phối giúp củng cố các đặc trưng mô hình đã học, khiến cả F1-score và Accuracy có sự gia tăng nhẹ (~0.02). Trọng tâm của bước này nằm ở việc xác nhận luồng CI/CD có khả năng tự động xử lý và cập nhật trọn vẹn mô hình khi có dữ liệu mới.
