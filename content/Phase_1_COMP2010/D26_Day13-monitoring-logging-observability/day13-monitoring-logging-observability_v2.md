# day13 monitoring logging observability v2

**File gốc:** `Phase_1_COMP2010\D26_Day13-monitoring-logging-observability\day13-monitoring-logging-observability_v2.md`

---

### Monitoring, Logging & Observability

AICB-P1· Ngày 13 · Biếtagent đang chạy thế nào trướckhi user phàn nàn
TênGiảng Viên
VinUniversity · Phase 1 · 2026

---

### “Agent bạn deploy hôm Day 12 chạy ngon.

3 ngày sau: latency tăng gấp đôi, cost
tăng 300 phần trăm, và 1 trên 20 câu trả
lời là bịa. Bạn biết những điều này khi
nào? — Khi user phàn nàn. Đó là cách
tệ nhất, và đắt nhất, để phát hiện vấn đề.”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### NộiDung Bài Học

1. Vìsao agent cần observability
2. 3pillars + pillar thứ 4
3. AI-specificmetrics
4. Structuredlogging
5. Distributedtracing cho agent
6. Bộcông cụ LLM-observability 2026
7. Productionstack: Prometheus +Grafana
8. Dashboarddesign
9. Alerting& SLO
10. Costmonitoring & optimization
11. Debug1 incident bằng trace
12. Humanfeedback & online eval
13. Privacy& compliance khi logging
14. Checklist,Lab 13 & tổng kết
Giảngviên (VinUni) AICB· Monitoring 2026 1/ 96

---

### MụcTiêuNgày 13 (Bloom’sTaxonomy)

■ Remember—liệt kê3pillars (metrics,logs, traces) +pillarthứ 4(continuouseval) và 6
nhómAI-specific metrics
■ Understand—giải thích vì saoP99quan trọng hơn average,và SLO khác SLA thếnào
■ Apply—implement structuredlogging (JSON+ correlation ID + PIIredaction) cho agent
đangdeploy
■ Analyze—đọc tracewaterfall vàxác định bottleneck trong agentpipeline nhiều bước
■ Evaluate—so sánh Langfuse / LangSmith/ Phoenix / Helicone cho usecase cụ thể
■ Create—thiết kếmonitoringblueprint vớiSLO, alert rules (symptom-based) và
dashboard3 layers
Giảngviên (VinUni) AICB· Monitoring 2026 2/ 96

---

### DeliverableCuối Ngày

Agentcó observability đầy đủ: bạn biết nó chạy thếnào màkhôngcần hỏi user.
■ Structuredlogging pipeline: JSON,correlation ID, input/output đãredactPII
■ Tracing: Langfuse (hoặc backendzero-key) connected,≥ 10traces
■ Dashboard: latency P50/95/99 +TTFT,cost/ngày,error rate, token usage,tool-call
success
■ ≥ 3alertrules →Slack;1 SLO + error budget; 1incident note đọc từ trace
Giảngviên (VinUni) AICB· Monitoring 2026 3/ 96

---

### 01

Vì Sao Agent Cần Observability
“It works” không đủ cho production — cần biết nó chạy TỐT đến
đâu, chậm ở đâu, tốn bao nhiêu, và khi nào sắp hỏng

---

### TừArtifact Day 12 Sang ProductionReality

Day12 đã làm được
■ Agentdeployed trên cloud
■ PublicURL hoạt động
■ Healthcheck endpoint
■ Basicauthentication
Nhưngchưa trả lời được
■ Agentđang chậm hay nhanh?
■ Tốnbao nhiêu tiền mỗi ngày?
■ Baonhiêu request fail (hoặc trả lời
sai)?
■ Khinào cần scale up?
Lưu ý:Không có monitoring, bạn chỉ biết agent hỏngkhi user phàn nàn. Health
check“200 OK” không có nghĩa câutrả lời đúng.
Giảngviên (VinUni) AICB· Monitoring 2026 4/ 96

---

### Monitoringvs Observability — Hai KháiNiệm Khác Nhau

Monitoring
Theodõi các câu hỏiđãbiết trước.
■ Dashboard+ alert dựng sẵn
■ Trảlời: “Xcó hỏng không?”
■ Tốtcho failure mode đã lườngtrước
■ “Known-knowns”
Observability
Thuộctính củahệthống: hỏicâu mớimà
khôngcần deploy code.
■ Telemetryđủ giàu (metrics + logs +
traces)
■ Trảlời: “TẠISAO X hỏng?”
■ Tốtcho failure modechưatừng
gặp
■ “Unknown-unknowns”
Giảngviên (VinUni) AICB· Monitoring 2026 5/ 96

---

### ObservabilityAI Khác Gì Monitoring PhầnMềm TruyềnThống?

Cùng input, output khác nhau mỗi lần.
Khôngthểtestbằng“sosánhstring”. Phải
đochấtlượng,không chỉ pass/fail.
App không “crash” — nó vẫn trả 200 OK
nhưng câu trả lời tệ dần. Không có ex-
ceptionđể bắt.
Mỗi request tốn tiền theo số token. Một
bug loop có thể đốt budget trong vài giờ
—CPU/RAM không nói cho bạnbiết.
Hallucinated tool args, vòng lặp vô tận,
context overflow, prompt injection —
nhữnglỗimàAPMtruyềnthốngkhôngcó
kháiniệm.
Giảngviên (VinUni) AICB· Monitoring 2026 6/ 96

---

### Costof Not Monitoring

Agenttrảlờisainhưngkhôngaibiết. User
mấtniềmtindần. Đếnkhipháthiệnthìđã
mấtuser.
Tokencosttăngdầnmàkhôngalert. Cuối
tháng nhận bill gấp 5 lần. Đốt hết budget
trướckhi kịp react.
Latency P95 tăng 10ms mỗi tuần. 6 tuần
sau: chậm gấp đôi. Không ai để ý vì
khôngcó baseline.
Bug report: “agent sai hôm qua.” Không
log,khôngtrace. Khôngreproduceđược.
Khôngfix được.
Giảngviên (VinUni) AICB· Monitoring 2026 7/ 96

---

### Observability: Vài Cột Mốc

Logs (text)
Metrics &
Prometheus
2012
Grafana 2014
Tracing &
OTel 2019
LLM-native
2023+
Giảngviên (VinUni) AICB· Monitoring 2026 8/ 96

---

### ControlTheory — Observability Là MộtFeedback Loop

Agent
System
Observe
metrics
Analyze
compare
Act
fix/scale
Feedbackloop
Mean Time To Detect: từ khi sự cố xảy
rađến khi phát hiện.
MeanTimeToRecover : từkhipháthiện
đếnkhi fix xong.
Observabilitytốt=giảm MTTDxuốngphút,khôngphảingày. Khôngcóobservability,
MTTD= thời gianuserphản ánh.
Giảngviên (VinUni) AICB· Monitoring 2026 9/ 96

---

### 02

3 Pillars + Pillar Thứ 4
Metrics nói bao nhiêu / bao lâu, logs nói chuyện gì xảy ra, traces
nói tại sao — và với AI có pillar thứ 4: câu trả lời có còn ĐÚNG
không

---

### 3Pillars of Observability

Metrics
Đolường
Logs
Ghichép
Traces
Theodõi
Bao nhiêu? Bao lâu?
Latency, error rate,
cost per day
Gì xảy ra?
Input, output, errors,
timestamps
Tại sao?
End-to-end journey,
bottleneck, root cause
Logsnóichuyện gì xảy ra.Metricsnóibao nhiêu và bao lâu.Tracesnóitại sao.
Giảngviên (VinUni) AICB· Monitoring 2026 10/ 96

---

### PillarThứ 4: Continuous/ Online Eval

Pillarthứ4 — VớiAIsystem,bapillartruyềnthốngkhôngtrảlờiđượccâuhỏiquan
trọng nhất:câu trả lời có còn đúng không?Pillar thứ 4 = đochất lượng output
liêntục trên production.
■ HTTP200 kháccorrectness— request “thành công” vẫn cóthể là câu trả lời bịa
■ Latencythấp kháchữuích — trả lời nhanh nhưngsai còn tệ hơn
■ Errorrate 0%kháckhôngđốt tiền — chi phí vẫncó thể tăng vọt
Day 13 đo chất lượngliên tục trên production(online). Day 14 đo chất lượngcó
hệthống bằng benchmark(offline). Cả hai bổsung cho nhau.
Giảngviên (VinUni) AICB· Monitoring 2026 11/ 96

---

### TạiSao Chỉ Logs Là KhôngĐủ?

Chỉcó logs
■ biếtrequest nào fail
■ nhưngkhông biết fail rate bao
nhiêu
■ khôngbiết latency đang tăng dần
■ khôngbiết bottleneck ở đâu
Đủpillars
■ metricscho biết trend (tăng/giảm)
■ logscho biết chi tiết từngrequest
■ tracescho biết chậm ở bướcnào
■ evalcho biết chất lượng còntốt
không
Logs giống camera an ninh. Metrics giống bảng điều khiển xe. Traces giống bản đồ
GPS.Eval giống người kiểm định chấtlượng. Cần cảbốn đểláian toàn.
Giảngviên (VinUni) AICB· Monitoring 2026 12/ 96

---

### PillarNào TrảLời CâuHỏi Nào?

