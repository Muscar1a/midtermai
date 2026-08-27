# day07 lecture slides

**File gốc:** `Phase_1_COMP2010\D18_Day07\day07-lecture-slides.md`

---

### Data Foundations

AICB-P1 · Ngày 7 · Embedding & Vector Store
Tên Giảng Viên
VinUniversity · Phase 1 · Tuần1 ·2026

---

### “Agent trả lời sai vì model yếu, hay vì

nó không có đúng dữ liệu để suy luận?
Ví dụ: Agent CS dùng GPT-4 nhưng trả sai chính
sách hoàn tiền — vì data là policy cũ 2023. ”
Giữcâu hỏi này trong đầu khihọc bài hôm nay

---

### Nội Dung Bài Học

1. Datastrategy cho AI product
2. Agentmemory architecture
3. Embeddings
4. Vectorstore
5. Kếtnối agent với data
6. Chunking& retrieval basics
7. Lab7 + deliverable
8. PreviewDay 08
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 1 / 38

---

### Mục Tiêu Ngày 7

■ Hiểu tầm quan trọng của dữ liệu choAI — data quality thường quyếtđịnh hơn model
selection
■ Phânbiệt được knowledge data, operational data, contextual data
■ Hiểu embeddinglàlớp biểu diễn nghĩa, khôngchỉ là một API call
■ Hiểuđược các bước và phương phápxử lý dữ liệu trướckhi đưa vào AI
■ Hiểu vector store lưugì, tìm gì, và lọcbằng metadata ra sao
■ Môtả được pipelineDocument→ Chunk→ Embed→ Store→ Query→ Inject
■ Buildđược một mini retrieval integration đểnối agent với dữ liệuriêng
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 2 / 38

---

### Deliverable Cuối Ngày

src/(codehoàn chỉnh) +report/REPORT.md (1báo cáo / sinh viên)
■ src/chunking.py —3 chunking strategies + cosinesimilarity
■ src/store.py —EmbeddingStore với search, filter,delete
■ src/agent.py —KnowledgeBaseAgent (RAG pattern)
■ 5benchmark queries + so sánh kếtquả giữa các strategy trong nhóm
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 3 / 38

---

### 01

Data Strategy Cho Sản Phẩm AI
Không phải dữ liệu nào cũng nên đưa vào agent; chọn đúng dữ
liệu quan trọng hơn nạp thật nhiều

---

### Vì Sao Day 07 Quan Trọng Với AI Product?

KhiLLM/VLM biếtcâutrả lời
Câu hỏi LLM/VLM Câu trả lời
Đơngiản — nhưng điều này hiếmkhi đủ cho sản phẩm thật.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 4 / 38

---

### Vì Sao Day 07 Quan Trọng Với AI Product?

KhiLLM/VLM không có sẵn câutrả lời
Câu hỏi LLM/VLM Câu trả lời
Data
In-Context RAG Finetuning
Dữliệu ngắn Corpuslớn Cầnstyle riêng
Day 07 tập trung vào nhánh RAG: đưa đúng dữ liệu vào agent thay vì phải đổi model.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 5 / 38

---

### Vì Sao Day 07 Quan Trọng Với AI Product?

%/ $B
AIuse AIuse
55%
78%
GenAI GenAI
33%
71%
2023 2024
Based on Stanford AI Index 2025.
■ AIadoption đã tăng rất nhanh.
■ Câuhỏi chuyển từ “dùng
modelnào” sang “agent được
phépbiết gì”.
■ Nếudữ liệu sai, cũ, bẩn,hoặc
khôngtruy được đúng lúc,
outputsẽ yếu dù model mạnh.
Lưu ý: Data quality và retrieval quality thường quyết định trải nghiệm thật hơn là đổi
sangmodel đắt hơn.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 6 / 38

---

### 3 Loại Data Agent Cần

Knowledge Data
Tài liệu, policy, SOP,
FAQ,manual,hợpđồng,
bàiviết nội bộ.
Operational Data
Database, trạng thái
đơn hàng, ticket, CRM
records, logs, transac-
tions.
Contextual Data
Session history, user
profile, preferences,
recent actions, channel
context.
Knowledge data phù hợp với retrieval;operational data thường cần query có kiểm
soát; contextual data nênđược inject ngắn và đúng lúc.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 7 / 38

