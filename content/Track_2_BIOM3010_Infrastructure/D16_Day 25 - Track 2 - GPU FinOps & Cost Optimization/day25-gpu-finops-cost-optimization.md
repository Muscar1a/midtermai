# day25 gpu finops cost optimization

**File gốc:** `Track_2_BIOM3010_Infrastructure\D16_Day 25 - Track 2 - GPU FinOps & Cost Optimization\day25-gpu-finops-cost-optimization.md`

---

### GPU FinOps &

Cost Optimization
AICB-P2T2 · Ngày 25 · Chương 5: Vận Hành
Giảngviên
VinUniversity · Phase 2 · Track2· Tuần5

---

### ngày? Và bao nhiêu % là lãng phí?

Case study (giá 2026): 4×H100 idle
12h/đêm @ neocloud $2.50/hr = $120/ngày
= $43,800/năm; cùng node trên hyper-
scaler ($7.44/hr) = $357/ngày =$130k/năm.
Hôm nay: cắt 40–95% chi phí GPU bằng
unit economics ($/1M-token), purchasing
strategy, MFU/MBU, và FinOps governance —
rồi close Chương 5 với Quiz + Milestone 2.”Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### NộiDung Bài Học

1. GPUCloud Cost Anatomy
2. BứcTranhGPU & Giá 2026
3. Neocloudsvs Hyperscalers
4. Purchasing& Commitment Strategy
5. UtilizationEfficiency: MFU/MBU/Roofline
6. Right-Sizing,Fractional GPU & Autoscaling
7. InferenceCost Levers
8. DisaggregatedServing & KV-cache
9. FinOpsFramework, FOCUS & Unit Economics
10. CostObservability & Allocation
11. Power& Sustainability Economics
12. Demo& Lab 25
13. TổngKết Chương 5 +Quiz+ Milestone 2
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 1 / 45

---

### MụcTiêu

Saubuổi học này,bạnsẽ:
1. Re-baselinechi phí GPU theo giá 2026(Blackwell/H200/MI300X) và đo bằng
$/1M-token,không phải $/GPU-hr
2. Chọnpurchasing strategy đúng (spot / on-demand/ Capacity Block / reserved) bằng
break-evenutilization
3. PhânbiệtGPU-Util%(đánhlừa)với MFU/MBU/goodput —thướcđohiệuquảchi
phíthật
4. Ápdiscount stack (batch−50% ×caching −90% ≈95%),disaggregation, fractional
GPU
5. ThiếtkếFinOpsgovernance: FOCUS,uniteconomicsKPI,showback →chargeback
Cost anatomy → Giá 2026 → Neocloud → Purchasing → MFU/MBU → Fractional
GPU → Inference levers → Disaggregation → FinOps/FOCUS → Observability →
Power →Quiz+ Milestone 2
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 2 / 45

---

### DeliverableCuối Ngày

Cost optimization plan + projected savings ($/1M-token before/after) + Quiz + Mile-
stone2 platform demo
■ Costbaseline report: GPUutilization (MFU/MBU), idle time, wasted spendhiện tại
■ Optimizationplan: purchasing +right-sizing + batching/caching — projected savings
cósố liệu
■ QuizChương 5: 15câu CI/CD, LLMOps, Monitoring, Governance, FinOps
■ Milestone2: Demooperations platform end-to-end
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 3 / 45

---

### ChiPhí GPU Cloud: Breakdown 2026

Compute(GPU hours) 50% Power15% Storage12% Net8% Other15%
■ Power= line-item tăng nhanh nhất:H100node ∼1,400W/GPU all-in; power∼10–20%TCO nhưng ∼30–40%
opex(xem§11)
■ Hiddencosts: egress$0.09/GB (AWS),NATgateway$0.045/GB, Secrets Manager $0.40/secret/tháng, inter-AZ
traffic
■ Đơnvị đo đúng không phải$/GPU-hrmàlà $/1M-token(inference)/ $/job(training)— xem §2 & §5
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 4 / 45

---

### LãngPhí & FinOps Maturity

1. GPUidle qua đêm — trainingxong, instance
vẫnchạy
2. Over-provisioned: H100 cho inference8B
(A10G/L4đủ)
3. Unusedreserved capacity mua 1 năm,
workloadđổi
4. Devenvironments chạy 24/7 (chỉ cầngiờ hành
chính)
5. Caođiểm GPU-Util% nhưng MFU thấp— trả
tiềncho FLOPS không dùng (§5)
■ Vòngđời Inform →Optimize →Operate
■ Hầuhết AI teams mới ởInform—audit
trướckhioptimize
■ Frameworkđầy đủ (Scopes “Cloud+”,
FOCUS,maturity,KPI) ở §9
Ruleof thumb: GPUutilization <30%(hay MFU thấp)
=cần right-size ngay.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 5 / 45

