# Day23 Disaster recovery High availability

**File gốc:** `Track_2_BIOM3010_Infrastructure\D14_Day 23 - Track 2 - Disaster recovery & High availability\Day23-Disaster-recovery-High-availability.md`

---

### Disaster Recovery & High Avail-

ability cho AI Infrastructure
AICB-P2T2 · Ngày 23 · Chương 5: Vận Hành
Giảng viên
VinUniversity · Phase 2 · Track 2 · T uần 5

---

### “us-east-1 vừa sập. Model serving end-

point của bạn nằm ở đó. Bạn có bao
nhiêu phút trước khi khách hàng nhận
ra? Và quan trọng hơn — bạn có biết
câu trả lời trước khi nó xảy ra không?”
Giữ câu hỏi này trong đầu khi học bài hôm nay

---

### Nội Dung Bài Học

1. RTO/RPO cho AI Systems
2. Multi-Region Deployment Patterns
3. Stateful Component Recovery
4. Failover Automation & Runbooks
5. Chi Phí Standby Capacity
6. DR Drills & Game Days

---

### Mục Tiêu

Sau buổi học này, bạn sẽ:
1. Định nghĩa RTO/RPO cho từng thành phần trong AI stack (serving, vector DB,
feature store)
2. Thiết kế kiến trúc multi-region active-passive / active-active cho inference
3. Lập kế hoạch backup & replication cho state (model weights, vector DB,
metadata)
4. Viết runbook failover và chạy được một DR drill có đo RTO thực tế
Agenda hôm nay
RTO/RPO fundamentals→ Multi-region patterns→ State recovery→ Failover
automation → Cost tradeoffs → Game day demo

---

### Deliverable Cuối Ngày

Artifact cần nộp
DR runbook + failover demo có đo RTO thực tế + cost tradeoff analysis
■ RTO/RPO table cho 4 component chính của hệ thống bạn đang xây (serving,
vector DB, feature store, metadata store)
■ Terraform snippet: cross-region S3 replication cho model weights
■ Runbook 1 trang: các bước failover khi region chính down
■ Kết quả DR drill: RTO đo được vs RTO mục tiêu, và gap nếu có

---

### 01

RTO/RPO cho AI Systems
Vì sao AI infrastructure ”sập” khác với web app thường, và
cách đo mức độ chịu đựng downtime

---

### AI Infra Khác Web App Thường Ở Đâu?

Thành phần Web app thường AI system
State cần khôi phục DB rows (KB–GB) Model weights (GB–TB)
Thời gian ”khởi động
lại”
Vài giây Cold-start GPU pool: 5–15 phút
Dữ liệu ”tươi” quan
trọng
Transaction log Vector DB embeddings + fea-
ture store freshness
Chi phí standby Rẻ (CPU instance) Đắt (GPU instance đứng chờ)
Hệ quả: DR cho
AI không thể copy-paste playbook từ web app — phải tính riêng chi phí GPU standby và thời gian nạp lại state.

---

### Case Study: Khi Một Region Sập Thật

AWS us-east-1, Dec 2021
Sự cố network internal khiến us-east-1 gián đoạn ∼7 giờ. Nhiều công ty AI/SaaS chạy inference tại đây bị
downtime toàn phần vì không có region phụ hoặc có nhưng chưa test failover bao giờ.
Điều đã xảy ra:
■ Dashboard/monitoring cũng host ở cùng region
→ không biết mình đang sập
■ DNS failover có sẵn nhưng chưa test → cutover
thất bại lần đầu
Bài học cho AI infra:
■ Observability stack phải sống ở region khác với
workload nó theo dõi
■ ”Có DR plan” và ”DR plan hoạt động” là hai việc
khác nhau

---

### RTO vs RPO — Hai Câu Hỏi Sống Còn