---

### Data Quality Pyramid

Raw
Cleaned
Structured
Enriched Tầng Ví dụ cụ thể
Raw PDFscan lệch, OCR ra “đổ1 trả”, HTML
chứatag rác
Cleaned “đổi trả”, bỏ header/footer, chuẩn hóa
Unicode
Structured Chunk theo heading, gắn source
refund-v3.pdf
Enriched Tag category:support, access:public,
quality:verified
Lưu ý: Sailầmphổbiến: indexngaydữliệu rawrồikỳvọngretrievalsẽtựchữamọi
vấnđề.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 8 / 38

---

### Data Ownership Và Governance

□✓ Ai sở hữu dữ liệu? teamnào chịu trách nhiệm cậpnhật?
□✓ Ai được phép truy cập? dữliệu nào cần ACL, dữ liệunào public nội bộ?
□✓ Data freshness baolâu phải re-index?
□✓ PII / sensitive fields cócần mask trước khi embed không?
□ Không index mọi thứ theo kiểu “cứ nạp hết vào vector DB đã”.
Ví dụ: FAQ do team CS sở hữu, public nội bộ, re-index mỗi tuần, không chứa PII.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 9 / 38

---

### 02

Agent Memory Architecture
Memory không chỉ là lưu nhiều hơn; nó là quyết định xem agent
được nhớ gì, quên gì, và truy gì khi cần

---

### Short-term Memory vs Long-term Memory

Short-term Memory
■ Nằmtrong context window
■ Giữlịchsửgầnđâyvàtaskhiệntại
■ Rẻđể dùng, nhưng dễ đầy token
■ Phùhợp cho session logic ngắn
Long-term Memory
■ Nằmngoài context window
■ Thườnglà vector store, DB, profile
store
■ Phảitruy xuất khi cần
■ Phùhợp cho tri thức tích lũyvà
userhistory chọn lọc
Contextwindowkhôngphảilàvectorstore. Agentchỉ“nhớdàihạn”khicócơchếtruy
xuấthoặc lưu trữ bên ngoài.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 10 / 38

---

### 03

Data Processing
Xử lý dữ liệu để phục vụ cho AI rất quan trọng vì ảnh hưởng
trực tiếp đến chất lượng câu trả lời

---

### Xử Lý Dữ Liệu — Format Nào Tối Ưu Cho LLM?

Format Token hiệu
quả
Giữ cấu trúc Khi nào dùng
Markdown ⋆⋆⋆⋆⋆ Heading, list, table,
bold
Mặc định được lựa
chọn trong nhiều
trườnghợp
HTML (clean) ⋆⋆⋆ Bảng lồng, colspan,
layoutphức tạp
Khi MD mất thông tin
cấutrúc
Plain Text ⋆⋆⋆⋆ Khôngcó cấu trúc Email, chat log, tran-
script
JSON / YAML ⋆⋆⋆ Key-value, nested ob-
jects
Structured output,
functioncalling
Nên chọn Markdown. So với HTML cùng nội dung, tiết kiệm∼30–50% token vì không có
closing tags, attributes, class names. LLM được train trên lượng lớn MD nên hiểu rất tự
nhiên.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 11/ 38

---

### Xử Lý Dữ Liệu — Pipeline Phổ Thông Cho Dữ Liệu Văn Bản

Scanned
Image / PDF
OCR
Engine
Raw
Text
Clean &
Structure Markdown
Extract
Text Parse
Đường thay thế cho tài liệu
có text sẵn (Word, HTML)
Lưu ý: Sai lầm phổ biến: bỏ qua bướcClean & Structure, đưa raw text thẳng vào
chunking. Kếtquả: chunkchứaheader/footerrác,OCRlỗi,kýtựđặcbiệt—retrieval
qualitygiảm rõ rệt.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 12 / 38

---

### 04

Embeddings
Embedding biến ngôn ngữ thành không gian toán học để máy có
thể so sánh nghĩa thay vì chỉ so chữ

