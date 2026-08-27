# day15 trien khai thuc te dinh huong

**File gốc:** `Phase_1_COMP2010\D28_Day15-trien-khai-thuc-te-dinh-huong\day15-trien-khai-thuc-te-dinh-huong.md`

---

### Triển Khai Thực T ế, Chi Phí Vận

Hành & Định Hướng Chuyên Sâu
AICB-P1 · Ngày 15 · Ngày cuối Phase 1
T ên Giảng Viên
VinUniversity · Phase 1 · 2026

---

### “15 ngày trước bạn chưa biết LLM hoạt

động thế nào. Hôm nay bạn đã có agent
deployed, monitored, và evaluated.
Câu hỏi bây giờ: đi sâu hướng nào?”
Giữ câu hỏi này trong đầu khi học bài hôm nay

---

### Nội Dung Bài Học

1. 15 ngày nhìn lại
2. Triển khai enterprise
3. Cost anatomy
4. Cost optimization
5. Scaling production
6. Skills map recap
7. 3 Track Phase 2
8. Career paths & AMA

---

### Mục Tiêu Ngày 15

■ Hiểu thách thức triển khai enterprise : security, compliance, legacy systems
■ Phân tích cost anatomy của AI system và biết cách tối ưu chi phí
■ Nắm cost optimization strategies: model routing, semantic caching, prompt
compression
■ Nhìn lại skills map đã tích luỹ qua 15 ngày
■ Chọn track Phase 2 phù hợp với mục tiêu nghề nghiệp

---

### 01

15 Ngày Nhìn Lại
T ừ “AI là gì?” đến agent deployed, monitored, evaluated —
một hành trình 15 ngày xây dựng năng lực thực chiến

---

### Timeline: Hành Trình 15 Ngày

N1
LLM
N2
Bài toán
N3
Agent
N4
T ool Call
N5
Product
N6
PM
N7
Data
N8
RAG
N9
Multi
N10
UX
N11
Safety
N12
Deploy
N13
Monitor
N14
Eval
N15
Wrap-up
Nền tảng
Xây dựng
Production
3 giai đoạn: Hiểu nền tảng (N1–5) → Xây dựng hệ thống (N6–10) → Đưa lên production
(N11–15)

---

### Milestones Đã Đạt Được

Kỹ thuật
■ Gọi LLM API, so sánh models
■ Build ReAct agent + tool calling
■ RAG pipeline grounded
■ Multi-agent + MCP
■ Guardrails + safety testing
Sản phẩm
■ Problem statement + PRD
■ UX với trust layer
■ Deployed trên cloud
■ Monitoring + alerting
■ Evaluation + benchmark
Thông điệp
Bạn không chỉ học lý thuyết. Bạn đã build, deploy, monitor, và evaluate một
AI product thật.

---

### 02

Triển Khai Enterprise
Lab deploy lên Railway là bước đầu. Enterprise có thêm
security policies, compliance, legacy systems, và network
restrictions

---

### Enterprise Challenges

Security & Compliance
■ Data không được rời khỏi VN
■ PII phải encrypted at rest
■ Audit trail cho mọi AI decision
■ Compliance: PDPA, ngành tài
chính
T echnical Constraints
■ Legacy systems, mainframe
■ Network restrictions,
air-gapped
■ On-premise infrastructure only
■ Limited GPU resources
Lưu ý: Enterprise deploy khác startup deploy. Không phải mọi thứ đều “push
lên cloud” được. Đôi khi LLM phải chạy on-premise.

---

### On-Premise vs Cloud vs Hybrid

Cloud API On-Premise Hybrid
Data control Thấp Cao nhất T uỳ chọn
Setup time Phút T uần–tháng T uần
Cost model Per-token Capex + GPU Mixed
Performance Nhanh T uỳ hardware T uỳ routing
Best for MVP, startup Bank, gov Enterprise
Trend 2025–2026
Hybrid đang trở thành default cho enterprise VN: sensitive data on-prem , non-
sensitive qua cloud API.

