"""
Rebuild questions.json: 30 questions per day (10 Easy + 10 Medium + 10 Hard)
covering ALL topics of the day.

Strategy:
- Select the 10 most pedagogically diverse questions per difficulty
- For dropped topics, append coverage notes to nearest relevant question's explanation
- For days with duplicate Easy topics, use custom index selection
"""
import json, subprocess, re
from collections import defaultdict

# Load original 45-per-day data from git main
orig = json.loads(subprocess.check_output(
    ['git', 'show', 'origin/main:data/questions.json']
))

# Build day/diff buckets
by_day_diff = defaultdict(list)
for q in orig:
    by_day_diff[(q['day'], q['difficulty'])].append(q)

all_days = sorted(set(q['day'] for q in orig))

# ─────────────────────────────────────────────
# SELECTION INDICES per (day, difficulty)
# Default = first 10; override for duplicate-topic days
# ─────────────────────────────────────────────
SELECTIONS = {}
for day in all_days:
    for diff in ['Easy', 'Medium', 'Hard']:
        SELECTIONS[(day, diff)] = list(range(10))

# Day 01: Easy has 3× Hyperparameters, 2× (Gemini+Anthropic redundant)
SELECTIONS[('Day 01', 'Easy')]   = [0, 1, 2, 5, 6, 7, 8, 9, 12, 13]
# Medium: skip Stop Sequences[8], keep Async API[11] instead; skip Multilingual[10]
SELECTIONS[('Day 01', 'Medium')] = [0, 1, 2, 3, 4, 5, 6, 7, 9, 11]
# Hard: drop Softmax Math[8] and Dual SDK Adapter[9]
SELECTIONS[('Day 01', 'Hard')]   = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11]

# Day 02: Easy has 2× Prompt Foundations, 3× Reasoning Techniques, 2× Structured Outputs, 2× Prompt Patterns
SELECTIONS[('Day 02', 'Easy')]   = [0, 2, 3, 4, 5, 8, 10, 11, 12, 14]
# Hard: drop Context Compression[10] and Prompt Optimization vs Fine-tuning[11]
SELECTIONS[('Day 02', 'Hard')]   = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Day 03: All unique. Keep most fundamental agent topics.
SELECTIONS[('Day 03', 'Easy')]   = [0, 1, 2, 3, 4, 5, 6, 8, 9, 11]
# Drop: Action Parser[7], Failure Modes[10], Reflection[12], Execution[13], Frameworks[14]

# Day 04: Easy has 2× Tool Choice, drop Gemini-specific[7]
SELECTIONS[('Day 04', 'Easy')]   = [0, 1, 2, 3, 5, 6, 8, 9, 10, 11]
# Drop: dup Tool Choice[4], Gemini Function Calling[7], Tool Choice Specific[12], Security[13] → keep Security
SELECTIONS[('Day 04', 'Easy')]   = [0, 1, 2, 3, 5, 6, 8, 9, 11, 13]

# ─────────────────────────────────────────────
# EXPLANATION EXTENSIONS
# Key: (day, difficulty, kept_index_in_original)
# Value: extra sentence(s) appended to explanation to cover dropped topics
# ─────────────────────────────────────────────
EXT = {}

# Day 01 Easy dropped: Top-p[3], Top-k[4], Gemini[10], Anthropic[11], Cost Estimation[14]
EXT[('Day 01', 'Easy', 2)] = (
    " | Mở rộng: Ngoài Temperature, các siêu tham số chính khác gồm Top-p (Nucleus Sampling) "
    "— chỉ lấy mẫu từ tập token có xác suất tích lũy ≥ p — và Top-k — giới hạn ứng viên về k "
    "token có xác suất cao nhất. Kết hợp hợp lý 3 siêu tham số này giúp kiểm soát tính sáng tạo và "
    "độ tập trung của đầu ra LLM."
)
EXT[('Day 01', 'Easy', 5)] = (
    " | Mở rộng: Cả ba nhà cung cấp lớn (OpenAI, Anthropic Claude, Google Gemini) đều hỗ trợ Streaming "
    "qua SSE. Anthropic yêu cầu tham số `max_tokens` bắt buộc; Gemini sử dụng thư viện `google-genai` "
    "với `gemini-1.5-flash` cho tốc độ nhanh, chi phí thấp. Luôn lưu API Key trong biến môi trường."
)
EXT[('Day 01', 'Easy', 0)] = (
    " | Mở rộng: Ví dụ tính chi phí thực tế — Giá Input $2.50/1M, Output $10.00/1M: "
    "1 request với 2,000 token input + 500 token output = (2000×$2.50 + 500×$10.00)/1,000,000 = $0.01. "
    "Với 100,000 requests/ngày, chi phí tháng ≈ $30,000."
)

