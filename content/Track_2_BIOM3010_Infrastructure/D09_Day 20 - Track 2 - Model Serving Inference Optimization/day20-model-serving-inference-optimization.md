# day20 model serving inference optimization

**File gốc:** `Track_2_BIOM3010_Infrastructure\D09_Day 20 - Track 2 - Model Serving Inference Optimization\day20-model-serving-inference-optimization.md`

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
3. KVCache, Attention & Speculative
Decoding
4. Single-NodeServing Stack 2026 (8
engines)
5. Distributed& Multi-TenantServing
6. ServingRegimes 2026 (agentic,
reasoning,VLM,embed,cache,route,
RL,dLLM)
7. Auto-scaling& Operations
8. Edge& Hardware Landscape
9. Capacity,Benchmarking & SLA
(Goodput@SLO)
10. Lab20 + Milestone 1
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 1 / 53

---

### Mụctiêu bài học

Saubuổi học này,bạnsẽ:
1. Phânbiệt Throughputvs Goodput@SLO,đọc TTFT/TPOT trên dashboard
production
2. Ápdụng quantization (FP16/FP8/AWQ4-bit/NVFP4/GGUF) đểgiảm memory & tăng
throughput
3. HiểuKV Cache, PagedAttention, RadixAttention, FA3/FA4,MHA→MLA+ spec
decoding2026 (EAGLE-3 →DFlash/DSpark)
4. Sosánh 8 serving engines (vLLM, SGLang,Dynamo, llm-d, LMDeploy,TRT-LLM,
Ollama,llama.cpp)
5. Chọnparallelism (TP/PP/EP/DP)vàschedulingpolicy cho workload distributed
6. Hoànthành Lab 20 (llama.cpp tuning bonus)và submit Milestone 1
Agendahôm nay
Foundations →Quantization →KV/Attention/SpecDecoding →Single-Node →Dis-
tributed →Regimes2026 →Auto-scale →Edge →Capacity →Lab20
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 2 / 53

---

### DeliverableCuối Ngày

Artifactcần nộp
Optimizedinference stack + Lab 20 report+ Milestone 1 demo
■ Benchmarkreport: GGUF quantsweep (Q2_K→Q8_0)+ continuous batching,
P50/P95/P99
■ Loadtest: 10 &50 concurrent users (locust) trênllama-server
■ Lab20 report (benchmarks/results.md vớiP50/P95/P99 + bonus tuning notes)
■ Milestone1: AI infrastructureplatform demo (N16–N19)
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 3 / 53

---

### LatencyTaxonomy: TTFT· TPOT · Goodput

LatencyMetrics
■ TTFT(TimeToFirstToken) : từ request đến
tokenđầu tiên — phụ thuộcprefill compute +
queuewait
■ TPOT(TimePerOutput Token) =ITL:
khoảngcách đều giữa mỗi outputtoken
■ E2ELatency =TTFT+TPOT ×(N–1);SLO
thườngở P95/P99
Throughputvs Goodput
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 4 / 53

---

### Pre-LLMEra: Serving Infrastructure2017–2022

Pre-LLMServing Stack (2017–2022)
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
TạiSao Chúng Không Đủ ChoLLMs
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 5 / 53

---

### Quantization: Precision vs Performance

VRAMUsage (Llama-3-8B)
FP32 31.6GB
FP16 15.8GB
FP8 7.9GB
INT8 7.9GB
AWQ4-bit 4.5GB
NVFP4 ∼4.0GB
Đánhđổi accuracy
■ FP8: <1%drop, 2×memoryvs FP16 —
nativetừ Hopper trở đi
■ AWQ4-bit: ∼1ptMMLU trên model 8B+,
tệhơn rõ với<7B
■ NVFP4(Blackwell): 3.5×vsFP16, 1.8×
vsFP8, <1%loss
Chọnquantization
■ ProductionHopper: FP8/AWQ4-bit
■ ProductionBlackwell: NVFP4(default)
■ Maxquality: BF16 /FP16
■ Edge/laptop: GGUFQ4_K_M (i-quants
nếu <Q4)
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 6 / 53

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
FormatMechanics
■ GPTQ:inverse Hessian layer-by-layer (128
calib. samples) — quantizechậm, inference
nhanh
■ AWQ:scale salient weights trước khiround
INT4 →acc >GPTQcùng bits
■ NF4(bitsandbytes): 4-bit NormalFloat +double
quant,hợp weight phân phối chuẩn
■ GGUFk-quant: Q4_K_M = mixedQ4/Q6 theo
tensor; k=quanttốt hơn, m=sizetrung bình
KhiNào Dùng Gì
■ GPUcloud (Hopper): FP8—best
quality/perf
■ GPUVRAM tight: AWQ4-bit —tốt nhất ở
4-bit
■ CPU-only: GGUFQ4_K_M —
recommended
■ Cựckỳ constrained: GGUFQ2_K —last
resort
■ Fine-tune1 GPU:NF4+ QLoRA
Lưuý: model <7Bmấtqualitynhanhhơn13B+—
benchmarkperplexity sau khi quantize.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 7 / 53

---

### FP42026: MXFP4 vsNVFP4 & KV Cache Quantization