---

### Self-Hosted LLM: vLLM & Ollama

vLLM
Production-grade inference.
PagedAttention, continuous batch-
ing.
Dùng khi: cần throughput cao, có
GPU server
Ollama
Run models locally, dễ setup.
Download model, chạy 1 lệnh.
Dùng khi: dev, demo, edge deploy-
ment
Lưu ý: Self-hosted tiết kiệm khi volume cao (> 1M tokens/ngày). Dưới mức đó,
cloud API rẻ hơn khi tính cả chi phí GPU, ops, và maintenance.

---

### 03

Cost Anatomy Của AI System
AI agent production không chỉ tốn tiền token. Hiểu đầy đủ
cost structure mới optimize đúng chỗ

---

### Cost Breakdown

API T okens
Input + Output
Compute
CPU/GPU
Storage
Vector DB
Human
Review
Ops
Monitor
40–60% 15–25% 5–10% 10–15% 5–10%
Insight
API tokens chiếm 40–60% cost. Optimize token usage là ROI cao nhất cho
hầu hết AI systems.

---

### LLM API Cost Calculator

Công thức
Monthly cost =
(avg input tokens + avg output to-
kens)
× price per token
× requests per day
× 30 ngày
Ví dụ thực tế
1000 tokens/request
$3/1M input tokens (Sonnet)
500 requests/ngày
= 1000 × $0.000003 × 500 × 30
= $45/tháng chỉ LLM API
Lưu ý: Hidden costs thường gấp 1.5–2x API cost: retry overhead, guardrails
LLM calls, monitoring, eval pipeline. Budget phải tính tổng, không chỉ API.

---

### Budget Planning: 3-Tier Model

Tier Traffic Estimated cost Stack
MVP < 100
req/ngày
$50–
200/tháng
Cloud API + Rail-
way
Growth 100–5K
req/ngày
$200–
2K/tháng
Cloud API +
ECS/Cloud Run
Scale > 5K req/ngày $2K+/tháng Hybrid / self-
hosted
Nguyên tắc
Bắt đầu MVP tier. Chỉ upgrade khi traffic thật sự đòi hỏi. Premature optimization is
the root of all evil.

---

### 04

Cost Optimization Strategies
Khi cost bắt đầu đáng kể, 4 strategies sau giúp giảm 30–
70% chi phí mà không ảnh hưởng chất lượng

---

### 4 Strategies Chính

1. Model Routing
Cheap model (Haiku) cho simple
tasks.
Expensive model (Opus) chỉ cho
complex.
Tiết kiệm: 40–60% token cost
2. Semantic Caching
Cache LLM responses cho similar
queries.
Dùng embedding similarity để match.
Tiết kiệm: 20–40% nếu queries lặp
nhiều
3. Prompt Compression
Tóm tắt context trước khi gửi LLM.
Giảm token count mà giữ thông tin.
Tiết kiệm: 15–30% input tokens
4. Self-Hosted Models
vLLM, Ollama cho high-volume.
Break-even: khoảng 1M+ to-
kens/ngày.
Tiết kiệm: 50–80% so với API khi
scale

---

### Model Routing — Chi Tiết

User
Request
Complexity
Classifier
Haiku / GPT-4o-mini
Fast + Cheap
Opus / GPT-4o
Strong + Expensive
simple
complex
70% traffic
30% traffic
Kết quả
Nếu 70% requests dùng cheap model (10x rẻ hơn), tổng cost giảm khoảng50%
mà quality gần như không đổi trên simple tasks.

---

### 05

Scaling & Reliability Produc-
tion
Khi agent phục vụ enterprise, cần thêm queue, circuit
breaker, và SLA commitment

---

### Production Patterns