# Day 01 Medium dropped: Stop Sequences[8], Multilingual Tokenization[10],
#   Frequency Penalty[12], Logprobs[13], Client Lifecycle[14], Monthly Budget[15],
#   Batch API[16], Seed Determinism[17]
EXT[('Day 01', 'Medium', 0)] = (
    " | Mở rộng: Frequency Penalty phạt các token xuất hiện nhiều lần (giảm lặp từ); "
    "Seed Determinism kết hợp temperature=0 hỗ trợ tái lập kết quả nhất quán cho unit test. "
    "Đây là 2 siêu tham số thường bị bỏ qua nhưng rất hữu ích trong production."
)
EXT[('Day 01', 'Medium', 7)] = (
    " | Mở rộng: Stop Sequences (tham số `stop`) dừng sinh text ngay khi gặp ký tự định sẵn, "
    "rất hữu ích để đảm bảo đầu ra đúng format. Multilingual Tokenization: tiếng Việt tốn "
    "nhiều token hơn tiếng Anh 1.5–2.5× do ký tự có dấu bị tách nhỏ."
)
EXT[('Day 01', 'Medium', 9)] = (
    " | Mở rộng: `logprobs=True` trả về log-xác suất từng token, dùng để đo độ tự tin "
    "và phát hiện hallucination. Client Lifecycle: tái sử dụng object `OpenAI()` (singleton) "
    "để tận dụng HTTP Connection Pool, tránh khởi tạo lại mỗi request."
)
EXT[('Day 01', 'Medium', 11)] = (
    " | Mở rộng: Batch API (OpenAI/Anthropic) cho 50% giảm chi phí với hạn mức rate limit "
    "riêng biệt, phù hợp xử lý offline hàng loạt. Monthly Budget ví dụ: 100,000 req/ngày × "
    "1,500 in + 300 out tokens = ~$2,160/tháng (giá $1.00/1M in, $3.00/1M out)."
)

# Day 02 Easy dropped: Prompt Foundations×1[1], Reasoning×2[6,13], Structured×1[7], Patterns×1[9]
EXT[('Day 02', 'Easy', 0)] = (
    " | Mở rộng: Prompt Foundations bao gồm 2 nguyên tắc cốt lõi — (1) Rõ ràng về task và "
    "định dạng đầu ra mong muốn; (2) Cung cấp đủ context để mô hình không cần phỏng đoán. "
    "Một prompt tốt luôn phân biệt rõ instruction, context và output format."
)
EXT[('Day 02', 'Easy', 2)] = (
    " | Mở rộng: Chain-of-Thought (CoT) yêu cầu LLM 'suy nghĩ từng bước'; "
    "Tree of Thoughts (ToT) mở rộng thành cây tìm kiếm đa nhánh; "
    "Self-Consistency lấy đa số từ nhiều lần suy luận. Prompt Patterns như Role Prompting "
    "('Bạn là chuyên gia về...') và Few-shot Examples đều tăng đáng kể chất lượng đầu ra."
)
EXT[('Day 02', 'Easy', 4)] = (
    " | Mở rộng: Structured Outputs có 2 cấp độ: (1) JSON Mode — mô hình cố gắng sinh JSON hợp lệ "
    "nhưng không đảm bảo schema; (2) Strict Schema (Structured Outputs với Pydantic) — grammar-guided "
    "decoding ép đúng schema 100%. Thư viện Instructor giúp validate tự động qua Pydantic."
)

# Day 03 Easy dropped: Action Parser[7], Failure Modes[10], Reflection[12], Execution[13], Frameworks[14]
EXT[('Day 03', 'Easy', 6)] = (
    " | Mở rộng: Action Parser phân tích đầu ra text của LLM thành (tool_name, args) cấu trúc. "
    "Agent Frameworks phổ biến: LangGraph (state machine), CrewAI (role-based), AutoGen "
    "(conversation-driven). Mỗi framework có trade-off riêng về flexibility vs abstraction."
)
EXT[('Day 03', 'Easy', 9)] = (
    " | Mở rộng: Failure Modes phổ biến trong ReAct Agent: hallucination tool arguments, "
    "infinite loop (thiếu stopping criteria), context overflow. Agent Reflection (Reflexion): "
    "Agent tự đánh giá kết quả hành động trước đó và cập nhật chiến lược cho vòng lặp tiếp theo."
)
EXT[('Day 03', 'Easy', 11)] = (
    " | Mở rộng: Agent Execution là bước thực thi tool thực tế và thu nhận Observation. "
    "Agent Scratchpad lưu trace Thought→Action→Observation theo vòng lặp. "
    "Agent Environment là không gian mà Agent có thể quan sát và tác động."
)

