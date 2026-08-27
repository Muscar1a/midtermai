# 1 day20 model serving inference optimization

**File gốc:** `Track_2_BIOM3010_Infrastructure\D09_Day 20 - Track 2 - Model Serving Inference Optimization\1-day20-model-serving-inference-optimization.md`

---

### Model Serving & In-

ference Optimization
AICB-P2T2 · Ngày 20 · Chương 4: Hạ Tầng
Giảngviên
VinUniversity · Phase 2 · Track2· Tuần4

---

### “Model accuracy 95% nhưng latency 3 giây.

User đợi không nổi, churn tăng 40%. Model
tốt nhưng serve chậm = product thất bại.”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### NộiDung Bài Học

1. BốiCảnh & Vocabulary(latency,
pre-LLMera)
2. Quantization:
FP16/FP8/AWQ/GGUF/NVFP4
3. KVCache & Attention Optimization
4. Single-NodeServing Stack 2026 (8
engines)
5. Distributed& Multi-TenantServing
6. ServingRegimes 2026 (VLM, embed,
cache,route, power,security)
7. Auto-scaling& Operations
8. Edge& Hardware Landscape
9. ProductionSLA (Goodput@SLO)
10. Lab20 + Milestone 1
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 1 / 40

---

### Mụctiêu bài học

Saubuổi học này,bạnsẽ:
1. Phânbiệt Throughputvs Goodput@SLO,đọc TTFT/TPOT trên dashboard
production
2. Ápdụng quantization (FP16/FP8/AWQ4-bit/NVFP4/GGUF) đểgiảm memory & tăng
throughput
3. HiểuKV Cache, PagedAttention, RadixAttention, FlashAttention 3/4,MHA→MLA
4. Sosánh 8 serving engines (vLLM, SGLang,NVIDIA Dynamo, llm-d, LMDeploy,
TensorRT-LLM,Ollama, llama.cpp)
5. Chọnđúng parallelism strategy (TP/PP/EP/DP) cho workloaddistributed
6. Hoànthành Lab 20 (llama.cpp tuning bonus)và submit Milestone 1
Foundations → Quantization → KV/Attention → Single-Node → Distributed →
Regimes2026 →Auto-scale →Edge →SLA →Lab20
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 2 / 40

---

### DeliverableCuối Ngày

Optimizedinference stack + Lab 20 report+ Milestone 1 demo
■ Benchmarkreport: GGUF quantsweep (Q2_K→Q8_0)+ continuous batching,
P50/P95/P99
■ Loadtest: 10 &50 concurrent users (locust) trênllama-server
■ Lab20 report (benchmarks/results.md vớiP50/P95/P99 + bonus tuning notes)
■ Milestone1: AI infrastructureplatform demo (N16–N19)
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 3 / 40

---

### LatencyTaxonomy: TTFT· TPOT · Goodput

■ TTFT(TimeToFirstToken) : từ request đến
tokenđầu tiên — phụ thuộcprefill compute +
queuewait
■ TPOT(TimePerOutput Token) =ITL:
khoảngcách đều giữa mỗi outputtoken
■ E2ELatency =TTFT+TPOT ×(N–1);SLO
thườngở P95/P99
■ Throughput: tokens/s toàn hệthống ở
saturation,không có SLO constraint
■ Goodput: req/sthỏamãn TTFT+TPOTSLO
—metricproduction quan trọng nhất
■ QueueDepth: requests đang chờprefill —
chỉbáo saturation
Ví dụ thực tế— H100 · Llama-3-70B · batch32:TTFT ≈450ms ·TPOT ≈25ms ·
Throughput1,800tok/s · Goodput@SLO(TTFT<1s,TPOT <50ms) ≈1,200tok/s
Lưu ý:Throughput@saturation ̸= Goodput@SLO. Báo cáo chỉ throughput mà bỏ qua
SLOconstraint là misleading — luônreport goodput cho production.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 4 / 40

---

### Pre-LLMEra: Serving Infrastructure2017–2022

■ TFServing (Google2017): SavedModel,
gRPC,versioned endpoints, static batch
■ TritonInference Server(NVIDIA2019):
multi-framework,dynamicbatchingpermodel
■ ONNXRuntime (2019): cross-framework
export,CPU/GPU/NPU optimized kernels
■ TorchServe(Facebook2020): MAR
archives,REST API, multi-model serving
■ BentoML(2020): Python-native packaging,
pluggableruntimes
■ Memoryfragmentation: KV cache cần
contiguousblock cố định — 60–80%VRAM
waste
■ Staticbatching: chờ đủ batch,thêm
200–500ms latency
■ Notoken streaming: client chờ toànbộ
responsetrước khi nhận
■ Nocontinuous batching: 1 long request
blocktoàn queue
■ Fixed-lengthI/O:không xử lý được
variable-lengthgeneration
The Shift (Jun 2023)— vLLM PagedAttention: KV cache qua virtual memory
pages(non-contiguous,nofragmentation)+ continuousbatching (requestsvào/ra
liêntục) →LLMserving era. 24×throughputvs naive HF Transformers.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 5 / 40

---