---

### “Làm sao để máy biết hai thứ “giống

nhau” — khi chúng không cùng
ngôn ngữ, không cùng định dạng?”
Giữcâu hỏi này trong đầu khihọc bài hôm nay

---

### Bài Toán “Khoảng Cách”

Text
“chínhsách
hoàntiền”
←→
Text
“refund
policy”
khác ngôn ngữ,
cùng nghĩa
Ảnh
mèongồi
←→ Ảnh
mèonằm
khác pose,
cùng chủ thể
Text
“acat on
asofa”
←→ Ảnh
mèotrên
sofa
khác modality,
cùng nội dung
Con người nhìn là biết “giống nhau”. Nhưng máy cần biến text, ảnh, audio thànhsố
trongcùng không gian — rồi mớiđo khoảng cách được.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 13 / 38

---

### Giải Pháp: Embedding Model

Text
“chínhsách hoàn tiền”
Embedding
Model
[0.012, -0.034, 0.091, …]
1536chiều
Ảnh
mèotrên sofa
Embedding
Model
[0.045, 0.018, -0.072, …]
1536chiều
Audio
kháchgọi hotline
Embedding
Model
[-0.008, 0.056, 0.031, …]
1536chiều
Cùngkhông gian
⇒sosánh được!
Embedding model là hàm biến dữ liệu thô (text, ảnh, audio) thànhvector số cùng
kíchthước. Sau đó,đo khoảng cách giữa các vector= đo “độ giống nhau” vềnghĩa.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 14 / 38

---

### Embedding Là Gì?

hoàntiền / refund
vậnchuyển / shipping
trảhàng
Minh họa trực
quan: câu có nghĩa gần nhau sẽ ở gần nhau hơn trong vector
space.
■ Textđược biến thành vector
nhiềuchiều.
■ Từđó, máy có thể đođộ gần
về nghĩa.
■ Đâylà nền tảng cho semantic
search,clustering, dedup,
recommendation.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 15 / 38

---

### Đo “Gần” Như Thế Nào? Cosine vs Euclidean

d1
d2
⃗A
⃗B
θ
Euclidean
Cosine= cos θ
Cosine similarity
■ Đo gócgiữahai vector
■ −1đến 1;càng gần 1=càng giống
nghĩa
■ Khôngbị ảnh hưởng bởi norm
■ Dùng nhiều nhất trongNLPvàretrieval
Euclidean distance
■ Đo khoảng cách thẳng giữahai điểm
■ Càngnhỏ = càng gần
■ Bịảnh hưởng bởi scale / norm
Cosine là mặc định cho text embedding (so nghĩa, bỏ qua độ dài).Euclidean phù
hợpkhi cần đo khoảng cách tuyệtđối (image, geo).
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 16 / 38

---

### Công Thức: Đừng Sợ, Chỉ Có 2 Dòng

Cosine Similarity
cos(⃗A, ⃗B) =
⃗A· ⃗B
∥⃗A∥×∥ ⃗B∥
■ Tử: tích vô hướng(dot product)
■ Mẫu: tích hai độdài (chuẩn hóa)
■ 1=cùng hướng, 0=vuông góc,
−1=ngược
Euclidean Distance
d(⃗A, ⃗B) =
vuut
nX
i=1
(Ai− Bi)2
■ Khoảngcách “đường chim bay”
trong nchiều
■ 0=trùng nhau, càng lớn =càng xa
■ 1536chiều: công thứcy hệt, chỉ
nhiều ihơn
Lưu ý: Hầu hết vector store mặc định dùngcosine. Không cần tự code — nhưng
cầnhiểu score = 0.87 vs 0.31nghĩa là gì.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 17 / 38

---

### Ví Dụ Trực Quan: Score Nghĩa Là Gì?

