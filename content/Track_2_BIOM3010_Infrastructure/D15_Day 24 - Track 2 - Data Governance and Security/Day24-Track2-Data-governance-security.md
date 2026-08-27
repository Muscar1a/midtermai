# Day24 Track2 Data governance security

**File gốc:** `Track_2_BIOM3010_Infrastructure\D15_Day 24 - Track 2 - Data Governance and Security\Day24-Track2-Data-governance-security.md`

---

### Data Governance

& AI Security
AICB-P2T2 · Ngày 24 · Chương 5: Vận Hành
Giảng viên
VinUniversity · Phase 2 · Track 2 · T uần 5

---

### “Data governance ngày xưa trả lời

câu hỏi: “ai được đọc bảng này?” —
nhưng bây giờ người đọc là một agent
biết hành động , dùng credential của
bạn, trên input không đáng tin, ở tốc
độ máy. Vậy đơn vị phân quyền của
bạn còn là table grant nữa không?”
Giữ câu hỏi này trong đầu khi học bài hôm nay

---

### Nội Dung Bài Học

1. T ừ Data Governance sang Agent
Governance
2. Threat Model: OWASP ASI Top 10
(2026)
3. Identity & Authorization cho Agent
4. Data-Layer Controls: PII, Erasure,
Secrets
5. Compliance: Luật 91/2025, NĐ
356/2025, EU AI Act
6. Frontier: AI vs AI (offense &
defense)
7. Live Demo & Lab 24
Ngày canonical về security: Day 22 lo guardrails,
Day 23 lo telemetry, Day 26 lo MCP/A2A protocol,
Day 27 lo lineage — hôm nay lo threat model & control
plane.

---

### Mục Tiêu & Deliverable Cuối Ngày

Sau buổi học, bạn sẽ
1. Dựng threat model cho agent có quyền truy
cập dữ liệu (OWASP ASI Top 10)
2. Thiết kế authorization tại tầng tool-call,
không chỉ RBAC trên bảng
3. Triển khai containment cho lethal trifecta &
chứng minh bằng attack/re-attack
4. Map Luật 91/2025 + NĐ 356/2025 →
technical control → evidence
Artifact cần nộp
■ Repo agent có 4 control (mỗi control 1
commit)
■ Attack/contain report: log trước–sau
của cùng một payload
■ injection-corpus.md: ≥5 biến thể +
block rate
■ DPIA-lite + bảng requirement →
control → evidence
■ PII detection rate >95% trên VN test
set

---

### 01

Từ Data Governance sang
Agent Governance
Vì sao mô hình phân quyền cũ vỡ khi người đọc dữ liệu là
một agent biết hành động

---

### Ba Dịch Chuyển Làm Vỡ Mô Hình Cũ

Governance cũ (2020–2023) Agent era (2026)
Ai truy cập Human user qua BI tool / note-
book
NHI / agent — tỉ lệ NHI:human 90:1, có nơi
144:1
Input Query có cấu trúc, do người
viết
Nội dung không đáng tin — doc, email,
web page, tool output
Blast radius Đọc sai một bảng Hành động — gọi API, ghi DB, gửi mail, chi
tiền
Lưu ý: Agent không phải service account. Service account thi hành lệnh định trước ; agent diễn giải mục
tiêu và tự chọn hành động . Mọi control kế thừa từ thời service account đều thiếu một chiều: agency.

---

### Governance Control Plane — 5 Lớp

Policy — điều gì được phép: data contract, purpose, classification
Identity — ai/cái gì đang hành động: per-agent identity, delegation chain
Enforcement (PEP) — chặn tại tool call, TRƯỚC khi execute
Data controls — minimization, PII, masking, encryption, retention
Evidence — audit ledger append-only → nguyên liệu cho compliance
Thiếu 1 lớp
= governance
trên giấy
Điểm quyết định đã dịch chuyển: từ “grant trên catalog” (một lần, tĩnh) sang “runtime check tại mỗi tool call”
(liên tục, có ngữ cảnh).

---

### Classification × Agency — Ma Trận Thật Sự