Haiđịnh dạng 4-bit, không thaythế nhau
■ Cùng4 bit/phần tử (E2M1), khácởscale:
MXFP4= E8M0(luỹthừa2)/ 32giátrị; NVFP4=
E4M3(FP8)/16giátrị + 1 scale FP32toàn
tensor
■ Blocknhỏ hơn + scale phânsố→NVFP4
chínhxác hơn; giá làgấpđôi overheadscale
■ NVFP4cần Blackwell(TensorCore gen 5).
MXFP4là chuẩnOCP →chạyđược cả AMD
■ gpt-ossship bằng MXFP4—lý do là
portability,không phải accuracy
KVcache cũng quantize được
■ Weightquant giảmmodelmemory;KV quant
giảmmemory tỉlệ với context×
concurrency—đòn bẩy lớn hơn ở
long-context
■ TurboQuant(Google,arXiv 2504.19874):
xoayngẫu nhiên + hiệu chỉnhQJL 1-bit.3.5
bit/channel=quality-neutral, 2.5 bit = suy
giảmnhẹ; cách chặn lý thuyết≈2.7×
■ Data-oblivious,khôngcần train/calibrate—
dùngđược online
Chọnthếnào — NVIDIA-only,cầnaccuracy →NVFP4(DeepSeek-R1-0528: ≤1%
giảm so FP8). Cần chạy đa nền tảng / dùng gpt-oss→ MXFP4. Cảnh báo cho §6
Reasoning: KVquantization cóthểlàmhại reasoningmodelnhỏ—quantizeweight
trước,KV sau, và đo lại chứđừng bật cả hai một lượt.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 8 / 53

---

### KVCache & PagedAttention

Traditional: Contiguous
Wasted!
PagedAttention: Paged
PageTable
Nowaste
PagedAttention(vLLM)
■ KVcache như virtual memory pages
■ 24×vsnaive HF Transformers
■ Dynamicmemory allocation
PrefixSharing (RadixAttention)
■ Táisử dụng KV qua radixtree (prefix
sharing)
■ Lýtưởng cho RAG, multi-turn, agents
■ Engineeringchi tiết: xem§4 Prefix
Caching
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 9 / 53

---

### AttentionArchitecture: MHA →MLA& Long-Context

MHA GQA MQA MLA
KV:1× KV:4×less KV:8×less KV:10×less
Standard LLaMA-2/3 PaLM/ Falcon DeepSeek-V3
MLA(Multi-head Latent Attention)
■ CompressQ/K/V xuống latent vector nhỏtrước
attention
■ DeepSeek-V3: 10×ítKV memory vs standard
MHA
■ Kernel: FlashMLA, CutlassMLA, FlashInfer
(2025)
■ Chophép context dài hơn trêncùng VRAM
Long-ContextStack
■ YaRN:RoPE interpolation, không cần
retrain
■ StreamingLLM:attention sinks, ∞context
■ Jamba(AI21Labs): SSM/Transformer
hybrid,256K ctx
■ FA3+ MLA backends→kernelcho context
dài(xem §4)
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 10 / 53

---

### Hybrid& Sparse Attention: Khi KV Cache Ngừng Tăng

Hybrid: State Thay ChoCache
■ Xenkẽ attention layer (O(N2),KV O(N))với
SSM/linearlayer (O(N), stateO(1))
■ Statecốđịnh kích thước,cập nhậtin-place →
KV/requestkhông tăng theo context
■ Model2026: Qwen3-Next, KimiLinear,
MiniMax,Nemotron
■ SGLang: 2pool —Mamba pool cấp theo
request,KV pool theotoken
(--mamba-full-memory-ratio),co giãn lúc
chạybằng CUDA virtual memory
BaThứ Bị Vỡ Vì “In-Place”
■ Prefixcaching: không rollback đượcstate về
prefix → MambaRadixCache (2LRU riêng; KV
evictlá →gốc,state evict bất kỳ node)
■ Specdecoding: draft reject khôngrollback
được →mỗidraft tokenmộtslot riêng,accept
thìpromote
■ P/Ddisaggregation: KV stream theopage,
nhưngstate phải chuyểnnguyênkhối,
atomic
Sparse (DSA) + bức tranh chung— DeepSeek DSA(V3.2): “lightning indexer”
chọn top-k KV blocktrước attention → O(L2) →O(Lk), giá API giảm>50%. MLA
nénKV·linear/SSMlàmKV hằngsố ·DSA đọcít KV—bađònvàocùngbứctường
memory bandwidth. Từ SGLang v0.5.16UnifiedRadixTree là cache mặc định cho
SWA/Mamba/DSA.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 11/ 53

---

### SpeculativeDecoding & Continuous Batching

SpeculativeDecoding
■ Draftmodel sinh 4–8 tokens, targetverify
songsong trên cùng 1 forwardpass
■ EAGLE-3(NeurIPS’25): 3.0–6.5×,
+20–40%so EAGLE-2 — vẫn làbản EAGLE
mớinhất (chưacó EAGLE-4)
■ DeepSeekMTP (Multi-TokenPrediction):
∼1.8×,acceptance 85–90%(DeepSeek
eval)
■ Lookahead/ NGRAM:self-drafting khi
khôngcó draft model. Có sẵn trong
vLLM/SGLang/TRT-LLM
Continuous(In-Flight) Batching
■ Staticbatching (legacy): chờ đủ batch→
+200–500ms padding
■ Continuousbatching: requests vào/ra mỗi
step,no padding →5×latencygiảm
■ Tokenstreaming: client nhận từngtoken —
TTFTcảm giác ↓
■ vLLM“continuous” = TRT-LLM“in-flight”
batching;SGLang piecewiseCUDA graph
chovariable-length batch
Kinh tế batch— --speculative-algorithm EAGLE3 --speculative-num-steps 5
--speculative-eagle-topk 4 (cần draft ckpt / MTP head). Quy tắc cũ — “spec
decodinglà latencytool,batch ≥24verify-overheadlàm chậmhơn( ∼0,93×)”—chỉ
đúngvới drafterautoregressive. Thế hệ 2026: 3 frame kế tiếp.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 12 / 53

---

### DraftingLadder: EAGLE-3 →ParallelDrafting (2026)