Câuhỏi Pillar Côngcụ ví dụ
“Errorrate có tăng không?” Metrics Prometheus,Grafana
“Request req-abcđãlàm gì?” Logs Loki,JSON logs
“Chậm ở bước nào trong agent
loop?”
Traces Langfuse,Tempo
“Câutrả lời còn đúng không?” Eval (4th) LLM-judge,RAGAS
Chọn pillar theo câu hỏi bạn cần trả lời. Đừng thu thập telemetry chỉ vì có thể — mỗi data
pointđều tốn tiền lưu trữ(xem §10).
Giảngviên (VinUni) AICB· Monitoring 2026 13/ 96

---

### 03

AI-Specific Metrics
Monitoring truyền thống đo CPU, RAM, uptime — AI agent cần
thêm: token, cost, TTFT, chất lượng, tool-call success, retrieval
quality

---

### 4Nhóm Metrics Cho AI Agent

Performance
■ LatencyP50 / P95 / P99
■ Timeto first token (TTFT)
■ Throughput(req/s, tokens/s)
■ LLMcall duration
Quality(pillar 4)
■ Hallucination/ faithfulness
■ Taskcompletion rate
■ Thumbsup/down, regenerate rate
■ Guardrailtrigger rate
Cost
■ Tokensper request (in / out)
■ Costper request / per task
■ Costper day / per user/ per feature
■ Cachehit rate
Reliability
■ Errorrate, uptime
■ Tool-callsuccess / failure rate
■ Retryrate, loop rate
■ Retrievalrecall / empty-result rate
Giảngviên (VinUni) AICB· Monitoring 2026 14/ 96

---

### 4Golden Signals + 2 ChoAI Agent

GoogleSRE — 4 Golden Signals
1. Latency—thời gian phản hồi
2. Traffic—request rate (QPS)
3. Errors—error rate
4. Saturation—tài nguyên còn bao
nhiêu
AIagent cần thêm 2
5. Cost—$/request, $/user,token
usage
6. Quality—hallucination rate, CSAT,
groundedness
Lưuý: Agentcóthể“up”(traffic/latency/errorOK)nhưng trảlờisaivàđốttiền . Đây
là2 failure mode riêng của AImà monitoring truyền thống bỏ qua.
Giảngviên (VinUni) AICB· Monitoring 2026 15/ 96

---

### REDvs USE — Hai PhươngPháp Observability

RED(request-centric)
■ Rate— requests/giây
■ Errors— error rate
■ Duration— latency P50/P95/P99
Gócnhìn user: tôigửi request, được gì?
USE(resource-centric)
■ Utilization— tài nguyên dùng %
■ Saturation— có queue/chờ
không?
■ Errors— lỗi của resource
Gócnhìn resource: LLMAPI, queue đang làm gì?
Agentchậm(RED:DurationP95tăng) →debugbằngUSE(LLMrate-limitutilization
95%)→bịthrottle →upgradetier hoặc fallback.
Giảngviên (VinUni) AICB· Monitoring 2026 16/ 96

---

### Latency: Percentiles + TTFT

P50 ≈2.5s(nửa số request nhanh hơn)
P95 ≈5s(95% request nhanh hơn)
P99 ≈8s+
TTFT (Time To First Token)— Thời gian từ lúc gửi request đến token đầu tiên.
Quyếtđịnh cảm giác “nhanh”. Điển hình 2026: P50≈0.5–1.0s,P95 ≈1.5–2.5s.
Lưu ý:Trung bình (average) ẩn long tail. P95 mới là trải nghiệm thật.Reasoning
modelàlớp latency riêng (chậm hơn 5–30x)— tách ra khi đo.
Giảngviên (VinUni) AICB· Monitoring 2026 17/ 96

---

### PercentileMath — Vì Sao P99Quan Trọng

Bài toán — Agent có P99 = 5s, user
chat10 lượt. Xácsuất gặp≥ 1lần > 5s:
P = 1− 0.9910≈ 9.6%
■ 1/10user sẽ gặp lag rất tệ
■ 1.000user/ngày →96user bứcxúc
■ Họlà người tweet negative, churn
“Every 100ms of latency cost 1% of
sales.”→optimizetail,khôngchỉav-
erage. P99 / P99.9 là KPI chính thức
tạiAmazon, Google, Meta.
Lưu ý:Tail latencycompoundstrong agentic workflow nhiều bước — 5 bước, mỗi
bướccóP99riêng →gầnnhưchắcchắn1bướcchạmtail. ĐoP99cho cảpipeline,
khôngchỉ từng call.
Giảngviên (VinUni) AICB· Monitoring 2026 18/ 96

---

### Token& Cost Metrics —Output Đắt Hơn Input

Model(2026) Input$/1M Output $/1M Tỉ lệ out:in
ClaudeHaiku 4.5 1 5 5x
ClaudeSonnet 4.6 3 15 5x
ClaudeOpus 4.8 5 25 5x
OpenAIGPT-5.5 5 30 6x
Gemini3.1 Pro 2 12 6x
cost-per-task̸= cost-per-LLM-call — 1 task của agent có thể gọi LLM nhiều lần (plan +
tool+synthesize). Đocosttheo taskvàrolluptheongày/user/feature,khôngchỉtheotừng
call.
Lưu ý:Output token đắt 5–6x input. Một agent “nói nhiều” tốn tiền hơn nhiều so với độ dài
promptgợi ý⇒dashboardtoken phảitáchinput vs output.
Giảngviên (VinUni) AICB· Monitoring 2026 19/ 96

---

### QualityMetrics — Kim Tự Tháp4 Tầng

L4: Outcome Tasksuccess, revenue, retention
L3: User Signal Thumbsup/down, CSAT,follow-up
L2: LLM-as-Judge Relevance,faithfulness (RAGAS)
L1: Automated Heuristic Format,length, toxicity,PII leak
L1 rẻ, realtime nhưng không nói được quality thực. L4 là ground truth nhưng lag
hàngtuần. Production cầncả 4: L1/L2 đểalert,L3/L4 đểconfirmtrend.
Giảngviên (VinUni) AICB· Monitoring 2026 20/ 96

---

### Hallucination— Phát Hiện Thế Nào?

Hallucination — Agenttrảlời“rấttựtin”nhưngsaisựthật. Khôngcó1metricduy
nhất→cầncombo 4 patterns.
Mỗi claim trong output→ check có trong retrieved
contextkhông. Tool: RAGAS faithfulness, TruLens.
Gọi LLM 3 lần (temp 0.7); 3 câu mâu thuẫn→ nghi
ngờ. Cost 3x→chỉsample 1%.
Extract entities (tên, số, dates) → cross-check
DB/API.Cho finance, medical.
“Wasthishelpful?” +regenerateclick=tínhiệuhal-
lucination. Chậm nhưng rẻvà thật.
Lưu ý: Air Canada (2024): chatbot bịa chính sách bereavement fare. Nếu có
groundednesscheck vớipolicy DB→blocktừ đầu, tránh kiện tụng.
Giảngviên (VinUni) AICB· Monitoring 2026 21/ 96

---

### QualityMetrics — Đo Cái KhóĐo

Tínhiệu trực tiếp
■ Hallucinationrate (bịa thông tin)
■ Faithfulness/ groundedness (bám
nguồn)
■ Task-completionrate
Tínhiệu gián tiếp (từ user)
■ Thumbsup / down
■ Regenerate/ rephrase rate
■ Abandon/ escalate-to-human rate
Khôngthểchấmtaymọirequest. Sample1%→chấmbằngLLM-as-judge/RAGAS
→đẩythành 1 metric (gauge)→alertkhi tụt. Chitiết về eval có hệ thống:Day14.
Giảngviên (VinUni) AICB· Monitoring 2026 22/ 96

---

### Tool-Call& Retrieval Metrics

Toolcalls
■ Successrate / schema-fail rate
■ Timeoutrate
■ Looprate (gọi lặp lại)
■ Argshallucination (bịa tham số)
Retrieval(RAG)
■ Recall@k(proxy)
■ Empty-resultrate
■ Chunkrelevance
■ Retrievallatency
Đây là các failure moderiêng của agent. Một agent “chạy ok” nhưng tool-call suc-
cess60% nghĩa là 40% câu trảlời dựa trên dữ liệu saihoặc thiếu.
Giảngviên (VinUni) AICB· Monitoring 2026 23/ 96

---

### Reliability— Error Taxonomy

Loạilỗi Nguyênnhân Cáchhandle
LLMAPI 5xx Providerdown / rate limit Retry exponential backoff, fall-
backmodel
LLMtimeout Slowprovider,network Circuit breaker, client timeout <
server
Toolcall failed ExternalAPI lỗi Retry,graceful degradation
Toolschema invalid LLM sinh JSON lỗi Re-promptvới error feedback
Guardrailblock Contentpolicy vi phạm Log + user-friendly message
Emptyresponse LLMrefuse / filter Alternate prompt, escalate to hu-
man
Contextoverflow Input >limit Truncate,summarize history
Track error_type trong mỗi log. Alert fire→ biết ngay gọi ai: LLM provider? tool owner? prompt
engineer? “Error rate 5%”không có taxonomy = không fixđược.
Giảngviên (VinUni) AICB· Monitoring 2026 24/ 96

---

### Drift— Khi Data/Model Thay ĐổiÂm Thầm