Cấp độ dữ liệu read-summarize read-transform write export / egress
Public ✓ ✓ ✓ ✓
Internal ✓ ✓ ✓ policy
Confidential ✓ ✓ policy ×
Restricted (PII) no-egress run policy × ×
Đọc bảng: classification không chỉ drive policy — nó drive agency: agent được làm gì với dữ liệu đó. “ no-egress
run” = được đọc, nhưng chỉ trong run không có network (xem §6). Đây là bản upgrade của bảng 4-cấp truyền
thống: thêm trục hành động, vì agent hành động chứ không chỉ đọc.

---

### Governance Stack & Artifact Phải Sinh Ra

Ba lớp chuẩn — đừng chọn 1
■ EU AI Act — luật: yêu cầu pháp lý bắt
buộc
■ NIST AI RMF — phương pháp: Govern /
Map / Measure / Manage
■ ISO/IEC 42001 — chuẩn certifiable:
bằng chứng audit được
Mapping: Govern ↔ Clause 5–6, Map↔ impact
assessment, Measure ↔ monitoring, Manage ↔
operational controls.
Năm artifact bắt buộc
1. Data contract — schema + purpose +
retention
2. AIBOM + agent card — model, tool, MCP
server nào đang chạy
3. DPIA / hồ sơ đánh giá tác động
4. Policy-as-code repo — có PR review
history
5. Audit ledger — append-only, mọi tool
call
Quy tắc: governance không phải file PDF viết tay mỗi kỳ audit — là artifact máy đọc được và tự sinh evidence.
(Catalog & lineage: xem Ngày 27.)

---

### 02

Threat Model cho Agentic
System
OWASP ASI Top 10 · lethal trifecta · memory poisoning ·
MCP supply chain

---

### OWASP T op 10 for Agentic Applications (12/2025)

■ ASI01 Agent Goal Hijack — coi mọi nội dung
retrieved là untrusted
■ ASI02 T ool Misuse— least-agency scoping,
validate parameter
■ ASI03 Identity & Privilege Abuse — per-agent
identity, token ngắn hạn
■ ASI04 Agentic Supply Chain — component có
signature, AIBOM
■ ASI05 Unexpected Code Execution — sandbox,
egress deny-by-default
■ ASI06 Memory & Context Poisoning — validate
memory write
■ ASI07 Insecure Inter-Agent Comms — mutual
auth, signed message
■ ASI08 Cascading Failures — blast-radius
isolation, circuit breaker
■ ASI09 Human-Agent Trust Exploitation —
forced confirmation
■ ASI10 Rogue Agents — behavioral monitoring,
kill switch
Khác gì OWASP T op 10 for LLM?
LLM Top 10 nói về model như bộ sinh text. ASI Top 10 nói về model như actor: có credential, memory, tool,
và quyền tự chuỗi hành động nhiều bước. Công bố 09/12/2025, >100 chuyên gia tham gia.

---

### Lethal Trifecta — Vì Sao Không Thể “Vá”

Private data
mail, DB, file, memory
Untrusted content
doc, web, tool output
Exfil vector
HTTP, link, image, API
Đủ 3 chân
= mạch đóng
Case study: Claude Cowork, 01/2026
■ 48 giờ sau launch (13/01/2026), PromptArmor
demo full chain
■ File Word chứa white text vô hình → prompt
injection
■ Agent upload tài liệu tài chính của user (có SSN
một phần) lên account Anthropic của attacker
— attacker nhúng API key của mình vào injection
■ Lỗi Files API exfiltration đã báo qua HackerOne
từ 10/2025, chưa fix khi Cowork launch
Lưu ý: Model thông minh hơn không phải phòng thủ — LLM nhận lệnh và dữ liệu
trên cùng một token stream, không có ranh giới kiến trúc nào tách chúng. Và
bỏ chân nào của trifecta cũng làm agent vô dụng→ chuyển từpreventionsang
containment (§6).

---

### Memory & Context Poisoning (ASI06)

