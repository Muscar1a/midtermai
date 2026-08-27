# day13 monitoring logging observability

**File gốc:** `Phase_1_COMP2010\D26_Day13-monitoring-logging-observability\day13-monitoring-logging-observability.md`

---

### Monitoring, Logging & Observability

AICB-P1 · Ngày 13 · Biết agent đang hoạt động thế nào
Tên Giảng Viên
VinUniversity · Phase 1 · 2026

---

### “3 câu chuyện có thật: CFO hỏi vì sao hóa

đơn OpenAI tháng này $45,000 — không ai trả
lời được. Chatbot ngân hàng viral lên Twitter
vì trả lời xúc phạm — phát hiện sau 6 giờ.
Agent chạy “bình thường” nhưng engagement
giảm 30% suốt 2 tuần — không alert nào fire.”
Giữcâu hỏi này trong đầu khihọc bài hôm nay

---

### Nội Dung Bài Học

1. Foundations: Observability & 3pillars
2. AImetrics deep dive (TTFT,quality,
cost,drift)
3. Structuredlogging (schema, PII,
aggregation)
4. Distributedtracing (OpenTelemetry,
Langfuse)
5. SLO-basedalerting & dashboard
design
6. Toolslandscape2026 + case studies
7. Lab13: monitoring blueprintcho
agent
8. PreviewDay 14: Evaluationwith
RAGAS
Giảngviên (VinUni) AICB· Monitoring 2026 1/ 67

---

### Mục Tiêu Ngày 13 (Bloom’s Taxonomy)

■ Remember—liệt kê được 3 pillars ofobservability và 6 loại AI-specificmetrics
■ Understand—giải thích được vì sao P99quan trọng hơn average, và SLOkhác SLA thế
nào
■ Apply—implement được structured logging vớicorrelation ID + PII sanitization choagent
đangdeploy
■ Analyze—đọc được trace waterfall vàxácđịnh bottleneck trong agent pipelinenhiều bước
■ Evaluate—so sánh được Langfuse / LangSmith/ Helicone / Phoenix cho usecase cụ thể
■ Create—thiết kế được monitoring blueprintvới SLO, alert rules, và dashboard3 layers
Giảngviên (VinUni) AICB· Monitoring 2026 2/ 67

---

### Deliverable Cuối Ngày

Monitoring blueprint hoàn chỉnh cho deployed agent: structured logging + tracing +
dashboard+ alert rules dựa trên SLO.
■ 1structured logging pipeline: JSON, correlation ID, PII sanitized, 3 loglevels
■ 1Langfuse/LangSmith integration: ≥10traces với cost + latency+ quality tags
■ 1monitoring dashboard: 4golden signals + cost + quality (6panels tối thiểu)
■ 1SLO definition + alert rules: symptom-based, có runbook link
■ 1trang blueprint document: mô tả SLO, architecture diagram, alert playbook
Giảngviên (VinUni) AICB· Monitoring 2026 3/ 67

---

### 01

Foundations of Observability
Từ lý thuyết xuống thực hành: observability là gì, và vì sao chỉ
monitoring không đủ cho AI agent

---

### Monitoring vs Observability — Khác Nhau Thế Nào?

Monitoring (biết trước)
■ Đocác metrics biết trước sẽcần
■ Trảlời câu hỏiđã định sẵn
■ Phùhợp với known-unknowns
■ Vídụ: CPU >80%? uptime?
Observability (khám phá)
■ Hệthống phát ra đủdatađểhỏi
câuhỏi mới
■ Phùhợp với unknown-unknowns
■ Vídụ: vì saouser X với feature Y,
modelZ, tháng W latency cao?
AIagentcórấtnhiều unknown-unknowns(promptmới,modeldrift,usercreativity)
→observabilityquan trọng hơn monitoring đơn thuần.
Giảngviên (VinUni) AICB· Monitoring 2026 4/ 67

---

### Control Theory — Vì Sao Quan Trọng

Agent
System
Observe
(metrics)
Analyze
(compare)
Act
(fix/scale)
Feedbackloop
MTTD(MeanTimeToDetect): từ khi sự cố xảy
rađến khi phát hiện.
MTTR(MeanTimeToRecover): từ khiphát hiện
đếnkhi fix xong.
Monitoring tốt =giảm MTTD xuống phút, không phải ngày. Không có observability,
MTTD= thời gian user phản ánh.
Giảngviên (VinUni) AICB· Monitoring 2026 5/ 67

---

### Từ Artifact Day 12 Sang Production Reality

Day 12 đã làm được
■ Agentdeployed trên cloud
■ PublicURL hoạt động
■ Healthcheck endpoint
■ Basicauthentication
Nhưng chưa trả lời
■ Agentđang chậm hay nhanh? P99?
■ Tốnbao nhiêu tiền mỗi user/ngày?
■ Baonhiêu request fail, và loại lỗigì?
■ Câutrả lời có đúng không?
■ Khinào cần scale up?
Lưu ý: Không có monitoring, bạn chỉ biết agent hỏngkhi user phàn nàn . Với AI
agent,user thường không phàn nàn —họim lặng churn.
Giảngviên (VinUni) AICB· Monitoring 2026 6/ 67

---

### 3 Pillars of Observability + Profiles

Metrics
Đolường
Logs
Ghichép
Traces
Theodõi
Profiles
Phântích CPU
Bao nhiêu?
Bao lâu?
Latency, rate, cost
Gì xảy ra?
Input/output, event
Tại sao?
End-to-end flow
Tốn ở dòng
code nào?
Rare in AI
Metrics=số liệu aggregate (rẻ, alert).Logs=event chi tiết (đắt, debug).Traces=hành trình request (vừa phải,
root-cause).
Pillar thứ 4Profiles(CPU/memory) ít dùng cho AI vì bottleneck thường ở LLM API,
khôngcode local.
Giảngviên (VinUni) AICB· Monitoring 2026 7/ 67

---

### Cardinality — Tại Sao Metrics Đắt

Cardinality=số tổ hợp unique của cáclabel.
Ví dụ: metric llm_latency cólabels:
■ user_id: 100,000 giá trị
■ model: 4 giá trị
■ endpoint: 20 giá trị
■ status: 10 giá trị
Tổngseries = 100,000 × 4 × 20 × 10 = 8 × 107
series!
VớiPrometheus, mỗi series≈500bytes/15s →
∼40GB/giờ. Không khả thi.
Quy tắc cardinality
■ KHÔNGdùng user_id, request_id,
emaillàmmetric label
■ CÓdùng: model, env, feature, tier
■ High-cardinalitydata →vào logs
hoặc traces
■ Sampling1–10% cho AI workloads
Lưu ý: Sai cardinality là cách phổ biến nhất làmsập Prometheus và nhận bill
$40k/thángtừ Datadog không báo trước.
Giảngviên (VinUni) AICB· Monitoring 2026 8/ 67

---

### 3 Pillars Cùng Nhau — Một Ví Dụ Thực Tế