3loại drift cần monitor
■ Datadrift —input distribution đổi (user hỏi
kiểumới)
■ Conceptdrift —mapping input→output
đổi(luật mới)
■ Modeldrift —provider update model,
behaviorđổi
Pháthiện: PSI, KL-divergence, embeddingdrift
(cosine).
PSI =
∑
i
(pi−qi) ln pi
qi
< 0.1 stable · 0.1–0.25 mild · > 0.25 signifi-
cant(cần retrain).
Lưu ý:2024: OpenAI silently update GPT-4→ format output đổi→ nhiều pipeline
breaksâm thầm. Khôngdrift monitoring = không biết chođến khi user bỏ đi.
Giảngviên (VinUni) AICB· Monitoring 2026 25/ 96

---

### MetricNào Cho Ai?

Stakeholder Quantâm Metrics
Engineering Systemhealth, debug Latency P95, error
rate,tool-call failure
Product Userexperience Satisfaction, task com-
pletion, hallucination
rate
Finance/ Ops Costcontrol Cost/ngày, tokens/re-
quest,cost by model
Leadership ROIoverview Adoption, cost vs
value,uptime
Dashboard cho stakeholder phải nói bằngngôn ngữ business, không phải ngôn ngữ kỹ
thuật.
Giảngviên (VinUni) AICB· Monitoring 2026 26/ 96

---

### 04

Structured Logging
Log không cấu trúc giống ghi chú tay — khó search, khó aggre-
gate. Structured logging biến log thành DATA query được

---

### Unstructuredvs Structured Log

# Unstructured: kho search / filter / aggregate
# 10:23:45 INFO Agent responded 10:23:46 ERROR Tool failed
# Structured JSON: query/aggregate/correlate duoc
log = {
"ts": "2026-03-18T10:23:45Z", "level": "INFO",
"correlation_id": "req-abc123", "event": "agent_response",
"latency_ms": 1250, "input_tokens": 640, "output_tokens": 250,
"cost_usd": 0.0057, "model": "claude-sonnet-4-6",
}
Query được như data:filter theo field, aggregate, correlate across services—
điềutext log không làm được.
Giảngviên (VinUni) AICB· Monitoring 2026 27/ 96

---

### LogGì Cho 1 LLM Call?

□✓ correlation_id(nối mọi log của 1request)
□✓ model+ version, provider
□✓ prompttemplate id (KHÔNG log rawprompt chứa PII)
□✓ input_tokens/ output_tokens, latency_ms, TTFT
□✓ toolcalls + kết quả (đãsanitize), finish_reason
□✓ cost_usd(tính từ token)
□✓ evalscore (nếu có), error +stack trace
Giảngviên (VinUni) AICB· Monitoring 2026 28/ 96

---

### LogGì Và Không Log Gì?

Nênlog
■ Input(đã sanitize)
■ Outputsummary
■ Toolcalls + results
■ Latency,tokens, cost
■ Errors+ stack traces
■ CorrelationID
KHÔNGlog
■ PII(tên, SĐT,CCCD, email)
■ Fullprompts chứa sensitive data
■ APIkeys, tokens, secrets
■ Rawuser data chưa sanitize
■ Quánhiều DEBUG ở production
Lưu ý:Log PII = vi phạm PDPL (Việt Nam) / GDPR.Redact trước khi log, không
phảisau khi bị audit. Chi tiết: §13.
Giảngviên (VinUni) AICB· Monitoring 2026 29/ 96

---

### PIIRedaction TrongThực Tế

Kỹthuật
■ Regex: email, SĐT,thẻ, CCCD
■ NER/ entity detection: tên người,
địachỉ (Microsoft Presidio)
■ Hashing/ tokenization: giữ tính duy
nhất,bỏ giá trị gốc
■ Allowlist: chỉ log fieldđã duyệt
OSS (MIT) của Microsoft: phát hiện 50+
loại PII (email, thẻ, SĐT, SSN...). Redact
/ mask / hash qua “operators”. Lưu ý: hỗ
trợ tiếng Việt yếu — cần custom recog-
nizercho CCCD/SĐT VN.
Redacttạiđiểmphátsinh (trướckhivàopipelinelog/trace),khôngphảiởcuối. Nối
vớiguardrails Day 11.
Giảngviên (VinUni) AICB· Monitoring 2026 30/ 96

---

### LogLevels Đúng Cách

Level Khinào dùng Vídụ
DEBUG Devonly,rất chi tiết Full prompt, intermediate
state
INFO Normalflow,milestone Request received, re-
sponsesent
WARN Degradednhưng vẫn chạy Retrysucceeded,fallback
used
ERROR Failed,cần attention Tooltimeout, LLM error
Productionchạy INFOlevel. Khidebugissuecụthể, tạmbậtDEBUG cho1requestID,xong
tắtlại.
Giảngviên (VinUni) AICB· Monitoring 2026 31/ 96

---

### CorrelationID — Nối Tất CảLại

import uuid
def handle_request(user_input):
req_id = str(uuid.uuid4())[:8] # 1 id cho toan bo request
log.info("request_received",
correlation_id=req_id,
input_length= len(user_input))
result = agent.run(user_input, req_id=req_id)
log.info("response_sent",
correlation_id=req_id,
latency_ms=result.latency,
output_tokens=result.output_tokens)
return result
CorrelationID nốimọi log entry của 1request, dù đi qua nhiều service. Nó cũng làmầmcủa
trace_id —cầu nối sang distributed tracing(§5).
Giảngviên (VinUni) AICB· Monitoring 2026 32/ 96

---

### structlog+ contextvars — Correlation IDTự Động

import structlog, uuid
from structlog.contextvars import bind_contextvars, clear_contextvars
structlog.configure(processors=[
structlog.contextvars.merge_contextvars, # tu dong chen context
structlog.processors.add_log_level,
structlog.processors.TimeStamper(fmt= "iso", utc=True),
structlog.processors.JSONRenderer(), # -> JSON moi dong
])
log = structlog.get_logger()
async def handle_request(req):
clear_contextvars()
bind_contextvars(correlation_id= str(uuid.uuid4())[:8],
user_id=req.user_id, feature=req.feature)
# Tu day: moi log.* tu dong co 3 fields tren
log.info("request_received", query_len= len(req.query))
return await agent.run(req.query)
contextvars an toàn vớiasyncio — mỗi request có context riêng, không lẫn giữa
concurrentrequests. Idiomproductionthaychoviệctruyền req_idthủcôngquamọi
hàm(§5 nâng lêntrace_id).
Giảngviên (VinUni) AICB· Monitoring 2026 33/ 96

---

### LogSampling — Khi VolumeQuá Cao

Bài toán — 100k req/ngày× 10 log/req = 1M entries/ngày. Datadog∼ $0.10/1k
→ $100/ngàychỉ riêng log. Không scalable.
Strategies
■ Head—quyết định ngay đầu trace (rẻ,
cóthể miss errors)
■ Tail—quyếtđịnhsaukhixong(đắt,giữ
100%errors)
■ Reservoir—giữ N mẫu uniform
100%ERROR+WARN ·10%INFO ·1%DEBUG
· 100% request > 10s (tail-on-latency) · 100%
cost > $1/req(outliers).
Lưu ý:Sampling giảm cost 10–100x nhưng mất visibility vào normal pattern. Giữ
100%errors lànon-negotiable — đó là data debugquan trọng nhất.
Giảngviên (VinUni) AICB· Monitoring 2026 34/ 96

---

### LogAggregation Stacks

Stack Khinào dùng Cost/ tier
ELK Full-text search mạnh, complex
queries
Tựhost, OSS
Loki Label-based (giống
Prometheus),rẻ
Tựhost, OSS
DatadogLogs Setupnhanh,alerttốt,đắtởscale SaaS ∼ $0.10/GB
CloudWatch Đã ở AWS,tíchhợp IAM ∼ $0.50/GBingest
BigQuery AnalyticsSQL, long retention ∼ $0.02/GBscan
LangfusetựlàlogstorechoLLMcall(freetier). Devlocal: stdoutJSON+ jqlàđủ. Scaleupmớicần
ELK/ Loki — đừng dựngcluster Elasticsearch cho MVP.
Giảngviên (VinUni) AICB· Monitoring 2026 35/ 96

---

### AuditLog — Tách Biệt VớiApp Log

Audit log— Recordwho did what whencho compliance, legal, security — khác
hẳnapp log dùng để debug.
Applog
■ Mụcđích: debug, performance
■ Retention: 30–90 ngày
■ Cóthể sample, sửa/xóa
■ Truycập: devteam
Auditlog
■ Mụcđích: compliance, forensics
■ Retention: 2–7 năm (tùyngành)
■ Khôngsample; append-only
■ Truycập: restricted(compliance)
Lưuý: Trộnauditvàoapplog →khicầninvestigatebịthiếudata. Táchriêngtừngày
đầu: S3bucketvới ObjectLock,hoặcdedicatedauditservice. LiênquanPDPL§13.
Giảngviên (VinUni) AICB· Monitoring 2026 36/ 96

---

### 05

Distributed Tracing Cho Agent
Log cho biết gì xảy ra ở từng bước; trace cho biết hành trình của
1 request qua LLM→ tool→ LLM và mất bao lâu ở mỗi bước

---

### Trace,Span, Parent–Child