RTO — Recovery Time Objective
”Tối đa bao lâu được downtime?”
■ Đo từ lúc outage bắt đầu → lúc service
phục vụ lại
■ Model serving: RTO thường 5–15 phút
(SLA khách hàng)
■ Training pipeline: RTO có thể vài giờ
(không real-time)
RPO — Recovery Point Objective
”Tối đa mất bao nhiêu dữ liệu?”
■ Đo khoảng cách giữa backup gần nhất
và lúc sập
■ Vector DB: RPO vài phút (embeddings
mới liên tục ingest)
■ Model registry: RPO có thể vài giờ
(model ít thay đổi)
Nguyên tắc: RTO/RPO càng thấp → chi phí infra càng cao. Không có ”một RTO cho tất cả” — mỗi component
cần số riêng.

---

### RTO/RPO Theo Từng Component

Component RTO RPO Lý do
Inference API (serv-
ing)
5 phút N/A (stateless) User-facing, SLA nghiêm ngặt
Vector DB 15 phút 5 phút Cần fresh embeddings, nhưng
replica có thể lag nhẹ
Feature store 30 phút 15 phút Batch features chấp nhận lag lớn
hơn
Model registry /
weights
1 giờ 24 giờ Model ít thay đổi giữa các lần
train
Số liệu minh hoạ — điều chỉnh theo SLA thực tế của hệ thống bạn

---

### Availability Tiers — “9” Nào Là Đủ?

SLA Downtime/năm Y êu cầu kiến trúc Chi phí
99% 3.65 ngày Single region, backup định kỳ Thấp
99.9% 8.76 giờ Multi-AZ, automated failover Trung bình
99.95% 4.38 giờ Multi-AZ + warm standby re-
gion
Cao
99.99% 52.6 phút Active-active multi-region Rất cao
Lưu ý: Đừng thiết kế cho 99.99% nếu SLA thực tế chỉ cần 99.9% — chi phí GPU standby tăng phi tuyến
theo mỗi “9” thêm.

---

### 02

Multi-Region Deployment Pat-
terns
Active-passive, active-active, và cách route traffic khi
một region không còn phản hồi

---

### Active-Passive vs Active-Active

Active-Passive
Region A
ACTIVE — 100%
Region B
ST ANDBY — 0%
replicate
Active-Active
Region C
50% traffic
Region D
50% traffic
sync
Rẻ hơn, đơn giản hơn
Failover mất vài
phút (DNS cutover)
RTO ≈ 0, nhưng
đắt gấp đôi
Cần conflict res-
olution cho state

---

### Latency-Based Routing & DNS Failover

Route53 / Cloud DNS Health Check
■ Health check endpoint mỗi 10–30s
■ 3 lần fail liên tiếp → mark unhealthy
■ DNS record TTL thấp (60s) để cutover
nhanh
■ Latency-based routing: route đến region
gần nhất, tự động loại region unhealthy
Giới hạn thực tế của DNS failover
■ DNS cache ở client/ISP không tôn trọng
TTL → vài user vẫn miss
■ Không phải ”tức thì” — cộng thêm
30–90s vào RTO
■ Kết hợp với global load balancer
(Cloudflare/Anycast) để cutover nhanh
hơn DNS thuần

---

### Cross-Region Model Weight Replication

# terraform: S3 Cross-Region Replication
resource "aws_s3_bucket_replication_configuration" "
weights" {
bucket = aws_s3_bucket.model_weights_primary.id
role = aws_iam_role.replication.arn
rule {
id = "replicate-to-standby-region"
status = "Enabled"
destination {
bucket = aws_s3_bucket.model_weights_dr.arn
storage_class = "STANDARD"
}
filter {
prefix = "checkpoints/"
}
}
}
Lưu ý khi replicate weights
■ CRR có lag — không dùng cho RPO <
1 phút
■ Checksum verify sau replicate
(model corrupt = silent failure)
■ Versioning bucket bắt buộc —
rollback về checkpoint cũ
Chi phí
■ CRR: phí transfer + storage nhân đôi
■ Model 70B fp16 ≈ 140GB → tính phí
egress kỹ trước khi bật CRR toàn bộ

---

### Active-Passive vs Active-Active — Khi Nào Dùng Gì?