Queue-Based Processing
High load → request queue → smooth
out spikes.
User nhận “đang xử lý” thay vì timeout.
T ool:Redis Queue, Celery, Bull
Circuit Breaker
Khi LLM API down, degrade grace-
fully.
Trả cached response hoặc fallback
message.
Pattern: closed → open → half-open
Horizontal Scaling
Stateless agent → N instances.
Day 12: đã design cho stateless.
Scale: thêm instances khi load tăng
SLA Considerations
Enterprise cần uptime commitment.
99.9% = max 8.7h downtime/năm.
Cần: redundancy, failover, monitor-
ing

---

### 06

Skills Map Sau 15 Ngày
3 competency pillars đã được xây dựng — mỗi pillar mở ra
một career direction khác nhau

---

### Skills Map — 3 Pillars

CP3: AI Engineering
■ LLM API
■ ReAct Agent
■ Prompt Engineering
■ Tool Calling
■ Embedding
■ RAG Pipeline
■ Multi-Agent
■ Guardrails
■ Evaluation
CP2: Infrastructure
■ Vector Store
■ Data Pipeline
■ Docker
■ Cloud Deploy
■ Monitoring
■ Structured Logging
■ Tracing
CP1: Business
■ Problem Statement
■ AI Readiness
■ PRD
■ Risk Assessment
■ ROI Analysis
■ UX Design
■ Cost Analysis
Sau 15 ngày: bạn đã có deployed, monitored, evaluated AI product + skills across 3
pillars.

---

### 07

Market Intelligence & Định
Hướng Nghề Nghiệp Sâu
Trước khi chọn track Phase 2, hãy nhìn thị trường việc làm
AI toàn cầu qua lăng kính của WEF, McKinsey, Stanford
HAI, và chính các AI lab lớn nhất thế giới

---

### Thị Trường Việc Làm AI T oàn Cầu Đến 2030

170M
Việc làm mới
được tạo ra
92M
Việc làm bị mất đi
+78M
Tăng trưởng
ròng (+7%)
Bức tranh lớn
86% nhà tuyển dụng kỳ vọng AI sẽ biến đổi doanh nghiệp của họ đến 2030.
Nhưng 63% coi khoảng cách kỹ năng là rào cản lớn nhất — cơ hội không tự
động biến thành việc làm nếu thiếu kỹ năng đúng.
Nguồn: World Economic Forum, Future of Jobs Report 2025

---

### Việt Nam Trong Bức Tranh T oàn Cầu

Chỉ số Việt Nam T oàn cầu
Tổ chức có chương trình AI đang
chạy
96% 88%
Skills gap là rào cản chuyển đổi 78% 63%
Kế hoạch cắt giảm nhân sự vì AI 58% 41%
Kế hoạch reskilling để làm cùng
AI
52% 77%
Cải thiện phát triển nhân tài nội
bộ
≈0% 84%
Đọc vị: nhu cầu AI ở Việt Nam cao hơn thế giới, nhưng năng lực đào tạo lại nội bộ yếu hơn
nhiều — vừa là cơ hội vừa là lời cảnh báo cho sinh viên được đào tạo bài bản.
Nguồn: World Economic Forum, Future of Jobs Report 2025 — Vietnam Country Profile

---

### Nghịch Lý 2025–2026: Đầu Tư T ối Đa, Cắt Giảm T ối Đa

Đầu tư kỷ lục
■ Big Tech capex 2025: ~$325 tỷ
(+46% Y oY)
■ Hướng dẫn 2026: $725 tỷ (+77%)
■ Đầu tư AI doanh nghiệp toàn cầu:
$252.3 tỷ (2024) → $581.7 tỷ
(2025, +130%)
Nguồn: Stanford HAI AI Index 2025/2026; CNBC
Cắt giảm song song
■ Amazon: cắt 14.000 + 16.000 vị
trí (2025–2026)
■ Meta: cắt 8.000 (10% nhân sự)
■ Microsoft: 8.750 nghỉ hưu tự
nguyện
“Chúng tôi sẽ cần ít người hơn cho một
số công việc đang làm hôm nay.”
— Andy Jassy, CEO Amazon
Nguồn: CNBC (2025–2026)