0ms 2500ms
TotalRequest (trace): 2500ms
Parse50ms Retrieval600ms LLMCall 1400ms
Embed200ms Search350ms Generate1200ms
Mỗihàng ngang là 1span. Tất cả spancủa 1 request tạo thành 1trace. Span con lồngtrong
spancha. Nhìn tracebiết ngaybottleneckở đâu.
Giảngviên (VinUni) AICB· Monitoring 2026 37/ 96

---

### TraceCho Agent Pipeline (Multi-StepLoop)

User
Request
LLM
Plan
Tool
check_stock
LLM
Plan
LLM
Synthesize Response
400ms 600ms 300ms 1200ms
Agent loop = chuỗi LLM↔tool. Trace cho thấy mỗi vòng tốn bao lâu. Ở đây 2 LLM
callchiếm 64% latency⇒tốiưu prompt / model trước.
Giảngviên (VinUni) AICB· Monitoring 2026 38/ 96

---

### OpenTelemetry— Chuẩn TrungLập (Vendor-Neutral)

OpenTelemetry (OTel)— Chuẩn mở để sinh và xuất telemetry (traces, metrics,
logs). Instrumentcode mộtlần bằngOTel→gửitới bấtkỳbackendnào (đổiback-
endkhông sửa code).
AIService
(OTelSDK)
OTel
Collector
Backend
Langfuse/ Tempo/ Datadog
Tránhvendorlock-in. Cùng1tracecóthểvàoLangfuse(UIchoLLM)vàTempo(lưu
trữrẻ) song song.
Giảngviên (VinUni) AICB· Monitoring 2026 39/ 96

---

### OTelGenAI Semantic Conventions (gen_ai.*)

Attribute Ýnghĩa
gen_ai.operation.name chat/ execute_tool / invoke_agent
gen_ai.provider.name openai/ anthropic (thay gen_ai.system cũ)
gen_ai.request.model modelđược yêu cầu
gen_ai.usage.input_tokens inputtokens (thay prompt_tokens)
gen_ai.usage.output_tokens outputtokens (thay completion_tokens)
gen_ai.response.finish_reasons ["stop"], ["length"]
gen_ai.tool.name têntool (trên execute_tool span)
Lưu ý: Vẫn ở trạng thái Development (experimental) giữa 2026 — tên attribute còn có thể đổi. Tên cũ
prompt_tokens/completion_tokens/gen_ai.system đãdeprecated nhưng nhiều tutorial cũvẫn dùng.
Giảngviên (VinUni) AICB· Monitoring 2026 40/ 96

---

### Đọc1 TraceMulti-Step

# Span tree cua 1 agent run (ten span = "{operation} {model/tool}")
invoke_agent ecommerce-agent 2500ms
|- chat claude-sonnet-4-6 (plan) 400ms
|- execute_tool check_stock 600ms <-- cham!
|- chat claude-sonnet-4-6 (plan) 300ms
'- chat claude-sonnet-4-6 (synthesize) 1200ms
# Doc: tong 2500ms; check_stock 600ms la I/O cham,
# 2 lan synthesize chiem 1600ms -> toi uu prompt/model truoc.
Đọctrace=đọccâyspan: bướcnàolâunhất,bướcnàolỗi,bướcnàolặp. Đâylàkỹ
năngdùng lại ở §11(debug incident).
Giảngviên (VinUni) AICB· Monitoring 2026 41/ 96

---

### Sampling— Giữ TraceNào?

Quyết định giữ/bỏngay đầurequest (vd
giữ10%). Rẻ,đơngiản,nhưngcóthểbỏ
sóttrace lỗi.
Quyết địnhsau khi xongrequest: luôn
giữ trace lỗi / chậm, sample bớt trace
“bình thường”. Thông minh hơn, tốn
bufferhơn.
Lưuý: Labgiữ100%(datanhỏ). Khiscale,samplinglàcáchgiảmchiphílưutrace
—nhưng đừngbao giờ sample bỏ trace lỗi.
Giảngviên (VinUni) AICB· Monitoring 2026 42/ 96

---

### Trace,Span, Context — Terminology

Kháiniệm cốt lõi
■ Trace—toàn bộ request end-to-end,
có trace_id duynhất
■ Span—1 đơn vị công việc, có
span_id, parent_span_id
■ Contextpropagation —truyền
trace_id quaboundaries (HTTP
header,queue)
name (vd llm.generate) · start_time, duration
· attributes (model, tokens) · status (OK/ER-
ROR) · events (log gắn vào span)· links (vd
retry).
Trace=cây. Rootspan =entrypoint(HTTPrequest). Childspans =cácbướccon
(RAGretrieve, LLM call, tool call). Nhìn cây biết bottleneck.
Giảngviên (VinUni) AICB· Monitoring 2026 43/ 96

---

### 4Bottleneck Patterns TrongTrace

A→B→C, tổng = sum. Fix: parallelize A, B nếu
khôngphụ thuộc.
LoopgọiAPI/DBnhiềulần →nhiềuspanngắncùng
tên. Fix: batch / pre-fetch.
Span dài nhưng CPU idle (LLM API, DB, network).
Fix: parallelize, cache, timeout.
Nhiều span retry trong 1 trace; backoff quá ngắn,
không jitter. Fix: exponential backoff + circuit
breaker.
Nhìn span dài nhất→ “parallelize được không?”. Nhìnnhiều span ngắn lặp→
“batchđược không?”. Haicâu hỏi này giải quyết phầnlớn bottleneck.
Giảngviên (VinUni) AICB· Monitoring 2026 44/ 96

---

### 06

Bộ Công Cụ LLM-Observability
2026
Có cả một hệ sinh thái — chọn đúng theo nhu cầu: open-source
hay SaaS, dùng framework gì, self-host hay cloud

---

### BảnĐồ Công Cụ

Tool Kiểu Mạnhở License/ Note
LangSmith SaaS(self-host EE) Eval, trajectory, prompt
hub
Devfree 5k traces/th
Langfuse OSSself-host + cloud Tracing, cost, prompt
mgmt
MIT,self-host free
Phoenix(Arize) OSSself-host Tracing + eval,
notebook→prod
ElasticLicense 2.0
Helicone Proxy/gateway1-dòng Cost, cache Apache-2.0, mainte-
nancemode ’26
OpenLLMetry OTelauto-instrument Vendor-neutral, mọi
backend
Apache-2.0
Bắt đầu MVP:Langfuse (free, self-host hoặc cloud). Cần eval/trajectory sâu & đã dùng LangChain:LangSmith.
Muốnkhông lock-in: instrumentbằng OTel/OpenLLMetryrồigửi đi đâu cũng được.
Giảngviên (VinUni) AICB· Monitoring 2026 45/ 96

---

### Langfusevs LangSmith

Langfuse
■ Opensource (MIT),self-host miễn
phí
■ CloudHobby: 50k units/thángfree
■ Framework-agnostic
■ SDKPython v4(2026),OTel-based
■ Tracing,cost, prompt mgmt, eval
LangSmith
■ SaaS;self-host chỉEnterprise
■ Devfree: 5k traces/tháng,14 ngày
■ Hoạtđộng độc lập (không buộc
LangChain)
■ Mạnh: eval +trajectoryeval,
prompthub
■ Onlineeval production-ready
Giảngviên (VinUni) AICB· Monitoring 2026 46/ 96

---

### LangfuseIntegration — Vài Dòng Code(SDK v4, 2026)

# Cach 1: drop-in OpenAI wrapper (it code nhat)
from langfuse.openai import openai # chi doi import
resp = openai.chat.completions.create(
model= "gpt-4o", messages=[{ "role": "user", "content": "Hi"}])
# -> tu dong capture prompt, output, latency, tokens, cost
# Cach 2: decorator cho ham bat ky (van la idiom hien hanh)
from langfuse import observe
@observe(as_type= "generation")
def call_llm(prompt):
return agent.run(prompt)
Lưu ý: SDK Python hiện làv4 (3/2026), dựa trên OpenTelemetry. @observe()
vẫnlàidiomđúng—nhưngimportlà from langfuse import observe (KHÔNGphải
langfuse.decorators kiểuv2 cũ).
Giảngviên (VinUni) AICB· Monitoring 2026 47/ 96

---

### LLMGateway — Quan Sát +Cost Một Chỗ

LLM Gateway / Proxy— Một lớp đứng trước mọi LLM call (đổibase_url). Tập
trung observability, cost tracking, caching, rate-limit, budget — cho nhiều provider
quamộtinterface.
OSS, 1 API kiểu OpenAI cho 100+ model.
Budget/rate-limit theo key/team/user; “bud-
gethết →chặn”.
Gateway thương mại: observability +
guardrails + semantic cache. Helicone tích
hợp1 dòng (đang maintenance mode).
Gateway=điểmnghẽn(choke-point)đểápcost&policymộtchỗ,thayvìrảiráctrong
code.
Giảngviên (VinUni) AICB· Monitoring 2026 48/ 96

---

### ChọnCông Cụ Nào Khi Nào?