### Quantization: Precision vs Performance

VRAMUsage (Llama-3-8B)
FP32 31.6GB
FP16 15.8GB
FP8 7.9GB — Hopper/Blackwell native
INT8 7.9GB
AWQ4-bit 4.5GB
FP8: <1% drop, 2× mem-
ory vs FP16 (Hopper+ native)
AWQ 4-bit: ∼1pt MMLU drop
trên 8B+, lớn hơn với<7B
NVFP4 (Blackwell): 3.5× vs
FP16, 1.8× vs FP8,<1% lossChọn quantization:
Production Hopper: FP8 / AWQ 4-bit
Production Blackwell: NVFP4 (default)
Max quality: BF16 / FP16
Edge/laptop: GGUF Q4_K_M (i-quants
nếu <Q4)
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 6 / 40

---

### Quantizationfor Memory: GGUF· NF4 · GPTQ · AWQ

Format BPW 8BVRAM 70B VRAM Quality
FP16 16 15.8GB 140GB Baseline
FP8 8 7.9GB 70GB <1%drop
AWQ4-bit 4.5 4.5GB 40GB ∼1ptMMLU
GPTQ4-bit 4.0 4.0GB 35GB ∼1ptMMLU
GGUFQ4_K_M 4.5 4.8GB 43GB ∼1ptMMLU
GGUFQ2_K 2.6 2.7GB 24GB Noticeable
NF4(bnb) 4.0 4.0GB 36GB ∼1ptMMLU
■ GPTQ:inverse Hessian layer-by-layer (128
calib.samples). Chậm quantize,nhanh
inference.
■ AWQ:tìm salient weights (high activation
magnitude),scale trước INT4 rounding. Acc>
GPTQcùng bits.
■ NF4(bitsandbytes): 4-bit NormalFloat, optimal
chonormal-distributed weights. Doublequant:
constantsFP32 →FP8.
■ GGUFk-quant: Q4_K_M = mixedQ4/Q6 per
tensor(attn vs FFN).k=betterquant, m=medium
size.
■ GPUcloud (Hopper): FP8—best
quality/perf
■ GPUVRAM tight: AWQ4-bit —tốt nhất ở
4-bit
■ CPU-onlyinference: GGUFQ4_K_M —
recommended
■ Cựckỳ constrained: GGUFQ2_K —last
resort
■ Fine-tunetrên 1 GPU:NF4+ QLoRA
Lưu ý: <7B models mất quality nhanh hơn
13B+. Benchmark perplexity saukhi quantize.Giảngviên (VinUni) AICB· Ngày 20 Tuần4 7 / 40

---

### KVCache & PagedAttention

Traditional: Contiguous
Wasted!
PagedAttention: Paged
PageTable
Nowaste
■ KVcache như virtual memory pages
■ 24×vsnaive HF Transformers
■ Dynamicmemory allocation
■ Táisử dụng KV qua radixtree (prefix
sharing)
■ Lýtưởng cho RAG, multi-turn, agents
■ Engineeringchi tiết: xem§3 Prefix
Caching
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 8 / 40

---

### AttentionArchitecture: MHA →MLA& Long-Context

MHA GQA MQA MLA
KV:1× KV:4×less KV:8×less KV:10×less
Standard LLaMA-2/3 GPT-3era DeepSeek-V3
■ CompressQ/K/V xuống latent vector nhỏtrước
attention
■ DeepSeek-V3: 10×ítKV memory vs standard
MHA
■ Kernel: FlashMLA, CutlassMLA, FlashInfer
(2025)
■ Chophép context dài hơn trêncùng VRAM
■ YaRN:RoPE interpolation, không cần
retrain
■ StreamingLLM:attention sinks, ∞context
■ Jamba(AI21Labs): SSM/Transformer
hybrid,256K ctx
■ FA3+ MLA backends→kernelcho context
dài(xem §3)
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 9 / 40

---

### SpeculativeDecoding & Continuous Batching

■ Draftmodel sinh 4–8 tokens, targetverify
songsong trên cùng 1 forwardpass
■ EAGLE-3(NeurIPS’25): 3.0–6.5×,
+20–40%so EAGLE-2
■ DeepSeekMTP (Multi-TokenPrediction):
∼1.8×,acceptance 85–90%(DeepSeek
eval)
■ LookaheadDecoding: self-drafting khi
khôngcó draft model
■ Tíchhợp sẵn trong vLLM, SGLang,
TensorRT-LLM
■ Staticbatching (legacy): chờ đủ batch→
+200–500ms padding
■ Continuousbatching: requests vào/ra mỗi
step,no padding →5×latencygiảm
■ Tokenstreaming: client nhận từngtoken —
TTFTcảm giác ↓
■ vLLM(continuous batching), TensorRT-LLM
(in-flightbatching) —thuật ngữtương đương
■ SGLangpiecewiseCUDA graphcho
variable-lengthbatch
Spec-Decode CLI (SGLang) — --speculative-algorithm EAGLE3
--speculative-num-steps 5 --speculative-eagle-topk 4 . Yêu cầu draft model
checkpointhoặc model có MTP head.
Lưu ý: Spec decoding làlatency tool(memory-bound, batch 1–4). Ở batch≥24, verify-overhead có thể làm
chậmhơn( ∼0.93×)— engine tự tắt qua--speculative-disable-by-batch-size.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 10 / 40