---

### T ốc Độ Áp Dụng AI Đang T ăng T ốc

88%
Tổ chức dùng AI ở ít nhất 1
chức năng (McKinsey 2025)
72%
Dùng generative AI — tăng
vọt từ 33% năm 2024
300%+
Tăng trưởng AI hiring toàn
cầu trong 8 năm (LinkedIn)
20x
Số người thêm AI skill vào
hồ sơ từ 2016 (LinkedIn)
Nguồn: McKinsey State of AI 2025; LinkedIn Work Change Report 2025

---

### Nghề Nào Được Lợi, Nghề Nào Chịu Rủi Ro?

Các báo cáo lớn dùng nhiều khái niệm dễ nhầm lẫn. Hiểu đúng 3 khái niệm sau trước
khi đọc số liệu.
Exposure (phơi nhiễm) — bao nhiêu % nhiệm vụ có thể được AI hỗ trợ/thực hiện
— KHÔNG đồng nghĩa mất việc
Automation vs Augmentation — AI thay thế hoàn toàn nhiệm vụ, hay hỗ trợ con
người làm tốt hơn
Net employment change — số liệu thực tế việc làm tăng/giảm — con số quan
trọng nhất nhưng khó đo nhất

---

### Nghề T ăng Trưởng: Được AI Khuếch Đại

T op nghề tăng trưởng (WEF)
1. Big Data Specialists
2. FinTech Engineers
3. AI/ML Specialists
4. Software Developers
5. DevOps Engineers
Vì sao tăng trưởng
Wage premium kỹ năng AI: 56% trung
bình (PwC), có ngành tới 118%
Việc làm cần kỹ năng AI tăng nhanh
gấp 8 lần thị trường chung
Năng suất ngành phơi nhiễm AI cao:
tăng gần 4 lần (2018–2024)
Lưu ý
Việc làm vẫn tăng ngay cả ở nghề dễ tự động hoá nhất (PwC) — nỗi lo mất
việc hàng loạt chưa xảy ra trên diện rộng.
Nguồn: World Economic Forum 2025; PwC Global AI Jobs Barometer 2025

---

### Nghề Suy Giảm: Bị AI Thay Thế

T op nghề suy giảm (WEF)
1. Postal Service Clerks (–40%)
2. Bank Tellers (–35%)
3. Data Entry Clerks (–34%)
4. Cashiers/Ticket Clerks
5. Administrative Assistants
Mức độ phơi nhiễm
40% việc làm toàn cầu phơi nhiễm
AI (IMF): 60% (nước phát triển), 40%
(mới nổi), 26% (thu nhập thấp)
80% lực lượng lao động Mỹ có ≥10%
nhiệm vụ bị ảnh hưởng (Eloundou et
al., Science 2024)
Nghề phơi nhiễm cao nhất: biên phiên
dịch viên
Lưu ý: Nghịch lý: nghề lương cao có xu hướng phơi nhiễm AI cao hơn nghề
lương thấp — ngược với làn sóng tự động hoá/robot trước đây.

---

### Case Study Cân Bằng: Tự Động Hoá Không Phải Lúc Nào Cũng Thắng

Klarna: Cắt Rồi Phải Tuyển Lại
Cắt từ 5.500 xuống 3.400 nhân sự,
thay bằng chatbot AI (2024)
Sau đó: chất lượng dịch vụ giảm,
khách hàng phàn nàn → tuyển lại
người
“Luôn phải rõ ràng với khách hàng
rằng sẽ luôn có một con người nếu bạn
muốn.”
— Sebastian Siemiatkowski, CEO
Klarna
Nguồn: Fast Company; Entrepreneur (2025)
Lập Trình Viên Trẻ: T ác Động Đã
Xảy Ra Thật
Việc làm lập trình viên 22–25 tuổi:
giảm ~20% so với 2024
Tỷ lệ thất nghiệp SV mới ra trường CS:
6.1% vs 4.3% trung bình Mỹ
“Tại sao thuê junior $90K khi GitHub
Copilot chỉ tốn $10?”
— kỹ sư senior, khảo sát CIO.com
Nguồn: Stanford HAI AI Index 2026; CIO.com