■ MVP/ lab / startup: Langfuse free tier(cloud) hoặc self-host docker — đủtracing + cost +
dashboard.
■ Đãdùng LangChain/LangGraph, cần eval sâu: LangSmith.
■ Cầndata ở lại on-prem /VN (compliance): self-host Langfuse hoặcPhoenix.
■ Khôngmuốn lock-in: instrument bằng OTel(OpenLLMetry)→đổibackend tùy ý.
■ Tậptrung cost nhiều provider: thêm LLM gateway(LiteLLM).
Lưu ý:Đừng tự build observability từ đầu khi free tier đã đủ. Build dashboard customsau
khicó đủ data và biếtcâu hỏi cần trả lời.
Giảngviên (VinUni) AICB· Monitoring 2026 49/ 96

---

### DecisionFramework — Chọn ToolThế Nào?

Q1: Teamsize? Q3: Existing stack? Q5: Skill set?
1–5: SaaS free tier Datadog: stay + AIaddon Python-heavy: Langfuse
5–50: SaaS paid LangChain: LangSmith Infra ops: Grafana
50+: hybrid/self-host Agnostic: Langfuse Non-dev: Datadog
Q2: Compliance? Q4: Budget/tháng? Q6: Evaluation?
HIPAA/PCI:self-host $0: Langfuse cloud free Quality: Phoenix/Lang-
Smith
GDPR/PDPL: EU/VN re-
gion
$100–500: Lang-
Smith/Helicone
Costonly: Helicone
None: bất kỳ $500+: Datadog full Fullstack: Langfuse
Lưuý: Khôngcó“besttool”,chỉcóbesttoolcho team+usecase+budget củabạn. Đừngcopystack
củaFAANG— họ cóinfra team 50 người.
Giảngviên (VinUni) AICB· Monitoring 2026 50/ 96

---

### 07

Production Stack: Prometheus +
Grafana + OTel
Prometheus thu metrics, Grafana vẽ dashboard, OTel Collector
kết nối tất cả — bộ stack open-source kinh điển, nay có thêm lớp
LLM

---

### KiếnTrúcStack

AIService
OTelSDK
OTel
Collector
Prometheus
(metrics)
Loki
(logs)
Tempo
(traces)
Grafana
(dashboards)
Langfuse
(LLMUI)
Instrument 1 lần (OTel)→ Collector fan-out: metrics→Prometheus, logs→Loki,
traces→Tempo,Grafanavẽ tất cả; Langfuse nhận traceLLM song song.
Giảngviên (VinUni) AICB· Monitoring 2026 51/ 96

---

### Prometheus: Metric Types+ Pull Model

Type Dùngcho
Counter Chỉtăng(requests,errors,
tokens)
Gauge Lên/xuống (active reqs,
queuedepth, eval score)
Histogram Phân phối (latency →
P50/P95/P99)
Prometheus scrape /metrics của ser-
vicemỗi15s(khôngphảiservicepush).
PromQLví dụ:
histogram_quantile(0.95, ...) cho
P95.
Counter/Gauge cho con số đơn; Histogram chia bucket để tính P95/P99 — thứ bạn
cầncho latency SLO.
Giảngviên (VinUni) AICB· Monitoring 2026 52/ 96

---

### Instrument1 AI Service (prometheus_client)

from prometheus_client import Counter, Histogram, start_http_server
REQS = Counter( "agent_requests_total", "Requests", [ "model", "status"])
LAT = Histogram( "agent_latency_seconds", "Latency", [ "model"])
TOKS = Counter( "agent_tokens_total", "Tokens", [ "model", "direction"])
def handle(req, model):
with LAT.labels(model=model).time(): # do latency -> histogram
resp = agent.run(req)
REQS.labels(model=model, status= "ok").inc()
TOKS.labels(model=model, direction= "output").inc(resp.output_tokens)
return resp
start_http_server(8000) # expose /metrics cho Prometheus scrape
Lưu ý: Giữ label cardinality THẤP: model/status ok; đừng đặt user_id hay
request_id làmlabel — sẽ nổ số series(xem slide sau).
Giảngviên (VinUni) AICB· Monitoring 2026 53/ 96

---

### Cardinality: Kẻ Đốt TiềnThầm Lặng

Cardinality — Sốtổhợpgiátrịlabelcủa1metric. Mỗitổhợp=1time-seriesriêng
phảilưu. Label giátrị tự do (user_id, request_id, rawprompt)→bùngnổ series.
LabelAN TOÀN(thấp)
■ model, status, tool_name
■ direction (in/out)
LabelNGUY HIỂM (cao)
■ user_id, request_id
■ prompt, session_id
Lưu ý:Bài học thật: Coinbase từng nhận hóa đơn Datadog$65 triệu(2022), phần
lớn do custom metrics cardinality cao. High-cardinality thuộc vềlogs/traces, không
phảimetric label.
Giảngviên (VinUni) AICB· Monitoring 2026 54/ 96

---

### GrafanaDashboard-as-Code

# Dashboard luu duoi dang JSON/YAML, version trong git -> review qua PR
# provisioning/dashboards/agent.yaml
apiVersion: 1
providers:
- name : agent-dashboards
folder: "AI Agents"
type: file
options:
path: /var/lib/grafana/dashboards # JSON dashboards o day
Dashboardtronggit=cóversion,reviewquaPR,táitạođược,không“clickchuộtrồi
mất”. Cùng triết lývới IaC ở Day 12.
Giảngviên (VinUni) AICB· Monitoring 2026 55/ 96

---

### Self-Hostvs SaaS vs LLM-Tool

Lựachọn Khinào Đánhđổi
Prometheus+Grafana
(self-host)
Có infra ops, muốn kiểm
soát+ rẻ ở quy mô
Tự vận hành, tự build
LLMview
Datadog / New
Relic(SaaS)
Cầnnhanh, có budget Đắt khi scale (cardinal-
ity!)
Langfuse /
Phoenix (LLM-
tool)
Cần LLM-native (trace,
cost,eval)
Bổ sung, không thay
metricstack
Nhiều team dùngkết hợp: Prometheus/Grafana cho metric hạ tầng + Langfuse cho LLM
trace/cost. OTellà lớp keogiữa chúng.
Giảngviên (VinUni) AICB· Monitoring 2026 56/ 96

---

### 08

Dashboard Design
Mỗi stakeholder một câu hỏi, một dashboard — nhồi mọi thứ vào
một màn hình là cách chắc chắn không ai nhìn

---

### Dashboard— 3 Layers

Layer1: Overview —Health, uptime, key alerts
Layer2: Detail —Latency,cost, error rate, tokens
Layer3: Drill-down —Traces,log search, root cause
Choleadership
Choengineering
Chodebugging
Mỗistakeholderchỉnhìn1layer. Leadershipcầnoverview,khôngcầntrace. Engineer
cầndrill-down, không cần revenue chart.
Giảngviên (VinUni) AICB· Monitoring 2026 57/ 96

---

### 6Panel Bắt Buộc Cho AIService

1. Request rate
(traffic)
2. Latency
P50/P95/P99+ TTFT
3. Error rate
(bytype)
4. Cost / token
usage(in/out)
5. Tool-call
successrate
6. Quality / eval
score(sampled)
Sovớiservicethường,agentthay“CPU/GPUpanel”bằng tool-callsuccess vàeval
score—vì failure mode của agent nằmở đó.
Giảngviên (VinUni) AICB· Monitoring 2026 58/ 96

---

### PanelTypeNào Khi Nào?

Paneltype Dùngcho Vídụ
Timeseries (line) Trendtheo thờigian Latency P95,
cost/ngày
Stat/ single value 1 con số hiện tại Uptime%, error rate
Heatmap Phânphối theo thời gian Latency distribution
Table Top-N,breakdown Costbymodel/feature
Lưu ý:Một dashboard = một câu hỏi. Tối đa 6–9 panel/màn. Nhiều hơn nữa thì không ai
đọcđược — tách thành dashboardriêng.
Giảngviên (VinUni) AICB· Monitoring 2026 59/ 96

---

### DashboardTools

Open source, mạnh. Kết
nối mọi data source.Khi
nào: teamcó infra ops.
LLM-native: trace, cost,
eval sẵn. Khi nào: cần
LLM dashboard nhanh
choMVP.
All-in-one SaaS. Nhanh,
đắt khi scale. Khi nào:
cầnnhanh, có budget.
Lưu ý: Cho lab: Langfuse dashboardđủ cho MVP. Đừng dành thời gian build
Grafanacustom trước khi có đủ data.
Giảngviên (VinUni) AICB· Monitoring 2026 60/ 96

---

### DashboardAnti-patterns — 5 Điều NênTránh

1. “Wallof metrics”—30 panel, không ai nhìnhết. Giới hạn 6–8panel/layer.
2. Timerangemặcđịnhquádài —default1giờchoops,khôngphải1tháng(chemấtspike).
3. Khôngcó baseline/threshold line—P95 = 2.1s tốt hayxấu? Luôn vẽ đườngSLO lên
chart.
4. Metrickhông có đơn vị/context—“Cost: 1250” làgì? USD? ngày? Luôn label đầy đủ.
5. Khôngauto-refresh —ops dashboard cần realtime (15–30s);monthly report thì khác.
Đưa dashboard cho người ngoài team xem 30s→ họ nói được “hệ thống OK” hay “có vấn
đềở X” không? Nếu không, redesign.
Giảngviên (VinUni) AICB· Monitoring 2026 61/ 96

---

### 09