---

### CúSụp Giá H100 — vàBẫy “Năm Nào Cũng Rẻ Hơn”

■ Đỉnh ∼$8/GPU-hr(2023) → ∼$2/hrneocloud
(cuối2025): giảm 64–75%
■ 2026đảochiều: hợp đồng 1-nămbật lại+40%
($1.70→$2.35/hr,10/2025 →3/2026)
■ On-demandHopper “sold out”; hyperscaler
on-demandlên ∼$7.44/hr
■ H100SXM ∼$50ktrọnđời 5 năm
■ Chothuê <$1.65/hr →lỗ
■ >$2.85/hr →thắngcả thị trường chứng
khoán
Re-baseline mọi TCO về giá 2026 (số A100/A10G 2023thổi phồng chi phí 3–4×).
Thịtrường đangsiếtlại →khóareserved sớm, đừng đặt cược “chờrẻ hơn”.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 6 / 45

---

### $/GPU-hrLà “VanityMetric” —Ngân Sách Theo $/1M-token

Chip/ config $/GPU-hr $/1M-token Bàihọc
H100(cùng chip, đa cloud) $1.49–$6.98 — 4–5×chênh →providerarbitrage
GB300NVL72 vs Hopper caohơn 35×rẻhơn/token 50×throughput/MW
B300vs B200 (Llama-70B FP4) +23% −26%($0.055vs $0.074) mới= rẻ hơn/token
MI300X(decode mem-bound) $1.85–2.5 — −55%$/GB-VRAM vsH100
Quytắc: chuẩnhóa về$/1M-token(inference)hoặc $/job(training). $/hr caokhôngnghĩađắt hơn/token — GB300
đắt/giờnhưng rẻ nhất/token.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 7 / 45

---

### ThựcĐơn Silicon 2026: Chọn Chip Theo Workload

Vendor/ chip $/chip-hr(neocloud) Mạnhnhất cho Lock-in
NVIDIAH100 / H200 $1.5–7/ mainstream ∼$2.5 sànHopper / inference 141GB thấp(portable)
NVIDIAB200 / B300 $4–6/ $3.29 spot biêngiới rẻ nhất/token thấp
AMDMI300X / MI355X $1.85–2.5/ 288GB 70Bsingle-GPU, $/GB-VRAM trung(ROCm)
AWSTrainium2/3 ∼30–60%rẻ hơn traininggiá-perf cao(AWS)
GoogleTPU v6e/v7 ∼$4.2–4.5 batchJAX captive cao(GCP)
Quyếtđịnh: NVIDIA= portable + spot arbitrageđa-cloud; AMD = đòn bẩy đàmphán + $/GB-VRAM; Trainium/TPU= rẻ
30–60%/đơnvị nhưngcaptivemộtcloud. Đòi$/1M-token benchmark trên workload củabạn trước khi cam kết
customsilicon (vendortok/$ claims dùng FP4 +model chọn lọc).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 8 / 45

---

### Neocloudvs Hyperscaler 2026: Khoảng Cách Giá, Làm Mới

■ Hyperscaler ∼$7.44/GPU-hrvsneocloud
∼$2.5/hr= ∼3×/67% rẻ hơn
■ Đuôirẻ: AWS$6.88 vs RunPod∼$2.39/
Lambda ∼$2.49vs spot floor $1.03 =tới∼85%
rẻhơn
Lưu ý: Frontier đảo ngược: B200
neocloud ∼$5.09/GPU-hr,+24%Q1
2026,volatility11.4%(vs0.5%H100
hyperscaler) — thị trường mỏng,
tăng,biến động.
Cậpnhật quy tắc:“40–70%rẻ hơn” (A100-era)→naylà ∼3×mainstream,3–6 ×siliconmới. Mộtchính sách mua
khônghợp mọi thế hệ.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 9 / 45

---

### StackNeocloud: Từ$/GPU-giờĐến$/1M-token(vàGiáCủaDiscount)

■ Bare-metal/reserved($/GPU-hr)
■ Per-secondserverless scale-to-zero(Modal
H100 ∼$3.95/active-hr)
■ Per-tokenAPI (Together$0.03–$4.50/1M;
Llama3.3 70B $1.04/$1.04)
■ Chọntheo duty cycle: spiky→scale-to-zero;
ổnđịnh →reserved;util thấp →muatoken,
khôngmua GPU
Lưuý: Cáigiá(governance): SLA
99.99% vẫn =∼52 phút/năm down-
time;managedservicesmỏng;rủiro
đối tác thật (một neocloud∼$8.7B
nợ, ∼$7.5Bđáohạn2026). FinOps
phảiđịnhgiá exit/migration+ khả
năng thanh toán của nhà cung
cấp.
Vìsao rẻ: nănglượng rẻ +nợGPU-backed (CoreWeave$8.5B @ ∼5.9%)= arbitrage chi phí vốn.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 10 / 45