Kịch bản: Alertfire lúc 3h sáng: “P99 latency>8ssuốt 10 phút”.
1. Metricschothấy P99 đã tăng từ 2s→8strong 10 phút. Error rate vẫn 0%.
→ Biết có vấn đề, nhưng chưa biết vì sao.
2. Tracescho10 request chậm nhất: spanvector_search chiếm6.5s (bình thường 200ms).
→ Bottleneck tại retrieval, không phải LLM.
3. Logstạiservice retrieval: ``Pinecone request timeout after 6000ms'' bắtđầu từ 02:47.
→ Root cause: Pinecone có sự cố, cần chuyển sang fallback vector DB.
Metrics →phát hiện. Traces→localize. Logs →root cause. Thiếu 1 trong 3, MTTR sẽ kéo
dàitừ phút lên giờ.
Giảngviên (VinUni) AICB· Monitoring 2026 9/ 67

---

### Cost of Not Monitoring — 4 Rủi Ro

Agenttrảlờisai,khôngaibiết. Đếnkhipháthiệnthì
đãmất user.
Tokencosttăngdầnkhôngalert. Cuốithángbillgấp
5lần dự kiến.
Latency P95 tăng 10ms/tuần. 6 tuần sau: 2x chậm
hơn. Không baseline→khôngai để ý.
“Agent sai hôm qua.” Không log, không trace.
Khôngreproduce →khôngfix.
Lưu ý: Air Canada 2024: chatbot tư vấn sai chính sách, tòa buộc trả tiền theo câu
chatbot. Không monitoring=khôngphòng vệ.
Giảngviên (VinUni) AICB· Monitoring 2026 10 / 67

---

### SLI / SLO / SLA — Ngôn Ngữ Của Reliability

Thuật ngữ Định nghĩa Ví dụ cho agent
SLI ServiceLevelIndicator—1metric
đolường được
P95latency =2.3s
SLO Objective: mụctiêunộibộchoSLI P95 ≤ 3s trong 99.5% thời gian
(28ngày)
SLA Agreement: cam kết với khách
hàng,có phạt
99% uptime, nếu không sẽ re-
fund10%
Error Budget Dungsai cho phép SLO sailệch 100% − 99.5% = 0 .5% = 3.6
giờ/tháng
SLO chặt hơn SLA (buffer để không bao giờ breach SLA). Khi error budget còn nhiều→
đượcphép deploy risky. Hết budget→freeze,chỉ fix bug.
Giảngviên (VinUni) AICB· Monitoring 2026 11/ 67

---

### Error Budget Math — Bao Nhiêu Downtime Chấp Nhận?

SLO Downtime/tháng Downtime/tuần Downtime/ngày
99% 7.2giờ 1.68giờ 14.4phút
99.5% 3.6giờ 50.4phút 7.2phút
99.9% (3
nines)
43.2 phút 10.1 phút 1.44 phút
99.99% (4
nines)
4.32phút 1.01phút 8.6giây
99.999% (5
nines)
25.9giây 6.05giây 0.86giây
Lưu ý: Mỗi thêm 1 “nine” tốn gấp 10 lần tiền. AI agent thực tế→ SLO 99%–99.5% là đủ.
Đừnghứa 99.99% khi LLM API chỉ99.9%.
Giảngviên (VinUni) AICB· Monitoring 2026 12 / 67

---

### 4 Golden Signals + 2 Cho AI Agent

Google SRE — 4 Golden Signals
1. Latency—thời gian phản hồi
2. Traffic—request rate (QPS)
3. Errors—error rate
4. Saturation—tài nguyên còn bao nhiêu?
AI Agent cần thêm 2
5. Cost—$/request, $/user,token usage
6. Quality—hallucination rate, user CSAT,
groundednessscore
Agent có thể “up” (traffic OK, latency OK, error OK) nhưngtrả lời sai và đốt tiền. Đây là 2
failuremode riêng của AI mà monitoringtruyền thống bỏ qua.
Giảngviên (VinUni) AICB· Monitoring 2026 13 / 67

---

### RED vs USE — Hai Phương Pháp Observability

RED (request-centric)
■ Rate— requests/giây
■ Errors— error rate
■ Duration— latency P50/P95/P99
Perspective: user — tôi gửi request, được gì?
USE (resource-centric)
■ Utilization— tài nguyên dùng %
■ Saturation— có queue/chờ không?
■ Errors— lỗi của resource
Perspective: resource — LLM API, queue đang
làm gì?
Agentchậm(RED:DurationP95tăng) →debugbằngUSE(LLMratelimitutilization95%) →bịthrottle →upgrade
tierhoặc fallback.
Giảngviên (VinUni) AICB· Monitoring 2026 14 / 67

---

### 02

AI Metrics Deep Dive
AI agent cần metrics riêng: performance, quality, cost, reliability,
và drift — những thứ monitoring truyền thống không có

---

### Performance Metrics — Deep Dive

Metrics truyền thống
■ Latency—thời gian end-to-end
■ Throughput—requests/giây
■ Queue depth —backlog
■ Uptime—availability
AI-specific (mới)
■ TTFT—TimeToFirst Token
■ TPOT—TimePer Output Token
■ Tokens/sec—tốc độ generate
■ Context fill % —dùng bao nhiêu
window
Với streaming UI, user cảm nhậnTTFT, không phải total latency. TTFT 500ms→ nhanh kể
cảtổng 8s. TTFT3s →lagkể cả tổng 4s. Optimize TTFT trước total.
Giảngviên (VinUni) AICB· Monitoring 2026 15 / 67

---

### Percentile Math — Vì Sao P99 Quan Trọng

Bài toán: Agentcó P99 =5s,user chat 10 lượt.
Xác suất user gặp ≥ 1 lần > 5s:
P = 1 − 0.9910 ≈ 9.6%
■ 1/10user sẽ gặp lag rất tệ
■ Với1,000 user/ngày →96user bức xúc
■ Họsẽ là người tweet negative, churn,complain
Amazon Rule
“Every 100ms of latency cost them
1% of sales.”
→Optimize tail,khôngchỉaverage.
→P99, P99.9 là KPI chính thức tại
Amazon,Google, Meta.
Service có P99= X ms, user dùng N lượt→ khả năng gặp tail= 1 − 0.99N. Tail latency
compounds nhanh trongagenticworkflownhiềubước—5bước ×P99=P95củatoànbộ!
Giảngviên (VinUni) AICB· Monitoring 2026 16 / 67

---

### Percentile Latency — P50 vs P95 vs P99

P50= 800ms (nửa số requestnhanh hơn)P50
P95= 2.1s (95% request nhanhhơn)P95
P99= 5.3sP99
Lưu ý: Trung bình (average) ẩn giấu long tail. Nếu P50 là 800ms nhưng P99 là 5s,
nghĩalà 1 trên 100 user phải chờ rất lâu —và họ là người dễ churnnhất.
Giảngviên (VinUni) AICB· Monitoring 2026 17 / 67

---

### Quality Metrics — Kim Tự Tháp 4 Tầng

L4: Outcome Tasksuccess, revenue, retention
L3: User Signal Thumbsup/down, CSAT,follow-up
L2: LLM-as-Judge Relevance,faithfulness (RAGAS)
L1: Automated Heuristic Format,length, toxicity,PII leak
L1 rẻ, realtime nhưng không nói được quality thực. L4 là ground truth nhưng lag
hàngtuần. Productioncầncả 4 — L1/L2 đểalert, L3/L4 để confirm trends.
Giảngviên (VinUni) AICB· Monitoring 2026 18 / 67