Câu A Câu B Cosine Nghĩa
“Chínhsách hoàn tiền” “Quyđịnh đổi trả” ∼0.87 Rất gần nghĩa
“Chínhsách hoàn tiền” “Cáchgiao hàng nhanh” ∼0.52 Liên quan nhẹ
“Chínhsách hoàn tiền” “Thờitiết hôm nay” ∼0.31 Không liên quan
“Chínhsách hoàn tiền” “Refundpolicy” ∼0.82 Cross-lingual!
Embedding model hiểu nghĩacross-lingual: “hoàn tiền” và “refund” gần nhau dù khác ngôn
ngữ. Đây là sứcmạnh so với keyword search.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 18 / 38

---

### Embedding Dùng Để Làm Gì Trong AI Product?

Use case Cách hoạt động Ví dụ thực tế
Semanticsearch Embed query + embed tài
liệu,tìm cosine cao nhất
Userhỏi“trảhàng” →tìmđược
chunk “chính sách đổi trả” dù
khôngtrùng từ
Clustering Gom các vector gần nhau
thànhnhóm
10,000 ticket CS→ tự phân
thành 15 chủ đề (hoàn tiền, lỗi
app,giao hàng…)
Dedup Socosinegiữacáccặp,đánh
dấucặp >threshold
Phát hiện 2 bài FAQ nội dung
gầngiống, gộp lại
Recommendation Embed user intent + embed
item,rank theo cosine
Uservừađọc“Reacthooks” →
gợiý bài “useState patterns”
Lưu ý: Embedding không tự tạo ra “sự thật”. Nếu text nguồn sai, thiếu, hoặc chunk xấu thì
retrievalvẫn tệ —garbage in, garbage out.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 19 / 38

---

### Chọn Embedding Model: Trade-off Thực Tế

Model Dim MTEB Avg Khi nào dùng
text-embedding-3-small 1536 62.3 Demo, PoC, lab (rẻ,
nhanh)
text-embedding-3-large 3072 64.6 Production cần chất
lượng
Open-source(e5, BGE) 768–4096 61–66 Self-host, data nhạy
cảm,free
■ Khôngcó model “tốt nhất” cho mọiuse case. Chọntheoquality, latency, storage,
language.
■ Vớiproduct thực tế, model cân bằngthường tốt hơn model mạnh nhấtnhưng chậm và đắt.
Trên thực tế có hàng trăm embedding model (Cohere, Voyage, Gemini, Jina…). Xem bảng xếp hạng đầy đủ: MTEB
Leaderboard trên Hugging Face.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 20 / 38

---

### Embeddings — Python Example

from openai import OpenAI
import numpy as np
client = OpenAI()
texts = [ "Chính sách hoàn ￿ tin", "Quy định đ￿ i ￿ tr", "ờThi ￿ tit hôm nay"]
resp = client.embeddings.create(
model= "text-embedding-3-small", input=texts
)
vecs = [np.array(d.embedding) for d in resp.data]
# Cosine similarity: ĩngha ￿ gn => score cao
cos = lambda a, b: a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
print(cos(vecs[0], vecs[1])) # ~0.87 hoàn ￿ tin <-> đ￿ i ￿ tr
print(cos(vecs[0], vecs[2])) # ~0.31 hoàn ￿ tin <-> ờthi ￿ tit
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 21 / 38

---

### 05

Vector Store
Vector store không chỉ lưu vector; nó lưu cả nguồn, metadata, và
khả năng lọc để retrieval có ngữ cảnh đúng

---

### Vector Store Lưu Những Gì?

Mỗi record gồm 4 thành phần:
ID
Originalchunk (text gốc)
Embeddingvector (float array)
Metadata(key-value)
Lưutrong
vectorstore
Searchresults (top-k + scores)
Output khi query, không phải thứ được lưu
Ví dụ 1 record thật:
Trường Giá trị
ID policy-returns-001
Chunk “Khách hàng có 30 ngày kể từ ngày
nhận hàng để yêu cầu đổi trả. Sản
phẩmphải còn nguyên tem.”
Vector [0.012, -0.034, 0.091, …] (1536
số)
Metadata source: refund-v3.pdf
category: support
updated: 2026-03-01
access: public-internal
Vectordùngđể tìm(semanticsearch).
Chunkdùngđể inject vàoprompt cho LLM.
Haithứ khác nhau, lưu cùngnhau.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 22 / 38

---