# Day 04 Easy dropped: Tool Choice dup[4], Gemini Function Calling[7], Choice Specific[12], Pydantic[14]
EXT[('Day 04', 'Easy', 2)] = (
    " | Mở rộng: Tool Choice có 3 mode: 'auto' (LLM quyết định), 'required' (bắt buộc gọi tool), "
    "và chỉ định tool cụ thể (tool_choice={'type':'function','function':{'name':'...'}}) — "
    "Gemini gọi là tool_config với mode NONE/AUTO/ANY. Pydantic model có thể convert sang JSON Schema "
    "qua `.model_json_schema()` để tạo tool definition."
)
EXT[('Day 04', 'Easy', 8)] = (
    " | Mở rộng: Tool Description là phần quan trọng nhất của tool definition — LLM chọn tool "
    "dựa vào description, không phải implementation. Mỗi parameter cũng cần description rõ ràng. "
    "Tool Args Parsing: khi LLM trả về tool_calls, extract arguments bằng json.loads(call.function.arguments)."
)

# Day 05 Easy dropped: Cost Modeling[10], HITL UX[11], Latency Budget[12], Disclaimers[13], Prioritization[14]
EXT[('Day 05', 'Easy', 4)] = (
    " | Mở rộng: AI Latency Budget: phân bổ ngân sách thời gian cho từng thành phần "
    "(retrieval: 100ms, LLM call: 800ms, post-processing: 100ms). "
    "AI Disclaimers: thông báo rõ 'Nội dung do AI tạo ra, cần kiểm tra trước khi sử dụng'. "
    "Cost Modeling: ước tính chi phí theo số users × avg tokens × model price."
)
EXT[('Day 05', 'Easy', 7)] = (
    " | Mở rộng: Human-in-the-Loop UX: thiết kế điểm can thiệp của người dùng cho các quyết định "
    "có rủi ro cao (xác nhận trước khi gửi email, phê duyệt trước khi deploy). "
    "AI Feature Prioritization: dùng ma trận Impact × Confidence × Ease để ưu tiên tính năng AI."
)

# Day 06 Easy dropped: Incident Runbooks[10], Data Readiness[11], Ethical Checklist[12], Post-Mortem[13], Roadmap[14]
EXT[('Day 06', 'Easy', 7)] = (
    " | Mở rộng: AI Risk Assessment bao gồm cả việc xây dựng AI Incident Runbooks — "
    "quy trình xử lý khi mô hình hoạt động sai trong production (ai xử lý, escalation path, "
    "thời gian phản hồi tối đa). Data Readiness Assessment: kiểm tra chất lượng, volume, "
    "và freshness của dữ liệu trước khi bắt đầu sprint AI."
)
EXT[('Day 06', 'Easy', 9)] = (
    " | Mở rộng: AI Roadmap Planning: tránh 'Waterfall AI' bằng cách build theo từng increment "
    "có thể đánh giá được. AI Ethical Checklist: kiểm tra bias, fairness, transparency "
    "trước khi launch. Post-Mortem in AI: tập trung vào data/model root cause, không chỉ infrastructure."
)

# Day 07 Easy dropped: Truncation[10], ANN[11], Dot Product vs Cosine[12], Inference[13], Storage Formats[14]
EXT[('Day 07', 'Easy', 7)] = (
    " | Mở rộng: FAISS hỗ trợ nhiều index: Flat (chính xác, chậm), IVF (xấp xỉ, nhanh), HNSW (cân bằng). "
    "ANN (Approximate Nearest Neighbor) hy sinh độ chính xác lấy tốc độ — phù hợp production. "
    "Dot Product tương đương Cosine Similarity khi vector đã chuẩn hóa về unit length."
)
EXT[('Day 07', 'Easy', 9)] = (
    " | Mở rộng: Embedding Truncation: một số model cho phép dùng ít dimension hơn "
    "(Matryoshka Embeddings) mà vẫn giữ chất lượng cao. Storage Format: vector thường lưu "
    "dưới dạng float32 (4 bytes/dim) hoặc float16 (2 bytes) — ảnh hưởng trực tiếp đến VRAM."
)