T ấn công vào bộ nhớ
■ PoisonedRAG: chỉ 5 document độc
trong corpus hàng triệu → RAG trả lời
theo ý attacker 90% với truy vấn mục
tiêu
■ AI Recommendation Poisoning
(Microsoft, 02/2026): làm bẩn
persistent memory để lái quyết định tài
chính & vận hành ở quy mô enterprise
■ Đặc điểm: tấn công một lần, ảnh hưởng
mọi session sau
Controls
■ Validated memory write — ai/cái gì
được phép ghi vào memory?
■ Provenance + chữ ký nguồn — hash
document, timestamp index
■ TTL / ephemeral context — memory
không mặc định vĩnh viễn
■ Versioning embedding — biết khi nguồn
đổi
■ T argeted rollback— xoá đúng entry có
nguồn bẩn
Mảnh ghép data-governance ↔ agent: agent memory là một data store. Nó cần classification, retention,
audit và quyền xoá — y như một bảng trong warehouse.

---

### Supply Chain & MCP (ASI04 + ASI02)

Attack vector của MCP
■ T ool poisoning— mô tả tool độc nằm ở
phần context user không thấy (tương
đương indirect prompt injection)
■ Rug pull — tool đổi hành vi sau khi đã
được approve
■ Cross-server tool shadowing
■ Confused deputy & token passthrough
■ SSRF qua tool connector; rogue server
registration
Controls
■ OAuth 2.1 + PKCE bắt buộc cho
user-facing flow
■ T oken exchange (RFC 8693)— không
forward token upstream xuống
downstream
■ Tool definition immutable + versioned +
signed (hướng ETDI)
■ MCP allowlist + internal registry + review
cadence
Lưu ý: >30 CVE nhắm MCP server / client / infra chỉ trong01–02/2026. MCP
spec không có phòng thủ native cho tool poisoning hay rug pull — đó là việc
của bạn. (Protocol & routing: xem Ngày 26.)

---

### 03

Identity & Authorization cho
Agent
Non-human identity, delegation chain, và policy-as-code
tại tool call

---

### Non-Human Identity — Bài T oán Chính

90:1
NHI : human trong
nhiều tổ chức
(có nơi 144:1)
51%
tổ chức không
có ownership
rõ ràng cho NHI
92%
tổ chức bị AI-
breach không có
AI access control
Mỗi agent phải có — không có thì không được lên production
■ Business owner — chịu trách nhiệm dùng để làm gì
■ T echnical owner— chịu trách nhiệm chạy thế nào
■ Purpose khai báo được + scope đo được + expiry cụ thể
Không có owner → không ai review, không ai revoke khi mục đích agent thay đổi.

---

### Delegation Chain & Least Agency

User
identity gốc
Agent
identity riêng
Sub-agent
depth ≤ 2
T ool
per-task catalog
Data
row/column scope
on-behalf-of
+ TTL 15 phút
PEP kiểm tra
trước execute
masking
+ audit
Least privilege → least agency
Không chỉ giới hạn dữ liệu agent thấy, mà giới
hạn tool catalog theo từng task . Agent re-
search: search + read, không write. Không cấp
sẵn “mọi tool có thể cần”.
Last mile ở data layer
Unity Catalog / Apache Ranger: row-level +
column-level + dynamic masking. Đây là một
PEP — không phải toàn bộ câu trả lời.

---

### Policy-as-Code tại T ool-Call PEP

# OPA / Rego — gate MOI tool call
package agent.authz
default allow := false
allow if {
input.agent.owner != "" # co owner
input.request.purpose in
data.contracts[input.data.asset].purposes
not blocked
}
blocked if { # chan trifecta
input.data.classification == "restricted"
input.run.egress_enabled
}
blocked if { input.delegation.depth > 2 }
Input của quyết định
■ data.classification — từ catalog
■ request.purpose — từ data
contract
■ agent.owner — từ NHI registry
■ delegation.depth — chống agent
đẻ agent
■ run.egress_enabled — chân thứ 3
của trifecta
Vì sao ghi reason
■ Ghi decision + reason vào audit
ledger
■ reason chính là evidence cho
compliance (§5)
■ Deny không có lý do = không
debug được, không audit được