---

### Hallucination — Phát Hiện Thế Nào?

Hallucination =agenttrả lời “rất tự tin” nhưngsai sự thật. Không có 1 metric duy nhất→cần
combo4 patterns:
Pattern 1: Groundedness (RAG)
■ Mỗiclaim trong output, check có trongretrieved
contextkhông
■ Tool: RAGASfaithfulness,TruLens
Pattern 2: Self-consistency
■ GọiLLM 3 lần với temp=0.7
■ Nếu3 câu trả lời mâu thuẫn→nghingờ
■ Cost 3× → dùngcho sample 1%
Pattern 3: Entity verification
■ Extractentities (tên, số, dates)
■ Cross-checkvới DB/API đáng tin
■ Chofinance, medical use cases
Pattern 4: User feedback loop
■ “Wasthis helpful?” button
■ Regenerateclick =tínhiệu hallucination
■ Signalchậm nhưng rẻ và thật
Lưu ý: Air Canada revisited: Chatbot tư vấn chính sách bereavement farekhông tồn tại.
NếucógroundednesscheckvớiactualpolicyDB →blockcâutrảlờitừđầu,tránhkiệntụng.
Giảngviên (VinUni) AICB· Monitoring 2026 19 / 67

---

### Cost Engineering — Công Thức Cốt Lõi

Cost per request khôngphải 1 con số đơn giản:
Costreq = Tin
106 · Pin
| {z }
inputcost
+ Tout
106 · Pout
| {z }
outputcost
+ Tcache
106 · Pcache
| {z }
cacheread
Ví dụ: Claude Sonnet 4.5 (2026)
■ Input: $3 / Mtokens
■ Output: $15 / Mtokens
■ Cachewrite: $3.75 /M
■ Cacheread: $0.30 /M (10x rẻ hơn input)
Request điển hình: RAG agent
■ System +docs: 8,000 tokens in
■ Userquery: 200 tokensin
■ Response: 500 tokens out
■ Cost = 8200 · 3
106 + 500 · 15
106
■ =$0.0246 +$0.0075 = $0.032/req
Với 100k requests/ngày, cost=$3,200/ngày = $96k/tháng. Nếu prompt cache hit 80% cho
system: giảm còn $1,100/ngày=tiếtkiệm $63k/tháng.
Giảngviên (VinUni) AICB· Monitoring 2026 20 / 67

---

### Cost Attribution — Tiền Đi Đâu?

Câu hỏi CFO luôn hỏi: “$50ktháng này,ai tốn?” — bạn phải attributeđược.
Dimension Tag gắn vào trace Dùng để...
Peruser user_id Biếtpower user,tính pricing
Perfeature feature="summary" Prioritizeoptimization
Permodel model="claude-sonnet-4-5"Sosánh cost/value các model
Pertenant tenant_id Multi-tenantbilling
Perenv env="prod" Táchdev/staging noise
Percohort plan="enterprise" Marginanalysis
Mọi LLM call phải có3 tags tối thiểu: user_id, feature, model. Thiếu 1 trong 3→khi CFO
hỏi,bạn không trả lời được, vàngân sách bị cắt.
Giảngviên (VinUni) AICB· Monitoring 2026 21 / 67

---

### 4 Cost Optimization Patterns

1. Prompt Caching
Cachesystemprompt +docstĩnh. Anthropic: 10x
rẻ hơn cacheread. → giảm 70% cost
2. Model Routing (Cascade)
Dễ →Haiku. Khó→Sonnet. Classifier nhẹ quyết
định. → 40–60% giảm cost
3. Semantic Cache
Querytươngtự →trảlờicached(embeddingsim-
ilarity >0.95). → Hit rate 20–40%
4. Batch API
Non-realtime(summaryđêm) →batchgiá 50%. →
50% offline work
Applycả 4 patterns: $96k/tháng→$22k/tháng(77% tiết kiệm). Đây làFinOps for AI —kỹ năng hot 2026.
Giảngviên (VinUni) AICB· Monitoring 2026 22 / 67

---

### Reliability Metrics — Error Taxonomy

“Error rate 5%” —nhưng loại lỗi gì? Không taxonomy→khôngfix được.
Loại lỗi Nguyên nhân Cách handle
LLMAPI 5xx Providerdown/rate limit Retry exponential backoff,fallback model
LLMtimeout Slowprovider,network Circuit breaker,clienttimeout <server
Toolcall failed ExternalAPI lỗi Retry,graceful degradation
Toolschema invalid LLM sinh JSON lỗi Re-promptvới error feedback
Guardrailblock Contentpolicy vi phạm Log +user-friendlymessage
Emptyresponse LLMrefuse/filter Alternateprompt, escalate to human
Contextoverflow Input >limit Truncate,summarize history
Track error_type fieldtrong mỗi log. Alert fire→biếtngay gọi ai (LLM provider? tool owner? prompt engineer?).
Giảngviên (VinUni) AICB· Monitoring 2026 23 / 67

---

### User-centric Metrics — Ngoài Kỹ Thuật

Engineering metrics xanh không có nghĩa là user happy. Cầnđo trực tiếp:
Explicit signals
■ Thumbs up/down —gắn vào mỗi response
■ CSAT survey—weekly sample
■ NPS—quarterly
■ Escalation to human —rate
→ Signal rõ, response rate thấp ( < 5%)
Implicit signals (quan trọng hơn)
■ Regenerate rate —user bấm “thử lại”
■ Session length —dùng lâu =hàilòng?
■ Follow-up rate —câu hỏi tiếp
■ Conversion—action sau chat
■ Return rate —quay lại trong 7 ngày
Họ thấy Regenerate rate làpredictor tốt nhất cho churn — hơn cả thumbs down. User
khôngbấm thumbs down, họ chỉ... rời đi.
Giảngviên (VinUni) AICB· Monitoring 2026 24 / 67

---

### Drift — Khi Data/Model Thay Đổi Âm Thầm

3 loại drift cần monitor:
■ Data drift —input distribution thay đổi (userhỏi kiểu mới)
■ Concept drift —mapping input→outputthay đổi (luật mới)
■ Model drift —provider update model, behavior đổi
Phát hiện bằng:
■ PopulationStability Index (PSI)
■ KL-divergencegiữa distributions
■ Embeddingdrift (cosine similarity)
PSI formula
PSI =
∑
i
(pi − qi) ln pi
qi
Interpret:
■ <0.1— stable
■ 0.1–0.25— mild drift
■ >0.25— significant, cần retrain
Lưu ý: Case2024: OpenAIsilentlyupdateGPT-4 →formatoutputđổi →nhiềupipelinesbreaksinsilence. Không
driftmonitoring =khôngbiết.
Giảngviên (VinUni) AICB· Monitoring 2026 25 / 67

---

### Metric Nào Cho Ai?

Stakeholder Quan tâm Metrics
Engineering Systemhealth, debug Latency P95/P99, error rate, tool call failure,
saturation
Product Userexperience CSAT,taskcompletion,hallucinationrate,re-
generaterate
Finance/ Ops Costcontrol Cost/day, tokens/request, cost by model, at-
tribution
Leadership ROIoverview Adoption rate, cost vs value, uptime, user
growth
Security/ Legal Compliance PIIleakrate,auditlogcompleteness,datare-
tention
Dashboardcho stakeholders phải nói bằngngôn ngữ business. “P95 = 2.1s”→“95%user nhận trả lời trong2s”.
Giảngviên (VinUni) AICB· Monitoring 2026 26 / 67