# Day 08 Easy dropped: Context Stuffing[10], Cross-Encoder[11], Groundedness[12], HyDE[13], Metadata[14]
EXT[('Day 08', 'Easy', 5)] = (
    " | Mở rộng: Hallucination trong RAG gồm 2 loại: Intrinsic (mâu thuẫn với context được lấy) "
    "và Extrinsic (bịa thông tin không có trong context). Groundedness score đo mức độ câu trả lời "
    "có căn cứ từ tài liệu retrieved. HyDE tạo 'tài liệu giả định' để cải thiện embedding retrieval."
)
EXT[('Day 08', 'Easy', 7)] = (
    " | Mở rộng: Context Stuffing (nhồi nhét quá nhiều context) dẫn đến 'Lost in the Middle' — "
    "LLM bỏ sót thông tin ở giữa context dài. Cross-Encoder Re-ranking đọc (query, doc) cùng lúc "
    "để cho điểm chính xác hơn Bi-Encoder, dùng sau retrieval để re-rank top-k kết quả. "
    "Metadata trong chunk (nguồn, ngày, tác giả) giúp filter và trích dẫn chính xác."
)

# Day 09 Easy dropped: MCP Tool Discovery[10], Frameworks[11], Specialization[12], Infinite Loop[13], Security Sandbox[14]
EXT[('Day 09', 'Easy', 4)] = (
    " | Mở rộng: MCP Tool Discovery: Client gọi `tools/list` để nhận danh sách tool từ Server. "
    "MCP Security Sandbox: Server cần chạy trong môi trường kiểm soát quyền truy cập "
    "(filesystem, network) để tránh Agent thực thi lệnh nguy hiểm."
)
EXT[('Day 09', 'Easy', 6)] = (
    " | Mở rộng: Multi-Agent Frameworks phổ biến: LangGraph (state machine), CrewAI "
    "(role-based), AutoGen (conversation). Agent Specialization: chia Agent thành 'Researcher', "
    "'Coder', 'Reviewer' giúp tăng chất lượng. Infinite Loop phòng tránh bằng max_iterations "
    "và stopping condition rõ ràng."
)

# Day 10 Easy dropped: Dead Letter Queue[10], Telemetry[11], Airflow[12], PII Masking[13], Alerting[14]
EXT[('Day 10', 'Easy', 8)] = (
    " | Mở rộng: Schema Validation thường đi kèm Dead Letter Queue (DLQ) — hàng đợi nhận "
    "records lỗi để retry hoặc điều tra. Airflow DAG (Directed Acyclic Graph) là cấu trúc "
    "workflow phổ biến nhất. Pipeline Alerting: gửi cảnh báo khi task fail 3 lần liên tiếp."
)
EXT[('Day 10', 'Easy', 6)] = (
    " | Mở rộng: OpenLineage chuẩn hóa event lineage. Pipeline Telemetry theo dõi "
    "Pipeline Freshness (thời gian từ nguồn đến đích). PII Masking trong pipeline: "
    "dùng Presidio hoặc regex để phát hiện và thay thế email, phone, CCID trước khi lưu."
)

# Day 11 Easy dropped: Toxic Content[10], System Prompt Leakage[11], Fallback[12], Self-Check[13], Presidio[14]
EXT[('Day 11', 'Easy', 7)] = (
    " | Mở rộng: Ngoài Intrinsic/Extrinsic Hallucination, các vấn đề phổ biến: "
    "Toxic Content thường phân loại theo 7 nhóm (hate speech, violence, sexual, ...). "
    "System Prompt Leakage xảy ra khi user dùng kỹ thuật như 'Repeat your instructions above'. "
    "Fallback Response chuẩn: 'Tôi không thể trả lời câu hỏi này.' — ngắn gọn, không xin lỗi dài dòng."
)
EXT[('Day 11', 'Easy', 6)] = (
    " | Mở rộng: PII (Personally Identifiable Information) gồm tên, email, CCCD, số điện thoại, "
    "địa chỉ. Thư viện Presidio (Microsoft) dùng NER + regex để detect và redact PII tự động. "
    "Self-Check Rail: LLM tự đánh giá đầu ra của mình trước khi trả về user."
)