---

### Buyvs Rent vs Reserve —Khi Nguồn Cung GPU Đã NớiLỏng

■ Buy: ∼$25k–30k/H100(PCIe); break-eventhô ∼8,300GPU-hr; all-in(điện/làmmát/khấuhao/ops) ∼16–18+tháng
ở ∼100%utilization
■ Renton-demand: rẻnhất trừ khi utilization caobền vững; AWScắt EC2 GPUon-demand tới44–45%(hiệulực
1/6/2025)
■ ...nhưng1/2026 AWStăng CapacityBlocks ∼15%(p5e.48xlarge$34.61 →$39.80/hr)— scarcitypremium cho
capacityđảm bảo
■ Reserve(neocloud blocks): conđường giữa — giá dướion-demand, không capex; tốt cho workloadổn định 12
tháng+
Cúcắton-demand( −45%)vàcútăngCapacityBlock(+15%)cáchnhau ∼7tháng— giálàtínhiệucung-cầuthời
gianthực,không phải xu hướng mộtchiều.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 11/ 45

---

### ThangCam Kết2026: Spot / On-Demand/ CapacityBlock /Reserved

Tầng Discount Camkết Dùngkhi
Spot/ Preemptible −40–70%(GCP tới −80%) không,thu hồi jobchịu gián đoạn + checkpoint
On-Demand/ Serverless 0%(base) không tảispiky,util <5–6h/ngày
CapacityBlock (AWS) vừa 1–182ngày,đặt ≤8tuần burstđảm bảo, giá cố định
DWSFlex-start (GCP) −53% ≤7ngày batch/trainingngắn
Reserved/ CUD 1–3yr ∼45–55%(GPU) 1–3năm workloadổn định, util cao
break-even utilization≈ 1 − discount%. Discount 45%→ cần ∼55% util (∼13.2h/ngày) để reserved có lời. Re-
servedchạy 70% utilvẫnphí ∼30%—gắn quyết định mua vàoutilđođược.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 12 / 45

---

### SpotInstances: Interruption GiờTheo Từng Chip

■ AWSSpot: −40–70%,notice ∼2phút
■ GCPSpot/Preemptible: tới −80%,notice ∼30
giây
■ SpotFleet: request đaAZ/instance type để
giảmgián đoạn
■ H100: <5%
■ A100: 15–20%
■ V100/ RTXPRO 6000: >20%
■ ⇒chipmới = spotantoàn hơn
Mixedfleet: 20%on-demand (baseline) + 80% spot(burst) — cân bằng cost vsreliability.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 13 / 45

---

### CheckpointStrategy cho Spot Training

Epoch1
Train
Checkpoint
toS3
Epoch2
Train
Spot
Terminated!
NewSpot
Instance
Load
Checkpoint
Epoch2
Resume
■ Savestate mỗi epoch (hoặc mỗi30 phút cho long epochs); lưuS3/GCS→resumebất kỳ instance nào
■ PyTorchLightning ModelCheckpoint /async checkpointing tự động hoá
■ Bestpractice: test resumeflow trướckhichạy long training
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 14 / 45

---

### DiscountLadder & Multi-cloud Spot Arbitrage

■ ManagedSpot: ∼3×(GPUtrain) đến6.5×
(CPUbatch)rẻhơn—auto-recoverpreemption
+route GPU rẻ nhất
■ SkyServe: serve∼50%rẻhơn cross-cloud
■ sky launch task.yaml chọnprovider tối ưu
■ AWSH100 3yr: ∼45%(headline72% là
thờiCPU)
■ AzureND H100 v5 3yr:∼55%
■ Neocloudblocks: tới 60%
■ GCP:acceleratorbị loạikhỏiflexible
CUD
Lưuý: BẫyFinOps: đừngáp%CUDtoàn-cloudchoGPU—modeltheoSKUthực
trướckhi cam kết.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 15 / 45

---

### BlackwellKhan Hiếm: KhóaCapacity Sớm