---

### 03

Structured Logging
Biến log thànhdata có thể query được — nền tảng cho debug
AI agent ở scale

---

### Unstructured vs Structured Log

# --- Unstructured: kho search, kho filter ---
# 2026-03-18 10:23:45 INFO Agent responded to query
# 2026-03-18 10:23:46 ERROR Tool call failed
# --- Structured JSON: de query, de aggregate ---
log_entry = {
"ts": "2026-03-18T10:23:45Z",
"level": "INFO",
"correlation_id": "req-abc123",
"user_id": "u_7842",
"event": "agent_response",
"latency_ms": 1250,
"tokens_in": 850, "tokens_out": 120,
"cost_usd": 0.0043,
"model": "claude-sonnet-4-5",
"feature": "summary"
}
Structured log cho phépfilter theo field, aggregate theo metric, correlate across
services—điều unstructured log không làm được.
Giảngviên (VinUni) AICB· Monitoring 2026 27 / 67

---

### Log Schema — 3 Tier Design

Tier 1: Required
Mỗilog entry phảicó:
■ ts(ISO8601)
■ level
(INFO/WARN/ERROR)
■ correlation_id
■ servicename
■ eventtype
Tier 2: Context
Nên có khiliên quan:
■ user_id(hashed)
■ session_id
■ feature
■ model
■ env
Tier 3: Payload
Event-specificmetrics:
■ latency_ms
■ tokens_in/out
■ cost_usd
■ error_type
■ tool_name
ViếtthànhPydanticmodelhoặcJSONSchema,validatetrướckhiemit. Nếumỗiservicelog
khácnhau →dashboardkhông build được.
Giảngviên (VinUni) AICB· Monitoring 2026 28 / 67

---

### Python structlog — Setup Chuẩn

import structlog, logging
structlog.configure(
processors=[
structlog.contextvars.merge_contextvars,
structlog.processors.add_log_level,
structlog.processors.TimeStamper(fmt= "iso", utc=True),
structlog.processors.StackInfoRenderer(),
structlog.processors.format_exc_info,
structlog.processors.JSONRenderer(),
],
wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
cache_logger_on_first_use=True,
)
log = structlog.get_logger()
log.info("agent_started", service= "rag-agent", version= "1.2.0")
# --> {"event":"agent_started","level":"info","timestamp":"..."}
Native JSON output, contextvars support, processor pipeline linh hoạt. Tiêu chuẩn
de-factocho Python production.
Giảngviên (VinUni) AICB· Monitoring 2026 29 / 67

---

### contextvars — Correlation ID Tự Động

from structlog.contextvars import bind_contextvars, clear_contextvars
import uuid
async def handle_request(request):
clear_contextvars()
bind_contextvars(
correlation_id= str(uuid.uuid4())[:8],
user_id=request.user_id, feature=request.feature,
)
# Tu day tro di, moi log.* tu dong co 3 fields nay
log.info("request_received", query_len= len(request.query))
result = await agent.run(request.query)
log.info("response_sent", latency_ms=result.latency)
return result
contextvars an toàn vớiasyncio — mỗi request có context riêng, không bị lẫn giữa
concurrentrequests.Giảngviên (VinUni) AICB· Monitoring 2026 30 / 67

---

### Correlation ID — Xuyên Suốt Services

Client API Gateway Agent RAG Service LLM Provider
X-Request-ID propagate propagate header
correlation_id = "req-abc123"
Mọilog entry đều có fieldnày→grep1 ID ra full journey
HTTPheader traceparent(W3CTraceContext) =correlationIDchuẩnquốctế. Mọi
frameworkhiện đại (FastAPI, Express) đều support.
Giảngviên (VinUni) AICB· Monitoring 2026 31 / 67

---

### PII Sanitization — Nên Log Gì Và Không

Nên log
■ Input đã sanitize (độdài, topic)
■ Outputsummary (không full text)
■ Toolcalls+ results (metadata)
■ Latency,tokens, cost
■ Errors+ stack traces
■ CorrelationID, hashed user ID
KHÔNG log
■ PII(tên, SĐT,CCCD, email)
■ Fullprompt chứa sensitive data
■ APIkeys, tokens, secrets
■ Creditcard, bank account
■ Fullraw user input
■ DEBUGverbose ở production
Lưu ý: LogPII =viphạmGDPR,PDPA,CCPA.Phạtcóthể 4% revenue toàn cầu (GDPR).Sanitize trướckhilog,
khôngphải sau khi bị audit.
Giảngviên (VinUni) AICB· Monitoring 2026 32 / 67

---

### PII Scrubbing — Regex + Presidio

# --- Cach 1: regex nhanh cho common patterns ---
import re
PII_PATTERNS = {
"email": r "[\w\.-]+@[\w\.-]+\.\w+",
"phone_vn": r "(\+84|0)\d{9,10}",
"cccd": r "\b\d{12}\b",
"credit_card": r "\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
}
def scrub(text):
for n, p in PII_PATTERNS.items():
text = re.sub(p, f "[REDACTED_{n.upper()}]", text)
return text
# --- Cach 2: Microsoft Presidio (NER-based, robust) ---
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
analyzer, anonymizer = AnalyzerEngine(), AnonymizerEngine()
results = analyzer.analyze(text=user_input, language= "en")
safe = anonymizer.anonymize(text=user_input, analyzer_results=results).text
Regex cho format cố định (email, phone). Presidio cho NER (tên, địa chỉ) — robust
hơnnhưng chậm 10x.
Giảngviên (VinUni) AICB· Monitoring 2026 33 / 67

---

### Log Levels — Khi Nào Dùng

Level Khi nào dùng Ví dụ Prod?
DEBUG Devonly,rất chi tiết Fullprompt, intermediate state Không(sample1%)
INFO Normalflow,milestone events Request received, response
sent
Có
WARN Degradednhưng vẫn hoạt động Retry succeeded,fallback used Có
ERROR Failed,cần attention Toolcall timeout, LLM error Có,alert
CRITICAL System-levelfailure DB unreachable, all models
down
Có,page
Production chạyINFO. Debug cụ thể: tạm bật DEBUG cho request ID đó, xong tắt. Không để DEBUG luôn-on→
logvolume 100x, bill lên trời.
Giảngviên (VinUni) AICB· Monitoring 2026 34 / 67

---

### Log Sampling — Khi Volume Quá Cao

Vấn đề: 100krequests/ngày ×10log entries/request =1Mentries/ngày. Elastic/Datadogtính
$0.10/1kentries →$100/ngàychỉ riêng log. Không scalable.
Strategies
■ Head sampling —quyết định sample
ngaykhi trace bắt đầu (rẻ, cóthể miss
errors)
■ Tail sampling—quyết định sau khi trace
xong(đắt, giữ được 100% errors)
■ Reservoir sampling —giữ N mẫu
uniform
Strategy điển hình cho AI agent
■ 100%ERROR và WARN
■ 10%INFO (cho normal requests)
■ 1%DEBUG (cho deep debug)
■ 100%requests >10s(tail-sampling on
latency)
■ 100%cost >$1/request(outliers)
Sampling giảm cost 10–100x, nhưng mất visibility vào normal pattern. Giữ 100% errors là
non-negotiable— đó là data debug quantrọng nhất.
Giảngviên (VinUni) AICB· Monitoring 2026 35 / 67