### Metadata Quan Trọng Không Kém Similarity

Trường metadata Ví dụ Tác dụng
Source/ file name refund-policy-v3.pdf truyvết và hiển thị nguồn
Category finance, support, legal lọc đúng domain trước khi
search
Time/ freshness 2026-03-01 tránhdùng nội dung cũ
Accesslevel public-internal,
restricted
giớihạn truy cập
Section/ chunk id returns.section.4 debugvà cite chính xác hơn
Retrieval tốt cần semantic similarity kết hợp metadata filtering
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 23 / 38

---

### Top-k, Score Threshold, Filter

Tham số Ý nghĩa Ví dụ
Top-k Lấy bao nhiêu chunk gần
nhất
n_results=3 : đủ cho hầu hết
câu hỏi đơn. n_results=10 :
khicầntổnghợpnhiềunguồn
Score thresh-
old
Bỏ chunk có cosine thấp
hơnngưỡng
Threshold = 0 .7: chỉ giữ
chunk thật sự liên quan.
Threshold = 0 .4: chấp nhận
liênquan nhẹ
Attribute filter Lọc theo metadata trước
khisearch
where={"category":
"support"}: chỉ tìm trong
tài liệu CS, bỏ qua finance,
legal
Filtertheocategorytrước →semanticsearch→lấytop-3cóscore > 0.6. Retrievaltốtthường
đếntừ chunk đúng + metadata đủ + filter hợp lý —không phải đổi model.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 24 / 38

---

### Chroma — Add + Query + Inject (Full Flow)

import chromadb
client = chromadb.Client()
col = client.create_collection( "policies")
# 1. Add: chunk + metadata -> vector store
col.add(
ids=[ "p1", "p2"],
documents=[ "Khách hàng có 30 ngày đ￿ đ￿ i ￿ tr.",
"Hoàn ￿ tin trong 7 ngày làm ệvic."],
metadatas=[{ "cat": "returns"}, { "cat": "refund"}],
)
# 2. Query: semantic search
results = col.query(query_texts=[ "đ￿ i size"], n_results=2)
# 3. Inject: dùng ￿ kt ￿ qu làm context cho LLM
context = "\n".join(results["documents"][0])
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 25 / 38

---

### 06

Kết Nối Agent Với Data
Retrieval pipeline là chiếc cầu nối giữa dữ liệu riêng và hành vi
của agent

---

### Hai Pha Của Retrieval Pipeline

Ingestion
chạy 1 lần
Document Chunk Embed Store
PDF, docs,
HTML
chia theo
section vector hóa index + metadata
Retrieval
mỗi câu hỏi
Question Embed
query Search Inject
user hỏi gì? cùng model
embed
cosine top-
k + filter
chunk →
prompt → LLM
vector store
Lab 7 scope
Lưu ý: Ingestion chạy offline khi dữ liệu thay đổi. Retrieval chạy online mỗi khi user
hỏi. Hai pha này tách biệt nhau.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 26 / 38

---

### Chunking Là Gì?

Chinh sach doi tra
Khach hang co 30 ngay...
Chinh sach hoan tien
Hoan tien trong 7 ngay...
Giao hang
Mien phi don tren 500k...
1 file PDF / doc (nhièu section)
⇓ chunking
Chunk1: chinh-sach-doi-tra (150tokens)
Chunk2: chinh-sach-hoan-tien (120tokens)
Chunk3: giao-hang (90tokens)
Chunking=chia tài liệu dài thành cácđoạn
nhỏhơn để embed và index riêng.
Vì sao phải chunk?
■ Embeddingmodel có giới hạn token
input
■ Mộtfile dài embed thành 1 vector→
khôngthể tìm đoạnliênquan, chỉ tìm
fileliênquan
■ Chunknhỏ →retrievalchính xác hơn,
injectít nhiễu hơn
Chiến lược chunk phổ biến:
■ Theo heading / section (phổbiếnnhất)
■ Theo số token cố định (200–500
tokens)
■ Theo câu / paragraph
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 27 / 38

---

### Chunking: Quá To Hay Quá Nhỏ Đều Trả Giá