EAGLE-1/2
(2024)
EAGLE-3
(2025)
P-EAGLE· DFlash
(2026)
DSpark
(2026)
Draft ở feature
space + draft tree
Multi-layer hid-
den state, AL≈4
Parallel: cả block
trong 1 forward
Semi-AR + confi-
dence scheduling
Từvựng bắt buộc
■ AcceptanceLength (AL, τ): số token trung
bìnhđược nhậnmỗivòng verify — chỉ sốso
sánhthật, không phải “N×”
■ Blocksize γ: số token drafterđề xuất/vòng
(DFlash& DSpark: 7offline, 5ởproduction
V4)
■ Lossless/ distribution-preserving: rejection
samplinggiữ nguyên phân phối target→
outputyhệt nhưkhông dùng spec
■ Drafttree + tree attention(EAGLE-2): verify
nhiềunhánh trong 1 forward pass
Vìsao AR drafting hết dưđịa
■ EAGLE-3draft Ktoken= Kforwardpass
tuầntự củadrafter →draftlatency tăng tuyến
tínhtheo K
■ TăngK: AL tăngchậmdần,chi phí draft tăng
đều →tốiưu kẹt ởK ≈ 3
■ Paralleldrafting: Ktokentrong 1forward →
P-EAGLEđạt đỉnh ởK=7,nhanh hơn
EAGLE-3tới 1.69×(gpt-oss-20B,B200)
■ Cáigiá mới: mấtphụ thuộc giữa các token
trongblock →suffixdecay (bàitoán DSpark
giải)
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 13 / 53

---

### DFlash: Block Diffusion Drafting+ KV Injection

Cơchế: 1 forward= cả block
■ Drafterlà blockdiffusion LM:nhận γ mask
token,attention non-causal →sinhcả block
trong1forward pass(5layer,chạy 1lần thay
vìKlần)
■ KVinjection: hidden state củatarget nhét
thẳngvào KV cache drafter→khỏimô hình
lạicontext
■ Ablation(LMSYS): bỏ KV injection, riêng
diffusionvẫn thắng EAGLE-3 — thắngnhờ
draftlatency,không nhờ draft giỏi hơn
Sốđo (nguồn gốc)
■ arXiv2602.06036: > 6×lossless,tới 2.5×so
EAGLE-3
■ Qwen3-4B(LMSYS): GSM8K AL 4.2→3.3×
vsEAGLE-3 AL 4.2→2.1×—ALngang
nhau,speedup gấp ∼1.5×
■ NVIDIA:gpt-oss-120b, 8×B300,TRT-LLM—
ở500–600 tok/s/user,throughput >15×so
ARdecoding
Chạy thử — SGLang: --speculative-algorithm DFLASH
--speculative-draft-model-path <ckpt> --speculative-dflash-block-size
8. vLLM:quathưviện Speculators—đổiEAGLE-3 →DFlashlà thayconfig,không
sửacode. Ckpt mở:deepseek-ai/dflash_qwen3_*_block7.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 14 / 53

---

### DSpark: Semi-Autoregressive + ConfidenceScheduling

Haicái đầu nhỏ, hai vấnđề khác nhau
■ Vấnđề: drafter parallel khôngcó phụ thuộc
nội-block →tokencàng cuối block càng dễ
reject(suffixdecay)
■ Markovhead: low-rank logit bias(r=256)từ
tokenliền trước, trả lại phụthuộc. Giá:
+0.2–1.3%latency. --markov-rank 0 ⇒thoái
hoávề DFlash
■ Confidencehead: linear+sigmoid, đoán xác
suấtđược accept của từng vịtrí
Sốđo (arXiv 2607.05147, Bảng 1)
■ Qwen3-4B,AL/vòng — GSM8K: 5.14
(EAGLE-3)· 5.40 (DFlash) ·6.11;MT-Bench:
2.39· 3.07 ·3.64
■ Trungbình +26–31%ALso EAGLE-3,
+16–18%soDFlash
■ DeepSeek-V4live trafficvs baselineMTP-1:
mỗiuser nhanh hơn60–85%ởcùng
throughput;ở SLA vừa, throughput tổng
+51–52%
Confidence-scheduledverification — Verifyblockdàicho mọirequestlàlãngphí
—tokennguycơrejectcaovẫnchiếmchỗtrongbatch. DSparkướclượng xácsuất
sống sót của prefixrồi cắtđộ dài verify riêng từng requesttheo profile throughput
củaengine: lầnđầuspecdecodingcoi batchcapacitylàtàinguyênphảilậplịch .
Code: deepseek-ai/DeepSpec (MIT).
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 15 / 53

---

### ChọnThuật ToánSpec Decoding(Aug 2026)

Thuậttoán Kiểudrafting Điểmmạnh Dùngkhi
NGRAM/ Lookahead Khôngcần model Zerotraining, zero VRAM Outputlặp nhiều (code, JSON)
MTP/ NEXTN Headcó sẵn trong model Khôngcần checkpoint rời Modelđã kèm MTP head (DeepSeek)
EAGLE-3 Autoregressive,Kpass Chín, hỗ trợ rộngnhất Batchnhỏ, latency-first
P-EAGLE Parallel,1 pass Giữkiến trúc EAGLE-3,K=7 Đãcó pipeline EAGLE-3
DFlash Blockdiffusion+ KV inj. Draftlatency thấp nhất Cầninteractivity cực cao
DSpark Semi-AR+ confidence ALcao nhất, lập lịch verify Servingđông concurrency
Lưu ý: Ba khoản chi phí, ba đòn khác nhau: (1) draft latency → parallel drafting; (2)host–device sync →
SGLang Spec V2 overlap scheduler(mặc định từ v0.5.16; Qwen3-8B, 1×B200, concurrency 32: 11.4→ 15.3
ktok/s, +33%); (3)verify waste→ confidence scheduling. Ladder thư việnvllm-project/speculators: EAGLE-3
(v0.1.0) → DFlash (v0.5.0)→ P-EAGLE (v0.6.0)→ DSpark (v0.7.0).Cảnh báo: DSpark đã có trong Speculators
nhưngchưacócờ DSPARKtrongSGLang — kiểm tra enginetrước khi hứa với khách hàng.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 16 / 53