Active-Passive
■ RTO mục tiêu > 5 phút chấp nhận được
■ Budget GPU hạn chế — không đủ chạy 2
pool full-time
■ State ít conflict (không cần
multi-master)
■ Phù hợp: hầu hết AI startup / team vừa
Active-Active
■ RTO mục tiêu ≈ 0 (fintech, healthcare
real-time)
■ Budget cho phép double GPU capacity
■ Có chiến lược conflict resolution cho
vector DB / feature store
■ Phù hợp: enterprise SLA 99.99%+

---

### Kiến Trúc Tham Chiếu — Ghép T oàn Bộ Section Lại

Global DNS / LB
health check 15s
Region A — ACTIVE
Serving + Vector DB
Region B — ST ANDBY
Warm GPU pool
S3 CRR: model weights
+ vector DB snapshot
Postgres PITR
(registry + metadata)
failover
Điểm mấu chốt: DNS/LB,
compute, và state (S3 + Postgres) là 3 lớp cần replicate riêng — thiếu 1 lớp là failover
không hoàn chỉnh.

---

### 03

Stateful Component Recovery
Backup và replication cho phần khó nhất: vector DB,
model registry, và metadata store

---

### Vector DB Backup & Multi-Region Replica

Pinecone / Weaviate multi-region
■ Pinecone: replica pod ở region khác,
sync gần real-time
■ Weaviate: backup snapshot → S3/GCS,
restore vào cluster mới
■ Self-hosted (Qdrant/Milvus): snapshot
định kỳ + WAL shipping
Điều dễ bị bỏ quên
■ Re-index từ raw documents luôn là
fallback — nhưng chậm (giờ, không phải
phút)
■ Backup index nhưng quên backup
embedding model version → index không
tương thích khi restore
■ Test restore định kỳ — backup chưa test
= không có backup

---

### Model Registry & Checkpoint Recovery

MLflow Model
Registry
S3 Primary
Region
S3 DR Region
CRR replica
async replicate
DR Region: registry metadata (Postgres) restore từ snapshot → point vào S3 DR bucket
Nguyên tắc
Registry metadata (Postgres/RDS) và model artifacts (S3) phải backupđồng
bộ — registry point đến path không tồn tại là lỗi phổ biến nhất khi restore.

---

### PITR cho Metadata Store

Point-in-Time Recovery
■ RDS/Aurora: continuous backup +
transaction log → restore về bất kỳ giây
nào trong 35 ngày
■ Dùng cho: feature registry, experiment
tracking DB, model registry metadata
■ Restore tạo instance mới — không
overwrite instance đang chạy
Khi nào PITR không đủ
■ Cross-region: PITR restore trong cùng
region — cần thêm cross-region read
replica cho DR thật
■ Logical corruption (bad migration) vẫn
replicate sang DR nếu dùng sync replica
— cần backup point-in-time riêng, không
chỉ replica

---

### Backup Schedule Cheatsheet

Component Phương pháp T ần suất Retention
Model weights S3 CRR + versioning Continuous 90 ngày
Vector DB Snapshot → S3 Mỗi 6 giờ 30 ngày
Metadata (Postgres) PITR + cross-region
replica
Continuous 35 ngày
Feature store (offline) Table snapshot Hàng ngày 14 ngày
Điều chỉnh tần suất theo RPO mục tiêu của từng component

---

### 04

Failover Automation & Run-
books
T ừ health-check đến DNS cutover đến GPU pool ấm sẵn ở
region phụ

---

### Kiến Trúc Health-Check-Based Failover

Health Checker
mỗi 15s
DNS / Global LB Region chính
serving
Region phụ
warm standby
PagerDuty / Slack: alert on-call + trigger runbook
cutover
Nguyên tắc: failover đầu tiên nên là bán tự động (alert + 1-click
confirm), không full-auto — tránh flapping gây failover 2 chiều liên tục.

---

### GPU Pool Warm-Up Ở Region Phụ