---

### Việt Nam: Ngành Nào Phơi Nhiễm AI Cao Nhất?

Ngành Mức độ phơi
nhiễm AI
Tài chính & Bảo hiểm 82.6%
Bán buôn & Bán lẻ 76.3%
Thông tin & Truyền thông 74.3%
Đọc vị: phơi nhiễm cao không đồng nghĩa mất việc — đây là ngành có nhiều nhiệm vụ có
thể được AI hỗ trợ, cơ hội để tăng năng suất nếu biết dùng AI đúng cách, thay vì lo sợ bị
thay thế.
Nguồn: IMF SDN/2024/001, phân tích theo ngành cho Việt Nam

---

### Tương Lai & Chọn Track Cho Chính Bạn

Ngay cả những người tạo ra AI cũng đang tranh luận về tương lai việc làm. Đừng
hoảng loạn theo một tuyên bố đơn lẻ — hãy nhìn toàn cảnh và tự quyết định.
4 câu hỏi sẽ giúp bạn chọn đúng track:
1. Chuyên gia AI nói gì — và họ có thực sự đồng thuận không?
2. Việc làm junior có thực sự bị đe doạ?
3. Kỹ năng nào vẫn bền vững dù AI phát triển đến đâu?
4. Track nào phù hợp với sở thích, khả năng, và mức độ chấp nhận rủi ro của
bạn?

---

### Ngay Cả Chuyên Gia Cũng Thay Đổi Quan Điểm

5/2025 — Cảnh báo mạnh
“AI có thể xoá sổ 50% việc làm văn phòng entry-level, thất nghiệp có thể lên 10–20%.” — Dario Amodei,
CEO Anthropic (Axios)
1/2026 — Giữ nguyên lập trường
Amodei tiếp tục cảnh báo trong essay “The Adolescence of Technology” ; dự báo AGI có thể chỉ còn 1–2
năm
5/2026 — Đổi giọng cùng lúc với Altman
“T ự động hoá 90% công việc nghĩa là con người làm 10% còn lại nhưng năng suất tăng gấp 10 lần.”— Amodei
viện dẫn Jevons Paradox (Fortune). Cùng tuần, Sam Altman thừa nhận: “trực giác của tôi đã sai” về tác
động entry-level (Time)
Nguồn: Axios 5/2025; darioamodei.com 1/2026; Fortune & Time 5/2026

---

### Cuộc Tranh Luận: Có Nên Lo Về Việc Làm Junior?

Phe Cắt Giảm
“Chúng tôi sẽ không tuyển thêm kỹ sư
phần mềm năm sau vì năng suất đã
tăng hơn 30% nhờ AI.”
— Marc Benioff, CEO Salesforce
22% CHRO xác nhận có lãnh đạo đã
ngừng tuyển entry-level vì AI (Gart-
ner)
Nguồn: Salesforce Ben; Gartner 2025–2026
Phe Phản Bác
“Ý tưởng AI thay thế lập trình viên junior
là một trong những điều ngu ngốc nhất
tôi từng nghe.”
— Matt Garman, CEO AWS
IBM: tăng gấp 3 lần tuyển dụng entry-
level tại Mỹ năm 2026
Nguồn: phát biểu công khai Matt Garman; IBM (Arvind Krishna),
2026

---

### Kỹ Năng Bền Vững Trong Kỷ Nguyên AI

