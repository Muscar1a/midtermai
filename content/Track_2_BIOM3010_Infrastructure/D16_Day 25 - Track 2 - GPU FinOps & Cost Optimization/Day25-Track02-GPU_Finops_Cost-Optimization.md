# Day25 Track02 GPU Finops Cost Optimization

**File gốc:** `Track_2_BIOM3010_Infrastructure\D16_Day 25 - Track 2 - GPU FinOps & Cost Optimization\Day25-Track02-GPU_Finops_Cost-Optimization.md`

---

### GPU FinOps &

Cost Optimization
AICB-P2T2 · Ngày 25 · Chương 5: Vận Hành
Giảng viên
VinUniversity · Phase 2 · Track2 ·Tuần5

---

### “Bạn đang tiêu bao nhiêu cho GPU mỗi ngày?

Và bao nhiêu % là lãng phí?Case study:
4x A100 idle overnight (12h) = $144 wast-
ed/day = $52,560/year. Hôm nay chúng ta
học cách cắt giảm 40–60% chi phí GPU —
và close Chương 5 với Quiz + Milestone 2.”
Giữcâu hỏi này trong đầu khihọc bài hôm nay

---

### Nội Dung Bài Học

1. GPUCloud Cost Anatomy
2. Spot& Preemptible Instances
3. Right-Sizing& Utilization
4. InferenceCost Optimization
5. CostAllocation & Chargeback
6. SustainableAI: Carbon & Energy
7. TổngKết Chương 5
8. Quiz + Milestone 2
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 1 / 20

---

### Mục Tiêu

Saubuổi học này,bạnsẽ:
1. Phântích chi phí GPU cloud vàphát hiện lãng phí
2. Ápdụng spot/preemptible instances với checkpoint strategy
3. Tốiưu training cost bằng mixed precision(AMP) và autoscaling
4. Tốiưu inference cost bằng batching, caching,model cascading
5. Thiếtkế cost allocation & FinOps reviewprocess cho team
Cost anatomy→ Spot strategy→ Right-sizing + Autoscaling→ Mixed precision→
Inferenceoptimization →FinOpsgovernance →Quiz+ Milestone 2
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 2 / 20

---

### Deliverable Cuối Ngày

Labnotebook hoàn thành (8 Parts) +cost charts + Quiz + Milestone2 demo
■ Parts 1–5: Mockcluster monitoring, spot savings, autoscaler,waste report
■ Parts 6–7: Visualizationcharts + full FinOps workflowend-to-end
■ Part 8: RealGPU training FP32 vs AMP —time/memory/cost comparison
■ Quiz Chương 5: 15câu hỏi CI/CD, LLMOps, Monitoring, Governance,FinOps
■ Milestone 2: Demooperations platform end-to-end
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 3 / 20

---

### Chi Phí GPU Cloud: Breakdown

Compute (GPU hours) 60% Storage 15% Net 10% Other 15%
■ Hidden costs: datatransfer egress ($0.09/GB AWS),NATgateway ($0.045/GB), Secrets Manager
($0.40/secret/mo)
■ Wasted spend: idleGPUs (training done, instance running),over-provisioned instances, unused reserved capacity
■ FinOps maturity: Inform →Optimize →Operate— hầu hết AI teamschỉ ở Inform level
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 4 / 20

---

### Wasted Spend Patterns — Tại Sao Phí Tiền?

1. GPUidle overnight — training xong nhưng
instancevẫn chạy
2. Over-provisioned: dùng H100 choinference
8Bmodel (A10G đủ rồi)
3. Unusedreserved capacity mua 1 năm nhưng
workloadthay đổi
4. Developmentenvironments chạy 24/7 (chỉ
cầngiờ hành chính)
■ 4xA100 idle 12h/day
■ Chiphí: 4 ×$3.0/hr ×12h= $144/ngày
■ $52,560/năm—chỉ riêng idle time!
■ Fix: auto-shutdown schedule→tiếtkiệm
ngay
Rule of thumb: GPUutilization <30%= cần right-size
ngay
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 5 / 20

---

### Spot Instances: Tiết Kiệm 60–70%