Vấn đề: Cold GPU = RTO chết
■ Provision GPU instance mới: 3–8 phút
■ Pull image + load model weights: thêm
2–10 phút
■ Tổng cold-start có thể vượt RTO mục
tiêu
Giải pháp: Warm standby
■ Karpenter/NAP (đã học Ngày 16) giữ sẵn
1–2 node GPU “ấm” ở region phụ, scale
0→N khi failover
■ Model weights pre-loaded vào node
cache, không load từ S3 lúc failover
■ Trade-off: chi phí node ấm vs RTO — xem
Phần 5

---

### Runbook: Region Chính Down

□✓ Xác nhận outage: health check + status page của cloud provider
□✓ Thông báo incident channel + bắt đầu tính RTO clock
□✓ Scale GPU pool ở region phụ từ warm → full capacity
□✓ Verify model weights + vector DB replica ở region phụ đã sync gần nhất
□✓ DNS/LB cutover traffic sang region phụ
□✓ Verify golden signals (latency, error rate) ở region phụ ổn định
□ Post-incident: đo RTO thực tế, so với mục tiêu, viết postmortem

---

### Anti-Patterns Thường Gặp

Lưu ý: Runbook chỉ tồn tại trên
giấy — chưa test lần nào → 90%
khả năng sai bước khi thực thi lúc
hoảng loạn.
Lưu ý: Failover tự động không có
circuit breaker— 2 region flap qua
lại liên tục khi health check không
ổn định (flapping).
Lưu ý: Backup DR region cùng
account/cùng credentials — một
sự cố IAM/billing đánh sập cả 2 re-
gion cùng lúc.
Lưu ý: Không ai biết RTO thực tế
— chỉ có số ”lý thuyết” trên slide,
chưa đo lần nào bằng drill thật.

---

### Sau Failover: Blameless Postmortem

T emplate postmortem
1. Timeline: outage bắt đầu, phát hiện,
alert, cutover, resolved
2. RTO đo được vs mục tiêu — gap ở bước
nào?
3. Root cause (5 whys) — không đổ lỗi cá
nhân
4. Action items có owner + deadline cụ thể
Blameless — vì sao quan trọng
■ Đổ lỗi cá nhân → lần sau người ta giấu lỗi
thay vì báo cáo sớm
■ Câu hỏi đúng: ”hệ thống/process nào
cho phép lỗi này xảy ra?”
■ Postmortem tốt → input trực tiếp để sửa
runbook

---

### 05

Chi Phí Standby Capacity
RTO thấp luôn đắt — câu hỏi là đắt bao nhiêu, và có đáng
không

---

### Warm vs Cold vs Pilot-Light

Chiến lược Mô tả RTO Chi phí GPU
Cold Provision từ đầu khi
failover
15–30 phút 1x (chỉ region chính)
Pilot-light Giữ metadata/config,
scale GPU khi cần
8–15 phút 1.1x
Warm standby 1–2 node GPU ấm sẵn,
scale nhanh
3–8 phút 1.3–1.5x
Hot (active-
active)
Full capacity 2 region
song song
≈ 0 2x
Cost tương đối — Cold = 1x baseline

---

### Decision Framework: Chọn Chiến Lược Nào?

RTO mục tiêu < 5 phút?
Có → Warm/Hot standby Không → tiếp câu hỏi
Chấp nhận 15–30 phút downtime?
Có → Cold / Pilot-light Không → tính lại budget, hoặc giảm SLA
Câu hỏi thật: không phải ”RTO tốt nhất có thể” mà
là ”RTO nào đủ, với chi phí công ty chấp nhận được”.

---

### 06

DR Drills & Game Days
Cách duy nhất để biết RTO thật: mô phỏng outage và
bấm giờ

---

### Game Day — T ại Sao Phải Diễn T ập?

Sự thật khó chịu
■ Runbook chưa test = giả định, không phải
sự thật
■ RTO ”trên giấy” thường thấp hơn RTO
thật 2–3 lần
■ Backup chưa test restore = có thể không
dùng được lúc cần
Game day làm gì
■ Chủ động tạo outage có kiểm soát
(không phải chờ outage thật)
■ Đo RTO/RPO thực tế, so với mục tiêu
■ Tìm gap trong runbook trước khi khách
hàng tìm ra