Chunk quá to
Dính nhiều chủ đề vào
cùng một vector, re-
trieve trúng nhưng in-
jectrất nhiễu.
>1000tokens
Chunk hợp lý
Một ý / một section
trọnvẹn,cóoverlap10–
15% giữa các chunk
liềnkề.
200–500tokens
Chunk quá nhỏ
Mất ngữ cảnh, retrieve
nhiềumảnhrờirạc,khó
tổng hợp thành câu trả
lờitốt.
<50tokens
Khicắtchunk,lấythêm1–2câucuốicủachunktrướclàmphầnđầuchunksau. Giúp
giữngữ cảnh tại điểm cắt, tránhmất nghĩa giữa chừng.
Rule of thumb: bắt đầu đơn giản với chunk theo section / heading, rồi tối ưu sau bằng eval thay vì đoán cảm tính.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 28 / 38

---

### Ví Dụ: Cùng Một FAQ, Ba Cách Chunk

Chunk quá to
Q1: Hoàntiền mất bao lâu?
A1: 7 ngày.
Q2: Đổisize được không?
A2: Trong30 ngày.
Q3: Shipquốc tế?
A3: Không hỗ trợ.
Query“đổi size” →retrievecả 3 Q&A→LLMbị
nhiễubởi Q1, Q3.
Chunk hợp lý
Q2: Đổisize được không?
A2: Được, trong vòng 30 ngày
kểtừ ngày mua.
Query“đổi size” →retrieveđúng Q2 →LLMtrả lời
chínhxác.
Chunk quá nhỏ
“Trong30 ngày.”
Query“đổi size” →retrieve“Trong30 ngày” →
thiếungữcảnh,LLMkhôngbiết30ngàychoviệcgì.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 29 / 38

---

### Retrieval Khác Gì Memory?

Retrieval
■ Tìmcontext liên quan cho câu hỏi
hiệntại
■ Đọctừ knowledge base
■ Trọngtâm: relevancevà
grounding
Ví dụ: User hỏi “chính sách đổi trả”→ agent tìm
trongFAQ →trảlời dựa trên tài liệu.
Memory
■ Lưutrạng thái, sở thích, lịch sử
chọnlọc
■ Từuser profile hoặc interaction
history
■ Trọngtâm: continuityvà
personalization
Ví dụ: Cùnguserhỏilần2 →agentnhớlầntrước
đãđổisizeM →gợiý“bạnmuốnđổilạisizekhác?”
Lưu ý: Nhiều hệ thống dùng cả hai:retrieval để biết domain facts,memory để biết
usernày là ai và đã làmgì trước đó.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 30 / 38

---

### Failure Demo: Chunk Xấu vs Chunk Tốt

Query: “Chínhsách đổi trả áp dụngtrong bao lâu?”
Chunk xấu (raw,không section)
Retrieved (cosine: 0.61): “…giao hàng miễn phí
đơn trên 500k. Đổi trả trong 30 ngày. Liên hệ hot-
line1900…”
LLM answer: “Bạncóthểđổitrảvàliênhệhotline
1900…” (nhiễu, thiếu chi tiết)
Chunk tốt (theosection + metadata)
Retrieved (cosine: 0.89): “Chính sách đổi trả:
Khách hàng có 30 ngày kể từ ngày nhận hàng để
yêucầu đổi trả. Sản phẩm phải còn nguyên tem.”
LLM answer: “30ngàykểtừngàynhận,sảnphẩm
cònnguyên tem.” (chính xác, có nguồn)
Lưu ý: Cùngmodel, cùng query — khác nhauhoàn toàn vìchất lượng chunk.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 31 / 38

---

### 07

Hands-on 7
Mục tiêu của lab là nối được dữ liệu riêng vào hệ thống AI theo
pipeline tối thiểu nhưng đúng bản chất

---

### Lab 7: Hai Pha