■ Discount60–70% so với on-demand
■ 2-mintermination notice
■ SpotFleet: request từnhiều AZ/instance
types
■ Giảminterruption rate từ 15%→3%
■ Discounttới 80%
■ Terminatesau24h (Preemptible) hoặc
flexible(Spot)
■ Phùhợp jobs <20h
■ Tựđộng reschedule trên GKE
Mixed fleet strategy: 20%on-demand (baseline) + 80% spot(burst) — balance cost vs reliabilitySkyPilot: Multi-cloud
spotabstractionlayer—tựđộngtìmcheapestspotacrossAWS/GCP/Azure. sky launch task.yaml chọnprovidertốiưu.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 6 / 20

---

### Checkpoint Strategy cho Spot Training

Epoch 1
Train
Checkpoint
to S3
Epoch 2
Train
Spot
Terminated!
New Spot
Instance
Load
Checkpoint
Epoch 2
Resume
■ Savemodel state mỗi epoch (hoặc mỗi30 phút cho long epochs)
■ Checkpointlưu lên S3/GCS — resume từbất kỳ instance nào
■ PyTorchLightning ModelCheckpoint callbacktự động hoá
■ Bestpractice: test resumeflow trướckhichạy long training
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 7 / 20

---

### GPU Utilization: Mục Tiêu >70%

Workload Typical Util Target Action nếu thấp
Inference(single model) 20–40% >60% Multi-modelserving, MIG
Inference(batched) 50–70% >75% Tunebatch size, queue
Fine-tuning 60–80% >80% Largerbatch, gradient accum
Pre-training 80–95% >90% Optimisedata loading
Monitoring: nvidia-smi dmon -d 5 hoặcDCGM Exporter →Prometheus →Grafanadashboard
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 8 / 20

---

### Multi-Model Serving & MIG

■ vLLMserve Llama-3-8B + Mistral-7B trên
A10G(24GB)
■ Dynamicloading: swap modelstheo request
■ Utilizationtăng từ 25%→65%
■ A10080GB →7isolatedinstances(3g.20gb)
■ 7models chạy song song, isolation đảmbảo
■ K8s: nvidia.com/gpu.shared: true
■ Perfectcho inference farm
Vertical Pod Autoscaler (VPA): recommendCPU/memory limits dựa trên actualusage — avoid over-provisioning
resources.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 9 / 20

---

### GPU Autoscaling: KEDA-like Approach

■ Scale-up: GPUutilization >80% →add
node
■ Scale-down: utilization <20% →remove
idlenode
■ Cooldown: 60sgiữa các scaling events
■ Bounds: min1 node, max 8 nodes
■ KEDA:event-driven autoscaling cho K8s
■ Prefercheapest GPU type khi scale-up (T4
trướcA100)
■ Scale-downidle nodes trước — tiết kiệm
ngay
■ Spotinstances cho burst capacity
■ Monitor: nếuidle >50%GPUs →scaledown
Key metric: Costper useful GPU-hour,khôngphải tổng
spend
Lab demo: Configureautoscaler policy →submitworkloads →observescale-up/down decisions →measurecost
impact.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 10 / 20

---

### 5 Kỹ Thuật Giảm Chi Phí Inference

Request Batching
10 req/batch → 8x throughput
Redis Caching
30–40% hit rate for chatbot
Model Cascading
8B handles 80%, escalate 20%
Quantization
AWQ 4-bit: cost/M tokens ↓34%
Spot for Inference
Stateless + LB failover
Combined effect: Batching+ Caching + Cascading +
Quantization →70–85%cost reduction so với naive deployment.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 11/ 20

---

### Request Batching & Caching Chi Tiết

■ Group10 requests mỗi batch
■ Throughputtăng 8x, cost/request giảm 85%
■ vLLMcontinuous batching tự động
■ Tune max_num_seqs theolatency SLO
■ Rediscache cho identical prompts
■ Hitrate 30–40% điển hình cho chatbot
■ Semanticcache: embed prompt→similarity
search
■ TTL:1h cho dynamic, 24h cho staticprompts
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 12 / 20

---

### Model Cascading & Quantization ROI

■ Smallmodel (Llama-3-8B) xử lý 80%
requests
■ Escalate20% complex queries→large
model
■ Router: classify difficultybằngfast classifier
■ Costreduction: 60–70%
Mode Tok/s $/M tok
FP16(A10G) 1200 $0.83
AWQ4-bit 1800 $0.55
Savings 34%
Spot cho inference: statelessinference servers phù hợp spot instancesnếu có load balancer automatic failover.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 13 / 20

---

### Mixed Precision Training: Giảm Cost & Tăng Speed