---

### Game Day — Quy Trình 4 Bước

Lên kế hoạch
Thông
báo team
Kích hoạt
outage giả
Đo & rút
kinh nghiệm

---

### Chaos Engineering Nhẹ Cho AI Infra

Fault injection mức thấp rủi ro
■ Kill 1 pod GPU serving — verify HPA/K8s
tự phục hồi
■ Inject latency vào vector DB call — verify
timeout + fallback hoạt động
■ Block network đến region chính (chaos
mesh) — verify DNS failover
Nguyên tắc an toàn
■ Luôn chạy ở staging trước, production
sau khi tự tin
■ Có ”kill switch” dừng thí nghiệm ngay lập
tức
■ Thông báo trước cho on-call — game
day không phải bất ngờ với người trực

---

### DR Maturity Model — Bạn Đang Ở Đâu?

Level T ên Đặc điểm
0 Không có plan Backup thủ công, không ai biết RTO thật
1 Runbook viết sẵn Có tài liệu nhưng chưa test lần nào
2 Failover tự động một phần Health check + DNS cutover, cần người bấm con-
firm
3 Test định kỳ (game day) Chạy DR drill hàng quý, đo RTO thực tế, cập nhật
runbook
4 Chaos-engineered Fault injection thường xuyên, failover không cần
con người can thiệp
Mục tiêu thực
tế cho hầu hết team: Level 2–3 — Level 4 chỉ đáng đầu tư khi SLA yêu cầu 99.99%+.

---

### Live Demo: Region Failover Drill

LIVE DEMO
1. Setup: 2 region (staging), model serving + vector DB replica ở cả hai
2. Trigger: chặn traffic đến region chính (simulate outage) — bắt đầu bấm
giờ RTO
3. Quan sát: health check phát hiện fail → alert → DNS cutover
4. Verify: request mới được serve từ region phụ, latency/error rate ổn định
5. Kết quả: so RTO đo được với RTO mục tiêu (5 phút) — ghi lại gap

---

### Lab #23

LAB #23
Mục tiêu: Thiết kế RTO/RPO table cho hệ thống đang xây, viết Terraform
cross-region replication cho model weights, và chạy 1 DR drill đo RTO thực
tế
Deliverable: RTO/RPO table + Terraform snippet + runbook 1 trang + kết quả
drill (RTO đo được vs mục tiêu)
Thời gian: 2h

---

### T ổng kết — Key T akeaways

Những ý chính cần nhớ trước khi sang bài tiếp theo
1 RTO/RPO phải định nghĩa riêng cho từng component — không có ”một số cho tất cả”,
và AI infra có state nặng hơn (model weights, vector DB) so với web app thường.
2 Active-passive đủ cho hầu hết trường hợp; active-active chỉ đáng chi phí gấp đôi khi
RTO mục tiêu thật sự cần ≈ 0.
3 Runbook chưa test qua game day = giả định, không phải kế hoạch — RTO thật chỉ biết
được sau khi đo, không phải sau khi viết.

---

### Tiếp theo & Bài tập

Bài tiếp theo
Ngày 24: Data Governance &
Security
“RBAC, encryption, PII han-
dling, compliance (GDPR/ISO
27001/NĐ13) — bảo vệ data nhạy
cảm trong AI pipeline”
Bài tập về nhà
■ Hoàn thành Lab 23: DR
Runbook + Failover Drill
■ Review lại RTO/RPO table đã
làm — mang vào buổi sau để
đối chiếu với governance
requirements
■ Đọc trước: Vietnam Decree
13/2023 về bảo vệ dữ liệu cá
nhân

---

### Hỏi & Đáp

Câu hỏi nào về RTO/RPO, multi-
region, state recovery, hay DR drills?

---

### Cảm ơn!

AICB-P2T2 · Ngày 23
Disaster Recovery & High Availability cho AI Infrastructure
lms.vinuni.edu.vn · Slide & template trên LMS