Alerting & SLO
Metrics chỉ có giá trị nếu có người nhìn. Alert sai cách còn tệ
hơn không có. SLO cho bạn một ngân sách lỗi để quyết định khi
nào cần lo

---

### AlertRules Cho AI Agent

Metric Threshold Severity Channel
LatencyP95 >5 giây Warning Slack
Errorrate >5% Critical Slack+ Email
Dailycost >budget ngày Critical Email+ SMS
Tool-callfailure >10% Warning Slack
Evalscore tụt> 10% Warning Slack
Uptime <99% Critical PagerDuty
Alertphải actionable. Nếu nhận alertmà không biết làm gì, alertđó cần redesign hoặc bỏ.
Giảngviên (VinUni) AICB· Monitoring 2026 62/ 96

---

### Symptom-Basedvs Cause-Based Alerting

Symptom-based(NÊN page)
Alerttrên cáiusercảm nhận được.
■ Errorrate / latency vượt SLO
■ “Câutrả lời sai tăng vọt”
■ Ítfalse positive, luôn thật
Bốn golden signals: Latency, Traffic, Er-
rors,Saturation.
Cause-based(để DEBUG)
Alerttrên nguyênnhân cóthể.
■ “CPU80%”, “cache miss cao”
■ Cóthể chưa ảnh hưởng user
■ Nhiềunoise nếu để page
Dùng cho chẩn đoán, không phải để gọi
người.
Giảngviên (VinUni) AICB· Monitoring 2026 63/ 96

---

### AlertFatigue — Khi Alert QuáNhiều

Alertfatigue xảy ra khi
■ quánhiều alert không quan trọng
■ mọingười bắt đầu ignore
■ alertthật bị lẫn trong noise
■ teammất tin tưởng hệ thống
Cáchtránh (Google SRE)
■ chỉpage khi cầnhànhđộng ngay
■ mỗipage phải đòitrítuệ (không
robotic)
■ pagevề vấn đềmới,chưa từng thấy
■ phầncòn lại→ticket/ dashboard
Lưu ý:Nếu team ignore alert thường xuyên, hệ thống alerting đangtệ hơn không
có. Nguy hiểm nhất: 1 page thật bịche lấp trong noise.
Giảngviên (VinUni) AICB· Monitoring 2026 64/ 96

---

### SLI/ SLO / SLA —Định Nghĩa Chính Xác

SLI — Indicator —
con số bạn đo. Vd:
% request < 5s; error
rate.
SLO — Objective —
mục tiêu cho SLI.
Vd: 99.9% request <
5s/tháng.
SLA — Agreement —
hợp đồngcó hậu quả
nếu miss (hoàn tiền,
phạt).
Hỏi “điều gì xảy ra nếu không đạt?” Không có hậu quả rõ ràng⇒ đó là SLO, không
phảiSLA. SLI = số đo, SLO= mục tiêu, SLA = lờihứa.
Giảngviên (VinUni) AICB· Monitoring 2026 65/ 96

---

### ErrorBudget — Math Cụ Thể

Error budget— = (1−SLO)× cửa sổ thời gian. Đó là “ngân sách lỗi” bạn được
phéptiêu. Còn budget→shipnhanh; hết budget→đóngbăng, lo độ ổn định.
SLO Downtime/tháng (30 ngày)
99.5% 3.6giờ (216 phút)
99.9% 43.2phút ←“threenines”
99.95% 21.6phút
Page khiburn 14.4x trong 1h(tiêu 2% budget) hoặc6x trong 6h(5%); mởticket khi 1x
trong3 ngày. Long+short window = vừa chính xácvừa reset nhanh.
Giảngviên (VinUni) AICB· Monitoring 2026 66/ 96

---

### On-CallCơ Bản

Severity& escalation
■ SEV1(down/critical) →pagengay
■ SEV2(degraded) →Slack,giờ làm
■ SEV3(minor) →ticket
■ Escalation: primary→secondary→
lead
MTTD = thời gian phát hiện.MTTR = thời
gian khắc phục. Mục tiêu observability:
giảmcả hai.
Lưuý: BốicảnhVN:lịchon-calltheo UTC+7;tránhdeploylớndịp Tết;nhớnghĩavụ
báocáo sự cố dữ liệu72giờ theoPDPL (§13).
Giảngviên (VinUni) AICB· Monitoring 2026 67/ 96

---

### Multi-WindowMulti-Burn-RateAlerting

Bàitoán — Alertđơn“error > 1%trong5phút” →firequánhanh(noise)hoặcquá
chậm(miss incident). Giảipháp Google: kết hợp2 window với 2 burn rate.
Severity Shortwin Longwin Burn rate (vs
SLO)
Page(critical) 5phút 1giờ 14.4x
Ticket(warn) 30phút 6giờ 6x
“14.4x”: giữmứcnàythìburnhếterrorbudgetthángtrong2ngày. Alertfirekhi cả2window
cùngvượt→shortreactnhanhvớispikethật,longfilternoisengắn. (GoogleSREWorkbook
Ch.5.)
Giảngviên (VinUni) AICB· Monitoring 2026 68/ 96

---

### AlertAnatomy — Alert Tốt CóGì?

Templatecho mỗi alert:
■ Titlerõ: “[P1] Agent P95latency> 5scho feature=summary ”
■ Severity: P1 (page ngay)/ P2 (giờ hành chính) /P3 (ticket)
■ Impact: “5% user đangbị chậm> 5s”
■ Currentvalue: “P95 = 6.3s,bình thường 1.8s, threshold 5s”
■ Dashboardlink (pre-filtered)+ Tracelink (top10 chậm nhất)
■ Runbooklink (playbookfix) +On-callowner
Lưuý: Alertkhôngcó runbook=alertkhôngthểxửlýlúc3hsáng. Viếtrunbooklàmộtphần
củawork “tạo alert”, không phảinice-to-have.
Giảngviên (VinUni) AICB· Monitoring 2026 69/ 96

---

### 10

Cost Monitoring & Optimization
Token cost là dòng chi phí lớn nhất và dễ mất kiểm soát nhất
của một AI agent — phải đo như một metric hạng nhất

---

### VìSao Cost Là First-Class Metric

CostAI khác cost phần mềm
■ Tỉlệ vớitoken,không phải request
■ Mộtloop bug đốt budget trong vàigiờ
■ Outputđắt 5–6x input
■ Costtăng tuyến tính với traffic
Tokens (in/out), cost/request, cost/task,
cost/ngày,cost/user,cost/feature,cachehit
rate. Rollup + dailybudget alert.
Haiku$1/$5·Sonnet$3/$15·Opus$5/$25·GPT-5.5$5/$30·Gemini3.1Pro$2/$12
(mỗi1M token in/out). Chọn đúng model là đòn bẩycost lớn nhất.
Giảngviên (VinUni) AICB· Monitoring 2026 70/ 96

---

### ĐoCost Ở Đâu Và ThếNào

Côngthức — cost = input_tokens
106 ×Pin[model] + output_tokens
106 ×Pout[model]
■ Tínhcost tạimỗi LLM calltừtoken usage (provider trả về sẵn)
■ Gắnnhãn theo model / feature /user→rolluptheo ngày
■ Setdailybudget alert: cost hôm nay> ngưỡng→báongay
■ Theodõi cachehit ratenhưmột cost SLI
Lưu ý:Cost-per-LLM-call rẻ (∼$0.005) nhưng một agent task gọi nhiều lần. Luôn
rollup— con số đáng lo làtổng theo ngày/user,không phảitừng call.
Giảngviên (VinUni) AICB· Monitoring 2026 71/ 96

---

### 4Chiến Lược Giảm Cost

Dùng model nhỏ nhất đủ tốt cho mỗi
bước. HaikurẻhơnOpus5x. Route: việc
dễ→modelrẻ.
Bớtfew-shotthừa,tómtắtlịchsử,chỉđưa
contextcần thiết (RAG top-k nhỏ).
Câu hỏi gần giống→ trả lời từ cache,
khônggọi LLM.∼70%hit cho FAQ.
Cache system prompt / tool defs / RAG
context dùng lại→ cache read rẻ 90%
(Anthropic).
Mỗichiếnlượccầnmộtmetric: cost-by-model,promptlength, cachehitrate. Không
đothì không biết có hiệu quả.
Giảngviên (VinUni) AICB· Monitoring 2026 72/ 96

---

### SemanticCache + Prompt Cache

Semanticcache — Embedcâuhỏi →
socosinevớicâucũ →trùng(vd ≥ 0.8)
thì trả lời từ cache. Benchmark: hit
∼60–70%,giảmcost ∼70%,nhanhhơn
nhiều.
Prompt cache (prefix) — Provider
cache phần đầu prompt lặp lại. An-
thropic: cache read =0.1xgiá input (rẻ
90%), write 1.25x/2x. OpenAI tự động,
Gemini90% (2.5+).
Lưu ý:Semantic cache đánh đổiđộ chính xác: ngưỡng similarity quá thấp→ trả
lời cũ/sai cho biến thể tinh tế. Phải theo dõi cache hit ratevà chất lượng câu trả lời
từcache.
Giảngviên (VinUni) AICB· Monitoring 2026 73/ 96

---

### CostAnti-Patterns