---

### FlashAttention: IO-AwareAttention (FA1→FA4)

FlashAttn-1
(Dao2022)
FlashAttn-2
(2023)
FlashAttn-3
(2024)
FlashAttn-4
(2025)
NeurIPS’22 arXivJul ’23 Hopper Blackwell
Tiling + SRAM
O(N) mem, 3–4×
Seq parallelism
2× FA1 speed
TMA async, FP8
warp specialization
FP4 KV cache
B200 native
■ Standardattn: Q×K(N2×d)viết HBM →đọc
lạisoftmax →đọclại ×V— 3 HBM round trips
■ FA:tile Q/K/V vào SRAM,online softmax, ghi
output1lần duy nhất
■ Memory: O(N) thay vìO(N2)— context dài
khôngOOM
■ FA3: Hopper TMAasync pipeline + FP8. FA4:
BlackwellFP4 KV,SGLang auto-selects
■ torch.nn.attention.flex_attention:
BlockMaskAPI
■ Express: causal, sliding window,document
boundary,prefix+causal
■ Compilequa torch.compile →Triton
kernel,không cần CUDA custom
■ Tíchhợp: PyTorch
F.scaled_dot_product_attention,vLLM,
SGLangcustom patterns
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 11/ 40

---

### ModelCompilation: torch.compile +CUDA Graphs + TensorRT

■ Capturecomputation graph quatorch.fx;
TorchInductortạo Tritonkernels
■ Kernelfusion: nhiều element-wiseops →1
kernel,ít HBM reads hơn
■ mode="max-autotune" : tìm optimal kernel
config(compile chậm, run nhanh)
■ mode="reduce-overhead" : loại Python
overheadnhanh
■ dynamic=True : variable shapes khôngtrigger
recompile
■ Speedup: 1.1–1.5×trênLLM decode phase
■ Record: chạy 1 forwardpass, capture GPU
commandstream
■ Replay: skip Python overheadmọi lần sau
(0.5–2ms/step tiết kiệm)
■ LLMdecode = cùng ops lặpN_tokens lần→
CUDAgraph lý tưởng
■ vLLMv1: decode dùng CUDAgraph replay;
prefillchạy eager (variable shape)
■ SGLang: ”piecewise CUDA graph”cho
mixedstatic/dynamic batch sizes
■ Cộngthêm 10–20% throughput trên mọi
optimizationkhác
TensorRT Compilation— ONNX → layer fusion→ kernel selection→ FP8/INT8
calibration → .trtengine. 3–5×vsvanillaPyTorch. Compiletime: 5–30min/model.
Dùngtrong TensorRT-LLMvà NVIDIA TritonInference Server.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 12 / 40

---

### ServingStack 2026: 8Engines That Matter

Engine Ưuđiểm chính Bestfor API
vLLM PagedAttention,Auto Prefix Cache + chunkedprefill LLM production OpenAI-compat
SGLang RadixAttention,structured gen, MLA backend Multi-turn/ chat OpenAI-compat
NVIDIADynamo DisaggregatedP/D orchestrator (GA 1.0) Multi-tenantcloud OpenAI-compat
llm-d K8s-native,KV-awarerouting Productionat scale OpenAI-compat
LMDeploy TurboMindengine, hiệu suất cao Highthroughput OpenAI-compat
TensorRT-LLM NVIDIAnative, FP8/FP4 optimized NVIDIAGPU fleet Tritonbackend
Ollama 1lệnh: ollama run (wrapsllama.cpp) Localdev/testing REST
llama.cpp GGUFnative, CPU+GPU mixed offload,AppleMetal Local/ CPU / edge REST/ OpenAI-compat
Lưu ý: Production 2026: vLLM v1 hoặc SGLang. Disaggregated scale: llm-d / Dynamo.
LocalCPU/Mac: llama.cpp. Container: Ollama. NVIDIA fleet: TensorRT-LLM.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 13 / 40

---

### InferenceEngine Evolution: 2020→2025

HF
Transformers
DeepSpeed
Inference
Faster-
Transformer
vLLM
PagedAttn
SGLang
RadixAttn
vLLMv1
Disagg. era
2020 2021 2021 Jun2023 Jan2024 Jan2025
Manual batching
inference scripts
Tensor parallel,
ZeRO-Inference
Optimized
CUDA kernels
PagedAttn,
continuous batching
RadixAttention,
prefix sharing
APC default,
disaggregated P/D
2020–2022: manual/static batching, CUDA kernels — framework-level optimizations.Jun 2023:PagedAttention
→ continuous batching→ 24× throughput jump, ecosystem convergence. 2024–25: prefix sharing + disaggre-
gatedP/D →TTFTvà goodput là SLO first-class.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 14 / 40

---

### PagedAttention: vLLM v0→v1Deep Dive