---

### Log Aggregation Stacks

Stack Components Khi nào dùng Cost/tier
ELK Elasticsearch, Logstash,
Kibana
Full-text search mạnh, com-
plexqueries
Tự host,
OSS
Loki Loki,Promtail, Grafana Label-based (giống
Prometheus),rẻ
Tự host,
OSS
Datadog Logs SaaS Setup nhanh, alert tốt, đắt ở
scale
$0.10/GB
CloudWatch AWSnative Đãở AWS,tích hợp IAM $0.50/GB in-
gest
BigQuery GCPDW AnalyticsSQL,longretention $0.02/GB
scan
Langfuse tự là log store cho LLM calls+ SaaS free tier. Dev local→ stdout JSON+ jq là
đủ. Scale up mớicần ELK/Loki.
Giảngviên (VinUni) AICB· Monitoring 2026 36 / 67

---

### Audit Log — Tách Biệt Với App Log

Audit log =record who did what when chocompliance, legal, security.
App log
■ Mụcđích: debug, performance
■ Retention: 30–90 ngày
■ Cóthể sample
■ Cóthể sửa/xóa
■ Truycập: dev team
Audit log
■ Mụcđích: compliance, forensics
■ Retention: 2–7 năm (tùyngành)
■ Không sample —100%
■ Append-only—không sửa được
■ Truycập: restricted (complianceofficer)
Lưu ý: Sailầmphổbiến: trộnauditlogvàoapplog →khicầninvestigatebịthiếudata. Tách
riêngtừ ngày đầu: S3 bucket với Object Lock, hoặcdedicated audit service.
Giảngviên (VinUni) AICB· Monitoring 2026 37 / 67

---

### 04

Distributed Tracing
Trace cho biết toàn bộ hành trình của 1 request qua nhiều bước
— công cụ số một để debug AI agent pipeline

---

### Trace, Span, Context — Terminology

Khái niệm cốt lõi
■ Trace—toàn bộ request end-to-end, có
trace_id duynhất
■ Span—1 đơn vị công việc trongtrace,
có span_id, parent_span_id
■ Context propagation —cơ chế truyền
trace_id quaboundaries (HTTP
headers,queue messages)
Span có gì?
■ name—tên operation (e.g.llm.generate)
■ start_time, duration
■ attributes —key-value (model, tokens)
■ status—OK / ERROR
■ events—logs gắn vào span
■ links—related spans (e.g. retry)
Trace = cây. Root span là entry point (HTTP request). Child spans là các bước con (RAG
retrieve,LLM call, tool call). Nhìn cây biết bottleneck.
Giảngviên (VinUni) AICB· Monitoring 2026 38 / 67

---

### Trace Là Gì — Waterfall View

0ms 2500ms
Total Request: 2500ms
Parse: 50ms Retrieval: 600ms LLM Call: 1400ms
Embed: 200ms Search: 350ms Generate: 1200ms Post: 100ms
Mỗihàng ngang là 1span. Tất cả spanscủa 1 request tạo thành 1trace. Nhìn trace biếtngay
bottleneck ở đâu.
Giảngviên (VinUni) AICB· Monitoring 2026 39 / 67

---

### OpenTelemetry — Tiêu Chuẩn Mở

OpenTelemetry (OTel) =CNCFgraduated project (2024), vendor-neutral tiêu chuẩncho
observability.
OTel gồm 3 phần
■ API—interface để instrument code
(ngônngữ-agnostic)
■ SDK—implementation cho ngôn ngữ cụ
thể(Python, Go, Java...)
■ Collector—receive, process, export
datađến backend (Jaeger,Tempo,
Datadog...)
Vì sao quan trọng
■ Instrument 1 lần —switch backend tự do
(khỏivendor lock-in)
■ Auto-instrumentationcho FastAPI,
requests,SQLAlchemy...
■ 2024: OTelphát hànhGenAI Semantic
ConventionschoLLM tracing
Học OTel một lần→ dùng được Langfuse, Datadog, Jaeger, New Relic đều được. Tất cả
đềuaccept OTLP protocol.
Giảngviên (VinUni) AICB· Monitoring 2026 40 / 67

---

### OpenTelemetry Python — Manual Instrumentation

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# Setup 1 lan o startup
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer( "agent-service")
# Instrument function
def rag_retrieve(query):
with tracer.start_as_current_span("rag.retrieve") as span:
span.set_attribute("rag.query_len", len(query))
results = vector_db.search(query)
span.set_attribute("rag.result_count", len(results))
return results
with tracer.start_as_current_span(...) tự động set parent-child relationship.
Attributes =metadatađể filter/search trace sau.
Giảngviên (VinUni) AICB· Monitoring 2026 41 / 67

---

### OTel GenAI Semantic Conventions

Tiêu chuẩn từ 2024: mọiLLM trace nêndùngcác attribute names này→toolvendor-agnostic hiểu được.
Attribute Ý nghĩa
gen_ai.system Provider: “anthropic”, “openai”, “google”
gen_ai.request.model Modelname: “claude-sonnet-4-5”
gen_ai.request.temperature Samplingtemp
gen_ai.request.max_tokens Maxtokens cap
gen_ai.usage.input_tokens Inputtokens
gen_ai.usage.output_tokens Outputtokens
gen_ai.response.finish_reasons “stop”,“length”, “tool_use”
gen_ai.operation.name “chat”,“completion”, “embeddings”
Dùng namespacegen_ai.* →dashboard queries reusable. Tránh custom names nhưmy_model — không interop-
erable.
Giảngviên (VinUni) AICB· Monitoring 2026 42 / 67

---

### Auto-instrumentation — Ít Code Hơn

# --- Install ---
# pip install opentelemetry-distro opentelemetry-exporter-otlp \
# opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-anthropic
# --- Run (khong can sua code) ---
# opentelemetry-instrument --traces_exporter otlp uvicorn app:main
# --- app.py: code thong thuong, khong co OTel boilerplate ---
from fastapi import FastAPI
from anthropic import Anthropic
app = FastAPI(); client = Anthropic()
@app.post("/chat")
async def chat(msg: str):
r = client.messages.create(model= "claude-sonnet-4-5",
max_tokens=1024, messages=[{ "role":"user","content":msg}])
return {"reply": r.content[0].text}
# Moi HTTP request + LLM call tu dong tao span
Nhanhnhưngítkiểmsoát. Productionhybrid: autochoHTTP/DB,manualchobusi-
nesslogic.
Giảngviên (VinUni) AICB· Monitoring 2026 43 / 67

---

### Trace Cho Agent Pipeline

User
Request
Input
Guards
Agent
Router
RAG
Retrieve
LLM
Generate Response
20ms 50ms 600ms 1400ms 30ms
LLM Generate chiếm 67% latency. Muốn tối ưu→ bắt đầutừ LLM call: model nhỏ
hơn,prompt ngắn hơn, streaming hoặc parallelizeRAG với LLM warmup.
Giảngviên (VinUni) AICB· Monitoring 2026 44 / 67