Dữ liệu thực đo, không chỉ là quan điểm
Lao động 15+ năm kinh nghiệm đánh giá năng lực AI hiện tại thấp hơn ~10 điểm % so với lao động năm đầu
— vì AI “thiếu phán đoán, nhận thức ngữ cảnh, và suy luận tình huống” (Anthropic Economic Index, 6/2026)
Khảo sát ngành nhân sự
Khi được hỏi kỹ năng con người nào quan trọng hơn khi AI đảm nhận nhiều việc hơn: kiểm soát chất lượng
đầu ra AI (50%) và tư duy phản biện (46%) đứng đầu (Korn Ferry TA Trends 2026)
Andrew Ng
“Chỉ một phần nhỏ công việc của kỹ sư phần mềm là viết code.” — kỹ năng còn giá trị: thu thập yêu cầu,
thiết kế hệ thống, giao tiếp liên chức năng.
Nguồn: Ai4 2026 conference; Anthropic Economic Index; Korn Ferry

---

### Ba Nhóm Nghề AI: Từ Nghiên Cứu Đến Sản Phẩm

Trước khi quyết định track, hãy nhìn cụ thể vào 3 nhóm nghề mà 3 track Phase 2 dẫn
tới — mỗi nhóm có tốc độ tăng trưởng, mức lương, và rào cản gia nhập khác nhau.
AI Engineer
#1 fastest-growing job title
(LinkedIn, 2 năm liên tiếp)
AI Infrastructure
Kỹ năng khó tuyển #1 toàn
cầu (ManpowerGroup
2026)
AI Product
Tăng trưởng +300%/3 năm,
nhưng thiếu cửa junior

---

### AI Engineer / AI Researcher

Demand & Lương
#1 fastest-growing job title 2 năm liên
tiếp (LinkedIn)
ML Engineer trung vị: $272.5K (lev-
els.fyi)
Frontier lab: OpenAI SWE $253K–
$1.27M+
Case cực đoan: gói đãi ngộ re-
searcher tới $1.5 tỷ (Meta, bị từ chối)
Rào Cản Gia Nhập
Research track: gần như bắt buộc
PhD (OpenAI/DeepMind/FAIR)
Applied track: cử nhân/thạc sĩ +
portfolio mạnh là đủ
PhD mới tại Mỹ/Canada tăng 22%
(2022–2024) nhưng phần lớn vào
academia, không phải industry
Nguồn: LinkedIn Jobs on the Rise 2025; levels.fyi; Stanford HAI AI Index 2025; TechCrunch

---

### AI Infrastructure: Nhóm Khó Tuyển Nhất Thế Giới

Demand & Lương
MLOps: tăng trưởng 9.8x trong 5 năm
(LinkedIn Emerging Jobs)
Senior/staff MLOps: $257K–$312K
Chi tiêu hạ tầng AI toàn cầu: $334
tỷ (2025) → $497 tỷ (2026) → vượt
$1.000 tỷ vào 2029 (IDC)
Khan Hiếm Nhân Sự
“AI Model & Application Develop-
ment” là kỹ năng khó tìm #1 toàn cầu
— vượt qua mọi ngành kỹ thuật truyền
thống
20% nhà tuyển dụng toàn cầu xác
nhận đây là kỹ năng khó tìm nhất
72% doanh nghiệp toàn cầu khó tuyển
được nhân sự phù hợp
Nguồn: ManpowerGroup 2026 Global Talent Shortage Survey; IDC AI Infrastructure Spending; LinkedIn Emerging Jobs

---

### AI Product: T ăng Trưởng Nhanh Nhưng Thiếu Cửa Junior

Demand & Lương
AI PM postings: +300% trong 3 năm,
nhân đôi năm 2025
Lương trung vị AI PM: $194–197K (hội
tụ Glassdoor & axialsearch)
AI Strategist: $208K trung vị, $279K
ở cấp Director
OpenAI PM trung vị: ~$860K
Lưu ý: Chỉ 2% postings AI PM là
cấp junior — 47% là cấp Manager+.
AI Strategist còn nghiêng hơn: 69–
80% là Director/VP/C-suite. Thị
trường “nóng nhưng chưa có lộ
trình sự nghiệp rõ ràng cho người
mới bắt đầu”.
Nguồn: axialsearch Labor Market Analysis 2026; Glassdoor; levels.fyi