---

### FlashAttention: IO-AwareAttention (FA1→FA4)

FlashAttn-1
(Dao2022)
FlashAttn-2
(2023)
FlashAttn-3
(2024)
FlashAttn-4
(2026)
NeurIPS’22 arXivJul ’23 Hopper Blackwell
Tiling + SRAM
O(N) mem, 3–4×
Seq parallelism
2× FA1 speed
TMA async, FP8
warp specialization
Blackwell 2-CTA
∼1613 TFLOPs BF16
CoreInsight: IO-Awareness(FA1)
■ Standardattn: Q×K(N2×d)viết HBM →đọc
lạisoftmax →đọclại ×V— 3 HBM round trips
■ FA:tile Q/K/V vào SRAM,online softmax, ghi
output1lần duy nhất
■ Memory: O(N) thay vìO(N2)— context dài
khôngOOM
■ FA3: Hopper TMAasync pipeline + FP8.FA4
(arXivMar’26) đã ship—tích hợp vàovLLM
v0.27(Aug’26)kèm FP8 KV trên SM100
FlexAttention(PyTorch2024)
■ torch.nn.attention.flex_attention:
BlockMaskAPI
■ Express: causal, sliding window,document
boundary,prefix+causal
■ Compilequa torch.compile →Triton
kernel,không cần CUDA custom
■ Tíchhợp: PyTorch
F.scaled_dot_product_attention,vLLM,
SGLangcustom patterns
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 17 / 53

---

### ModelCompilation: torch.compile +CUDA Graphs + TensorRT

torch.compile(PyTorch2.0+)
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
CUDAGraphs
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 18 / 53

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
TrạngtháiAug2026 : vLLMv0.27.1(11/08)·SGLang v0.5.17(08/08). Cảhai đangchuyển
frontend sangRust — cùng một lý do: Python GIL nghẽn ở request-handling path. Version
drift ∼2tuần/lần: dạy kỹthuật,coi flag là thứ dễđổi.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 19 / 53

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
Keyshift
2020–2022: manual/static batching, CUDA kernels — framework-level optimizations.Jun 2023:PagedAttention
→ continuous batching→ 24× throughput jump, ecosystem convergence. 2024–25: prefix sharing + disaggre-
gatedP/D →TTFTvà goodput là SLO first-class.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 20 / 53

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
v0(2023) →v1(default Mar 2025)
■ v0: KV như virtual-memorypages, block 16 tokens,
24×vsHF naive; continuous batching; prefixcaching
opt-in
■ v1: unified pool (KV+ activations),APCON mặc
định,chunked prefill mặc định, prefix-aware
scheduler— 1.7×v0
Keycommands — vllm serve MODEL
--tensor-parallel-size N
--gpu-memory-utilization 0.9
--max-model-len 8192
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 21 / 53

---

### PrefixCaching: RadixAttention, APC,HiCache & Pricing

Engineering: KV Reuse
■ vLLMv1 APC:Automatic Prefix Caching,
ONmặc định
■ RadixAttention(SGLang): radix-tree, cache
hit= skip prefill toàn bộshared prefix
■ HiCache3tầng: GPU VRAM→hostRAM
→external(HF3FS/Mooncake),
attach/detachkhông cần restart
■ Cross-instance: LMCache, Mooncake
globalpool trên cluster
■ Tiếtkiệm prefill: −70%TTFT trên repeated
systemprompts
PricingTier2026
■ Anthropic: cached read−90%(Claude
Opus4.8 / Haiku 4.5)
■ DeepSeek: cache-hit∼98%off(V4 Flash
$0.14/$0.28/M)
■ OpenAI:cached input −75%(GPT-4.1/
GPT-5.x)
■ Google: cached read−90%(Gemini2.5 /
3.x)
Takeaway — Prefix caching = engineering optimizationvà pricing tier. Đặt system
prompt/context cố định ởđầu prompt để tối đa cache-hit. Cache miss vẫn tính full
price →monitorcache-hit rate trên dashboard.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 22 / 53

---

### AttentionBackend Selection: FA3/ FA4/ FlashInfer/ FlashMLA

HardwareAuto-Selection
■ H100/H200(Hopper,CUDA 12.3+) → fa3
■ B200(Blackwell) → trtllm_mha hoặc fa4
■ A100/A40 → flashinfer
■ DeepSeekV3/R1 MLA → flashmla
(page=64)
■ ROCm/ Ascend / CPU→ triton
(cross-platformfallback)
BackendFeature Highlights
■ FA3: TMA async, FP8KV — Hopper native
■ FA4: Blackwell SM100, shiptrong vLLM
v0.27
■ FlashInfer: page-size>1,FP8 KV,
spec-decodetopk >1
■ TRTLLM-MLA:DeepSeek MLA, verified
spec-decode
MLA Backends (DeepSeek V3/R1)— FlashMLA · CutlassMLA · FlashInfer-MLA
· TRTLLM-MLA — 3.1× throughput vs MHA, 10× less KV memory. Tự chọn
theo GPU + model; override chỉ khi benchmark/debug: --attention-backend
{fa3|fa4|flashinfer|trtllm_mha|flashmla|triton}
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 23 / 53

---

### StructuredGeneration: XGrammar,Tool& Reasoning Parsers

Grammar-ConstrainedOutput
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
Tool& Reasoning Parsers
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 24 / 53

---