■ B200/GB200bán hết tới giữa 2026,backlog
∼3.6triệu chip
■ AWSCapacityBlocks +∼20%(1/7/2026): B300
$11.70→$14.04,B200 $10.30→$12.36/acc-hr
■ ReservedBlackwell đangđắtlên,không rẻ đi
■ Blackwell(khan): đảmbảo sớmbằng
commitment/ Capacity Block
■ H100/A100(đãnới lỏng, xem §2): giữlinh
hoạtspot/ on-demand
■ GiáGPU mang tínhchukỳ —theo
cung-cầuthực, đừng đặt cược mộtchiều
Một chính sách muakhông hợp mọi thế hệ: khan→ commit; dư→ spot. Gắn mọi
camkết vàobreak-evenutilization (§4).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 16 / 45

---

### GPU-Util%Nói Dối: nvidia-smi100% ̸=HiệuQuả Chi Phí

Lưuý: nvidia-smi“GPU-Util” =%thời
gian có ≥1 kernel chạy. KHÔNG đo
dung lượng tính toán —1 thread trên
1SM đã báo 100%.
■ Trainingbáo 100% GPU-Util nhưngMFUthực chỉ
∼20–30%
■ ⇒trảfull GPU-hour cho< 1
2 FLOPSthực dùng
■ MFUchotraining (compute-bound)
■ MBUchodecode (memory-bound)
■ Lấytừ DCGM:SM activity,TensorCore %,
HBMBW — không phải GPU-Util
FinOps: đừngcapacity-plan / mua thêm GPUdựa trên GPU-Util — đó làđồng hồ “đang bận”, không phải“đang hiệu
quả”.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 17 / 45

---

### MFU,MBU & Roofline: Hai Thước Đo Chi Phí Thật

■ =achieved FLOPs / peak FLOPs(từ PaLM)
■ Tốt35–45%,xuất sắc50%+;Llama-3 405B
∼38–43%
■ 70Bconfig mặc định<30% →sửaTP 8→1+
selectivecheckpointing = ∼2×MFU= ∼2×rẻ
hơn
■ MBU= achieved BW / peakBW;target
∼60%(H100-80GBbatch-1)
■ RidgeH100 ∼295FLOP/byte (BF16);
decodebatch-1 chỉ1–2FLOP/byte →
memory-bound
■ Decodescale theo HBM BW:H1003.35
→H2004.8 →B2008TB/s
Hệquả mua sắm:chodecode, trả tiền cho$/TB-bandwidth,không phải $/TFLOP (H200∼1.9×inferencevs H100 nhờ
BW).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 18 / 45

---

### Goodput& Cost-per-Token: Thước Đo FinOps Cuối Cùng

■ Goodput= req/sđạtSLO (TTFT+ TPOT)
■ 10req/s nhưng 3 đạt SLO→goodput= 3 (7
reqđã trả tiền nhưng vôdụng)
■ Tốiưu goodput = cắt fleetGPU (disaggregation
tới ∼2×req/GPU— chi tiết §8)
■ BlackwellDeepSeek-R1: ∼6,000
tok/s/GPU,$0.12/1M= ∼35×rẻhơn
Hopper
■ Đònbẩy lớn nhất làutilization: GPU ở
10%tải →10×cost/token
■ ThuêGPU thô chỉ là 25–35%TCO
self-host
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 19 / 45

---

### Right-Sizing: GPU-Util Là KhởiĐầu, Không Phải Đích

Workload GPU-Util(time-active) Target Action nếu thấp
Inference(single model) 20–40% >60% Multi-modelserving, MIG, fractioning
Inference(batched) 50–70% >75% Tunebatch size, continuous batching
Fine-tuning 60–80% >80% Largerbatch, gradient accum
Pre-training 80–95% >90% Optimisedata loading
Lưu ý: Cột trên làGPU-Util (time-active)— chỉ báo “đang bận”. Hiệu quả chi phí thật đo bằngMFU/MBU (§5).
Nguồnutil: nvidia-smi dmon /DCGM Exporter →Prometheus →Grafana.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 20 / 45

---

### ServerlessGPU & Scale-to-Zero: TrảTiềnTheo Giây

■ ModalH100 ∼$3.95/hr,B200 ∼$6.25/hr
■ RunPodFlex H100 PRO∼$4.18/hr
■ Baseten(per-minute) H100 ∼$6.50/hr
■ Flex(scale-to-zero) vs Active (24/7,−20–32%
khiuptime cao)
Lưu ý: Cold start = paid dead
time: 20–60s init+model-load tính
fullrate. “ModelParkingTax”: keep-
warm +26–66 W/GPU (>98% idle
power).
Break-even ∼30%duty cycle: tảispiky →serverless;
tảiổn định cao→reserved(serverless premium
∼1.3–3×bare-metal).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 21 / 45

---

### FractionalGPU: Một Card, Nhiều Tenant— Cắt $/User