# Day 12 Easy dropped: Multi-Stage[10], Non-Root[11], .dockerignore[12], Memory Limits[13], TLS[14]
EXT[('Day 12', 'Easy', 7)] = (
    " | Mở rộng: Multi-Stage Build giảm image size đáng kể (build stage với all deps, "
    "final stage chỉ copy binary). Non-Root User trong container tăng security. "
    ".dockerignore loại trừ node_modules, .git, __pycache__ khỏi build context."
)
EXT[('Day 12', 'Easy', 9)] = (
    " | Mở rộng: Memory Limit trong container: khi vượt quá OOM Killer sẽ kill process. "
    "TLS/HTTPS là yêu cầu bắt buộc cho AI API production — dùng cert-manager + Let's Encrypt "
    "hoặc managed certificate từ cloud provider."
)

# Day 13 Easy dropped: PII Masking[10], LangSmith[11], Cost Anomaly[12], Log Aggregation[13], SLA/SLO[14]
EXT[('Day 13', 'Easy', 8)] = (
    " | Mở rộng: Feedback Metric Logging nên được sanitize (PII masking) trước khi lưu log. "
    "LangSmith Run Trees visualize toàn bộ trace của LangChain/LangGraph application. "
    "Cost Anomaly Alerts: thiết lập threshold % tăng chi phí token để phát hiện bug early."
)
EXT[('Day 13', 'Easy', 9)] = (
    " | Mở rộng: Dashboard Visualization tốt nên có SLA/SLO panel — Error Rate < 0.1%, "
    "P99 latency < 2s. Log Aggregation (ELK, Grafana Loki) tập trung log từ nhiều service "
    "vào một nơi để tìm kiếm và phân tích nhanh."
)

# Day 14 Easy dropped: HumanEval[10], GSM8K[11], Synthetic Eval[12], DeepEval[13], Ground Truth[14]
EXT[('Day 14', 'Easy', 8)] = (
    " | Mở rộng: Ngoài MMLU, các benchmark quan trọng: HumanEval (code generation, pass@k), "
    "GSM8K (math reasoning, exact match). Ground Truth Definition: label 'đúng' được xác định "
    "bởi domain expert hoặc golden answer từ curated dataset."
)
EXT[('Day 14', 'Easy', 9)] = (
    " | Mở rộng: Benchmark[9] MMLU bao gồm 57 domains. Ngoài ra, DeepEval framework cung cấp "
    "metric sẵn có (faithfulness, contextual precision). Synthetic Eval Data Generation dùng "
    "LLM tạo cặp (question, answer, context) từ tài liệu để xây golden dataset tự động."
)

# Day 15 Easy dropped: Capacity Planning[10], Post-Mortem[11], Zero-Downtime[12], AI KPIs[13], Exam Strategy[14]
EXT[('Day 15', 'Easy', 9)] = (
    " | Mở rộng: Model Lifecycle bao gồm: training → validation → staging → production → "
    "monitoring → retrain/retire. Zero-Downtime Migration dùng Blue-Green hoặc Rolling Update. "
    "Capacity Planning: dự báo GPU/CPU cần thiết dựa trên QPS × avg latency × headroom factor."
)
EXT[('Day 15', 'Easy', 5)] = (
    " | Mở rộng: TCO gồm: compute, storage, networking, engineering time, và monitoring. "
    "AI Product KPIs: task completion rate, user satisfaction (thumbs up/down), cost per query. "
    "Post-Mortem in AI: luôn hỏi 'Tại sao model hành xử sai?' — data quality hay model drift?"
)

# Day 16 Easy dropped: Google TPU[10], Cerebras[11], SRAM vs DRAM[12], VRAM Capacity[13], Training vs Inference[14]
EXT[('Day 16', 'Easy', 7)] = (
    " | Mở rộng: FP8 (8-bit float) mới nhất trong Hopper/Ada Lovelace cho tốc độ gấp 2× FP16. "
    "SRAM (on-chip cache, nhanh nhưng nhỏ ~50MB) vs DRAM/HBM (off-chip VRAM, chậm hơn nhưng lớn). "
    "VRAM Capacity quyết định model size: LLaMA-7B cần ~14GB VRAM (FP16)."
)
EXT[('Day 16', 'Easy', 8)] = (
    " | Mở rộng: TDP (Thermal Design Power) quyết định yêu cầu làm mát và chi phí điện. "
    "Google TPU (Tensor Processing Unit) tối ưu cho matrix multiplication trong TensorFlow. "
    "Hardware Selection: Training cần VRAM lớn + NVLink; Inference cần latency thấp + throughput cao."
)