■ torch.cuda.amp.autocast: forward pass
FP16
■ GradScaler: tránh underflow khibackward
■ Memorygiảm ∼30–40% →batchsize lớn
hơn
■ Trainingtime giảm 20–50% tuỳ model
■ Accuracygần như không đổi (<0.5%drop)
Metric FP32 AMP
Time/epoch 1.0x 0.6–0.8x
Peakmemory 100% 60–70%
Cost/run $1.00 $0.60–0.80
Savings 20–40%
BF16 trên A100/H100: khôngcầnGradScaler,stablehơn
FP16
Lab demo: TrainResNet-18 CIFAR-10FP32 vsAMP trên Kaggle GPU→sosánh time, memory,power,cost thực tế.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 14 / 20

---

### Tagging & Cost Allocation Strategy

■ team=ml-platform
■ project=rag-service
■ env=production
■ cost-center=engineering
■ Enforcetags bằng SCP/OPApolicies
■ ResourceQuota pernamespace
■ Teambudget: max 4 GPUs,100GB storage
■ Kubecost: per-podcost breakdown
■ “RAGservice $45/day,Embedding $12/day”
AWS Cost Explorer + Budgets: alertkhi spending vượt $1,000/day→immediateinvestigation. Monthly FinOps
review: sharedashboard →ownershipdrives optimization.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 15 / 20

---

### Carbon & Energy Optimization

■ Chạytraining khi grid sạch nhất
■ us-west-2 (Oregonhydro) 10x greener than
us-east-1
■ CodeCarbonlibrary: track CO2 per
experiment
■ Scheduleheavy jobs off-peakhours
■ Distilledmodels: Phi-3-mini vsGPT-4—
100xsmaller,70% accuracy
■ Chain-of-thoughttăng cost 3–5x — chỉ dùng
khicần
■ GreenAI metric: CO2 gramsper 1000
inferences
■ Track& report cùng performance metrics
Takeaway: SustainableAI không chỉ “nice-to-have” —region selection + model selection =cost savings + carbon
reductioncùng lúc.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 16 / 20

---

### Live Demo: GPU FinOps Lab (Docker Compose + Kaggle GPU)

1. Part 1–2: Clustermonitoring+workloadsubmission →đoutilization,pháthiện
idleGPUs
2. Part 3: Spotbidding + preemption simulation→savingsreport (60–70%
discount)
3. Part 4: Autoscalerpolicy tuning →observescale-up/down decisions
4. Part 5: Costtracker (OpenCost-like): wastereport + optimization
recommendations
5. Part 6–7: Visualization+ end-to-end FinOps workflow
6. Part 8: RealGPU training FP32 vs AMP trênKaggle→đotime, memory,cost
thựctế
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 17 / 20

---

### Lab #25

Mục tiêu: GPUFinOps Optimization Workshop
Deliverable: Labnotebook8parts(Dockermockcluster+KagglerealGPU)+cost
charts+ Milestone 2 demo
Thời gian: 2.5h
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 18 / 20

---

### Recap Chương 5: Vận Hành

N21
CI/CD for AI
N22
LLMOps
N23
Monitoring
N24
Governance
N25
FinOps
Chương 5: Operations Layer Complete
■ Key insight: operationscost thường = infrastructure costsau 6 tháng production
■ FinOps quick wins: scheduleidle shutdown + quantize models+ implement caching = 40–60% reduction
■ Invest early: CI/CD+ monitoring + governance +FinOps — trả nợ sớm, khôngphải trả lãi
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 19 / 20

---

### Tổng kết — Key Takeaways

Những ý chính cần nhớ trướckhi sang bài tiếp theo
GPU cost anatomy: Compute 60% + hidden costs — audit waste trước khi optimize. Au-
toscalergiúp scale-down idle nodes tựđộng.
2 Spot instances tiết kiệm 60–70% — checkpoint mỗi 30 phút. Mixed Precision (AMP) giảm
thêm20–40% training cost.
Inference optimization: batching + caching + cascading + quantization = 70–85% cost reduc-
tionso với naive deployment.
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 19 / 20

---

### Tiếp theo & Bài tập

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
Giảngviên (VinUni) AICB· Ngày 25 Tuần5 20 / 20

---

### Hỏi & Đáp

Câu hỏi nào về GPU FinOps, spot instances,
inference optimization, hay cost allocation?

---

### Cảm ơn!

AICB-P2T2 · Ngày 25
GPU FinOps & Cost Optimization
lms.vinuni.edu.vn · Slide & template trên LMS