---

### 04

Data-Layer Controls
PII gate · anonymization · right-to-erasure · secrets — tất
cả dưới góc nhìn agent

---

### PII Gate Trước Ingestion (Presidio + VN)

from presidio_analyzer import (AnalyzerEngine, Pattern,
PatternRecognizer)
from presidio_anonymizer import AnonymizerEngine
# Recognizer rieng cho PII Viet Nam
cccd = PatternRecognizer(
supported_entity="VN_CCCD", supported_language= "vi",
patterns=[Pattern("cccd", r "\b\d{12}\b", 0.85)])
# vi_engine: xem canh bao ben phai
analyzer = AnalyzerEngine(nlp_engine=vi_engine,
supported_languages=["vi"])
analyzer.registry.add_recognizer(cccd)
def pii_gate(text: str) -> str: # TRUOC moi lan ghi
hits = analyzer.analyze(text=text, language= "vi",
entities=["PERSON", "VN_CCCD", "PHONE_NUMBER"])
return AnonymizerEngine().anonymize(
text=text, analyzer_results=hits).text
Gate chắn ba đích
1. Training set (cách nghĩ cũ)
2. RAG corpus — đọc được là leak
được
3. Agent memory — PII vào là vĩnh viễn
PII đặc thù VN
CCCD 12 số; SĐT +84/0[35789]xx; số tài
khoản, BHXH, biển số; địa chỉ cần custom
NER.
Lưu ý: Presidio không có "vi" sẵn —
phải cấu hình NlpEngineProvider với spaCy
model tiếng Việt ( vi_core_news_lg, com-
munity). Chỗ đa số sinh viên tắc.

---

### Pseudonymization vs Anonymization

Pseudonymization — có thể đảo
■ Thay PII bằng pseudonym nhất quán
■ Đảo được nếu có lookup table → vẫn là
dữ liệu cá nhân về mặt pháp lý
■ Dùng cho: internal analytics, A/B test,
join across table
■ Lookup table phải bảo vệ như PII gốc
Anonymization — không đảo được
■ Không thể re-identify
■ k-anonymity: mỗi record giống ít nhất
k − 1 record khác
■ Generalization: tuổi 32 → nhóm 30–39
■ Synthetic data cho public dataset /
research sharing
Lưu ý: Quy tắc cũ “anonymize trước ingestion” giờ áp cho cả vector store và
agent memory, không chỉ training set. Sai lầm thường gặp 2026: PII được lọc
khỏi training data, nhưng chảy nguyên vẹn vào RAG index.

---

### Right-to-Erasure Xuyên AI Stack

Lakehouse
delete + vacuum
Feature store
online + offline
Vector index
xoá theo doc id
Agent memory
targeted rollback
Logs / traces
cả vendor side
Model weights — không đảo được
Lưu ý: Machine unlearning không phải thứ bạn dám cam kết với cơ quan
quản lý → PII trong model weights là liability vĩnh viễn. Và phải map cả
data flow phía vendor : ví dụ Anthropic áp retention 30 ngày cho safety
monitoring trên Fable 5 — đó là một luồng dữ liệu bạn phải khai trong DPIA.
Thực tế phũ phàng: phần lớn LLM API off-the-shelf không cung cấp log-
ging/lineage/deletion đủ cho audit.

---

### Encryption & Secrets — Góc Nhìn Agent

Encryption (nền, đã học Ngày 16)
■ In transit: TLS 1.3 bắt buộc
■ At rest: AES-256 (KMS managed
key)
■ Column-level cho PII: tên, email,
CCCD
■ Envelope: DEK bọc bởi KEK — KEK
rotate hằng năm, DEK hằng tháng
Secret — mục tiêu exfil số 1
■ Không để long-lived key ở filesystem agent
đọc được — dùng OIDC federation, credential
ngắn hạn
■ Sandbox chặn write thôi là chưa đủ: cho đọc
~/.aws/credentials mà egress không chặn →
vẫn leak
■ Filesystem isolation + network isolation
phải đi cùng nhau
■ Deny rule phải áp cho: subprocess, package
script, child shell, symlink/hardlink, path
traversal, hidden dir, imported script
Đổi khung tư duy: encryption bảo vệ dữ liệu khi bị đánh cắp; secret hygiene ngăn agent tự nguyện đưa chìa
khoá cho attacker.