---

### 4 Bottleneck Patterns Trong Trace

Pattern 1: Sequential dependency
■ A →B →C,tổng =sum
■ Fix: parallelize A, Bnếu không phụ thuộc
Pattern 2: N+1 queries
■ Loopgọi API/DB nhiều lần
■ Trace: nhiều span ngắncùng tên
■ Fix: batch API, hoặcpre-fetch
Pattern 3: Waiting (không phải CPU)
■ Spandài nhưng CPU idle
■ LLMAPI, DB, network
■ Fix: parallelize, cache, timeout
Pattern 4: Retry storm
■ Nhiềuspan retry trong 1 trace
■ Backoffquá ngắn, không jitter
■ Fix: exponential backoff,circuitbreaker
Nhìnspandàinhất →hỏi“cóparallelizeđượckhông?”. Nhìnnhiềuspanngắnlặp →hỏi“có
batchđược không?”. Đólà 80% tối ưu hóa.
Giảngviên (VinUni) AICB· Monitoring 2026 45 / 67

---

### Tool Comparison — 4 Lựa Chọn Hàng Đầu

Tool Strength Best for Pricing OSS?
Langfuse Full stack: tracing,
eval,prompts, cost
Self-host, framework-
agnostic
Freetier,cloudpaid Yes(MIT)
LangSmith TightLangChain,play-
ground,datasets
LangChainusers Free tier, seat-
based
No(SaaS)
Helicone Proxy approach, 0
codechange
Rapidintegration Free tier, usage-
based
Yes(Apache)
Arize Phoenix OpenTelemetry-
native,OSS
Research, eval work-
flows
FreeOSS Yes(Apache)
Chọn Langfuse — open source, free cloud tier, framework-agnostic, đã support OTel GenAI conventions. UI tốt
nhấtcho LLM-specific features.
Giảngviên (VinUni) AICB· Monitoring 2026 46 / 67

---

### Langfuse Integration — 5 Dòng Code

from langfuse.decorators import observe, langfuse_context
from anthropic import Anthropic
client = Anthropic()
@observe()
def rag_agent(query: str, user_id: str):
langfuse_context.update_current_trace(user_id=user_id, tags=[ "prod","rag"])
docs = retrieve(query)
response = client.messages.create(
model= "claude-sonnet-4-5", max_tokens=1024,
messages=[{ "role":"user","content":f"Docs: {docs}\n\nQ: {query}"}])
langfuse_context.update_current_observation(
metadata={ "doc_count": len(docs)},
usage_details={ "input": response.usage.input_tokens,
"output": response.usage.output_tokens})
return response.content[0].text
Latency, input/output, cost (model pricing built-in), trace waterfall. Xem ngay trên
Langfusedashboard.
Giảngviên (VinUni) AICB· Monitoring 2026 47 / 67

---

### Case Debug Thực Tế — Dùng Trace Để Tìm Bottleneck

Vấn đề: Userphàn nàn agent chậm “đôikhi”. Metrics nói P95=2.3s,OK. P99 =12s— không
OK.
1. Filter trace theo duration > 10strong24h qua →được47 traces
2. Nhóm theo feature tag →42/47thuộc feature "legal_qa"
3. Mở waterfall 1trace: LLM span=800ms(OK), RAG span=10.2s(!)
4. Drill vào RAG span: sub-span vector_search =9.8svới query length 4,200 tokens
5. Root cause: userdán full document vào query→embeddinggọi với input lớn→chậm
6. Fix: truncatequery to 500 tokens beforeembedding, thêm warning cho user
Không có trace→chỉ biết “đôi khi chậm”, không biết bước nào, không biết pattern nào. Với
trace: 10 phút từbug report →rootcause.
Giảngviên (VinUni) AICB· Monitoring 2026 48 / 67

---

### 05

SLO-based Alerting & Dash-
board
Metrics và traces chỉ có giá trị nếu có người nhìn — học design
alert chất lượng dựa trên SLO

---

### Symptom vs Cause — Alert Về Cái Gì?

Cause-based (sai)
Alertvề nguyên nhân kỹ thuật:
■ CPU >80%
■ RAM >90%
■ Disk >85%
■ LLMAPI retry count>5
Cause cao nhưng user không bị ảnh hưởng →
false positive. Ignore dần.
Symptom-based (đúng)
Alertvề impact tới user:
■ P95latency >SLO
■ Errorrate >1%
■ Cost/hour >budget
■ Hallucinationrate spike
Chỉ alert khi user thực sự bị ảnh hưởng. Ít false
positive.
“Page on symptoms, not causes.” Causealerts chỉ là supplementary infođể debug sau khi symptom alertfire.
Giảngviên (VinUni) AICB· Monitoring 2026 49 / 67

---

### Multi-Window Multi-Burn-Rate Alerting

Vấn đề: Alertđơn giản “error rate>1%trong 5 phút”→firequá nhanh (noise) hoặc quá chậm
(missincident). Giải pháp của Google: kếthợp 2 windows với 2burn rates:
Severity Short window Long window Burn rate (vs SLO)
Page(critical) 5 phút 1giờ 14.4x
Ticket(warn) 30 phút 6giờ 6x
Ý nghĩa
“14.4x burn rate”: nếuerror giữ mức này,tháng sẽ burn hết error budgettrong 2 ngày thay vì
30.
Alertfirekhi cả 2 window cùngvượtthreshold. Shortwindow →reactnhanhvớispikethực.
Longwindow →filternoise ngắn. GoogleSRE WorkbookChapter 5.
Giảngviên (VinUni) AICB· Monitoring 2026 50 / 67

---

### Alert Anatomy — Alert Tốt Có Gì?

Template cho mỗi alert:
■ Title rõ ràng: “[P1] Agent P95 latency > 5s cho feature=summary ”
■ Severity: P1(page ngay) / P2 (trong giờhành chính) / P3 (ticket)
■ Impact statement: “5%user đang bị chậm>5s”
■ Current value: “P95 =6.3s,bình thường 1.8s, threshold 5s”
■ Dashboard link: pre-filteredvới feature tag, last 1h
■ Trace link: top10 traces chậm nhất trongwindow
■ Runbook link: playbookfix step-by-step
■ On-call owner: team/ngườichịu trách nhiệm
Lưu ý: Alert không có runbook= alert không thể xử lý lúc 3h sáng. Viết runbook làmột
phầncủawork “tạo alert”, không phảinice-to-have.
Giảngviên (VinUni) AICB· Monitoring 2026 51 / 67

---

### Alert Rules Cho AI Agent — Bộ Tối Thiểu

Metric Threshold Severity Channel + Action
LatencyP95 >5s,30 phút P2Warning Slack,investigate trace
Errorrate >5%,5 phút P1Critical Slack +PagerDuty,rollback
Hourlycost >$50(budget ×2) P2Warning Email,check users/features
Dailycost >dailybudget P1Critical Email +SMS,kill switch
Toolcall failure >10%,15 phút P2Warning Slack,check tool provider
Hallucinationrate >baseline +2σ P2Warning Slack,review outputs
Uptime <99%,1 giờ P1Critical PagerDuty,incident response
Alertphải actionable. Không biết phảilàm gì→redesignhoặc bỏ. Alertnào không fire 90 ngày→bỏ.
Giảngviên (VinUni) AICB· Monitoring 2026 52 / 67