### ProductionTuning: Memory,Scheduling & Observability

Memory& Scheduling Knobs
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
Observability& Crash Recovery
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 25 / 53

---

### RequestScheduling: Ai ĐượcChạy Trước?

Đangcó trong engine (bật đượchôm nay)
■ vLLM --scheduling-policy fcfs (mặcđịnh) |
priority —giá trịnhỏhơn chạytrước, hoà
theothời điểm đến
■ SGLang --schedule-policy: mặc địnhcũng
fcfs;thêm lpm(longest-prefix-match— xếp
lạirequestđểtăngcachehit,đổilạischeduling
overhead), priority, lof, routing-key…
■ HếtKV →preempt;vLLM v1 mặc định
RECOMPUTE(rẻhơn SWAP).
--max-num-batched-tokens =ngân sách
token/step: tăng→TTFTtốt, giảm →ITLtốt
Vẫnlà nghiên cứu (đừng hứavới khách)
■ Fairness: VTC — VirtualTokenCounter
(OSDI’24,arXiv 2401.00588), chặn trên2×
chênhlệch phục vụ giữa 2client backlog.
Chưaengine nào ship
■ Đoánđộ dài outputđểxếp SJF (ELIS, arXiv
2505.09142)— OSL không biết trướclà gốc
củamọi bài toán scheduling LLM
■ Real-timelẫn best-effortchung cụm (arXiv
2504.09590). vLLM: preempt requestđang
chạybằngpriority mới chỉ là featurerequest
(#40004),chưaship
Vì sao frame này quan trọng— Núm rẻ nhất mà gần như không ai vặn:không
tốn GPU, không đổi model. Cả hai engine đều mặc định FCFS— cache-aware
(lpm) phảitự bật. Tài liệu mirror thời v0.4.x nóilpm là mặc định:không còn đúng—
đọc server_args.py đúngversion.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 26 / 53

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
Systems2026
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 27 / 53

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
Multi-LoRAStack 2026
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 28 / 53

---

### ExpertParallelism: MoE Scaling

Architecture
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
KeyOptimizations
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 29 / 53

---

### DataParallelism: DP,DPA& Cache-AwareRouter

DPvs DPA(DP Attention)
■ DP:replicate toàn bộ model +KV cache→
memoryduplication
■ DPA:chỉ replicate attention; MoE/FC layers
chiasẻ qua EP→khôngduplicate KV cache
■ MLAbenefit: DPA+MLA = batch size lớn
hơn,VRAM tiết kiệm đáng kể(DeepSeek
V3/R1)
■ Flags: --dp-size N --enable-dp-attention
sgl-router: Cache-AwareLoad Balancing
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 30 / 53

---

### DistributedInference: Parallelism StrategyGuide

Strategy Split Bestfor Tradeoff
DataParallelism (DP) Requests Multi-user,replicated model NoKV cache sharing
TensorParallelism (TP) Weights/layer Largemodel, single-node All-reducesync mỗi layer
PipelineParallelism (PP) Layers Multi-node,128K+ context Bubblelatency,micro-batch
ExpertParallelism (EP) MoEexperts Mixtral/ DeepSeek-V3 671B Expertrouting overhead
DisaggregatedP/D Prefill/Decode LongRAG, prefill-heavy KVtransfer bandwidth cost
Multi-nodevLLM (Ray Cluster)
■ ray start --head / ray start
--address=... mỗinode
■ --tensor-parallel-size 4
--pipeline-parallel-size 2 →8GPU / 2
nodes
■ NCCLcollective ops; Ray tự quảnlý device
mesh
■ NCCL_IB_HCA=mlx5 choInfiniBand NIC
PlacementRules
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 31 / 53

---

### PipelineParallelism: Ultra-Long Context

Architecture
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
OptimalChunk Size (2025)
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 32 / 53

---

### AgenticServing: Multi-Turn,Long-Prefix, Tool-Gapped

WorkloadThật (đo được)
■ TraceLab(arXiv2606.30560): ∼4.300
sessioncoding-agent, ∼350KLLM step,
∼430Ktool call (Claude Code +Codex)
■ Vònglặp tự trị dài;contextdài, output ngắn;
toolcall phân bốđuôinặng
■ TraceCodex: tớilượt 30context ≈80K
token,tỉ lệ input:output≈131:1
■ Prefix-cachehit caonhưng không hoàn hảo
VìSao Cache Vỡ
■ Capacity: context 100K token= hàng GB KV
→mộtinstance hết chỗ
■ Cross-instancemiss: load balancer đẩy
sessionsang instance chưa từng thấyprefix
→recomputetoàn bộ
■ Evict-on-completionsai: engine xoá KV
requestvừa xong — nhưng agentsẽquay lại
sautool call
■ Toolgap: khoảng nghỉ giữa2 lượt (đôi khi
theonhịp con người)
Cách chữa: KV pool dùng chung— vLLM × Mooncake Store— GPUDirect
RDMA chuyển KV block thẳng GPU↔pool. Trace Codex thật,12×GB200: 3.8×
throughput, 46× giảm P50 TTFT,8.6× giảm E2E, cache hit1,7% →92,2%. Pool
dùng chung biến cache locality từ bài toánroutingthànhstorage— affinity routing
dễvỡ khi autoscale, còn pool tốtthì round-robin cũng đủ.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 33 / 53

---

### ReasoningModels: Chế ĐộCapacity-Bound

ĐổiChế Độ, Không Chỉ DàiHơn
■ Chuỗireasoning dài đẩy inferencerakhỏi
vùngcompute-bound prefill sang vùng
capacity-bound(ISCA’26,arXiv 2605.19775)
■ Bẫycapacity của DP:KV phân mảnh→
throttleadmission sớm, computenằmkhông
■ TPthu hồiphầnmemory bỏ phí; lợi ích
sublinearquanh ngưỡng ∼32B
■ Dense(Llama-405B) →TPbậccao;MoE(R1)
→chiếnlược lai vì overhead routing/sync
BốnTriệuChứng Ở Production
■ Memoryvolatility: KV dao độngmạnh ngay
trongmột lần chạy
■ Straggler: một request “nghĩ”lâu chặn cả
batch
■ Latencykhông đoán được: OSL không biết
trước →khôngschedule theo nó được
■ Domainpreference: hành vi đổitheo loại bài
toán
Phảntrựcgiác+hệquảsizing — Quantizationvàspecdecoding cólợi chorea-
soning model; nhưngprefix caching và KV quantization có thểgây hại accura-
cy/throughput với reasoning modelnhỏ (arXiv 2510.18672) — không tối ưu nào an
toànvôđiềukiện. ChatmodelsizeKVtheo p95(ISL+OSL);reasoningmodelcóOSL
đuôidài không kiểm soát được→admissioncontrol + token budget làbắtbuộc.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 34 / 53

---

### ServingCho RL: Rollout Là MộtWorkloadRiêng

Vònglặp: generate →train →sync
■ RLHF/GRPOsinh trajectorybằngchính
engineserving (vLLM/SGLang), không bằng
backendtraining (FSDP/Megatron) — nên
pipelineRL tách trainer khỏi inference
■ Colocated(train+infercùng GPU) vs
disaggregated: colocated tiết kiệmGPU
nhưngphải nhườngbộnhớ mỗi vòng
■ Nútthắt thật làweightsync mỗistep, không
phảitốc độ sinh token. Engine biết LoRA→
chỉđẩy adapterdelta (dướimili-giây), không
broadcasttoàn bộ tham số
Cơchế trong vLLM
■ Sleepmode (--enable-sleep-mode): level1
=weight →CPURAM, bỏ KV;level2 =bỏ
luônweight (khisẽcậpnhật weight). Giải
phóng >90%VRAM,khôngtắt server
■ Endpoint: POST /sleep?level=1 · /wake_up ·
/is_sleeping;đánh thức từng phần:
tags=["weights"]
■ Weighttransfer: API cắm-thay-được để
trainerđẩy weight mới vào engine.Partial
rolloutlưusample dở khi sync→khôngphí
GPUchờ straggler
Phânvai với Ngày 21–22— Ngày20 sở hữuphíaserving: rollout engine, sleep-
/wake, weight transfer, elasticity (ROSE, arXiv 2605.06534). Thuật toán RL (PPO/-
GRPO/DPO) thuộcNgày 21–22. Điểm nối: sleep mode là cách một cụm serving
chomượn VRAMcho training mà không phải dựngcụm thứ hai.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 35 / 53

---

### DiffusionLLM: Khi Model Đích KhôngCòn Autoregressive

Khácgì so với AR serving
■ Sinhcảblock song songrồikhử nhiễu dần
thayvì 1 token/forward — “TPOT”không còn
làđơn vị đo tự nhiên;cỡ block = núm chất
lượng ↔độtrễ
■ Côngthức chủ đạo: khởi tạo từ modelARcó
sẵnrồi train tiếp bằng mụctiêu diffusion—
khôngtrain từ đầu
■ Númchất lượng/tốc độ mới:sốbước khử
nhiễu(ARkhông có tham số tươngđương)
Đãra khỏi phòng thí nghiệm
■ Mercury(Inception): dLLM thương mạiđầu
tiên, >1000tok/s trênH100
■ Mercury2 (13/08/2026): hãng công bố“10×
nhanhhơn”, giá$0.25/$1.00per1M in/out.
Mọicon số tok/s ở đâyđều là hãng tự báo
■ LLaDA2.0 (arXiv2512.15745): chuyển model
ARcó sẵnthànhdLLM qua lịch 3 pha;mini
16B/flash 100B,MoE, open-source
Vòng khép kín với §3— Diffusion đã vào stack của bạn ở vaidrafter (DFlash —
§3)trướckhi vàoởvai modelchính. Cùngmộtýtưởng: bỏràngbuộc“mỗiforward
một token”. Hệ quả serving: giả định của PagedAttention/continuous batching (KV
lớn dần đúng 1 token/step)không còn đúng— đừng bê thẳng công thức sizing của
§9sang dLLM.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 36 / 53

---

### Multimodal(VLM) Serving: Encode–Prefill–Decode

Image-TokenExplosion
■ 1ảnh 10242 ≈1,100–4,100tokens
(Qwen3-VL ∼1,139,Pixtral 4,096)
■ Video30FPS ≈350Kvisual tokens/phút
(pre-compression)
■ TTFTgiờ là hàm củasốảnh,không phải
outputlength
■ Visionencoder (ViT)khônghưởnglợi từ TP
—chậm đi ở TP=8
EPDDisaggregation (2026)
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 37 / 53

---

### Embedding& Reranker Serving: The Retrieval Half

KhácGì Với LLM Decode
■ Prefill-bound: 1 forward pass,khôngKV
cache,khôngdecodeloop
■ Throughputqua largestatic batch
(token-sorted),không phải continuous
batching
■ Cross-encoderreranker: chấm điểm(query,
doc)— nặng hơn bi-encoder embedding
■ FP8: ∼50%throughput ↑ở >99%cosine
similarity
Stack2026
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 38 / 53

---

### SemanticCaching: The StackIs 3 Caches Deep

3-LayerCache Stack
■ 1. Semantic cache(meaning-based): hit→
100%compute saved
■ 2. Prefix / KVcache: hit→skipprefill cho
sharedprefix
■ 3. Full inference: cache miss hoàntoàn
■ Semantic= embed prompt→vectorsearch →
trảresponse cũ nếu sim>threshold
ThựcTế & Rủi Ro
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 39 / 53

---

### ModelRouting & Cascades: Cross-Model Cost

HaiChiến Lược
■ Routing(pre-generation): classifier chọn
modeltrướckhisinh
■ Cascade: chạy model rẻtrước,deferlên
modelmạnh khi confidence thấp
■ RouteLLM(ICLR’25): −85%chi phí GPT-4
ở95% MT-Bench
■ FrugalGPT:cascade match GPT-4ở −98%
cost
Production3-TierStack
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 40 / 53

---

### Tokens-per-Joule& The Power Wall

ThePower Wall
■ GB200NVL72 120–132kW/rack;GB300
135–150kW;VeraRubinNVL144 ∼190kW
■ Datacenterđiện: IEA dựbáo ∼485 →950TWh
(2025→2030)
■ Tokens-per-joulegiờlà first-class metric
(MLPerfPower v5.1)
■ Medianthực: ∼0.31Wh/query (ước tính cũ thổi
phồng4–20 ×)
ĐònBẩy Năng Lượng
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 41 / 53

---

### ConfidentialInference: TEE &the Attack Surface

GPUConfidential Computing
■ TEEtrên GPU: data mã hoácả khi đang tính
(in-use)
■ HopperPPCIE(8-GPU HGX, 2025) — nhưng
NVLinkplaintext
■ Blackwell: NVLink encryption +TEE-I/O
(multi-GPUmã hoá đầu tiên)
■ Overhead: <9%throughputmodel lớn (∼0%
Llama-70B), ∼19%TTFT
Inference-LayerAttacks
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 42 / 53

---

### Auto-scaling: Kiến Trúc& Chiến Lược

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
scaleout / in
Least-busyrouting
ScaleTriggers
■ Scaleout: GPUutil >80%hoặcqueuedepth
>10request
■ Scalein: GPU util<30%
■ KEDA+ Knative: event-drivenautoscaling
■ Scale-to-zero: 0 replica khino traffic— xem
framekế tiếp về cái giácủa nó
Optimization
■ Least-busyrouting: +30% vsround-robin
■ Requestbatching: cửa sổ50ms, +40%
throughput
■ Warmpool: Ninstance idle sẵn cho spike
■ Đánhđổi cốt lõi:costvs cold-start latency
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 43 / 53

---

### ColdStart & WeightLoading: Thuế Của Scale-to-Zero

VìSao Replica Không Bật TứcThì
■ Coldstart production >40giây,so với
∼30ms/token khi đã warm
■ Scale-to-zero: request đầu tiêngánhtoànbộ
chiphí đó — hoặc nhậnluôn lỗi
■ Khởiđộng vLLM =6bước,và chủ yếu
CPU-bound,không phải GPU (arXiv
2606.07362)
■ Mỗibước scaledựđoán đượctheotham số
model/hệthống →coldstart là bài toán tính
được,không phải điều bí ẩn
BốnĐòn Bẩy,Theo ThứTự
■ Streamweight, bỏ chặng đĩa: Run:AI Model
Streamerđọc thẳng object store→CPUmem
→GPU( s3://, az://);tích hợpnativetrong
cảvLLM và SGLang, báo cáotới6×
■ Đổiformat: CoreWeaveTensorizernạp thẳng
vàoGPU, ∼53–60%thờigiancủasafetensors
■ Cachecompile: giữ lại torch.compile/
CUDA-graphcapture giữa các lần khởiđộng
■ Đừngvề 0 thật: warm pool, hoặc
scale-to-zerocóauto-wake
Quy tắc— SLAinteractive → không scale-to-zero: giữ tối thiểu 1 replica ấm và
trả tiền cho nó. Trafficbatch/dev/nội bộ→ scale-to-zero là đúng, vì không ai đang
chờ. Đây cũng làlý do warm-up phải bị loạikhỏi mọi số benchmark.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 44 / 53

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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 45 / 53

---

### HardwareLandscape 2026: BeyondH100

Chip FP4/FP8peak Memory Niche/ 2026 Status
NVIDIAH200 SXM FP8(no FP4) 141GB HBM3e Cost-effectivebaseline; +43% decode vs H100
NVIDIAB200 9PFLOPS FP4 192GB HBM3e FP4native; GB200 NVL72 = 72-GPUNVLink domain
NVIDIAB300/GB300 15PFLOPS FP4 288GB HBM3e BlackwellUltra —currentgold standard
NVIDIAVeraRubin 50PFLOPS NVFP4 288GB HBM4 Fullproduction 01/06/26; ships H2’26, 8clouds
AMDMI355X 20PFLOPS FP4 288GB HBM3e B200parity (MLPerf v6.0); GA Oct’25
GoogleTPU v7 4,614TFLOPS FP8 192GB HBM3e Ironwood;powers Anthropic Claude
AWSTrainium3 2.52PFLOPS FP8 144GB HBM3e GADec’25; ∼50%cost cut (Uber)
Lưuý: HBMbandwidth,khôngphảiFLOPs,làbottleneck —nguồncungHBM2026sold
out; memory bandwidth quyết định decode throughput. Frontier labs đa dạng hoá silicon:
Anthropicchạy Claude trên Google TPUv7 Ironwood + AWSTrainium,không chỉ NVIDIA.
Bằng chứng sống (Aug’26): VR200 giữ đúng hẹn 50PFLOPS NVFP4, nhưng NVIDIAhạ
spec HBM4 từ 22TB/s xuống∼20TB/s — con sốtính toánvề đích, con sốbăng thôngthì
không.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 46 / 53

---

### CapacityPlanning: ToánSizing

KVcache trên mỗi token
2 ×nlayer ×nkvhead ×dhead ×b
(hệsố 2 = K vàV;b=byte/phần tử)
Llama-3.3-70B, 80 layer, GQA 8 KV head,dhead=128,
FP16:
2 × 80 × 8 × 128 × 2 = 327 .680B ≈ 320 KB/token
→context8K ≈2,5GB KV / 1 request
Ngânsách VRAM
VRAM = weights + KV + activations +
overhead
Một H200 (141GB) , 70B ở FP8 (≈70GB
weights),chừa ≈10GB activations/overhead:
141 − 70 − 10 ≈ 61 GBchoKV
61/2,5 ≈ 24request8K đồng thời
Đó là câu trả lời cho “sao không serve nổi 100
usertrên 1 GPU”.
Đònbẩy nhân con số 24lên:FP8KV ×2·NVFP4 KV ×4(soFP16) · MLA thay GQA×2,7–4,7·layer linear/hybrid →
KVO(1)·giảm nửa context×2·prefix cachingkhôngđổitrần, chỉ tăng throughput thựctế
Lưu ý:PagedAttention kéo lãng phí phân mảnh xuống<4% — nhỏ nhưng khác 0.Ngày 25 (GPU FinOps)trả
lời“tốnbao nhiêu tiền”;ở đây ta chỉ trảlời “cóvừa không, được bao nhiêuuser”.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 47 / 53

---

### Benchmarking: Đo Sao ChoKhông Nói Dối

SốĐo Vô Nghĩa Nếu Thiếu
■ ISL/OSL :TTFTlàcâuchuyệncủaISL,TPOT
làcủa OSL — thiếu thìkhông so sánh được
■ Closed-loop(giữNin-flight)hay open-loop
(Poisson)? Closed-loopkhôngthể lộqueueing
collapse
■ Percentile,không phải mean—batching
làmtrung bình nói dối
■ Loạiwarm-up (coldstart + CUDA graph +
compile)và ghi rõversionengine + flag +
hardware
ClientCủa Bạn Đang Nói Dối
■ Benchmarkclient phổ biến làsingle-process
asyncio →tựtạo nghẽn hàng đợiphíaclient
(arXiv2605.24217)
■ Môhình M/G/1: GILthổi phồng TTFT/TPOT
khităng request rate
■ Bạnđang đochínhclient của mình,không
phảiserver. Sửa: clientmulti-process+
metricNTPOT
Công cụ & bài học— vllm bench serve · AIPerf · InferenceMAX. SPEED-
Bench(NVIDIA,arXiv2604.09557)chospecdecoding: token ngẫunhiên thổiphồng
throughput ∼23%khi bật SD; domain entropy thấp (code, math) có AL cao hơn hẳn
roleplay —workload quyết định kết quả. Lab 20 dùng locust→ nhiều process
worker.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 48 / 53

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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 49 / 53

---

### ProductionSLA: Best Practices

Reliability& Timeout
■ Multi-AZdeployment + health checks
■ Timeout10–60s cho LLM generation
■ Circuitbreaker: fallback khioverloaded
■ Gracefuldegradation: trả cached/shorter
response,route sang smaller model
Cost-Performance
■ Chiphí $/1M token: mô hình hoá ởNgày25
(GPUFinOps)
■ Spotinstances cho batch inference
■ Scale-to-zerokhi no traffic(KEDA)
■ Right-sizeGPU: đừng dùng A100 cho7B
Lưuý: Benchmarkvới locust/k6trướckhiproduction. Không đoánlatency — đo thực tế.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 50 / 53

---

### Lab20: Model Serving& Inference Optimization

Repo
Day20-Track2-ModelServing-Lab/—chạyđượctrênWindows/macOS/Linux,low-
speclaptop OK
CoreTracks(llama.cpp throughout)
■ 00-setup: hardware detection +
cross-platforminstall
■ 01-quickstart: llama-cpp-python baseline
P50/P95/P99
■ 02-server: OpenAI-compatllama-server +
Prometheus+ locust load test
■ 03-milestone-integration: nối endpoint với
N16–N19
Bonustracks
■ llama.cpptuning: build flags
(AVX2/AVX-512,NEON), thread sweep,
ctx-lensweep, GPU offload
(Metal/CUDA/Vulkan),quant tradeoffQ2_K
→Q8_0
■ MLX(macOS):Apple Silicon native runtime,
optional
Lưuý: Low-speclaptop(8GBRAM,noGPU)?Vẫnchạyđượctoànbộcoretracks. Bonustrackhoạtđộngtrên
mọiCPU— càng ”yếu” càng họcđược nhiều về tối ưu.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 51 / 53

---

### Milestone1: AI InfrastructurePlatform

Deliverable
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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 52 / 53

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
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 53 / 53

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
Quantization 2026: FP8/NVFP4 (Hopper+/Blackwell) cho production cloud, AWQ 4-bit cho
general,GGUF Q4_K_M cho edge.
Speculative decoding đổi vai: drafter autoregressive (EAGLE-3) chỉ làlatency tool; parallel
drafting(P-EAGLE/DFlash)+confidencescheduling(DSpark)kéonósangcả throughput—
DeepSeekđã thay MTP-1 trong production.
Serving2026rộnghơn“chạy1model”: vLLMv1+SGLangcore,P/Ddisaggregationởscale,
cộngVLM/embedding/semanticcache/routing/RLrollout/dLLM—và Goodput@SLO,không
phảithroughput@peak, mới quyết địnhthành bại.
Giảngviên (VinUni) AICB· Ngày 20 Tuần4 53 / 53

---

### Tiếptheo & Bài tập

Bàitiếp theo
Chương5: CI/CD forAI Systems
“Từ hạ tầng sang vận hành — deploy
AImodels an toàn, tự động, liêntục.”
Bàitập về nhà
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