---

### 05

Compliance: Việt Nam & EU
Luật 91/2025 · NĐ 356/2025 · EU AI Act sau Digital Om-
nibus

---

### Khung Pháp Lý Việt Nam 2026

Luật BVDLCN số 91/2025/QH15
■ Quốc hội thông qua 26/6/2025
■ Hiệu lực 01/01/2026
■ Xác lập quyền: được biết, đồng ý, truy
cập, chỉnh sửa, yêu cầu xoá
■ “Y êu cầu xoá”→ chính là delete cascade
ở slide trước
NĐ 356/2025/NĐ-CP
■ Ban hành 31/12/2025, hiệu lực
01/01/2026
■ 5 chương, 42 điều, phụ lục 10 biểu mẫu
■ Xuyên biên giới: lập hồ sơ đánh giá tác
động trong 60 ngày kể từ ngày chuyển
■ Hồ sơ thiếu → hoàn thiện trong 30 ngày,
không thì xem xét xử phạt hành chính
■ Miễn đánh giá: nhân sự, logistics, thanh
toán quốc tế, khẩn cấp
■ Kiểm tra: định kỳ + đột xuất
Lưu ý: NĐ 13/2023 không còn là khung hiện hành — đừng dùng lại slide cũ.
Và điều quan trọng nhất cho lớp này: gọi LLM API ở nước ngoài là chuyển dữ
liệu cá nhân xuyên biên giới → thuộc diện hồ sơ 60 ngày ở trên.

---

### EU AI Act sau Digital Omnibus (2026)

1 2 3 4
27/7/2026
Digital Omnibus on AI
hiệu lực (OJ 24/7/2026)
02/8/2026
Transparency + AI literacy
— giữ nguyên timeline
02/12/2027
High-risk An-
nex III — đã hoãn
02/8/2028
AI nhúng trong sản phẩm
(Annex I) — đã hoãn
Đã có hiệu lực, không thay đổi
Art.5 bans (unacceptable risk) + nghĩa vụ
provider của GPAI model. AI Office độc quyền
giám sát AI system xây trên GPAI model khi cùng
một provider.
Từ 02/8/2026 bạn phải làm
Disclose khi người dùng đang tương tác với AI;
mark output generative theo dạng machine-
readable. Art.10 (data governance cho high-
risk) buộc phải có đúng bộ artifact ở §1.

---

### Requirement → Control → Evidence

Requirement T echnical control Evidence
Luật 91/2025 — quyền yêu
cầu xoá
Delete cascade (§4) Job log + vector index diff
NĐ 356/2025 — hồ sơ
xuyên biên giới 60 ngày
Data-flow inventory cho mọi
LLM API call
DPIA + biểu mẫu NĐ356
ASI03 — privilege abuse Per-agent identity + STS token
15 phút
IAM report + TTL policy
ISO 42001 Clause 5–6
(Govern)
Policy-as-code repo có review PR history
EU AI Act transparency
(02/8/2026)
Disclosure + output marking Screenshot UI + config
Đây là format bạn phải nộp trong Lab 24. Compliance là build artifact sinh ra từ audit ledger — không phải
văn bản viết tay mỗi kỳ audit.

---

### 06

Frontier: AI vs AI
Offense đã thực sự xảy ra, dual-use frontier model, và kiến
trúc containment

---

### Offense — Những Gì Đã Thực Sự Xảy Ra