■ MIG(A100/H100): phân vùng phầncứng,
memoryriêng, isolation cao
■ Time-slicing/ MPS:mật độ cao hơn, isolation
thấphơn
■ Đánhđổi: costdensity ↔isolation
■ Hiệuquả compute(MFU)doanh nghiệp
thườngchỉ ∼5%,dù GPU-Util time-active
60–70%
■ Run:ai: 0.5GPU = 77% throughput, 86%
usercapacity;co-location →tới3×
users
■ KAIScheduler open-source(Apache 2.0,
4/2025)— bỏ phí license
■ DRAGA K8s1.34(8/2025): cấp“GPU ≥X
GB”native
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 22 / 45

---

### KubernetesCost-Autoscaling Stack 2026: Zero Idle GPU

■ Karpenter—consolidation + bin-packing: gom pod vào ít node nhất,xóa node rỗng; spot GPU→giảm ∼40–60%
vsCluster Autoscaler
■ KEDA—scale-to-zero: GPU inferencepods →0replica khi util = 0qua cooldown
■ Kueue—gang scheduling + quota theoteam + cohort borrowing→chốngGPU hoarding
■ DRA+ KAI Scheduler—nền fractioning native + fair-share/over-quota
Tấn côngcả 2 lớp lãng phí: idletrong-card (fractioning §trên) + idlenguyên-node (autoscaling/spot). Hai lớp này
nhânnhau.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 23 / 45

---

### LLMflation: Giá TokenRơi∼10×/năm— Nhưng Không Đều

■ Cùngnăng lực: inferencegiảm ∼10×/năm
■ GPT-3-level$60/1M(2021) →$0.06/1M(Llama
3.23B, 2024) =1,000×trong3 năm
■ “NgangGPT-4”ra mắt $30/$60/1M(3/2023)
nay <$1/1M
Lưu ý: KHÔNG đều (Epoch AI):
biên độ 9×–900×/năm, trung vị
∼50× → tách dự báo theo tầng
nănglực.
Frontier6/2026: GPT-5.5$5/$30 · Opus 4.8 $5/$25 ·
Gemini3.1 Pro $2/$12 (gấp đôikhi prompt>200K).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 24 / 45

---

### CúSốc DeepSeek: KiếnTrúcLÀ Đòn Bẩy ChiPhí

Lưu ý: Headline $5.576M chỉ là
GPU pre-training (∼2,048 H800 × 55
ngày). KHÔNGgồmCapEx/R&D.Thực
tế (SemiAnalysis): ∼$1.6B CapEx +
$944M opex, ∼50k GPU → chênh
∼100×.
Bàihọc: luônđòi fullTCO,không tin headline.
■ MLA(Multi-headLatent Attention):
−93.3%KV-cache
■ MoE:chỉ kích hoạt 37B/671B
params/token
■ FP8: $/token rẻ
■ API:R1 $0.55/$2.19 vs o1 $15/$60=
∼27×rẻhơn
■ Thịtrường: Nvidia mất∼$600Bvốn hóa 1
ngày(27/1/2025)
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 25 / 45

---

### Reasoning= Bom Chi Phí MỗiTruyVấn

Lưu ý: Test-time compute nổ chi phí
mỗi truy vấn: “thuế reasoning” +5–10×
token bị tính; thinking-token ẩn tính giá
output (∼10k token suy luận cho 1 câu
500token = ×21).
■ 21.8%cặpmodel đảogiá (tới28 ×): rẻ
trêngiấy,đắt khi chạy
■ Tintốt: reasoninggiảm nhanh —
o4-mini-low ∼$0.05/task
■ ⇒benchmark$/taskthực,chiến lược
“chờ& định giá lại”
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 26 / 45

---

### DiscountStack: Batch −50% ×Caching −90% ≈95%Off

Lever Giảm Điềukiện
BatchAPI −50% SLA24h; latency-tolerant (eval, enrich, nightly)
Promptcaching (read) −90%(0.1×) Anthropic;write 1.25×/2×,cần ≥2reads
OpenAI/ Gemini cache −50đến −90% Geminicó phílưu $1–4.5/1M-tok-giờ
Batch ×Caching(stack) ≈95%off multipliernhân được (Anthropic xác nhận)
Lưuý: Caveat: cachingchỉlờitrênngưỡngread;phílưuGeminicóthểlậtngượcphéptính →cachecóchủđích ,
đừngcache mù.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 27 / 45

---

### TầngSmall-Model: Batching ·Caching · Cascading · Quantization