Lưu ý: Không tách input vs output
→khôngthấyoutput(đắt5–6x)làthủ
phạm.
Lưu ý:Không có cost-per-feature→
khôngbiết feature nào đốt tiền.
Lưu ý: “Đo mọi thứ” với label car-
dinality cao → bill observability nổ
(Coinbase$65M).
Lưuý: Khôngcódailybudgetalert →
pháthiện khi nhận hóa đơn.
Quan sát chính nó cũng tốn tiền (lưu metric/log/trace). Cân bằng: đủ telemetry để
trảlời câu hỏi, không nhiều đếnmức bill quan sát vượt billLLM.
Giảngviên (VinUni) AICB· Monitoring 2026 74/ 96

---

### CostAttribution — TiềnĐi Đâu?

Dimension Taggắn vào trace Dùngđể...
Peruser user_id Biếtpower user,tính pricing
Perfeature feature="summary" Prioritizeoptimization
Permodel model="sonnet-4-6" Sosánh cost/value các model
Pertenant tenant_id Multi-tenantbilling
Perenv env="prod" Táchdev/staging noise
Percohort plan="enterprise" Marginanalysis
Mọi LLM call phải cóuser_id + feature + model. Thiếu 1 trong 3→ khi CFO hỏi “$50k tháng này ai
tốn?” bạn không trảlời được, và ngân sách bịcắt.
Giảngviên (VinUni) AICB· Monitoring 2026 75/ 96

---

### CaseStudy — Notion AI CostOptimization

Bốicảnh — NotionAIphụcvụhàngtriệuuser(summary,Q&A,writingassist). Cost
OpenAIban đầu∼30%revenue. Monitoring insight:
■ 70%queries là “summarize” với promptgiống nhau
■ 15%user chiếm 60% cost (powerusers, doc dài)
■ Regeneraterate cao ở feature “writingassist”
Actions(theo thứ tự ROI):promptcache system prompt (−40%input)→route“summary” qua
modelnhỏ(Haikutier, −60%)→per-userratelimitchofreetier →cảithiệnprompt“writingassist”
(−35%regenerate).
Cost/MAU giảm58% trong3tháng,khônggiảmquality. Làmđượcvìcómonitoring
chitiết theofeature+ user + model(xemCost Attribution).
Giảngviên (VinUni) AICB· Monitoring 2026 76/ 96

---

### 11

Debug 1 Incident Bằng Trace
Khi có observability, bạn tìm root cause trong vài phút thay vì vài
ngày — đi từ metric, tới log, tới trace

---

### SựCố: “Agent ChậmGấp Đôi Từ Sáng Nay”

User báo agent phản hồi rất chậm từ 9h sáng. Không có deploy nào rõ ràng. Bạn
bắtđầu từ đâu?
■ Sailầm thường gặp: lao vào đọclog thô của hàng nghìn request.
■ Đúng: bắtđầutừ metric(khoanhvùng) →log(lọctheocorrelation_id) →trace(tìm
bướcchậm).
Metric trả lời “có gì đó chậm, từ khi nào”. Log trả lời “request nào”. Trace trả lời
“chậmở bước nào” — đây làlý do cần cả ba.
Giảngviên (VinUni) AICB· Monitoring 2026 77/ 96

---

### Bước1–2: Metric KhoanhVùng→LogLọc

Dashboard: P95latencynhảytừ2.5s →5s
lúc9h. Token/requestkhôngđổi. Errorrate
bình thường. ⇒ không phải LLM, không
phảilỗi — là một bướcnào đó chậm đi.
Lọc log latency_ms > 4000 sau 9h→ lấy
vài correlation_id request chậm→ mở
tracecủa chúng.
Mỗi pillar thu hẹp không gian tìm kiếm cho pillar sau. Từ “cả hệ thống”→ “request
này”→“spannày”.
Giảngviên (VinUni) AICB· Monitoring 2026 78/ 96

---

### Bước3: Mở TraceCủa 1 Request Chậm

# Trace HOM NAY cua 1 request cham:
invoke_agent ecommerce-agent 5100ms (truoc: 2500ms)
|- chat claude-sonnet-4-6 (plan) 400ms
|- execute_tool rag_retrieve 2800ms <== ROOT CAUSE
| (truoc: 600ms)
|- chat claude-sonnet-4-6 (plan) 300ms
'- chat claude-sonnet-4-6 (synthesize) 1400ms
# LLM van binh thuong. rag_retrieve cham 4.6x -> dieu tra vector store.
Không có trace: bạn đoán mò giữa LLM, network, tool. Có trace: thấy ngay
rag_retrieve làthủ phạm trong 30 giây.
Giảngviên (VinUni) AICB· Monitoring 2026 79/ 96

---

### RootCause + Fix + Postmortem

Một index filter của vector store bị bỏ trong
deploy hạ tầng 8h45→ mỗi truy vấn quét
toànbộ. Khớp đúngthời điểm P95 nhảy.
Timeline · tác động (MTTD/MTTR) · root
cause · cái gì đã giúp phát hiện · ac-
tion items. Trách hệ thống, không trách
người.
Cùngquytrìnhmetric →log→tracedùngchomọiincident. Observabilitytốt=MTTD
vàMTTR thấp.
Giảngviên (VinUni) AICB· Monitoring 2026 80/ 96

---

### BàiHọc Từ Sự Cố Thật(2024–2025)

■ ReplitAI agent (7/2025): agent xoá DBproduction dù đang “code freeze” —mất dữ liệu
1.206lãnh đạo + 1.196 côngty. Tệ hơn: agentbịa4.000user giả và nói rollbackbất khả thi
(thựcra rollback được).⇒Least-privilege+ tách dev/prod; tin telemetry/backupđộc lập,
KHÔNGtin agent tự thuật.
■ AirCanada (Moffatt v. Air Canada, 2024): chatbot bịa chínhsách vé tang lễ; toà buộc
hãngbồi thường CA$650 — “chatbotlà thực thể riêng” bị bác.⇒Câutrả lời sai = trách
nhiệmpháp lý; phải monitor chấtlượng output.
■ Klarna: dồn AI thay700 agent rồiquayxe thuêlại người vì chất lượng.⇒Tỉlệ “AI xử lý
X%”(mean) che giấu variance ởtail — theo dõi phân phối,không chỉ trung bình.
Giảngviên (VinUni) AICB· Monitoring 2026 81/ 96

---

### 12

Human Feedback & Online Eval
Trong Production
Pillar thứ 4 khi vận hành: đo chất lượng trên dữ liệu thật, liên
tục, để bắt suy thoái trước khi user bỏ đi

---

### OfflineEval vs Online Eval

Offline(Day 14)
■ Testsetcốđịnh,expectedanswers
■ Chạytrước khi ship (CI gate)
■ Bắtregression
Online(Day 13)
■ Trafficthật, không có groundtruth
■ Chạyliên tục trên production
■ Bắtsuy thoái + drift
Modelkhông“crash”khisuythoái—nóvẫntrả200OK.Chỉonlineeval(pillar4)mới
pháthiện chất lượng tụt trên dữliệu thật.
Giảngviên (VinUni) AICB· Monitoring 2026 82/ 96

---

### ThuHuman Feedback

Thumbs up/down, rating sao, “câu trả lời
nàycóhữuích?”. Rõràngnhưngtỉlệphản
hồithấp.
Regenerate, copy, rời đi, hỏi lại, escalate-
to-human. Nhiều tín hiệu,cần diễn giải.
Implicit signal (regenerate rate, abandon rate) thườngnhiều và trung thực hơn
explicitrating. Log cảhai, gắn vào trace.
Giảngviên (VinUni) AICB· Monitoring 2026 83/ 96

---

### Eval-as-MetricLoop

Sample1%
production
LLM-judge
/RAGAS
Gauge
metric
Alertnếu
tụt
Lấymẫunhỏ →chấmtựđộng →đẩythànhgaugetrêndashboard →alertkhigiảm.
Chấtlượng trở thành metric như latency.
Lưu ý:LLM-judge cũng tốn tiền→ sample (1%) thay vì chấm 100%. Đây là lý do
“đochất lượng” phải cân với cost(§10).
Giảngviên (VinUni) AICB· Monitoring 2026 84/ 96

---

### Feedback→Dataset→CảiThiện (và Cẩn Trọng)

Câutrảlờitệ(thumbs-down/judgethấp) →
gom thành dataset→ thành test case cho
Day14 →sửaprompt/model →đolại.
Lưu ý: Judge drift: LLM-judge cũng
thayđổitheothờigian/phiênbản. Theo
dõi phân phốiđiểm (không chỉ mean);
định kỳ kiểm bằng gold set người
chấm.
Observability→eval→cảithiện→observability. ĐâylàvònglặpsảnphẩmAItrưởng
thành.
Giảngviên (VinUni) AICB· Monitoring 2026 85/ 96

---

### 13

Privacy & Compliance Khi Log-
ging
Log và trace là nơi PII rò rỉ nhiều nhất — full tracing vô tình biến
hệ thống quan sát thành một kho dữ liệu cá nhân

---

### VìSao AI Logging Rủi RoPII Cao

■ Usergõ tựdo vàoprompt: tên, SĐT,CCCD,bệnh án, thông tin tài chính
■ Fulltracing capturecảprompt lẫn output→khoPII ngoài ý muốn
■ Trace/logthường gửi sangSaaSnước ngoài(Datadog,LangSmith) = chuyển dữ
liệuxuyên biên giới
Lưu ý:Trong OTel GenAI semconv,gen_ai.tool.call.arguments và prompt/com-
pletionlà opt-inđúngvì lý do PII — mặcđịnh KHÔNG capture nội dung nhạycảm.
Giảngviên (VinUni) AICB· Monitoring 2026 86/ 96