LogicalKV PhysicalPages
L0
L1
L2
L3
P0
P3
P1
P5
Page
Table
Sequential Non-contig.
■ PagedAttention: KV như virtualmemory pages,24×
vsHF naive
■ Blocksize: 16 tokens/page(default). FCFS scheduler
+preemption
■ Continuousbatching: requests join/leave
mid-generation
■ Prefixcaching opt-in (--enable-prefix-caching)
■ Unifiedmemory pool: KVcache + activations trong
cùngpool
■ APCON by default: Automatic Prefix Caching,
khôngcần flag
■ Chunkedprefill default: chiaprefill thành chunks,
interleavevới decode
■ Prefix-awarescheduler. 1.7×v0throughput.
Key Commands — vllm serve
MODEL · --tensor-parallel-size N
· --gpu-memory-utilization 0.9 ·
--max-model-len 8192
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 15 / 40

---

### PrefixCaching: RadixAttention, APC,HiCache & Pricing

■ vLLMv1 APC:Automatic Prefix Caching,
ONmặc định
■ RadixAttention(SGLang): radix-tree (prefix
trie),cache hit = skip prefilltoàn bộ shared
prefix
■ LMCache: cross-instance KV sharing
(CPU/disk)
■ MooncakeKVCache: global pool trên
disaggregatedcluster
■ Tiếtkiệm prefill: −70%TTFT trên repeated
systemprompts (RAG, agents, multi-turn)
■ Anthropic: cached read−90%(Claude
Opus4.8 / Haiku 4.5)
■ DeepSeek: cache-hit∼98%off(V4 Flash
$0.14/$0.28/M)
■ OpenAI:cached input −75%(GPT-4.1/
GPT-5.x)
■ Google: cached read−90%(Gemini2.5 /
3.x)
Tier1 GPUVRAM(active,hot) →Tier2 HostRAM(spillover) →Tier3 Externalstorage(HF3FS,Mooncake,disk).
Attach/detach backend không cần restart. Long-context: vượt GPU VRAM limit. Multi-turn: reuse KV qua nhiều
turns.
Takeaway — Prefix caching = engineering optimizationvà pricing tier. Thiết kế
promptvới system prompt/context cố định ởđầu để tối đa cache-hit rate.
Lưuý: Cachemiss vẫn tính full price. Monitor cache-hit rate trongproduction dashboard.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 16 / 40

---

### AttentionBackend Selection: FA3/ FA4/ FlashInfer/ FlashMLA

■ H100/H200(Hopper,CUDA 12.3+) → fa3
■ B200(Blackwell) → trtllm_mha hoặc fa4
■ A100/A40 → flashinfer
■ DeepSeekV3/R1 MLA → flashmla
(page=64)
■ ROCm/ Ascend / CPU→ triton
(cross-platformfallback)
Override: --attention-backend
{fa3|fa4|flashinfer|trtllm_mha|flashmla|triton}
■ FA3: TMA async, FP8KV,warp
specialization— Hopper native
■ FA4: FP4 KV cache— Blackwell SM100
(2025)
■ FlashInfer: page-size>1,FP8 KV,
spec-decodetopk >1,sliding window
■ TRTLLM-MLA:DeepSeek MLA optimized,
verifiedspec-decode
■ Triton: cross-platform fallback (ROCm,
Ascend,NPU, CPU)
MLA Backends (DeepSeek V3/R1)— FlashMLA · CutlassMLA · FlashInfer-MLA
· TRTLLM-MLA —3.1× throughput vs MHA,10× less KV memory. Tự động chọn
theoGPU + model; override chỉ khibenchmark/debug.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 17 / 40

---

### StructuredGeneration: XGrammar,Tool& Reasoning Parsers

■ Formats: JSON Schema, EBNF,Regex,
Pydanticmodel
■ Grammarbackends: XGrammar(default,
fastest),Outlines, Llguidance
■ Enginesupport: SGLang --grammar-backend
xgrammar,vLLM
--guided-decoding-backend xgrammar
■ API:OpenAI-compat
response_format={json_schema}
■ Reasoningmodels: constraint ápdụng sau
<think>...</think>
■ ToolParser --tool-call-parser [model] :
15+models (DeepSeek, Llama-3.1/4, Qwen,
Mistral,Kimi-K2); streaming args
incrementally
■ ReasoningParser --reasoning-parser
[model](deepseek-r1,qwen3, kimi_k2):
trích <think> → reasoning_content +
contenttáchbiệt
■ Kếthợp: --reasoning-parser deepseek-r1
--tool-call-parser kimi_k2
Workflow — Prompt → <think>(freereasoning) →grammar-constrainedoutput →
response: reasoning_content + contentquaOpenAI-compatible API.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 18 / 40

---

### ProductionTuning: Memory,Scheduling & Observability