80–90%
khối lượng chiến
thuật agent tự
chạy (GTG-1002)
832
account bị
ban vì cyber,
03/2025–03/2026
33→56%
actor medium/high-
risk dùng AI (1,7 ×)
■ GTG-1002 (09/2025, công bố 13/11/2025): actor nghi China-nexus dùng Claude Code orchestration
chạy gần trọn intrusion lifecycle — recon → exploit → credential harvesting → lateral movement → exfil —
trên ∼30 tổ chức, với chỉ 10–20% effort người thường cần. MITRE ATT&CK: campaign C0062.
■ Anthropic × MITRE mapping (2026): 13.873 hành động, 482 technique, đủ 14 tactic; 67,3% dùng AI viết
malware; 6,5% cho lateral movement. Một phần kết quả vào Verizon DBIR 2026.
■ Verizon DBIR 2026: phishing 44% trong initial access có AI hỗ trợ; cửa sổ phản ứng của defender từ
tháng xuống giờ; nhân viên dùng AI trên máy công ty 15%→45%, 67% bằng account cá nhân.
■ Kết luận: số technique không còn tương quan với độ tinh vi — thứ phân biệt actor nguy hiểm là
orchestration. ATT&CK hiện thiếu ID cho hành vi agentic.

---

### Dual-Use Frontier Model — Access Là Governance

Model Mốc Năng lực cyber Cơ chế access
Claude Mythos 04/2026 Chuyên tìm lỗ hổng software Rollout hạn chế vì năng lực
cyber
Claude Fable 5 09/6/2026 Mythos-class, đã làm an toàn
cho general use
Classifier safeguard route
query cyber/bio sang Opus
4.8; retention 30 ngày
Claude Mythos 5 09/6/2026 Cùng model nền, bỏ safeguard
cyber
Chỉ đối tác Project Glass-
wing (cyber defender)
GPT-5.6-Cyber 10/8/2026 95% completion trên task cyber
nâng cao; tìm lỗi high-sev trong
V8
Trusted partner qua chương
trình Daybreak
Điểm dạy
Cả hai lab lớn đều chuyển sang gated capability access. Nghĩa là trong tổ chức của bạn, câu hỏi “ai được
dùng model loại nào, cho mục đích gì, log ra sao ” đã trở thành policy question — thuộc đúng control plane
ở §1, không phải việc của phòng mua sắm.

---

### Defense — Agentic Security trong SDLC

Dependency & container scan — pip-audit, Trivy
SAST — Bandit, Semgrep trong CI
Secret scanning — git-secrets, truffleHog
Agent red-teaming — injection corpus
Agentic scanner + pentest
Tự động trong CI
Có gate người
Agentic scanner đã có thật
■ OpenAI Aardvark → Codex
Security (research preview,
06/3/2026): đọc repo liên tục,
đánh giá exploitability, đề xuất
patch theo commit
■ Google Big Sleep: zero-day đầu
tiên do AI tìm trong production
software (SQLite buffer underflow
OSS-Fuzz bỏ sót nhiều năm)
■ XBOW: agent tự trị #1
HackerOne, 1.060+ submission
validated
Lợi thế defender: bạn có source code,
telemetry, và quyền chặn merge — attacker
không có. Nhưng chỉ có giá trị nếu tự động
hoá.

---

### Containment Architecture — T ổng Hợp Cả Ngày

Run A — đọc untrusted
web, doc, tool output
KHÔNG network, KHÔNG private data
Run B — đọc private data
DB, mail, memory
chỉ nhận typed field từ A
sanitize
→ typed field
Không run nào có cả hai → mạch trifecta không đóng
Năm runtime control
1. Per-user data scoping
2. Per-task tool catalog
3. Allowlisted exfil channel
4. Policy enforcement chặn trước khi execute
5. Audit trail verifiable cho mọi tool invocation
Nền lý thuyết
6 design pattern chống prompt injection (arXiv
2506.08837) + CaMeL (DeepMind). action-
selector: tool output không quay lại agent. dual-
LLM & code-then-execute: mạnh nhất, phức tạp
hơn.
Ví dụ cụ thể: Claude Code = permissions + MCP allowlist + OS sandbox (bubblewrap/seatbelt) — dùng nội bộ
giảm 84% permission prompt.

---

### 07

Demo, Lab & T ổng Kết
Đóng mạch trifecta rồi chặn nó — và ba điều cần mang về

---