---

### PIITrongLogs/Traces—Làm Gì

Kỹthuật
■ Redact/ mask tại điểm phát sinh
■ Allowlistfield được log
■ Logtemplateid,không log raw prompt
■ Hashđịnh danh thay vì lưu gốc
Microsoft Presidio (detect + anonymize),
guardrails Day 11, OTel content-capture
opt-in. Tự viết recognizer cho CCCD/SĐT
VN.
Khôngcapturecáibạnkhôngcần. MỗifieldPIItrongloglàmộtrủiropháplývàmột
mụcphải xoá khi user yêu cầu.
Giảngviên (VinUni) AICB· Monitoring 2026 87/ 96

---

### Retention,Access & Audit

Đặt TTL theo loại data.
Trace chi tiết: ngắn (7–30
ngày). Metric tổng hợp:
dài. Retention dài = tốn
tiền+ rủi ro.
Ai xem được log/trace
chứa data người dùng?
RBAC+ chỉ cấp khi cần.
Ghi lại ai truy cập teleme-
try. Hỗtrợquyềnxoá/truy
cậpcủa user.
Retentionlàmộttrụctínhtiền(vdLangSmithtínhriêng“extendedtraces”400ngày).
Giữít hơn, lâu hơn một cáchcó chủ đích.
Giảngviên (VinUni) AICB· Monitoring 2026 88/ 96

---

### Compliance: ViệtNam +Quốc Tế

■ ViệtNam: Nghị định 13/2023(PDPD, hiệu lực 1/7/2023) nay đượcnâng lênLuật
Bảovệ Dữ liệu Cá nhân(PDPL,Luật 91/2025, hiệu lực1/1/2026).
■ Báocáo vi phạm dữ liệu trong72giờ tớiBộ Công an (A05). Chuyển dữ liệu xuyên
biêngiới cầnhồsơ đánh giá tác động (TIA),nộp trong 60 ngày.
■ Phạtnặng: vi phạmchuyển xuyên biên giới có thểtới5%doanh thunămtrước.
■ Quốctế: GDPR (EU), PDPA(Singapore/khu vực) — nguyên tắctương tự.
Lưu ý:Gửi log/trace chứa PII của user VN sang observability SaaS nước ngoài =
chuyểndữ liệu xuyên biên giới→cầnhồ sơ + cơ sở pháplý. Đi sâuởDay24.
Giảngviên (VinUni) AICB· Monitoring 2026 89/ 96

---

### 14

Checklist, Lab & Tổng Kết
Mục tiêu cuối: agent deployed có observability đầy đủ — bạn
biết nó chạy thế nào mà không cần hỏi user

---

### MonitoringChecklist

Logging
□✓ StructuredJSON, correlation ID □✓ PIIredacted, log levels đúng
Metrics
□✓ LatencyP50/95/99 + TTFT □✓ Tokenin/out + cost □✓ Tool-callsuccess
Tracing
□✓ Traceper request (span tree) □✓ OTel gen_ai.* attributes
Alerting& SLO
□✓ ≥ 3alertactionable □✓ 1SLO + error budget □✓ Symptom-basedpaging
Cost& Privacy
□✓ Dailybudget alert □✓ Cachehit rate □✓ Retention+ cross-border check
Giảngviên (VinUni) AICB· Monitoring 2026 90/ 96

---

### Lab#13

Mục tiêu: Gắn observability đầy đủvào agent (từ Day 12): structured logging
(correlation ID + PII redaction), AI metrics (token/cost/latency P95+TTFT/tool-call
success),distributedtracing(spantreekiểuOTel gen_ai.*),gửitớibackend(Lang-
fusehoặc backend zero-key offline),dashboard+ alert + 1 SLO.
Deliverable: Monitoringstackchạyđược: ≥ 10traces,dashboard6panel, ≥ 3alert
rule→Slack,1 SLO + error budget, 1incident note đọc từ trace thật.
Thờigian: ∼2giờ
Giảngviên (VinUni) AICB· Monitoring 2026 91/ 96

---

### ArtifactCần Nộp

Logging& Tracing
■ StructuredJSON logs + correlation
ID
■ Input/outputđã redact PII
■ Trace(≥ 10): span tree đọcđược
■ Cost& token per request
Dashboard,Alert & SLO
■ Dashboard: latency,cost,errors,
tool-success
■ ≥ 3alertrule + 1 SLO/error budget
■ Screenshotdashboard có data
■ 1incident note
(metric→log→trace)
Lưu ý: Không cần enterprise monitoring. Cần chứng minh bạnbiết agent đang
chạythế nàomàkhông phải hỏi user.
Giảngviên (VinUni) AICB· Monitoring 2026 92/ 96

---

### Observathon— Cuộc Thi Observability (Capstone)

Một agent e-commercehộp đen, im lặng, đầy bug(không phát log/metric/trace).
Muốnthắng: tựgắn observabilityđểbắt bug rồi sửa.
Nộp3 thứ
■ Findings: bug gì +bằng chứng
■ Configđãsửa (agent mis-config)
■ Wrapper: retry/cache/route/guardrail
Điểm= 1 con số
■ correctness+ LLM-eval quality
■ latency/ cost / error /drift↓
■ +thưởng theo chẩn đoán
Đội,∼4h. Publictest(giờ2,leaderboard) →private(3.5h,held-out+1bugẩn)xếp
hạng. Nộp quagitpush;model tự do (mock / local/ cloud).
Giảngviên (VinUni) AICB· Monitoring 2026 93/ 96

---

### 7Anti-patterns Từ Industry

1. “We’lladd monitoring later”—later = never. Add ngay từ MVP.
2. Logfull prompts + responses—vi phạm GDPR/PDPL, storage billnổ. Sanitize + sample.
3. Alerttrên mọi metric “quan trọng”—50 alert→alertfatigue →ignore.
4. Khôngcó runbook—alert fire 3h sáng, engineertrẻ lost, escalate lên senior.
5. Monitoringdev ̸=prodconfig —prod có issue không reproduceđược vì dev khác setup.
6. Chỉđo performance, quên cost—đến cuối tháng mới biếtđốt tiền.
7. Trustvendor telemetry mặc định—framework default có thể logsensitive data. Đọc docs
trướckhi deploy.
Lưuý: Anti-pattern#1phổbiếnvàtaihạinhất. Monitoringkhôngphảifeaturephụ—làphần
corecủaproduction system, ngang với authentication.
Giảngviên (VinUni) AICB· Monitoring 2026 94/ 96

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
1 4pillars. Metrics+logs+traces+ eval(cònđúngkhông). Chỉlogslàkhôngđủ;AIcầnpillar
thứ4.
2 AI-specific metrics. Token & cost (output đắt 5–6x input), P95 + TTFT, tool-call success.
“HTTP200” khác “trả lời đúng”.
3 Logging+tracing. JSON+correlationID → trace_id;spantreetìmbottleneck;chuẩnOTel;
redactPII.
Alert+SLO+cost. Pagetheosymptom&SLOburn,khôngtheocause. Đocostnhưmetric
hạngnhất; cache để giảm.
5 Onlineeval. Sample →judge →gauge →alert. Debug incident: metric→log →trace.
Giảngviên (VinUni) AICB· Monitoring 2026 94/ 96

---

### Tiếptheo & Bài tập

AIEvaluation & Benchmarking
“Day 13 đo “chất lượng có còn đúng
không” trên production. Day 14: đo
“tốt đến đâu” một cách có hệ thống
— sếp hỏi agent hơn ChatGPT bao
nhiêu,bạn trả lời bằng benchmark. ”
■ Chuẩnbị: 10 câuhỏi mẫu +
expectedanswer cho agent của
bạn
■ Đọctrước: tài liệuRAGAS (20
phút)
■ Suynghĩ: từ onlineeval hôm
nay,quality metric nào quan
trọngnhất cho use case của
bạn?
Giảngviên (VinUni) AICB· Monitoring 2026 95/ 96

---

### TàiLiệu Tham Khảo

1. OpenTelemetryGenAI Semantic Conventions —
github.com/open-telemetry/semantic-conventions-genai (trạngthái Development, 2026).
2. Langfuse—langfuse.com(OSS/MIT,SDKPythonv4,OTel-based). LangSmith—docs.langchain.com.
3. ArizePhoenix & OpenInference; OpenLLMetry (Traceloop)— OTel-nativeLLM instrumentation.
4. GoogleSRE Book & SRE Workbook— sre.google (SLI/SLO/SLA, error budget, multi-burn-rate
alerting,golden signals).
5. Prometheus& Grafana — prometheus.io, grafana.com. Microsoft Presidio —
microsoft.github.io/presidio(PII redaction).
6. VietnamPDPL (Luật 91/2025, hiệu lực1/1/2026); Anthropic/OpenAI/Google pricing & prompt-caching
docs.
Giảngviên (VinUni) AICB· Monitoring 2026 96/ 96

---

### Hỏi& Đáp

Monitoring tốt nghĩa là bạn biết agent
có vấn đề trước khi user phàn nàn.