---

### So Sánh T ổng Hợp: 3 Nhóm Nghề

Tiêu chí Engineer/Researcher Infrastructure Product
Tăng trưởng #1 fastest-growing title (2
năm)
9.8x/5 năm (MLOps) +300%/3 năm
Lương trung vị $272.5K (ML Engineer) $257–312K (senior) $194–208K
Rào cản gia nhập PhD (research) / portfolio
(applied)
2–3 năm kinh nghiệm liền kề Portfolio sản phẩm, ít đòi
bằng cấp sâu
Độ khó tuyển Cao ở tier elite Khó nhất thế giới (Man-
powerGroup #1)
Thiếu cửa junior, không
thiếu ứng viên
Nguồn: Tổng hợp LinkedIn, levels.fyi, ManpowerGroup, axialsearch (2025–2026)

---

### Chọn Track: Framework Cá Nhân Hoá

Trục Track 1 — Product Track 2 — Infra Track 3 — Application
Cơ hội thị trường Tăng nhanh (+300%/3
năm), ít cửa junior
Khó tuyển nhất thế giới
(ManpowerGroup)
#1 fastest-growing title 2
năm liên tiếp
Độ khó gia nhập Thấp–trung bình: portfo-
lio hơn bằng cấp
Trung bình–cao: cần nền
tảng hệ thống
Cao (research) / trung
bình (applied)
Phù hợp sở thích Kinh doanh, chiến lược,
giao tiếp đa bên
Hệ thống, vận hành, độ
tin cậy quy mô lớn
Thuật toán, xây dựng sản
phẩm kỹ thuật
Rủi ro AI tác động
ngược
Thấp — vai trò phán đoán
khó tự động hoá
Thấp — vẫn cần giám sát
hạ tầng dài hạn
Trung bình ở phần code
cơ bản (junior dev bị ảnh
hưởng nhiều nhất)
Việt Nam 2030 — cơ hội cho chính bạn
Chiến lược AI Quốc gia đặt mục tiêu đào tạo 500.000 lao động có kỹ năng AI, trong đó 50.000 chuyên gia trình độ cao — đến 2030. Không
có track “đúng tuyệt đối”; chọn theo giao điểm sở thích, năng lực, và mức độ sẵn sàng của chính bạn.
Nguồn: Vietnam National Strategy on AI to 2030; Digital Policy Alert

---

### 08

3 Track Giai Đoạn 2
Phase 1 cho nền tảng chung. Phase 2 đi sâu theo hướng
bạn chọn — mỗi track 3 tuần chuyên sâu

---

### Track 1 — AI Business & Product

Nội dung chính
■ Product Strategy cho AI products
■ Financial Modeling & ROI
■ AI Governance & Compliance
■ AI Act & regulatory landscape
■ Go-to-market cho AI products
Phù hợp với ai
Người muốn làm:
AI Product Manager
AI Business Analyst
AI Strategist
Output
Business plan cho AI product + financial model + compliance checklist + go-
to-market strategy.

---

### Track 2 — AI Infrastructure & Data

Nội dung chính
■ Lakehouse & Feature Store
■ vLLM deployment & optimization
■ CI/CD cho AI (LLMOps)
■ GPU FinOps & cost management
■ Production data pipeline
Phù hợp với ai
Người muốn làm:
AI Data Engineer
Platform Engineer
MLOps Engineer
Output
Production-grade data pipeline + self-hosted LLM + CI/CD pipeline + moni-
toring dashboard.

---

### Track 3 — AI Application

Nội dung chính
■ Advanced Agent patterns
■ Memory & long-term context
■ GraphRAG & knowledge graphs
■ Fine-tuning & model customization
■ Production evaluation systems
Phù hợp với ai
Người muốn làm:
AI Engineer
LLM Engineer
AI Agent Developer
Output
Advanced agent system + custom fine-tuned model + production eval
pipeline + technical portfolio.

---

### Chọn Track Như Thế Nào?

Thích business
hay technical?
Track 1
Business
Thích infra
hay app?
Track 2
Infra
Track 3
Application
business technical
infra app
Lưu ý: Không có track “đúng” hay “sai”. Chọn theo mục tiêu nghề nghiệp và
hứng thú cá nhân . Có thể đổi track sau tuần đầu nếu cần.

---

### 09

Career Paths & Kết Thúc
Phase 1
15 ngày, 15 labs, 1 deployed product. Bạn không còn là
beginner — bạn là builder

---

### Career Paths Sau Khoá Học

Pillar Roles Track Demand
CP1 AI PM, AI BA, AI
Strategist
Track 1 Cao, khan
hiếm
CP2 AI Data Engi-
neer, Platform
Eng, MLOps
Track 2 Rất cao
CP3 AI Engineer, LLM En-
gineer, Agent Dev
Track 3 Cao nhất
VSF Internship
T ừ portfolio khóa học→ dự án thực tế tại Vingroup. Portfolio mạnh = cánh cửa mở.

---

### AMA — Ask Me Anything

Open Q&A Session
Mọi câu hỏi về kỹ thuật, career, track selection, hoặc bất kỳ điều gì bạn muốn
hỏi.
Câu hỏi hay gặp nhất:
■ “Track nào dễ xin việc hơn?” — Cả 3 đều thiếu người. Chọn theo thế mạnh.
■ “Fine-tuning có cần không?” — 80% use cases không cần. RAG + prompt đủ.
■ “AI sẽ thay lập trình viên không?” — AI thay code, không thay builder.

---

### Final Assignment

Trước Ngày 16
1. Hoàn thành track selection form
2. Submit portfolio link
(GitHub/demo URL)
3. Cost analysis cho agent (Lab 15)
4. Final presentation (10 phút)
Portfolio nên có
■ Deployed agent URL
■ Monitoring dashboard
screenshot
■ Evaluation report + RAGAS
scores
■ README giải thích architecture
■ Cost analysis

---

### T ổng kết — Key T akeaways

Những ý chính cần nhớ trước khi sang bài tiếp theo
1 Enterprise deploykhác startup: security, compliance, on-premise, hybrid. Hiểu con-
text trước khi chọn architecture.
Cost optimization: model routing, semantic caching, prompt compression. API to-
kens chiếm 40–60% cost — optimize đúng chỗ.
3 pillars, 3 tracks: CP1 (Business) → Track 1, CP2 (Infra)→ Track 2, CP3 (Application)
→ Track 3. Chọn theo mục tiêu.
4 Y ou are no longer beginners — you are builders.15 ngày, 15 labs, 1 deployed product.
Phase 2 đi sâu hơn.

---

### T ài Liệu Tham Khảo

1. Anthropic & OpenAI Pricing Docs — anthropic.com/pricing, platform.openai.com/tokenizer.
Cost calculator.
2. vLLM Documentation — docs.vllm.ai. Self-hosted LLM inference, PagedAttention,
quantization.
3. Strubell et al. (2019), Energy and Policy Considerations for Deep Learning in NLP —
arXiv:1906.02243.
4. Market Intelligence (Section 7): WEF Future of Jobs Report 2025, McKinsey State of AI 2025,
Stanford HAI AI Index 2025/2026, LinkedIn Work Change Report, IMF SDN/2024/001, PwC AI
Jobs Barometer 2025, Goldman Sachs, Anthropic Economic Index, ManpowerGroup 2026,
Gartner, IDC — danh mục đầy đủ tại day15-career-market-research.md.

---

### Hỏi & Đáp

15 ngày từ zero đến deployed AI product. Phase
2 bắt đầu hành trình chuyên sâu của bạn.

---

### Cảm ơn!

Tên Giảng Viên
Email: a.nguyen@vinuni.edu.vn
Tài liệu: github.com/vinuni/aicb-materials
Chúc mừng hoàn thành Phase 1!