■ --mem-fraction-static (SGLang)/
--gpu-memory-utilization (vLLM):chừa
5–8GB baseline; quá thấp→OOM
■ --chunked-prefill-size: giảm 2048–4096
khiprefill OOM (default 8192)
■ --max-running-requests / --max-num-seqs:
capburst để tránh decode OOM
■ --schedule-conservativeness: 0.3
aggressive· 1.0 default · 1.3conservative
■ Queuedepth target: 100–2,000(saturation
>2K)
■ --enable-metrics →Prometheusendpoint
:30000/metrics
■ Keymetrics: num_running_reqs,
num_queue_reqs,TTFT/TPOT histograms,
cache-hitrate
■ Scrape →Grafanadashboard; vLLM expose
tươngtự qua prometheus_client
■ --log-requests (basic/full);crashdump:
rolling5-phút buffer
■ Replay: replay_request_dump.py để
reproducelỗi
Tuning + Debug Flow— Start conservativeness=1.0 → monitor queue depth→
Grafanaanomaly → --log-requests trace →crashdump replay →fix+ redeploy.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 19 / 40

---

### DisaggregatedPrefill/Decode Serving

Monolithic(vLLM v0)
GPUA
P+D
GPUB
P+D
prefillcontends
withdecode
Disaggregated
Prefill
Pool
Prefill
Pool
KVTransfer
(NVLink/IB)
Decode
Pool
Decode
Pool
■ NVIDIADynamo 1.0(GA2026): cross-engine
orchestrator,KV-awarerouter,NIXL
■ Mooncake(Kimi,FAST’25): 100B+tok/day,global KV
pool,RDMA zero-copy
■ llm-d: K8s-native P/D (vLLM+ Gateway API + NIXL),
scale-to-zero
■ DistServe(OSDI’24)/ Splitwise(ISCA’24): foundational
papers
Lưu ý: KV transfer overhead
∼10GB/s. Lợi ích rõ khi work-
load prefill-heavy (long context, RAG).
Khôngđáng cho short unique prompts.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 20 / 40

---

### Multi-LoRAServing

BaseModel
(7B–70B)
LoRA-1
SQL
LoRA-2
Med
LoRA-3
Code LoRA-N
1GPU Instance
■ Punica/SGMVkernels: fused
batched-adapterGEMM (vLLM, SGLang)
■ S-LoRA:paged LoRA weights, swap per
request
■ vLLM --enable-lora: Nadapters/ 1
endpoint
■ SageMakerLMI-Dist: managedmulti-LoRA
hosting
■ 12×throughputvs Nseparatesingle-model
servers
■ Overhead: +2ms/token cho adapter
application
■ SGLang: Chunked SGMV (20–80%lat↓);
LoRAoverlap loading (35% TTFT↓)
Usecase — 1basemodel+nhiềudomainadapters(SQL,ytế,code,finance)trên
1GPU — tiết kiệm VRAM vàserving cost so vớiNindependentdeployments.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 21 / 40

---

### ExpertParallelism: MoE Scaling

■ ChiaMoE expert weights qua nhiềuGPUs
(khôngreplicate)
■ Forwardpipeline: dispatch →pre-permute
→corerunner →combine
■ A2A(All-to-All) backends:
--moe-a2a-backend deepep (NVLink/IB),
mooncake,nixl
■ MoErunner: --moe-runner-backend
deep_gemm hoặccutlass
■ Constraint: hầu hết backendsyêu cầu
ep_size = tp_size
■ Two-BatchOverlap (TBO):
--enable-two-batch-overlap —xen kẽ
A2A/GEMM →+27–35%prefill
■ EPLB: --enable-eplb —load balancer giảm
GPUutilization variance
■ DeepEPmode: --deepep-mode auto /
normal/ low_latency
■ DeepSeek-V3/R1671B:prefill EP32/decode
EP144+DeepEP + EPLB (∼$0.20/1Mout)
Two-Batch Overlap (TBO)— TBO xen kẽ A2A communication và GEMM compu-
tation trên 2 micro-batches — giấu all-to-all latency→ +27–35% prefill throughput,
−50%peak memory (SGLang).
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 22 / 40

---

### DataParallelism: DP,DPA& Cache-AwareRouter

■ DP:replicate toàn bộ model +KV cache→
memoryduplication
■ DPA:chỉ replicate attention; MoE/FC layers
chiasẻ qua EP→khôngduplicate KV cache
■ MLAbenefit: DPA+MLA = batch size lớn
hơn,VRAM tiết kiệm đáng kể(DeepSeek
V3/R1)
■ Flags: --dp-size N --enable-dp-attention
■ Gửirequest đến instance có KVprefix cache
phùhợp nhất
■ Benchmark8 ×A10080GB: throughput
+92%,cache hit+275%(20% →75%)
■ Flags: --router-policy cache_aware
--cache-threshold 0.5
■ sgl-router: Rust-based, production-grade
(thaynative DP router)
DeepSeek-V3 DP+EP Config — --tp 8 --dp-size 8 --ep 8
--enable-dp-attention kết hợp DPA + Expert Parallelism + cache-aware routing
→+92%throughput.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 23 / 40

---

### DistributedInference: Parallelism StrategyGuide