---

### Alert Fatigue — Kẻ Giết Hệ Thống Alert

Alert fatigue xảy ra khi
■ quánhiều alerts không quan trọng
■ nhậnalert 24/7, ngay cả đêm
■ mọingười bắt đầu ignore
■ alertthật bị lẫn trong noise
■ teammất tin tưởng vào hệ thống
Cách tránh
■ chỉalert khi cầnhành động ngay
■ phânseverity rõ ràng (P1/P2/P3)
■ routeđúng người, đúng channel
■ reviewvà tuning alerts hàng tuần
■ auto-resolvekhi metric recovery
■ deduptrong window
Lưu ý: Nếuteamignorealertsthườngxuyên,hệthốngalertingđang tệ hơn không
có alert —alert thật sẽ bị miss. Ít alert chất lượngtốt hơn nhiều alert vô nghĩa.
Giảngviên (VinUni) AICB· Monitoring 2026 53 / 67

---

### Dashboard Design — 3 Layers

Layer 1: Overview — Health status, uptime, key alerts
Layer 2: Detail — 4 golden signals + Cost + Quality
Layer 3: Drill-down — Individual traces, log search, root cause
Choleadership
Choengineering
Chodebugging
Mỗi stakeholder chỉ cần nhìn 1 layer. Leadership cần overview, không cần trace.
Engineer cần drill-down, không cần revenue chart. Cùng 1 dashboard cho tất cả→
khôngai nhìn.
Giảngviên (VinUni) AICB· Monitoring 2026 54 / 67

---

### Dashboard Layer 2 — Bố Cục Chuẩn

Latency P50/P95/P99
time-series
Traffic (QPS)
time-series
Error rate %
time-series+ breakdown
Cost $/hour
cumulative+ forecast
Tokens in/out
stacked
Hallucination %
sampled,weekly
Nhiều panel hơn→ không ai đọc. Giới hạn 6 panels ở layer 2→ nhìn 5 giây biết
healthstatus. Muốn chitiết hơn→clickvào layer 3.
Giảngviên (VinUni) AICB· Monitoring 2026 55 / 67

---

### Dashboard Tools Landscape 2026

Opensource, powerful.
Kết nối mọi data source
(Prom, Loki, Cloud-
Watch).
Khi nào: team có infra
ops,muốn kiểm soát
All-in-oneSaaS.
Setup nhanh, alerting tốt,
đắtở scale.
Khi nào: cần nhanh, có
budget,muốn 1 tool
LLM-native hoặc Python
custom.
Full control, dễ cus-
tomize.
Khi nào: AI agent MVP,
demo,PoC
Lưu ý: Cho lab: Langfuse dashboard đã đủ cho MVP. Đừng dành thời gian build
Grafanacustom trước khi có đủ data— YAGNIprinciple.
Giảngviên (VinUni) AICB· Monitoring 2026 56 / 67

---

### Dashboard Anti-patterns — 5 Điều Nên Tránh

1. “Wall of metrics” —30 panels, không ai nhìn hết. Giới hạn 6–8panels/layer.
2. Time range mặc định quá dài —default 1 giờcho ops dashboard,không phải 1tháng (che
mấtspike)
3. Không có baseline/threshold line —nhìn số P95=2.1skhông biết tốt hay xấu. Luôn vẽ
đườngSLO lên chart.
4. Metric không có đơn vị/context —“Cost: 1250” làgì? USD? ngày? Luôn label đầy đủ.
5. Không auto-refresh —dashboard cần realtime (15–30s refresh)cho ops. Cho monthly
reportthì khác.
Đưadashboardchongườikhôngtrongteamxem30giây →họcónóiđược“hệthốngđang
OK”hay “đang có vấn đề ởX” không? Nếukhông, redesign.
Giảngviên (VinUni) AICB· Monitoring 2026 57 / 67

---

### 06

Tools Landscape & Case Studies
Chọn tool đúng tiết kiệm tháng setup. Học từ case thực: Notion
AI, Replit, và 7 anti-patterns từ industry

---

### LLM Observability Landscape 2026

Category Leader 2026 Strength Watch
LLM-native Langfuse,LangSmith Prompt, eval, cost Helicone, Phoenix
APM truyền
thống
Datadog,New Relic Infra + app + AI Honeycomb, Light-
step
OSSself-host Jaeger,Tempo,Loki Zero vendor lock SigNoz
Cost-focused Helicone,OpenMeter Tokenaccounting Vellum
Eval-focused Arize Phoenix, Pa-
tronus
Quality& drift Galileo
Converge: APM truyền thống (Datadog) add LLM features. LLM-native (Langfuse) add infra
tracing. Trong12 thángtới, OpenTelemetry GenAI semconv thànhchuẩn chung.
Giảngviên (VinUni) AICB· Monitoring 2026 58 / 67

---

### Decision Framework — Chọn Tool Thế Nào?

Q1: Team size?
■ 1–5: SaaS, free tier
■ 5–50: SaaS paid
■ 50+: Hybrid / self-host
Q2: Compliance?
■ HIPAA/PCI:self-host
■ GDPR:EU region SaaS
■ None: bất kỳ
Q3: Existing stack?
■ Datadog: stay,addAI addon
■ LangChain: LangSmith
■ Agnostic: Langfuse
Q4: Budget/month?
■ $0: Langfuse cloud free
■ $100–500: LangSmith/Helicone
■ $500+: Datadog full stack
Q5: Skill set?
■ Python-heavy: Langfuse
■ Infraops: Grafana
■ Non-dev: Datadog
Q6: Evaluation?
■ Qualitycần: Phoenix,
LangSmith
■ Costonly: Helicone
■ Fullstack: Langfuse
Không có “best tool”. Có best toolcho team + use case + budget của bạn . Đừng copy
stackcủa FAANG— họ cóinfra team 50 người.
Giảngviên (VinUni) AICB· Monitoring 2026 59 / 67

---

### Case Study 1 — Notion AI Cost Optimization

Bối cảnh: NotionAI phục vụ hàng triệu uservới nhiều features (summary,Q&A, writing assist).
CostOpenAI ban đầu∼30%revenue. Monitoring insight:
■ 70%queries là “summarize” với prompt giốngnhau
■ 15%user chiếm 60% cost (power usersvới doc dài)
■ Regeneraterate cao ở feature “writing assist”
Actions taken (theo thứ tự ROI):
1. Promptcache cho system prompt (tất cảfeatures)→giảm40% input cost
2. Route“summary” qua model nhỏ hơn (Haikutier)→giảm60% cost cho feature này
3. Per-userrate limit cho free tier→limitabuse power users
4. Improveprompt cho “writing assist”→giảmregenerate 35%
Total cost / MAU giảm58% trong 3 tháng, không giảm quality metrics. Điều làm được vì có
monitoringchi tiết theo feature + user+ model.
Giảngviên (VinUni) AICB· Monitoring 2026 60 / 67

---

### Case Study 2 — Replit Quality Debugging