■ Requestbatching: throughput ∼8×,cost/req ↓
(vLLMcontinuous batching)
■ Redis/semanticcache: hit 30–40%(chatbot)
■ Modelcascading: 8B xửlý 80%, escalate 20%
—FrugalGPT tới98%,RouteLLM 85%+
■ Quantization: FP8/FP4 (Blackwell) làfrontier;
AWQ4-bit là tầng INT4
Mode Tok/s $/M tok
FP16(A10G) 1200 $0.83
AWQ4-bit 1800 $0.55
Savings 34%
Stacked: batching+caching+cascading+quant →
70–85%vs naive.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 28 / 45

---

### Disaggregation: Tách Prefill/Decode =7–30×QPSCùng GPU

■ Ýtưởng: prefillcompute-bound, decode memory-bound — chạychung lãng phí cả hai→táchpool, right-size mỗi
pooltheo SKU rẻ nhất
■ DistServe(OSDI’24): 7.4×request/SLO chặt 12.6×(>90%req đạt SLO)
■ Mooncake(Kimi,FAST’25): +75%req thực,tận dụng CPU/DRAM/SSD nhàn rỗilàm KV tier
■ NVIDIADynamo: tới30×request(DeepSeek-R1671B, GB200 NVL72);>2×Llama-70BHopper;
Qwen3-235B-FP81.86 ×
Lưuý: KV-transfertăngtheođộdàicontext →thắngở QPScao+contextdàichiasẻ ;deploymentnhỏcóthể lỗ.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 29 / 45

---

### KV-cacheLà Tiền: cache-hit% Thay “Số Token”Làm KPI

■ Anthropicread 0.1×(∼90%off);OpenAI
50→90%
■ DeepSeekhit ∼1/10(V4 Flash ∼98%)
■ Chênh50–100×giữahit/miss
■ KVoffload/tieringcho vLLM: −69%chi
phíprefill @80%hit (4×H100,prompt
128K),throughput tới 15×
■ GA1/2026;dùng bởi GKE Inference,
CoreWeave,Cohere
Cấutrúcpromptđểprefixtĩnh(systemprompt,RAGcontext,few-shot)ổnđịnhcache;
theodõi cache-hit% như chỉ số chiphí chính.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 30 / 45

---

### Mỗi“Tối Ưu” Có Vùng ChiPhí Riêng — Đo $/token Trước/Sau

■ Speculativedecoding: −48%$/1M token khilatency-boundNHƯNG+19%khi throughput bão hòa;ROI gắn
acceptancerate (≥60%;EAGLE-3 ∼2.5×trênvLLM)
■ Chunkedprefill: bảo vệ ITL(inter-token latency) nhưng chunk 512 thêmtới+25%overhead;chunk ∼2048gần
như0
■ NVIDIANIM:chi phítheoGPU (AIEnterprise ∼$4,500/GPU/năm ≈$1/GPU-hr)+ tiền thuê GPU→chỉlời trên
ngưỡngbreak-even utilization
Lưu ý:Quy tắc: mỗi lever cóchế độ tảiphù hợp —đo unit economics trước và sau, đừng giả định “nhanh hơn
=rẻ hơn”.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 31 / 45

---

### FinOps2025: Từ CloudSang “Cloud+”, AI Là Một Scope

■ ThêmScopes: Public Cloud ·SaaS · Data
Center· AI·Licensing · Private Cloud
■ Vòngđời Inform →Optimize →Operategiữ
nguyên
■ Cloud+thực tế: SaaS90%, licensing 64%,
privatecloud 57%
■ 98%độiquản chi phí AI (so31% hai năm
trước)
■ “AIvalue management” = kỹ năngcần #1
■ Lãngphí cloud lên29%(Flexera2026) —
lầntăngđầusau5năm,doAIlàmforecast
khó
Whynow: đólà lý do GPU FinOpstồn tại — AI biến chiphí thành biến số khó dựbáo nhất.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 32 / 45

---

### AIUnit Economics: $/Token· $/Inference · $/Outcome

KPI Côngthức (FinOps for AI) Ví dụ
Cost/ Token Total$ / Tokens $2,500/ 1M =$0.0025
Cost/ Inference Total$ / #inferences $5,000/ 100k =$0.05
Utilization Actual/ Provisioned 800/1000= 80%
ROI (Benefit−Cost)/Cost 150%
Tokenyield rate %token tạo hành động KD nốitoken →value
“Một token rẻ đi, nhưngtổng token thì không.” Chi GenAI doanh nghiệp$1.7B (2023) → $37B (2025). Tối ưu
token yield(token tạo ra giá trị KD), đừng chỉ tối thiểu hóa token; structured-output cắt 30–60% token (model
routing/cascadingở §7).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 33 / 45

---

### FOCUS:Chuẩn Hóa Dữ Liệu ChiPhí Đa Nhà Cung Cấp