Phase 1 — Cá nhân
Hoànthành TODOtrong 3 file:
1. src/chunking.py —3 chunking
strategies+ cosine similarity
2. src/store.py — EmbeddingStore
(5methods)
3. src/agent.py —
KnowledgeBaseAgent (RAG)
Document và FixedSizeChunker đã implement sẵn
làmví dụ. Verify:pytest tests/ -v
Phase 2 — Nhóm: So sánh Strategy
1. Nhómchọn domain + thu thập
5–10docs
2. Thốngnhất 5 benchmark queries +
goldanswers
3. Mỗingười thử strategy riêng
(chunking,metadata)
4. Chạycùng queries, so sánh kết
quả
5. Demo+ thảo luận liên nhóm
Cùngcode,cùngmodel—khác data strategy sẽchokếtquảrấtkhác. Dataquality >model
selection.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 32 / 38

---

### Hosted vs Self-managed: Chọn Gì Cho Lab?

Hosted / managed
File Search / managed retrieval giúp đi
nhanh, giảm code hạ tầng, phù hợp
demovà PoC.
Self-managed
DùngChroma/Faiss/vectorDBkhicần
kiểm soát chunking, metadata, pipeline,
hoặccost path chi tiết hơn.
Hôm nay dùngChroma (self-managed) để hiểu pipeline end-to-end. Hosted option
tìmhiểu thêm ngoài giờ.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 33 / 38

---

### Deliverable Và Assessment

Nộp bài
■ src/—hoàn thành tất cả TODO
■ report/REPORT.md —1 báo cáo / sinh viên
Phần Điểm
Cánhân (code + phân tích) 60
Nhóm(strategy + so sánh) 40
Tổng 100
5 góc nhìn tự đánh giá
1. Retrieval Precision —top-3 có
đúngkhông?
2. Chunk Coherence —chunk giữ
đượcý trọn vẹn?
3. Metadata Utility —filter có giúp
tăngchính xác?
4. Grounding Quality —answer dựa
trêncontext?
5. Data Strategy Impact —strategy
phùhợp domain?
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 34 / 38

---

### Checklist Trước Khi Nộp

□✓ Tests pass: pytest tests/ -v khôngcó FAIL
□✓ 3 chunking strategies đềuimplement và so sánh được
□✓ EmbeddingStoresearch+ filter + delete hoạt động
□✓ KnowledgeBaseAgenttrảlời dựa trên retrieved context
□✓ 5 benchmark queries cógold answers và kết quả sosánh
□✓ Reportgiảithích approach + failure cases
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 35 / 38

---

### 08

Key Takeaways
Day 07 đặt nền cho RAG và mọi hệ thống AI dùng tri thức riêng

---

### 4 Ý Cần Nhớ Sau Buổi Học

1. Data quality thườngquan trọng hơn đổi sangmodel đắt hơn.
2. Embeddinglàlớp dịch ngôn ngữ sang khônggian có thể so sánh nghĩa.
3. Vector store làbộ nhớ dài hạn cóthể tìm kiếm bằng ngữ nghĩavàmetadata.
4. Retrieval pipeline làcầu nối từ dữ liệuriêng tới câu trả lời grounded củaagent.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 36 / 38

---

### Tài Liệu Tham Khảo

■ StanfordHAI. AI Index 2025. https://hai.
stanford.edu/ai-index/2025-ai-index-report
■ OpenAI. Embeddings Guide. https:
//platform.openai.com/docs/guides/embeddings
■ OpenAI. File Search. https://platform.openai.
com/docs/guides/tools-file-search
■ ChromaDocs. https://docs.trychroma.com/
■ HuggingFace. MTEB Benchmark.
https://huggingface.co/blog/mteb
■ Karpukhinet al. Dense Passage Retrieval.
arXiv:2004.04906
Danh sách đầy đủ có trong lab handout.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 37 / 38

---

### Tiếp Theo & Bài Tập

Bài tập sau buổi
■ Hoànthiện solution.py nếu chưa pass hếttests
■ Ràlại knowledge base: bỏ nội dung nhiễu, thêm
metadata
■ Thửthêm 3 queries khó hơn, tìmfailure cases
mới
Preview Day 08
Ngày 8 đi tiếp sang RAG
pipeline: indexing, retrieval,
generation,evaluation.
Giảngviên (VinUni) AICB· Ngày 7 Tuần1 38 / 38