# Day 17 Easy dropped: Sequence Parallelism[10], 3D Parallelism[11], Sync vs Async SGD[12], World Size[13], Checkpoint[14]
EXT[('Day 17', 'Easy', 9)] = (
    " | Mở rộng: Gradient Accumulation tích lũy gradient qua N micro-batches trước khi update "
    "— tương đương batch size lớn hơn với ít VRAM hơn. 3D Parallelism = Data × Pipeline × Tensor "
    "parallel — cần thiết cho model > 100B params. World Size = tổng số GPU; Rank = ID của mỗi GPU."
)
EXT[('Day 17', 'Easy', 6)] = (
    " | Mở rộng: ZeRO Stage 1 shard optimizer states; Stage 2 thêm gradients; Stage 3 "
    "thêm cả parameters. Sequence Parallelism chia các token theo chiều sequence cho nhiều GPU. "
    "Sync SGD chờ tất cả worker; Async SGD không chờ — nhanh hơn nhưng stale gradients."
)

# Day 18 Easy dropped: Network Congestion PFC[10], ECN[11], Jumbo Frames[12], DAS[13], In-Network Computing[14]
EXT[('Day 18', 'Easy', 8)] = (
    " | Mở rộng: NFS thường là bottleneck do single-point metadata server. "
    "PFC (Priority Flow Control) ngăn packet loss trong RoCEv2 bằng cách pause sending. "
    "ECN (Explicit Congestion Notification) báo hiệu congestion mà không drop packet."
)
EXT[('Day 18', 'Easy', 9)] = (
    " | Mở rộng: Jumbo Frames (MTU=9000) giảm CPU overhead per packet trong AI cluster. "
    "DAS (Direct Attached Storage) cho IOPS cao nhất nhưng không chia sẻ được. "
    "In-Network Computing (SmartNIC/DPU) offload AllReduce trực tiếp trong switch."
)

# Day 19 Easy dropped: Prefix Caching[10], FlashAttention[11], Model Offloading[12], Dynamic Sampling[13], Greedy vs Beam[14]
EXT[('Day 19', 'Easy', 9)] = (
    " | Mở rộng: TTFT (Time To First Token) phụ thuộc prefill latency; ITL (Inter-Token Latency) "
    "phụ thuộc decode speed. Prefix Caching lưu KV Cache của prefix chung (system prompt) "
    "để tái sử dụng. FlashAttention v2/v3 tính attention IO-aware, tiết kiệm VRAM."
)
EXT[('Day 19', 'Easy', 6)] = (
    " | Mở rộng: TensorRT-LLM tối ưu inference trên NVIDIA GPU với kernel fusion và quantization. "
    "Model Offloading: chạy model lớn hơn VRAM bằng cách offload layer sang CPU RAM. "
    "Greedy Decoding chọn token max probability; Beam Search giữ B hypothesis song song."
)

# Day 20 Easy dropped: KubeRay[10], #SBATCH[11], Node Affinity[12], DCGM Exporter[13], Slurm Env Vars[14]
EXT[('Day 20', 'Easy', 9)] = (
    " | Mở rộng: Gang Scheduling yêu cầu tất cả pod/node của job phải start cùng lúc "
    "— quan trọng cho distributed training. KubeRay deploy Ray Cluster trên Kubernetes. "
    "DCGM Exporter expose GPU metrics (utilization, memory, temperature) cho Prometheus."
)
EXT[('Day 20', 'Easy', 3)] = (
    " | Mở rộng: K8s GPU Resource: `nvidia.com/gpu: 1` trong resource limits. "
    "Node Affinity + Taints/Tolerations đảm bảo GPU pod chỉ schedule trên GPU node. "
    "Slurm #SBATCH directives: `--gpus-per-node=8 --nodes=4 --time=24:00:00`."
)

# Day 21 Easy dropped: Dynamic Resources[10], Fault Tolerance[11], Ray Data[12], Head vs Worker[13], Nested Tasks[14]
EXT[('Day 21', 'Easy', 8)] = (
    " | Mở rộng: Actor Handles: lưu reference đến remote Actor và gọi method async. "
    "Ray Fault Tolerance: task tự động retry khi worker fail (max_retries=3). "
    "Ray Data: streaming pipeline xử lý dataset lớn hơn RAM bằng lazy evaluation."
)
EXT[('Day 21', 'Easy', 9)] = (
    " | Mở rộng: Ray Train tích hợp với PyTorch DDP/FSDP cho distributed training. "
    "Head Node quản lý GCS (Global Control Store) và scheduling; Worker Node chạy task/actor. "
    "Nested Tasks: task có thể spawn remote task khác — tạo dynamic DAG tự nhiên."
)