■ FOCUS(FinOpsOpen Cost & Usage Spec)— chuẩn mở normalize billing đacloud về một schema
■ 1.2(5/2025)thêm cột virtual-currency/token ·1.3(12/2025)Contract Commitment + Split CostAllocation ·1.4
(6/2026)47 cột
■ Nativeexport từ >12nhà cung cấp: AWS,Azure,GCP,Oracle, Alibaba, Nebius, Databricks…
■ Nghềhóa: chứng chỉFinOpsCertified for AI(ramắt 6/2025, thi từ 3/2026);maturity Crawl/Walk/Run
Lưuý: AItokenconsumption đầyđủ (modelidentity,input/outputtokens)scopedcho FOCUS1.5—CHƯAratified
(6/2026).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 34 / 45

---

### HaiTầng Quan Sát Chi PhíAI: $/GPU-giờ + $/1M-token

■ DCGM →Prometheus →Kubecost3.0 /
OpenCost
■ Chiphí GPU theo pod/namespace, phânbổ
theomứcsử dụng
■ TáchWorkloadIdle vs Infrastructure Idle
■ LiteLLMproxy(100+ provider) +
Langfuse/Helicone
■ $/request,$/1M-token theo API-key/team
■ Budgetcứng chặn request vượt hạnmức
Hợpnhất: FOCUSđưa token vào cùng schemavới cloud (AI-token đầy đủ đợiFOCUS 1.5).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 35 / 45

---

### Tagging,Quota & Per-Service CostBreakdown

■ team=ml-platform · project=rag-service
■ env=production · cost-center=engineering
■ Enforcetags bằng SCP/OPApolicies
■ K8slabel →DCGM →Prometheus
■ K8s ResourceQuota pernamespace
■ Teambudget: max 4 GPUs,100GB
storage
■ Kubecost3.0 (GA9/2025): ClickHouse,
bỏPrometheus dep,GPU-aware(DCGM),
free <$1M
■ “RAG$45/day,Embedding $12/day”
Lưu ý:Cloud-native gotcha: split GPU/accelerator cost của EKS ởCUR 2.0 SCAD
/Data Exports,KHÔNG ở Cost Explorer UI (EKS-only,9/2025).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 36 / 45

---

### TừShowback Đến Chargeback TrênCụm GPU Dùng Chung

1. Visibility
tag+ DCGM cost
2. Showback
4–6tuần, vá tag
3. Chargeback
khitag >80%
4. $/Outcome
routewin-rate ∼70%
■ Môhình phân bổ: per-namespace / per-tenant / per-token /per-experiment
■ Chạyshowback4–6 tuầnválỗ hổng tag→chuyểnchargebackkhi tag-coverage >80%
■ UtilGPU AI TB chỉ∼60–70%,kiểm toán xấu nhất∼5%— lõi bài toán lãngphí
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 37 / 45

---

### BứcTranhCông Cụ &Cảnh Báo: TokenBill Chỉ Là 1/9

■ IBMmua Apptio + Kubecost→
Cloudability/Turbonomic/Kubecost
■ FOCUS-based: Vantage,CloudZero,Finout,
nOps
■ LLMtoken: LiteLLM, Langfuse(Helicone →
maintenancemode 2026)
Lưu ý: (FinOps X 2026) token bill
chỉ là1 trong 9 khoảnchi. 8 khoản
còn lại — retrieval, orchestration,
KV-cache infra, eval, governance,
nhân lực, lãng phí/lỗi, tích hợp —
thườngkhôngđượcđo.
Thangtrưởng thành: visibility →cost/token →costper verified outcome.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 38 / 45

---

### Power,Không Phải GPU, LàNút Thắt

■ Giácapacity lưới PJM tăng∼11×trong2 năm ($28.92→$329.17/MW-day);data center chịu63%khoảntăng
■ Mộtsite AI cần100–750MW;đấu nối lưới mới mất24–36tháng (4–7năm ở hub nghẽn) —capacity,không phải
chip,giới hạn tăng trưởng
■ $/MWlà đơn vị mới: ∼$10M/MW(vỏ) →$20–30M/MW(AI-optimized) → ∼$30–44M/MWall-in
■ Power ∼10–20%TCO nhưng ∼30–40%opex
Đặt training/batch latency-tolerant nơi điện rẻvà sạch: ∼5–6¢ (E. Washington) vs∼15¢/kWh (CA); carbon∼6 vs
∼660gCO 2/kWh(Norway vs Poland,>100×).
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 39 / 45

---

### Tokens-per-Watt: NăngLượng/TruyVấn Là Unit Economics