Bối cảnh: ReplitAI code assistant, user báo “suggestionsbị tệ hơn tuần trước”. Engineering
metricsđều xanh. Monitoring insight:
■ Regeneraterate tăng từ 12%→23%trong 2 tuần (implicit signal!)
■ Thumbs-downrate tăng chậm hơn (user ítbấm)
■ Đặcbiệt cho ngôn ngữpythonvà javascript
Investigation (bằng trace):
■ Filtertrace cho regenerate cases→contexttruncation happening
■ Thayđổi tokenizer version tuần trước→đếmtokens khác 10%
■ Truncationthreshold không được update→cutoffgiữa câu
Reverttokenizer,thêmintegrationtestchotokencounting. Lesson: implicit signals (regen-
erate)là early warning, explicit signals (thumbsdown) quá chậm. Cả 2 đều cần.
Giảngviên (VinUni) AICB· Monitoring 2026 61 / 67

---

### 7 Anti-patterns Từ Industry

1. “We’ll add monitoring later” —later =never. Add ngaytừ MVP.
2. Log full prompts và responses —vi phạm GDPR, storage bill lêntrời. Sanitize +sample.
3. Alert trên mọi metric “quan trọng” —50 alerts →alertfatigue →ignore.
4. Không có runbook —alert fire lúc 3h sáng, engineertrẻ lost, escalate lên senior.
5. Monitoring dev ̸= prod config —prod có issue không reproduce đượcvì dev khác setup.
6. Chỉ đo performance, quên cost —đến cuối tháng mới biết đốttiền.
7. Trust vendor mặc định —LangChain default telemetry có thểlog sensitive data. Đọcdocs
trướckhi deploy.
Lưu ý: Anti-pattern#1làphổbiếnnhấtvàtaihạinhất. Monitoringkhôngphảilàfeaturephụ
→làphần corecủaproduction system, ngang với authentication.
Giảngviên (VinUni) AICB· Monitoring 2026 62 / 67

---

### 07

Lab 13 & Closing
Monitoring đầy đủ cho agent: biết nó chạy thế nào mà không cần
hỏi user, và có blueprint bàn giao được

---

### Lab 13: Monitoring Blueprint Cho Agent

Gắn monitoring stack đầy đủ vào deployed agent từ Day 12: structured logging +
tracing+ dashboard + SLO-based alerts, vớiblueprint document bàn giao được.
Phase A: Instrumentation (30 phút)
1. SetupLangfuse project (free cloud tier), lấyAPI keys
2. Addstructlog cho structured JSON logging+correlationID với contextvars
3. IntegrateLangfuse @observe() decoratorcho 3 functions chính
4. Addtags: user_id, feature, model, env
Phase B: Dashboard + Alerts (30 phút)
5. DefineSLO: P95 latency,errorrate, daily cost budget
6. Builddashboard Layer 2 (6 panels tốithiểu)
7. Configure3 alert rules với runbook links
Phase C: Validation (30 phút)
8. Gửi10–20 requests variety→checktraces xuất hiện
9. Inject1 failure (bad prompt)→verifyalert fire
10. Viếtblueprint document (1 trang: SLO, architecture, playbook)
Giảngviên (VinUni) AICB· Monitoring 2026 63 / 67

---

### Lab 13 Troubleshooting — Lỗi Thường Gặp

Triệu chứng Cách xử lý
TracekhôngxuấthiệnởLangfuse Check API key envvar,network, bật LANGFUSE_DEBUG=true
Costkhông được track Model name sai (phải khớp Langfuse pricing DB) hoặc thiếu
usage_details
Correlation ID không propagate
quaasync
Dùng contextvars; kiểm traclear_contextvars ở đầu mỗi re-
quest
PIIleak vào log dù đãscrub Checkorderprocessors: scrubberphảichạy trướcJSONRen-
derer
Alertfire nhưng không Slack Checkwebhook URL, quota rate limit,severity routing rules
Dashboardtrống dù có traces Timerange filter,tag filter,hoặc data source chưa kếtnối
Bật DEBUGcho langfusevà opentelemetrylogger →thấytraceexportrequest/response,tìmravấnđềtrong5phút.
Giảngviên (VinUni) AICB· Monitoring 2026 64 / 67

---

### Blueprint Rubric — Chấm Điểm Deliverable

Logging & Tracing (40%)
■ StructuredJSON logs (10)
■ CorrelationID propagate (10)
■ PIIsanitized (10)
■ 10+Langfuse traces (10)
Dashboard & Alerts (40%)
■ 6+panels Layer 2 (15)
■ SLOdefined (5)
■ 3alert rules với runbook (15)
■ Screenshotcó data (5)
Blueprint document (20%)
■ SLOtable (5)
■ Architecturediagram (5)
■ Alertplaybook (5)
■ Cost& scaling plan (5)
Điểm bonus (+10)
■ Costoptimization (prompt cache)
■ Qualitymetric (heuristic-based)
■ OTelauto-instrumentHTTP
Giảngviên (VinUni) AICB· Monitoring 2026 65 / 67

---

### Tổng kết — Key Takeaways

Những ý chính cần nhớ trướckhi sang bài tiếp theo
1 3 pillars + 2 extras. Metrics,Logs, Traces + Costvà Qualityriêngcho AI.
2 SLO-driven, symptom-based alerting. Alertkhi user bị ảnh hưởng, luôncó runbook.
3 OpenTelemetry + FinOps. Instrument 1 lần; 4 cost patterns (cache/routing/semantic/batch)
giảm70%.
Giảngviên (VinUni) AICB· Monitoring 2026 65 / 67

---

### Tiếp theo & Bài tập

AI Evaluation & Benchmarking
“Sếp hỏi: AI agent tốt hơn ChatGPT
bao nhiêu? Bạn nói sao nếu không
có benchmark? Monitoring đo đang
hoạt động thế nào , evaluation đo có
tốt không. ”
■ Chuẩnbị: 10 câuhỏi mẫu với
expectedanswers cho agent,
covercác edge cases
■ Đọctrước: RAGAS
documentation— faithfulness,
answer_relevancy,
context_precision (20phút)
■ Suynghĩ: quality metricnào
quantrọng nhất cho use case
củabạn? Vì sao?
Giảngviên (VinUni) AICB· Monitoring 2026 66 / 67

---

### Tài Liệu Tham Khảo

1. GoogleSRE Workbook, Alerting on SLOs —sre.google/workbook. Multi-window multi-burn-rate
alerting,error budget.
2. Langfuse, Open Source LLM Observability —langfuse.com. Tracing,cost tracking, prompt
management,eval.
3. LangSmithDocumentation — docs.smith.langchain.com. Tracing,evaluation, datasets, monitoring.
4. OpenTelemetry,GenAI Semantic Conventions —opentelemetry.io/docs/specs/semconv/gen-ai.
Vendor-neutralstandard cho LLM tracing.
5. MicrosoftPresidio — microsoft.github.io/presidio. PII detection & anonymization SDK.
6. CharityMajors, Observability Engineering (O’Reilly2022) — quyển sách nềntảng về observability hiện
đại.
7. Anthropic, Prompt Caching Best Practices —docs.anthropic.com/prompt-caching. Giảm 70%cost.
Giảngviên (VinUni) AICB· Monitoring 2026 67 / 67

---

### Hỏi & Đáp

Monitoring tốt nghĩa là bạn biết agent có vấn đề trước khi user
phàn nàn — và có đủ data để fix trong phút , không phải giờ.