# Day 22 Easy dropped: Model Cards[10], Online vs Offline Feature[11], Retraining Triggers[12], Pipeline Caching[13], Packaging[14]
EXT[('Day 22', 'Easy', 8)] = (
    " | Mở rộng: Artifact Lineage = tracking mối quan hệ data → model → deployment. "
    "Model Cards tài liệu hóa: intended use, performance metrics, limitations, bias analysis. "
    "Automated Retraining Triggers: drift detected → alert → human review → retrain approval."
)
EXT[('Day 22', 'Easy', 9)] = (
    " | Mở rộng: DVC (Data Version Control) git-like versioning cho data và model files. "
    "Online Feature Store (real-time, low latency, Feast/Redis); Offline Feature Store (batch, "
    "high throughput, BigQuery/Hive). Pipeline Caching trong Kubeflow tránh re-run bước đã tính."
)

# Day 23 Easy dropped: Bottleneck[10], Petastorm[11], Prefetching[12], Streaming[13], Augmentation[14]
EXT[('Day 23', 'Easy', 8)] = (
    " | Mở rộng: Data Ingestion Bottleneck: CPU-bound (tokenization), I/O-bound (disk read), "
    "GPU-starved (dataloader chậm hơn training). Prefetching (num_workers + prefetch_factor) "
    "chạy background để luôn có batch sẵn. Petastorm: format chuẩn cho ML training từ Parquet."
)
EXT[('Day 23', 'Easy', 9)] = (
    " | Mở rộng: MinHash LSH: dùng Shingling (n-gram) + MinHash để estimate Jaccard similarity, "
    "sau đó LSH banding tìm near-duplicate trong tập lớn O(n) thay vì O(n²). "
    "Dataset Streaming: HuggingFace Datasets `load_dataset(..., streaming=True)` không cần disk."
)

# Day 23/Track 3 Easy dropped: Time-Travel[10], Streaming[11], TypedDict[12], create_react_agent[13], Subgraphs[14]
EXT[('Day 23 / Track 3', 'Easy', 9)] = (
    " | Mở rộng: Human-in-the-Loop Breakpoints trong LangGraph: `interrupt_before=['node_name']` "
    "dừng graph để human review. Time-Travel: `get_state_history()` + `update_state()` để "
    "rewind về trạng thái cũ. create_react_agent shortcut tạo ReAct agent không cần define graph thủ công."
)
EXT[('Day 23 / Track 3', 'Easy', 6)] = (
    " | Mở rộng: TypedDict State Schema định nghĩa cấu trúc state với type hints. "
    "Subgraphs: graph có thể chứa graph khác như node — cho phép modular multi-agent architecture. "
    "LangGraph Streaming: `graph.stream(input)` yield state updates theo từng node."
)

# Day 24 Easy dropped: PII Scrubbing[10], EU AI Act[11], Model Extraction[12], Adversarial[13], AI Governance[14]
EXT[('Day 24', 'Easy', 9)] = (
    " | Mở rộng: Model Watermarking nhúng signature vào weights/outputs để chứng minh ownership. "
    "PII Scrubbing at Scale: dùng NER (spaCy/Presidio) + regex pipeline. "
    "EU AI Act phân loại AI theo risk level: Unacceptable/High/Limited/Minimal."
)
EXT[('Day 24', 'Easy', 8)] = (
    " | Mở rộng: Membership Inference Attack: adversary xác định xem một sample có trong "
    "training data không. Adversarial Perturbations: thay đổi nhỏ input (ε-ball) đánh lừa model. "
    "AI Governance Board: committee đa chức năng review AI system trước deployment."
)

# Day 25 Easy dropped: Scale-to-Zero[10], CodeCarbon[11], Cost Anomaly[12], Model Tiering[13], Right-Sizing[14]
EXT[('Day 25', 'Easy', 9)] = (
    " | Mở rộng: Quantization Cost Savings: INT8 tiết kiệm 2× VRAM và ~1.5× throughput. "
    "Scale-to-Zero: serverless inference không charge khi không có traffic. "
    "Model Tiering: routing query đơn giản → small model, phức tạp → large model."
)
EXT[('Day 25', 'Easy', 7)] = (
    " | Mở rộng: FinOps for AI: tagging resource (team, project, env) để track chi phí. "
    "CodeCarbon đo lượng CO₂e của training job. Cost Anomaly Detection: alert khi chi phí "
    "tăng > X% so với baseline (AWS Cost Explorer, GCP Budget Alerts). Right-Sizing: "
    "chọn GPU/CPU instance phù hợp — không over-provision."
)