Strategy Split Bestfor Tradeoff
DataParallelism (DP) Requests Multi-user,replicated model NoKV cache sharing
TensorParallelism (TP) Weights/layer Largemodel, single-node All-reducesync mỗi layer
PipelineParallelism (PP) Layers Multi-node,128K+ context Bubblelatency,micro-batch
ExpertParallelism (EP) MoEexperts Mixtral/ DeepSeek-V3 671B Expertrouting overhead
DisaggregatedP/D Prefill/Decode LongRAG, prefill-heavy KVtransfer bandwidth cost
■ ray start --head / ray start
--address=... mỗinode
■ --tensor-parallel-size 4
--pipeline-parallel-size 2 →8GPU / 2
nodes
■ NCCLcollective ops; Ray tự quảnlý device
mesh
■ NCCL_IB_HCA=mlx5 choInfiniBand NIC
■ TPwithin node: NVLink 900GB/s —
all-reducekhông bottleneck
■ PPacross nodes: P2P activation chịuđược
IBlatency
■ KhôngTP qua nodestrừNVLink fabric
(NVL72/GB200)
■ EP:mỗi GPU giữ subset experts,A2A
routingon-demand
RuleofThumb — TP ≤GPUs/node;PP=nodes;EPchoMoE.Vídụ: --tp 4 --pp
2 --ep 8 →cluster2 nodes ×4GPU phục vụ DeepSeek-V3 671B fullprecision.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 24 / 40

---

### PipelineParallelism: Ultra-Long Context

■ Chiamodel layers qua nhiều pipelinestages
vớiP2P communication
■ Chunkedprefill: các nodesxử lý token
chunksđồng thời →giảmTTFT long context
■ --pp-size N :số stages; --nnodes M :số
nodes
■ --enable-dynamic-chunking: tự điều chỉnh
theoprefix length
■ Smoothfactor env var (default 0.75,range
0.6–0.85)
■ DeepSeek-V3.1: 4K fixed hoặc12K dynamic
(smooth=0.65)
■ Qwen3-235B:6K fixed hoặc 18K dynamic
(smooth=0.8)
■ Dynamic: dùng initial chunk2–3×baseline
đểamortize overhead
■ PiecewiseCUDA Graph (PCG) tự độngtắt
khibật PP
■ Usecase: 128K+ contexttrên multi-node
GPUcluster
PPvsTP — PP ̸=TP:dùngPPkhimodelquálớnchosingle-nodeTP(DeepSeek-
V3.1 full precision) hoặc cần 128K+ context — tận dụng multi-node inter-connect
bandwidth.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 25 / 40

---

### Multimodal(VLM) Serving: Encode–Prefill–Decode

■ 1ảnh 10242 ≈1,100–4,100tokens
(Qwen3-VL ∼1,139,Pixtral 4,096)
■ Video30FPS ≈350Kvisual tokens/phút
(pre-compression)
■ TTFTgiờ là hàm củasốảnh,không phải
outputlength
■ Visionencoder (ViT)khônghưởnglợi từ TP
—chậm đi ở TP=8
■ Tách3pha: Encode (ViT)→Prefill →
Decode,scale độc lập
■ SGLang2E1P: ∼6–8×TTFT↓trên
Qwen3-VL-235B
■ vLLMv0.11+: --mm-encoder-tp-mode data
(encoderdisagg)
■ CPUAMX encode song song GPU
prefill/decode(Xeon)
Multimodal prefix caching — Hash trên pixel/image-embedding (SHA-256) →
cachehit: 18s →1sTTFT(LMCache). Early-fusion(Llama4)bỏluônencoderstage
riêng.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 26 / 40

---

### Embedding& Reranker Serving: The Retrieval Half

■ Prefill-bound: 1 forward pass,khôngKV
cache,khôngdecodeloop
■ Throughputqua largestatic batch
(token-sorted),không phải continuous
batching
■ Cross-encoderreranker: chấm điểm(query,
doc)— nặng hơn bi-encoder embedding
■ FP8: ∼50%throughput ↑ở >99%cosine
similarity
■ HFTEI:Rust, phục vụ cả embedding+
reranker(Qwen3, ModernBERT)
■ SnowflakeArctic Inference: 16×vLLM
(disaggtokenize + FP8)
■ Models: Qwen3-Embedding-8B (MTEB rank
1),BGE-M3 (dense+sparse+ColBERT)
■ MRL:cắt chiều embedding linh hoạt;late
chunkinggiữ context
Lưu ý:RAG/agent inference =một nửa là retrieval. Self-host break-even∼50–100M tokens/tháng so với API
(OpenAI/Voyage).
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 27 / 40

---

### SemanticCaching: The StackIs 3 Caches Deep

■ 1. Semantic cache(meaning-based): hit→
100%compute saved
■ 2. Prefix / KVcache: hit→skipprefill cho
sharedprefix
■ 3. Full inference: cache miss hoàntoàn
■ Semantic= embed prompt→vectorsearch →
trảresponse cũ nếu sim>threshold
■ Hitrate thực: 30–68%FAQ/support,
10–25%open-ended (“95%” là marketing)
■ vCache(ICLR’26): threshold thích ứng
per-prompt+ error bound
■ AWSElastiCache+Bedrock, Azure APIM
llm-semantic-cache
■ Bảomật: cache-poisoning (NDSS’26
∼90%)+ KV timing side-channel
Takeaway — Semanticcacheđứng trênKVcache—bắtđượccâuhỏi paraphrase,
khôngchỉexactprefix. Đổilại: staleanswers+collisionrisk →đặtthresholdcẩnthận,
saltcache per-tenant.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 28 / 40