### Live Demo: Đóng Mạch Trifecta rồi Chặn Nó

LIVE DEMO
1. Demo 1: Đóng mạch trifecta trong 60 giây — injection doc trong corpus
→ agent POST PII ra sink
2. Demo 2: OPA từ chối một tool call — hiển thị decision + reason trả về
3. Demo 3: Presidio + VN recognizer trên log customer-support tiếng Việt
thật
4. Demo 4: Delete cascade — xoá một subject khỏi warehouse + vector
index + agent memory
5. Demo 5: Audit ledger → sinh ra một dòng compliance evidence theo
format §5

---

### Lab #24

LAB #24
Mục tiêu: Attack your own agent, then contain it: dựng agent đọc corpus
có PII tiếng Việt, red-team bằng indirect prompt injection để chứng minh ex-
fil, rồi triển khai 4 control (PII gate, OPA PEP, trifecta split + egress allowlist,
audit ledger) và chạy lại đúng payload cũ để chứng minh đã bị chặn
Deliverable: Repo 4 control (4 commit) + attack/contain report trước–
sau + injection-corpus.md (≥5 biến thể, có block rate) + DPIA-lite & bảng
requirement→control→evidence + PII detection >95% trên VN test set
Thời gian: 2h

---

### Nguồn Tham Khảo Chính

1. OWASP T op 10 for Agentic Applications 2026(ASI01–ASI10), OWASP GenAI Security
Project, 09/12/2025 — genai.owasp.org
2. Disrupting the first reported AI-orchestrated cyber espionage campaign (GTG-1002),
Anthropic, 13/11/2025; MITRE ATT&CK Campaign C0062
3. What we learned mapping a year’s worth of AI-enabled cyber threats to MITRE A TT&CK,
Anthropic, 2026
4. Cost of a Data Breach Report 2026, IBM — $4,99M trung bình; $6M cho breach có AI;
shadow AI ở 43% tổ chức bị breach
5. 2026 Data Breach Investigations Report, Verizon
6. Design Patterns for Securing LLM Agents against Prompt Injections, Beurer-Kellner et al.,
arXiv:2506.08837; CaMeL, Google DeepMind
7. Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 (hiệu lực 01/01/2026) & Nghị định
356/2025/NĐ-CP
8. Digital Omnibus on AI (OJ 24/7/2026, hiệu lực 27/7/2026) — sửa timeline EU AI Act

---

### T ổng kết — Key T akeaways

Những ý chính cần nhớ trước khi sang bài tiếp theo
Least privilege → least agency. Đơn vị phân quyền là tool call , không phải table
grant. Mỗi agent cần identity riêng, owner riêng, tool catalog theo task và credential
ngắn hạn.
Prompt injection là lỗi kiến trúc, không phải bug vá được. Giả định nó sẽ trúng;
thắng bằng containment — split run, cắt egress, PEP chặn trước execute, audit đầy
đủ. (Cowork: 48h sau launch, lỗi đã báo từ 10/2025.)
Governance phải tự sinh evidence — và nó đã là luật. Luật 91/2025 + NĐ 356/2025
hiệu lực 01/01/2026; 92% tổ chức bị AI-breach không hề có AI access control.

---

### Tiếp theo & Bài tập

Bài tiếp theo
Ngày 25: GPU FinOps & Cost Op-
timization + Quiz + Milestone 2
“Master GPU cost management,
hoàn thành Chapter 5 với quiz tổng
hợp và Milestone 2”
Bài tập về nhà
■ Hoàn thành Lab 24:
attack/contain agent + bảng
mapping compliance
■ Ôn tập Chapter 5: CI/CD,
LLMOps, Monitoring,
Governance & Security
■ Chuẩn bị Milestone 2: tổng
hợp artifacts từ Ngày 21–24

---

### Hỏi & Đáp

Câu hỏi nào về ASI Top 10, lethal tri-
fecta, agent identity, hay Luật 91/2025?

---

### Cảm ơn!

AICB-P2T2 · Ngày 24
Data Governance & AI Security
lms.vinuni.edu.vn · Slide & template trên LMS