# Day 26 Easy dropped: Model Registry[10], GTM[11], Data Gravity[12], Egress[13], Transit Gateway[14]
EXT[('Day 26', 'Easy', 9)] = (
    " | Mở rộng: Unified Control Plane (Anthos, Azure Arc) quản lý cluster trên nhiều cloud. "
    "Model Registry across Multi-Cloud: lưu model trên S3/GCS và sync. "
    "Egress Cost: data transfer ra khỏi cloud region tốn ~$0.08/GB — tối thiểu hóa cross-cloud calls."
)
EXT[('Day 26', 'Easy', 5)] = (
    " | Mở rộng: Data Sovereignty: dữ liệu phải ở trong jurisdiction quy định (GDPR → EU). "
    "Global Traffic Manager (GTM/GeoDNS) route traffic đến datacenter gần nhất. "
    "Data Gravity: dữ liệu lớn 'hút' compute về phía nó — compute should follow data."
)

# Day 27 Easy dropped: AV Sensor Fusion[10], Cold-Start[11], Fraud Scoring[12], Medical Explainability[13], Search Ranking[14]
EXT[('Day 27', 'Easy', 9)] = (
    " | Mở rộng: Healthcare AI Federated Learning: bệnh viện train local, chỉ chia sẻ gradients "
    "— đảm bảo privacy. AV Sensor Fusion: kết hợp LiDAR + Camera + Radar theo không gian và thời gian. "
    "Medical AI Explainability: SHAP values, GradCAM để giải thích quyết định cho bác sĩ."
)
EXT[('Day 27', 'Easy', 3)] = (
    " | Mở rộng: E-Commerce Recommendation cần giải quyết Cold-Start Problem: "
    "khi user/item mới chưa có interaction history — dùng content-based hoặc popularity-based. "
    "Real-time Fraud Scoring Engine cần latency < 50ms — dùng feature store + lightweight ML model."
)

# Day 28 Easy dropped: Reconfigurable[10], Biological-Silicon[11], Scaling Laws[12], Analog Optical[13], AI Engineer Mindset[14]
EXT[('Day 28', 'Easy', 9)] = (
    " | Mở rộng: Carbon-Neutral AI Data Centers dùng renewable energy và carbon offset. "
    "Scaling Laws (Chinchilla): tokens_optimal ≈ 20 × model_params — hướng dẫn compute budget. "
    "AI Engineer Mindset: luôn đặt câu hỏi 'cost-performance trade-off' và 'what could go wrong?'"
)
EXT[('Day 28', 'Easy', 8)] = (
    " | Mở rộng: Exam Strategy: Concept Mapping — vẽ sơ đồ kết nối các khái niệm. "
    "FPGA (Field-Programmable Gate Array) linh hoạt, lập trình lại được — dùng cho low-latency inference. "
    "Biological-Silicon Hybrid: kết hợp organoid computing với silicon chip — còn ở giai đoạn nghiên cứu."
)

# ─────────────────────────────────────────────
# BUILD RESULT
# ─────────────────────────────────────────────
result = []

for day in all_days:
    counter = 1
    day_slug = re.sub(r'[^a-z0-9]+', '_', day.lower()).strip('_')

    for diff in ['Easy', 'Medium', 'Hard']:
        qs = by_day_diff[(day, diff)]
        indices = SELECTIONS.get((day, diff), list(range(10)))

        for idx in indices:
            if idx >= len(qs):
                continue
            q = dict(qs[idx])
            q['id'] = f"{day_slug}_{counter:03d}"
            counter += 1

            # Apply explanation extension if defined
            ext_key = (day, diff, idx)
            if ext_key in EXT:
                q['explanation'] = q.get('explanation', '') + EXT[ext_key]

            result.append(q)

# Verify counts
from collections import Counter
day_counts = Counter(q['day'] for q in result)
diff_counts = Counter((q['day'], q['difficulty']) for q in result)

print("Total questions:", len(result))
print("\nPer day counts:")
for day in all_days:
    e = diff_counts[(day, 'Easy')]
    m = diff_counts[(day, 'Medium')]
    h = diff_counts[(day, 'Hard')]
    total = e + m + h
    flag = "✓" if total == 30 and e == 10 and m == 10 and h == 10 else "✗"
    print(f"  {flag} {day}: E={e} M={m} H={h} total={total}")

# Save
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nSaved to data/questions.json")