---

### ModelRouting & Cascades: Cross-Model Cost

■ Routing(pre-generation): classifier chọn
modeltrướckhisinh
■ Cascade: chạy model rẻtrước,deferlên
modelmạnh khi confidence thấp
■ RouteLLM(ICLR’25): −85%chi phí GPT-4
ở95% MT-Bench
■ FrugalGPT:cascade match GPT-4ở −98%
cost
■ nano(∼$0.10/M)classify →mid($1–3/M)
draft →frontier($10–15/M)hard tail
■ −60–80%cost, <5%routing latency
■ AzureAI Foundry Model Router (GA),
OpenRouterAuto
■ 2026: pre-genrouting >cascade(cascade
trảtiền sinh model rẻ trướckhi defer)
Costlever — Routinglà đònbẩychiphílớnnhấtởservinglayer —khôngphải
mọi query cần frontier model. Reasoning model tốn 13–25× energy/query → route
“easy”sang model nhỏ.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 29 / 40

---

### Tokens-per-Joule& The Power Wall

■ GB200NVL72 120–132kW/rack;GB300
135–150kW;VeraRubinNVL144 ∼190kW
■ Datacenterđiện: IEA dựbáo ∼485 →950TWh
(2025→2030)
■ Tokens-per-joulegiờlà first-class metric
(MLPerfPower v5.1)
■ Medianthực: ∼0.31Wh/query (ước tính cũ thổi
phồng4–20 ×)
■ FP8 ∼ −30%energy (ở batch≥64);FP4
25–50×vsH100 FP16
■ MoEsparsity: GPT-OSS-20B−26%
energy/1Ktok vs dense 32B
■ GreenLLM:phase-specific DVFS,
−10–34%energy, <3.5%SLO miss
■ Carbon-awaretemporal shifting: bùtới
∼70%carbon
Lưu ý: Reasoning model (15× tokens) → median energy 0.31→ 3.91Wh/query (13×). Power, không phải
FLOPs,là ràng buộc scale 2026.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 30 / 40

---

### ConfidentialInference: TEE &the Attack Surface

■ TEEtrên GPU: data mã hoácả khi đang tính
(in-use)
■ HopperPPCIE(8-GPU HGX, 2025) — nhưng
NVLinkplaintext
■ Blackwell: NVLink encryption +TEE-I/O
(multi-GPUmã hoá đầu tiên)
■ Overhead: <9%throughputmodel lớn (∼0%
Llama-70B), ∼19%TTFT
■ KVtiming side-channel(PROMPTPEEK,
NDSS’25): 99% reconstruct promptqua
TTFTprobing trên shared APC
■ StanfordICML’25: 7/8caching API chia sẻ
cachecross-user
■ Mitigation: cachesalting per-tenant
(vLLM),SafeKV
■ ZK-proofinference vẫn chậm 104–105×
Khi nào cần— Regulated industry (y tế, tài chính, chính phủ) — giờ khả thi với
<9% overhead. Kết hợp prefix-cache: bật cache salting để chặn cross-tenant KV
leak.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 31 / 40

---

### Auto-scalingArchitecture

Clients
(100 RPS)
Load
Balancer
GPU1
GPU2
GPU3
GPUN
(auto)
KEDA
Autoscaler
GPU util>80%: scale out
Queue depth>10: scale out
GPU util<30%: scale in
Least-busyrouting
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 32 / 40

---

### ScalingStrategies

■ GPUutilization >80%: scale out
■ Queuedepth >10requests
■ KEDA+ Knative: Event-DrivenAutoscaling
■ Scale-to-zero: 0 replicas khino traffic— tiết
kiệmchi phí đáng kể
■ Least-busyrouting: +30% vsround-robin
■ Requestbatching: 50ms window,+40%
throughput
■ Warmpool: Nidle instances cho spikes
■ Trade-off: cost vscold start latency
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 33 / 40

---

### EdgeDeployment Flow

PyTorch
Model
ONNX
Export
GGUF
(llama.cpp)
TensorRT
(NVIDIA)
Ollama
(Container)
GPU
Server
Edge /
Laptop
3–5× faster
FP8/INT8 calibration
GGUF Q4_K_M
Llama-3,
Qwen-3, Phi-3 GGUFLevels: Q2_K(extreme, quality
drop)· Q4_K_M(recommended) ·Q6_K (near-lossless) · Q8_0 (maxquality)
Models: Llama-3-8B,Qwen-3-8B, Phi-3-mini | Ollama: ollama run llama3 —1 lệnh duy nhất
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 34 / 40

---

### HardwareLandscape 2026: BeyondH100