■ 0.24Wh,0.03 gCO2e,0.26 mL nước
■ Giảm33×energy/44 ×carbontrong12tháng
■ Chỉ58%nănglượnglàTPU;bạntrảcho ∼42%
non-accelerator
Lưu ý: Reasoning tốn 74–86×
năng lượng/truy vấn: o3∼39.2 Wh,
DeepSeek-R1 ∼33.6 Wh vs GPT-
4.1nano ∼0.45Wh.
Đònbẩy: modelrouting + reasoning-token budget cắt
nănglượng (và $) 1–2 bậc;theo dõiWh/querynhư
$/1M-token.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 40 / 45

---

### Carbon& Nước Như Đòn BẩyChi Phí Có Quản Trị

■ PUEchạmsàn: Google fleet1.09vsindustry ∼1.56( →cơsở trung bình đốt thêm∼56%điện cho overhead trên
mỗiwatt IT)
■ Chuẩnhóa: SCIlà ISO/IEC 21031:2024(carbon/inference)— đối ứng carbon của$/1M-token cho dashboard &
ESG
■ Carbon-awarescheduling jobhoãn được: cắtcarbon ∼20–50%vàthườngtrúng điện off-peakrẻ hơn
■ Hyperscalerhedge điện: PPAhạt nhân 20 năm (MSFT835 MW Three Mile Island∼2028;Google 500 MW SMR;
Amazon320 MW +>5GW)
SustainableAIkhôngchỉ“nice-to-have”: region+modelselection+scheduling= costsavings+carbonreduction
cùnglúc.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 41 / 45

---

### LiveDemo: GPU CostAudit & Optimization 2026

1. Bước1 — Audit hiệu quả:nvidia-smi dmon +DCGM →đoMFU/MBU
(khôngchỉ GPU-Util%), phát hiện idle
2. Bước2 — Discount stack:bậtrequest batching + prompt caching,
benchmark$/1M-tokentrước/sau
3. Bước3 — Allocation:càiKubecost 3.0 + LiteLLM, tag resources,xem
per-service$/GPU-hr và$/token;export FOCUS
4. Bước4 — Purchasing:tínhbreak-evenutilization;viết checkpoint/resume
chotraining job trên spot
5. Bước5 — Report:costoptimization report: baselinevs optimized, projected
savings($/1M-token + $/job)
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 42 / 45

---

### Lab#25

Mụctiêu: GPUFinOps Optimization Workshop
Deliverable: Cost optimization report (baseline vs optimized, $/1M-token) + Mile-
stone2 platform demo
Thờigian: 2.5h
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 43 / 45

---

### RecapChương 5: VậnHành

N21
CI/CDfor AI
N22
LLMOps
N23
Monitoring
N24
Governance
N25
FinOps
Chương5: Operations LayerComplete
■ Re-baseline: giáGPU 2026 (Blackwell/H200/MI300X) — số2023 thổi phồng chi phí 3–4×;đo bằng$/1M-token,
không$/GPU-hr
■ Đođúng: GPU-Util%đánh lừa — dùng MFU/MBU/goodput;đòn bẩy lớn nhất là utilization(10% tải→10×
cost/token)
■ FinOpsquick wins: batch( −50%) ×caching( −90%) ≈95%off ;fractioning + autoscaling diệt idle;power là nút
thắtmới
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 44 / 45

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
1 Đobằng $/1M-token,không$/GPU-hr: GB300đắt/giờnhưngrẻnhất/token(35 ×vsHopper).
Re-baselinemọi TCO về giá 2026.
2 GPU-Util% nói dối — 100% có thể che MFU 20%. ĐoMFU (training) / MBU (decode) /
goodput;purchasing gắn vào break-even utilization≈1−discount%.
Discount stackbatch × caching ≈95% off; disaggregation 7–30× QPS; fractional GPU +
autoscalingdiệt idle; FinOps governance quaFOCUS + $/outcome.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 44 / 45

---

### Tiếptheo & Bài tập

Chương 6: Tổng Hợp — MCP/A2A
Infrastructure
“Agentgọiagent—MCPserverhost-
ing, A2A protocol, agentic routing cho
multi-agentsystems”
■ Hoànthành Lab 25 + Milestone
2demo
■ Đọctrước: Anthropic MCP
specification
■ Đọctrước: Google A2Aprotocol
overview
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 45 / 45

---

### Hỏi& Đáp

Câu hỏi nào về $/1M-token, MFU/MBU, purchas-
ing strategy, discount stack, hay FinOps governance?

---

### Cảmơn!

AICB-P2T2 · Ngày 25
GPU FinOps & Cost Optimization
lms.vinuni.edu.vn · Slide & template trên LMS