Chip FP4/FP8peak Memory Niche/ 2026 Status
NVIDIAH200 SXM FP8(no FP4) 141GB HBM3e Cost-effectivebaseline; +43% decode vs H100
NVIDIAB200 9PFLOPS FP4 192GB HBM3e FP4native; GB200 NVL72 = 72-GPUNVLink domain
NVIDIAB300/GB300 15PFLOPS FP4 288GB HBM3e BlackwellUltra —currentgold standard
NVIDIAVeraRubin 50PFLOPS NVFP4 288GB HBM4 Productionat CES’26; ships H2’26
AMDMI355X 20PFLOPS FP4 288GB HBM3e B200parity (MLPerf v6.0); GA Oct’25
GoogleTPU v7 4,614TFLOPS FP8 192GB HBM3e Ironwood;powers Anthropic Claude
AWSTrainium3 2.52PFLOPS FP8 144GB HBM3e GADec’25; ∼50%cost cut (Uber)
Lưuý: HBMbandwidth,khôngphảiFLOPs,làbottleneck —nguồncungHBM2026sold
out; memory bandwidth quyết định decode throughput. Frontier labs đa dạng hoá silicon:
Anthropicchạy Claude trên Google TPUv7 Ironwood + AWSTrainium,không chỉ NVIDIA.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 35 / 40

---

### SLADashboard: Key Metrics

120ms
P50Latency
Target: <200ms
380ms
P95Latency
Target: <500ms
850ms
P99Latency
Target: <1000ms
1,800
tokens/sper GPU
Benchmark: k6/locust
99.9%
Uptime
=8.7h downtime/year
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 36 / 40

---

### ProductionSLA: Best Practices

■ Multi-AZdeployment + health checks
■ Timeout10–60s cho LLM generation
■ Circuitbreaker: fallback khioverloaded
■ Gracefuldegradation: trả cached/shorter
response,route sang smaller model
■ Costper 1M tokens: liên tục optimize
■ Spotinstances cho batch inference
■ Scale-to-zerokhi no traffic(KEDA)
■ Right-sizeGPU: đừng dùng A100 cho7B
Lưuý: Benchmarkvới locust/k6trướckhiproduction. Không đoánlatency — đo thực tế.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 37 / 40

---

### Lab20: Model Serving& Inference Optimization

Day20-Track2-ModelServing-Lab/—chạyđượctrênWindows/macOS/Linux,low-
speclaptop OK
■ 00-setup: hardware detection +
cross-platforminstall
■ 01-quickstart: llama-cpp-python baseline
P50/P95/P99
■ 02-server: OpenAI-compatllama-server +
Prometheus+ locust load test
■ 03-milestone-integration: nối endpoint với
N16–N19
■ llama.cpptuning: build flags
(AVX2/AVX-512,NEON), thread sweep,
ctx-lensweep, GPU offload
(Metal/CUDA/Vulkan),quant tradeoffQ2_K
→Q8_0
■ MLX(macOS):Apple Silicon native runtime,
optional
Lưuý: Low-speclaptop(8GBRAM,noGPU)?Vẫnchạyđượctoànbộcoretracks. Bonustrackhoạtđộngtrên
mọiCPU— càng ”yếu” càng họcđược nhiều về tối ưu.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 38 / 40

---

### Milestone1: AI InfrastructurePlatform

Tíchhợp N16–N19 thành coherent AI infrastructureplatform demo
1. Cloudsetup: IaC +K8s cluster
2. Datapipeline: ingestion +processing
3. Lakehouse: Delta Lake +Medallion
4. Vectorstore: semanticsearch API
5. Featurestore: online/offline
6. Modelserving: optimized endpoint
7. Benchmarkreport: latency +cost
8. Livedemo: end-to-end flow
Lưuý: Submittrên LMS trước hết ngày. Demo live choinstructor trong lab session.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 39 / 40

---

### Chương4 Recap: HạTầng AI

Cloud
Infra
Data
Pipelines Lakehouse Vector &
Feature
Model
Serving
N16 N17 N18 N19 N20
Common mistakes:Skip validation→ data quality issues · No time travel→
no rollback · Static batching→ poor throughput
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 40 / 40

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
Quantization 2026: FP8/NVFP4 (Hopper+/Blackwell) cho production cloud, AWQ 4-bit cho
general,GGUF Q4_K_M cho edge.
Serving 2026: vLLM v1 + SGLang core;P/D disaggregation(Dynamo 1.0 / llm-d) là default
ở scale; serving giờ gồm cả VLM, embedding, semantic cache, routing, power & confidential
inference.
3 Goodput@SLO(khôngphảithroughput@peak)quyếtđịnhproductionsuccess—benchmark
P50/P95/P99trước khi deploy.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 40 / 40

---

### Tiếptheo & Bài tập

Chương5: CI/CD forAI Systems
“Từ hạ tầng sang vận hành — deploy
AImodels an toàn, tự động, liêntục.”
■ SubmitMilestone 1 đúng
deadline
■ Đọctrước: MLOps Principles—
GoogleCloud
■ Càisẵn GitHub Actions runner

---

### Hỏi& Đáp

Câu hỏi nào về Quantization, vLLM/SGLang, SLA, hay Milestone 1?

---

### Cảmơn!

AICB-P2T2 · Ngày 20
Model Serving & Inference Optimization
lms.vinuni.edu.vn · Slide & template trên LMS