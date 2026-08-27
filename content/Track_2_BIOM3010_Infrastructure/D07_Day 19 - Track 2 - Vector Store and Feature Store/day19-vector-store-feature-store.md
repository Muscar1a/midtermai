# day19 vector store feature store

**File gốc:** `Track_2_BIOM3010_Infrastructure\D07_Day 19 - Track 2 - Vector Store and Feature Store\day19-vector-store-feature-store.md`

---

### Vector Store & Feature Store

AICB-P2T2 · Ngày 19 · Chương 4: Hạ Tầng
Giảngviên
VinUniversity · Phase 2 · Track2· Tuần4

---

### “SQL database trả về exact match. Nhưng

AI cần “tương tự” — semantic search.
Tại sao SQL không đủ cho AI search,
và vector database thực sự lưu gì?”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### NộiDung Bài Học

1. VectorEmbeddings: Text →Số
2. VectorDB Landscape (3 tầng lưutrữ)
3. ANN,Filtered Search & Hybrid
4. RAGPipeline & Long Context
5. GraphRAG& Knowledge Graphs
6. AgenticRetrieval & Agent Memory
(code)
7. FeatureEngineering & Feature Store
(code)
8. Production: bảo mật, chiphí, case
studies
9. Ứngdụng: Wiki /CodeWiki / DocWiki
10. Demo: Semantic Search API
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 1 / 56

---

### Mụctiêu bài học

Saubuổi học này,bạnsẽ:
1. Hiểuvector embeddings và chọn modelbằngbằng chứng(VN-MTEB)
2. Deployvàqueryvectordatabase—vàchọnđúng tầnglưutrữ (RAM/SSD/object
storage)
3. Xâydựng RAG pipeline với hybrid search,filtered search và reranking
4. SetupFeast Feature Store với offline/onlinestore
5. Biếtrủi robảomật & tuân thủcủamột kho vector (OWASPLLM08,PDPL)
Agendahôm nay
Embeddings → Vector DB → ANN + Hybrid→ RAG → GraphRAG → Agentic &
Memory →FeatureStore →Production
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 2 / 56

---

### DeliverableCuối Ngày

Artifactcần nộp
Vectorsearch endpoint + Feature Storeoffline/online+ 4 mission nângcao
Core(NB1–NB4)
■ REST /search?q=... top-10,P99 <50ms
■ Hybrid: vector + BM25,merge bằng RRF
■ Feast: 3 feature views,materialize, online lookup
■ Benchmarkkeyword vs semantic vs hybrid
Nângcao (NB5–NB8)
■ Đorecall cliffcủa filtered search
■ Agent: retrieval-as-tool + táchcâu hỏi
■ Semanticcache: sweep ngưỡng+ demo rò tenant
■ Featureengineering: leakage +on-demand view
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 3 / 56

---

### Text →DenseVector: EmbeddingSpace

dim1
dim2
“cloudcomputing”
“serverinfrastructure”
“datacenter”
Techcluster
“nhàhàng”
“ẩmthực”
“mónăn”
Foodcluster
cos=0.92
EmbeddingModels
■ text-embedding-3-small: OpenAI,
1536d
■ text-embedding-3-large: 3072d,
Matryoshka
■ bge-m3: BAAI, 1024d, multilingual
■ nomic-embed: open-source
■ PhoBERT:VN lightweight baseline (xem
bảng2026)
Cosine Similarity —
⃗A·⃗B
|⃗A|×|⃗B| — giá trị
0–1, >0.85= very similar
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 4 / 56

---

### Embeddings: A Decade ofRepresentations (2013→2026)

word2vec FaceNet BERT Sentence-
BERT
OpenAI
ada-002
bge-m3/
3-large
2013 2015 2018 2019 2022 2024–26
Mikolov: word
→ 300d
Schroff: 128d face
+ triplet loss
Devlin: contextual
token embeddings
Reimers: sentence-
level retrieval
General-purpose
API embedding
Multilingual,
Matryoshka, MTEB
Keyshift over a decade
2013–2019: task-specificembeddings—mỗidomain(NLP,face,audio)trainriêng. 2020–2026: general-purpose
foundation embeddings — một model, nhiều use cases, multilingual, multi-modal. Re-index cost cao⇒ chọn cẩn
thậntừ đầu.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 5 / 56

---

### EmbeddingModels 2026: LựaChọn Theo Use Case

Model(2026) Dim Giá Chọn khi
gemini-embedding-2 3072 API đaphương thức
text-embedding-3-large 3072 $0.13/M chấtlượng cao
text-embedding-3-small 1536 $0.02/M baselinerẻ
cohere embed-v4 1536 API PDF/ảnh,VPC
bge-m3 1024 self-host tiếngViệt
Qwen3-Embedding 1024+ self-host OSSđa ngữ
TiếngViệt: xemslide VN-MTEB tiếp theo.Bảngnày sẽ cũ trong
vàituần —học cách chọn, đừng họcthuộc.
Matryoshka: Giảm Index 6×
■ text-embedding-3-large dùngMRL
—truncatable: 3072d →256d
■ 256dvẫn thắng ada-002 @ 1536d
trênMTEB
■ Tiếtkiệm RAM/disk 6×,giảm chi phí
vectorDB
■ Ápdụngngaykhiscale >10Mvectors
Lưu ý: Vệ sinh benchmark:MTEB v2
(Eng) và MMTEB (đa ngữ) làhai bảng khác
nhau;điểmv2khôngsođượcvớiv1 . Luôn
re-rank trêngolden set của bạn(Ngày 14).
Đổimodel = re-index toàn bộ.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 6 / 56

---

### TiếngViệt: ChọnEmbedding Bằng Bằng Chứng (VN-MTEB)

Model Params Dim VN-MTEB
bge-m3 568M 1024 64.90
Vietnamese_Embedding 568M 1024 63.34
halong_embedding 278M 768 61.60
vietnamese-bi-encoder 135M 768 54.89
VN-MTEB(arXiv 2507.21500, 07/2025): 41 datasets, 6
tasks,18 models.
Bađiều bảng này dạy ta
1. Generalistđa ngữ (bge-m3)thắngcả bản
fine-tunetiếng Việtcủachính nó trên
benchmarkrộng
2. Nhưngfine-tune vẫn có thể thắngtrên
domain hẹp ⇒phảiđo trên dữ liệu của
bạn
3. Modeldùng RoPEvượtmodel dùng
absolutepositional embedding — lý dokỹ
thuật,không phải “mới hơn”
Lưu ý:VN-MTEB đượcdịchtừ MTEB tiếng Anh⇒đo năng lựcngôn ngữ, chưa đovăn hoá/domain Việt Nam.
Rerankertiếng Việt: ViRanker (BGE-M3). Kết luận khôngđổi:goldenset của bạn là trọngtài cuối cùng.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 7 / 56

---

### SimilarityMetrics: Cosine vsDot vs Euclidean

CosineSimilarity
cos(⃗a, ⃗b) = ( ⃗a · ⃗b)/(∥⃗a∥ ∥⃗b∥)
■ Range [−1, 1],angle only
■ Defaultcho text embedding
■ OpenAI/BGE/e5unit-norm ⇒
dot= cosine
■ Matchmetric với pretraining
objective: sai metric degrade
recall10–20%
DotProduct
⃗a · ⃗b = ∑ aibi
■ Baogồm magnitude
■ Nhanhhơn (no
division)
■ ColBERT,DPR dùng
dot
Euclidean( L2)
d =
√∑(ai − bi)2
■ Triangleinequality ⇒
IVF/ kd-tree
■ CLIPimage, wav2vec
audio
■ Unit-norm:
d2 = 2(1 − cos)
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 8 / 56

---

### Multi-modalEmbeddings: VectorVượt Khỏi Text

Text
encoder
Image
encoder
Audio
encoder
Shared
embedding
space
Contrastivelearning
Models2026
CLIP(OpenAI):text+image, foundational
SigLIP(Google): backbone của ColPali
jina-clip-v2: multilingual incl. tiếngViệt
ImageBind(Meta): 6 modalities
GeminiEmbedding2 (GA04/2026): text+ảnh+
video+audio+PDFvào mộtkhônggian3072d,
100+ ngôn ngữ, MRL truncate. 1 request: 8K to-
kens / 6 ảnh / 120s video / 180s audio / 6 trang
PDF.
Usecases 2026
Visualsearch (Tiki,Shopee)· Contentmoderation (ảnh+caption)· Videoindexing (tìmcliptheoprompt)· Medical
(X-ray+reportđồng embedding).
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 9 / 56

---

### VectorDB So Sánh

Feature Pinecone Weaviate Qdrant pgvector
Hosting Managed Self/Cloud Self/Cloud Extension
API REST/gRPC GraphQL REST/gRPC SQL
Multi-modal × ✓ × ×
Filtering Metadata GraphQL Payload SQLWHERE
P99(1M vecs) 8–22ms ∼10ms ∼5ms 15ms
Quantization ✓ ✓ ✓(binary) scalar
Bestfor Production Multi-modal Self-hosted HavePostgres
Nguồn:
VectorDBBench2025·1Mvectors,768dims,HNSWindex,top-10query. pgvector+pgvectorscale(TimescaleDiskANN).
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 10 / 56

---

### FAISS& Pre-LLM VectorApplications

FAISS(Meta, 2017)
■ Library, notadatabase — C++/Python, no
server
■ GPU:1B vectors, top-K<1s
■ IVF,HNSW,PQ, OPQ, IVF-PQ —cùng một
API
■ In-memory+ on-disk indices
■ 2026: vẫnlàembeddedtierbêntrongMilvus,
Vespa,pgvector-rs
Pre-LLMUse Cases
■ Facerecognition: FaceNet,ArcFace —
FaceID,photo search
■ Pinterestvisual lens: CNNfeats + FAISS,
2017+
■ RecSyscandidate gen:
YouTube/Spotify/TikTok— ∼1Bvectors
■ Plagiarism/ dedup: Turnitin,news article
clustering
■ Audiofingerprinting: Shazam,Spotify
duplicatedetection
Deep Metric Learning— Pre-LLM vector retrieval dựa vào triplet loss (FaceNet),
contrastive loss, ArcFace angular margin — train embedding sao chocosine (hoặc
Euclidean) tách class. Đây là tiền thân của contrastive pretraining hiện đại (CLIP,
SigLIP).
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 11/ 56

---

### BaTầng Lưu TrữVector: RAM / SSD/ Object Storage

Tầng Vectornằm ở Latency Chi phí Dùngkhi
In-memory(HNSW) RAM 5–20ms caonhất hot,latency-critical, ≤10M
On-disk(DiskANN) SSDcục bộ ∼30ms trungbình 100M+,vẫn cần tương tác
Objectstorage S3/ GCS ∼100ms thấpnhất corpuskhổng lồ, query thưa
AmazonS3 Vectors(GA 12/2025)
■ Objectstorage đầu tiênnativelưu+ query
vector
■ 2tỷ vector/index,10.000 index/bucket
■ Chiphí upload+lưu+querygiảmtới 90%
■ Querythưa <1s; query thường xuyên
∼100ms
■ Tíchhợp Bedrock KB, OpenSearch,
SageMaker
Vìsao rẻ hơn hẳn?
Không phải thuật toán — mà làgiá lưu trữ: object
storage ∼$0,02/GBsovớiRAM ∼$2+/GB ⇒chênh
haibậc độ lớn.
Cùng tầng: turbopuffer, LanceDB (scale-to-zero
khirảnh).
Đánhđổi: latency caohơn, QPS thấp hơn.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 12 / 56

---

### HNSW:Hierarchical Navigable Small World

Layer2
Layer1
Layer0
Q
HNSW:Vì sao là default 2026
■ Graph-based,multi-layer skip list
■ Recall95%+ ở ∼10ms (in-memory)
■ Params: ef=200, m=16 (defaulttốt)
■ Native: Pinecone, Weaviate,Qdrant,
Milvus
KhiHNSW không phải lựa chọn
■ RAM-bound: >10Mvec @ 768d→tốn
∼10GB
■ Update-heavycorpus: re-build chậm
■ Static,billion-scale →DiskANN(slide
tiếp)
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 13 / 56

---

### HNSWvs IVF vs DiskANN: KhiNào Dùng Gì

HNSW
■ Graphin-memory,
multi-layerskip list
■ Recall95%+ @ ∼10ms
■ RAM-bound: ∼1KB/vec
(768dfp32)
■ Bestfor: ≤10Mhot
vectors,latency-critical
■ Params: ef=200, m=16
IVF(FAISS)
■ Cluster-basedinverted
index
■ LowerRAM, higher
latency( ∼30–50ms)
■ Retrainingcần khi data
driftlớn
■ Bestfor: batch-mode,
staticcorpus, CPU-only
infra
■ Params: nlist=1024,
nprobe=64
DiskANN
■ Graphtrên SSD —
billion-scale1 node
■ Latency ∼30ms @ 99%
recall
■ 10–50×rẻhơn HNSW
ởscale lớn
■ Dùngbởi: Pinecone
serverless,
pgvectorscale,Azure
CosmosDB
■ Bestfor: >100M
vectors,cost-sensitive
RaBitQ(SIGMOD2024BestPaper) — UnbiasedbinaryquantizationchoDiskANN
—tíchhợptrongpgvectorscale&VectorChord. GiảmRAMthêm32 ×vớichấtlượng
recalltương đương.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 14 / 56

---

### Quantization: Bí Quyết TiếtKiệm Bộ Nhớ 32×

float32
4B/dim
int8scalar
1B/dim
binary
1bit/dim
÷4 ÷8
Recall: 100%
(baseline)
Recall: ∼99%
RAM: 4× nhỏ hơn
Recall: 95–98%
RAM: 32× nhỏ hơn
100K vectors× 1536d (OpenAI):fp32 =
900MB → int8 = 225MB→ binary = 28MB
AsymmetricQuantization (Qdrant 1.15)
■ Binarystored (28MB) +scalarquery
(precise)
■ Bestof both: cheapstorage + high recall
■ Recall ≥99%với chi phí binary storage
ProductionDefault 2026
■ Qdrant,Weaviate,Pinecone, Milvus: hỗ trợ
binary/scalarout-of-the-box
■ Bậtquantization trướckhi ingest—không
phảisau
■ Re-quantize= re-index ⇒blue-green
(ProductionPatterns)
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 15 / 56

---

### HybridSearch: BM25 +Vector+ RRF

Query
BM25 / SPLADE
Vector ANN
(HNSW)
RRFMerge
k = 60
Top-K
Hybrid
sparse, exact-term match
dense, semantic match
Reciprocal Rank Fusion— score(d) =
∑
r
k +rankr(d) (k = 60)
Rank-only: không cần normalize raw scores giữa
BM25(TF-IDF) và cosine.
Production2026 (Hybrid wins)
■ Recall@10: hybrid >dense-only
∼10–15pp (đotrên golden set của bạn—
Lab19)
■ Latency+6ms (songsong) · storage1.4×
■ Native: Qdrant, Weaviate,OpenSearch,
Milvus
■ SPLADE:recall >BM25nhưng cần GPU
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 16 / 56

---

### FilteredSearch: Cái BẫyRecall Ít Ai Nói Đến

Post-filter
ANNtrước →lọcsau.
■ Xintop-100, filter khớp
2% ⇒còn2kết quả
■ Recallsập khôngbáo
lỗi
■ Cànglọc chặt càng tệ
Pre-filter(brute force)
Lọctrước →quéttoànbộsub-
set.
■ Kếtquả luônđúng
■ Nhưngmấtindex
■ Latencytăng theo kích
thướcsubset
Filtered-ANN(đúng)
Indextự biết filter.
■ Qdrant: filterable HNSW
payloadindex
■ Milvus: partition key
■ pgvector0.8: iterative
scan— tự nới rộng đến
khiđủ khàng
Lưu ý:“Lọc sớm cho nhanh” là bản năngsai. Filter phá tính liên thông của đồ thị HNSW⇒ đi lạc, trả về ít và
kém. Bài test bắt buộc:chạy golden set với filterchọn lọc mạnh (khớp ∼1% corpus) — đây là lúc hệ thống gãy,
khôngphải lúc query trống.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 17 / 56

---

### LateInteraction: ColBERT →ColPali(RAG cho PDF)

Single-vectorvs Late interaction
Single-vector: cả chunk nén thànhmột vector —
chitiết token bị bình quânhoá.
Late interaction: giữ vector từng to-
ken/patch, chấm điểm bằng MaxSim:
score = ∑
t∈q maxd∈D cos(t, d)
Mỗi token truy vấn tự tìm mảnh khớp nhất trong tài
liệu ⇒bắtđược chi tiết mà single-vectorbỏ sót.
ColPali: RAG không cầnOCR
■ Encodeảnhtrang PDFtrựctiếp
(SigLIP-So400m)
■ Lưới 32 × 32 = 1024patch/trang,mỗi patch
128d
■ Bảngbiểu, biểu đồ, form scan:hếtlà bài
toántiền xử lý
■ Họmodel: ColQwen2.5, ColSmolVLM,
ColInternVL
Lưu ý: Chất lượng mua bằng dung lượng.1 triệu trang× 1024 patch× 128d × 4B ≈ 524GB (còn ∼30–
60GB sau quantization). Vector DB một-vector-một-documentkhông lưu nổi— cần hỗ trợ multi-vector + MaxSim
(Qdrant,Milvus).
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 18 / 56

---

### RAGPipeline: End-to-End Flow

Documents Chunking Embedding Vector DB
512 tokens
50 overlap
text-embed-3
bge-m3
User
Query
Query
Embed
Retrieve
Top-K
LLM
Generate
Metadata filter:
source, date≥ 2024
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 19 / 56

---

### ChunkingStrategies: Quyết Định80% Chất Lượng RAG

4Strategies
■ Fixed-size: 512tokens, baseline, ngắt giữa
câu
■ Recursive: LangChain
RecursiveCharacterTextSplitter— tôn trọng
câu/đoạn
■ Semantic: similarity-based,nghỉ tại topic
shift— chậm + tốt nhất
■ Hierarchical: parent(page) + child
(paragraph),retrieve child, return parent
ProductionTuning
■ Chunksize: 200–500tokens cho RAG, 1K+
cholong-context
■ Overlap: 10–20%(~50–100 tokens)
■ Tooling: LangChain,LlamaIndex,
Unstructured.io
■ Vietnamese: tokenizeở sentence level,
khôngbyte-split
Lưu ý: Đo bằng golden set:Recall@k cải thiện đáng kể khi switch fixed→ semantic trên benchmarks. Bad
chunking= embedding tốt cũng vôdụng.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 20 / 56

---

### RAG:Production Best Practices

RetrievalHyperparameters
■ Top-K:5–10cho RAG, 20–50 trước reranker
■ ef_search(HNSW):200 default, tăng cho
recall
■ MMRdiversity: λ=0.5giảm chunks trùng
■ Metadatafilter: khôngphảicứ “lọc sớm” —
xemslide Filtered Search
ProductionGotchas
■ Embeddingmodel consistency: train=
inference
■ Queryrewriting: HyDE, multi-query
expansion
■ Embeddingversioning + zero-downtime
re-index(Production Patterns)
■ Monitorembedding drift hàng tuần
Lưu ý:Training và inferencephải dùng cùng embedding model version. Đổi model = re-
indextoàn bộ.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 21 / 56

---

### 2-StageRetrieval: VectorSearch + Reranking

Stage1: Recall (nhanh)
■ ANNsearch trả về top-100 candidates
■ Bi-encoder: query & docembedriêng
■ Latencythấp (<20ms), recall cao
Stage2: Precision (chínhxác)
■ Cross-encoder: query + doccùnglúc
■ Scorerelevance từng cặp (query,doc)
■ Chọntop-10 chất lượng cao nhất
Rerankers2026 — chọn theo latencybudget
■ Self-host+ GPU: bge-reranker-v2-m3,Jina
v3,Qwen3-Reranker — ∼50–200ms
■ ManagedAPI: CohereRerank v4, zerank —
∼600ms, không cần GPU
⇒ Rerankcộngthẳng vào P99
EmbeddingModel Hosting
■ Self-host: sentence-transformerstrên GPU
—kiểm soát, tiết kiệm ởscale lớn
■ API:OpenAI text-embedding-3-small,
Cohereembed v4 + Rerank 3.5— đơn giản,
triểnkhai nhanh
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 22 / 56

---

### “Cửasổ 1M token rồi, còncần RAG không?”

ContextRot (Chroma Research, 07/2025)
18model frontier,mở rộngtừ Needle-in-a-Haystack:
■ Chấtlượng giảmkhi input dài ra—kể cả task
đơngiản, và giảmkhôngđều giữacác model
■ Modelcửa sổ 1M: hiệu ứngthường thấy rõ
quanh300–400Ktoken
■ Multi-hop/ tổng hợp: gãysớmhơn nhiều
■ Phụthuộc độ giống câu hỏi,nhiễu, cấu trúc —
đúng những biến mà retrieval kiểm soát
Kinhtế học: mộtlần vs mỗi lần
Nhồi cả corpus:trả tiền chotoàn bộ corpus ở
mỗirequest.
Retrieval: trả tiền indexmột lần, mỗi query chỉ
trảcho phần đã chọn.
Chênh lệch nhân theo QPS — đây là lý do RAG
khôngbiến mất.
Mặcđịnh 2026
Retrieve 50K–200K tokenliên quan, rồi mới để
modellong-contextsuyluậntrênđó— lai,không
phảichọn một.
Cửasổ lớn làsứcchứa,không phảiđảmbảo.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 23 / 56

---

### GraphRAG:Khi Quan Hệ Quan TrọngHơn Đoạn Văn

VectorRAG (chunks)
q
Top-K nearest chunks
(cosine similarity)
GraphRAG(entity-relation)
Alice
ProjectX
Bob
PayPal Mahle
worked_on by
at
hired_by
q
Multi-hop: PayPal → Alice →
Project X→ Bob → Mahle
Câuhỏi mà vector RAG kém
“Ai ở PayPal từng cộng tác với người được Mahle
thuê?” — Vector trả về chunks về PayPal HOẶC
Mahle riêng lẻ; không thể cross-document multi-
hop. KG traverse 3-hoptrongµs.
UseCases 2026
■ P3Cdiabetes copilot(Memgraph): patient
journey+ drug interactions
■ Alzheimerresearch: 1.6M edges nối
genes-drugs-trials
■ M&Aintel (GlassDollar/Siemens,Mahle):
entitysearch across millions of companies
F Vector RAG = “đoạn văn liên quan”. GraphRAG = “mối quan hệ kết nối nhiều entity” — chọn
graphkhi câu trả lời làmộtrelationship,không phải đoạn text.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 24 / 56

---

### GraphRAGConstruction: Document →KnowledgeGraph

Documents
(text corpus)
NER
(spaCy / LLM)
Entity
Linking
Relation
Extraction
Community
Detection
Indexed KG
(Neo4j/Memgraph)
“Alice”,
“Project X”
dedupe &
canonical IDs
(Alice, worked_on,
Project X)
Leiden algo:
sub-graph clusters
ToolingLandscape 2026
■ MSGraphRAG:community summaries, chất
lượngcao, index đắt nhất
■ LazyGraphRAG:hoãn extraction sang
query-time— index rẻ ngang vectorRAG
■ LightRAG/Fast GraphRAG: index nhẹ
■ Neo4j(Cypher)· Memgraph(in-memory,
sub-mstraversal)
Vector +Graph: Layered (2026 default)
1. Start: vectorRAG cho conversational
grounding
2. AddKG: domainnhiều thực thể (legal,
medical,M&A)
3. Hybrid: vectorretrieve →KGexpand →
LLM
4. Cost: fullextraction 5–20×;Lazy ≈vector
RAG
Lưu ý:Cost 2026 đã đảo chiều:LazyGraphRAG hoãn phần đắt sang query-time⇒ index bằng vector RAG
(0,1% của full GraphRAG). “Graph quá đắt để thử”không còn là lý do hợp lệ— chọn theohình dạng câu hỏi ,
khôngtheo ngân sách index.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 25 / 56

---

### AgenticRetrieval: TruyXuất TrởThành Một CôngCụ

ClassicRAG vs Agentic retrieval
ClassicRAG —mộtlượt: embedquery →top-K →
sinhcâu trả lời. Dùng chotra cứu đơn giản.
Agentic retrieval— agentquyết định truy xuất thế
nào: phântíchđộphứctạp,táchcâuhỏinhiềuphần,
chọnnguồn, truy xuất nhiều vòng.
Cái giá: thêm LLM call⇒ thêm latency + token.
Khôngphảimặc định cho mọi query.
Vònglặp agentic
1. Hiểuquery —đơn giản hay nhiều bước?
2. Lậpkế hoạch—cần nguồn nào, thứ tựnào
3. Truyxuất —vector / BM25 / KG/ SQL / API
4. Phảntỉnh —đã đủ bằng chứng chưa?
5. Lặplại nếuchưa đủ, rồi mới sinhcâu trả lời
Hạ tầng đang mọc giao diện cho agent— Weaviate 1.37 (2026) nhúng sẵnMCP servertại
/v1/mcp, cùng cổng với REST API — agent truy vấnvà ghi thẳng vào vector DB, không cần lớp tích hợp riêng.
VectorDB không còn chỉlà thư viện phía sau, màlàmộtcông cụ agent gọi được(xemNgày 9: MCP).
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 26 / 56

---

### AgentMemory & Semantic Cache: Hai Nửa Của Bài HômNay

Agentmemory = chính hai khocủa hôm nay
Online storetrả lời “ta biết gì về usernày” (<10ms).
Vectorstore trảlời “đã từng nói gìliên quan”.
Bakiến trúc 2026:
■ Mem0: vector-first, trích “sựkiện” từ hội thoại
■ Zep: knowledge graphtheo thời gian (Graphiti)
■ Letta(ex-MemGPT):3 tầng core / recall/
archival
Benchmark: LoCoMo, LongMemEval, BEAM.
Semanticcache — đòn bẩy chiphí rẻ nhất
Querymới gầnquerycũ(cosine >ngưỡng) ⇒trả
lạicâu trả lời đã lưu.
AWSđotrên63.796querythật (ngưỡng0,75):
■ Chiphí inferencegiảmtới 86%
■ Latencycảithiện 88%trêncache hit
■ Độchính xác giữ∼91%
Lưuý: Cachesainguyhiểmhơnkhôngcache. 4kiểugãy: queryphụthuộcngữcảnh(giốngnhaunhưngcần
đáp án khác) · query nhạy thời gian (trả lời cũ) ·đổi embedding model⇒ vô hiệu toàn bộ cache(đúng cái bẫy
re-index)· cache nhầm một câubịa rồi phục vụ mãi. Ngưỡng similarity là tham sốphảiđo,không phải đoán.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 27 / 56

---

### RetrievalNhư Một Tool: Thứ Agent Thực Sự NhìnThấy

SEARCH_TOOL = {
"name": "search_docs",
# this description IS the retrieval prompt:
# the agent decides *from this text* when to call
"description": (
"Search internal product docs. Use for questions "
"about pricing, limits, API behaviour. Returns "
"ranked chunks with source URLs."
),
"input_schema": {
"type": "object",
"properties": {
"query": { "type": "string"},
"product": { "type": "string",
"enum": [ "core", "billing", "api"]},
"top_k": { "type": "integer", "default": 8},
},
"required": [ "query"],
},
}
Bốnđiều quyết định chất lượng
■ description làprompt truy
xuất—agent chỉ có nó đểquyết
địnhgọi hay không. Mơ hồ⇒
gọisai lúc.
■ Filterlà enum,không phải string
tựdo ⇒agentkhông bịa giá trị
■ Trảvề citation + score,không
chỉtext — để LLM (vàbạn) truy
nguồn
■ top_kcótrần —nếu không,
agenttự làm loãng context
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 28 / 56

---

### GhépNgữ Cảnh: NơiFeature Store Gặp VectorStore

def build_context(user_id: str, question: str) -> str:
# 1) WHO is this user? online store, <10 ms
f = store.get_online_features(
features=[ "user_profile:topic_affinity",
"user_profile:preferred_language"],
entity_rows=[{ "user_id": user_id}],
).to_dict()
# 2) WHAT is relevant? vector search + filter
hits = vdb.search(
embed(question), top_k=8,
filter={ "lang": f[ "preferred_language"][0]},
)
# 3) personalise, THEN ground
return PROMPT.format(
affinity=f[ "topic_affinity"][0],
docs= "\n".join(h.text for h in hits),
)
Haicâu hỏi khác nhau
Feature storetrả lời“user này là ai” →
cánhân hoá.
Vectorstore trảlời “cái gì liên quan” →
grounding.
Cá nhân hoá mà không grounding=
bịacóduyên . Groundingmàkhôngcá
nhânhoá =đúngnhưng vô hồn.
Ngânsách
Feature lookup <10ms — gần như
miễn phísovớimộtLLMcall. Đừngtiếc
nó.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 29 / 56

---

### SemanticCache: Hiện ThựcTrong12 Dòng

def cached_answer(user_id, q, threshold=0.75):
qv = embed(q)
# namespace per tenant: NEVER share across tenants
hit = cache.search(
qv, top_k=1,
filter={ "tenant": tenant_of(user_id)},
)
if hit and hit[0].score >= threshold:
return hit[0].payload["answer"] # HIT
ans = llm(build_context(user_id, q)) # MISS
cache.upsert(
qv, { "answer": ans, "q": q},
ttl=3600, # must expire
)
return ans
Batham số, ba loại lỗi
■ thresholdquáthấp ⇒trảnhầm
câutrả lời của câu hỏikhác.Phải
đo, đừng đoán (AWSdùng 0,75).
■ ttlthiếu ⇒câutrả lời cũ sống mãi
■ namespacethiếu ⇒userA nhận
câutrả lời chứa dữ liệuuser B —
đâylà lỗhổng bảo mật,không
phảibug cache
Lưuý: Đổiembedding model ⇒xoá
sạchcache. Vectorcũvà mới không
cùngkhông gian.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 30 / 56

---

### DebugAgent + Retrieval: TriệuChứng→CáchSửa

Triệuchứng Nguyênnhân thường gặp Cáchsửa
Agentgọi search5–6lầnrồi
bỏcuộc
description mơ hồ, hoặc filter
quáchặt trả về rỗng
Viết lại description; log filter
thựctế agentsinh ra
Trả lời chung chung dù tài
liệuđúng cótrongtop-K
top_k quá lớn→ context loãng
(contextrot)
Giảm top_k,thêm reranker
Chạy đúng lúc demo, sai
trênproduction
Querythật khác golden set Log query thật, refresh golden set
hàngtuần
Câutrả lời cũ dai dẳng Semantic cache không TTL /
khônginvalidate
TTL + xoá cache khi tài liệu nguồn
đổi
Agent làm theo “lệnh” nằm
trongtài liệu
Prompt injection qua retrieved
doc
Tách data khỏi instruction; re-
trieved text không được điều
khiểntool
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 31 / 56

---

### FeatureEngineering: 6 HọFeature Bạn Sẽ ViếtĐi ViếtLại

Bốnhọ “kinh điển”
1. Aggregationtheo cửa sổ— count/sum/avg
5phút, 1giờ, 7ngày. Xương sống của fraud
& recsys.
2. Tỷlệ & chuẩn hoá— amount / avg_7d của
chính user đó. Bắt bất thườngtươngđối.
3. Lag& delta—giá trị kỳ trước, độthay đổi.
Choxu hướng.
4. Recency— now - last_event . Feature rẻ
nhấtmà mạnh bất ngờ.
Haihọ “dễ sai”
5. Mãhoá categorical—one-hot (ít giá trị),
frequency/targetencoding (nhiều giá trị).
Targetencoding phải fit trongfold,nếu
khônglà leakage.
6. Embeddinglàm feature—vector user/item
đithẳng vào model. Cầu nối sang nửa đầu
bàihôm nay.
Mẹođặt tên
<entity>_<phép tính>_<c￿ a s￿ > — ví dụ
user_txn_count_7d. Tên tự mô tả cửa sổ thì PIT
joinvà debug đỡ đau.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 32 / 56

---

### TừÝ Tưởng ĐếnFeatureView: Code Thật (Lab19)

from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Int64
user = Entity(name= "user", join_keys=[ "user_id"])
src = FileSource(
path= "data/query_velocity.parquet",
timestamp_field= "event_timestamp", # PIT join key
)
query_velocity_features = FeatureView(
name= "query_velocity_features",
entities=[user],
ttl=timedelta(hours=1), # stale after 1h
schema=[Field(name= "queries_last_hour", dtype=Int64)],
source=src,
online=True, # -> online store
)
Bốnquyết định trong 20 dòng
■ entities —khoá tra cứu lúc
serving
■ timestamp_field —không
cónó thì không có PITjoin,
vàbạn sẽ leak
■ ttl—“cũ bao lâu thì vô
nghĩa”
■ online=True —tốn tiền, chỉ
bậtkhi serving cần
feast apply → feast
materialize-incremental
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 33 / 56

---

### On-DemandFeature: Tính TạiThời Điểm Request

from feast import Field, RequestSource
from feast.types import Float64
# feast 0.65: importing this from `feast` gives the MODULE
from feast.on_demand_feature_view import on_demand_feature_view
# amount exists only at request time
txn = RequestSource(
name= "txn",
schema=[Field(name= "amount", dtype=Float64)],
)
@on_demand_feature_view(
sources=[user_spend_stats, txn], # stored + request
schema=[Field(name= "amount_vs_avg", dtype=Float64)],
mode= "python",
)
def amount_vs_avg(inputs):
pairs = zip(inputs["amount"], inputs[ "avg_amount_7d"])
return {"amount_vs_avg":
[a / m if m else 0.0 for a, m in pairs]}
Vìsao cần on-demand?
Số tiền giao dịch chưa tồn tại lúc
materialize — không thể pre-compute.
Nhưng amount/avg_7d lại là feature
mạnhnhất của fraud.
On-demand ghépfeature đã lưu với dữ
liệu requestvàáp cùngmộtcôngthức
chocả training lẫn serving.
Lưuý:
write_to_online_store=True ⇒tính
lúc ghi;mặc định False ⇒lúc đọc.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 34 / 56

---

### FeatureStores: Uber Michelangelo→FeastLF AI&Data

Uber
Michelangelo
Feast
(Gojek+GCP)
Tecton
founded
Hopsworks/
DatabricksFS
VertexAI
FeatureStore
Feast →
LFAI&Data
2017 2019Jan 2019 2020–21 2021 2024Aug
Internal platform
for 100+ models
OSS reference
implementation
Ex-Uber team,
enterprise SaaS
Notebook-native
+ lakehouse FS
Managed FS
trên GCP
Vendor-neutral
open governance
Whyfeature stores emerged
Uber có 100+ ML models reuse cùng features (rider price, driver ETA)⇒ centralize để tránh skew + duplicate
compute. LLM-era twist:feature stores giờ host cảembedding feature views (user/item vectors) bên cạnh tabular
features— một hệ thống chocả ML cổ điển và RAGpersonalization.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 35 / 56

---

### FeatureStore Architecture

Feature
Registry
Offline Store
S3 / BigQuery
Online Store
Redis / DynamoDB
materialize
Training
Pipeline
batchfeatures
Inference
Service
<5ms lookup
Single source of truth= No skew
Train: df.mean() vs Serve: running_mean ⇒ bug!
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 36 / 56

---

### Feast: Define & ServeFeatures

FeatureDefinition
■ FeatureView(name="user_features")
■ Entities: ["user_id"]
■ TTL: timedelta(days=30)
■ Source: Delta/Iceberg tables (N18)
Materialize& Freshness
■ feast materialize-incremental
■ Batchfeatures: daily updatelà đủ
■ Streamingfeatures: cần sub-second
■ Feast0.65 (07/2026,LF AI&Data — release
hàng tháng,phải pin version): Push API,
on-demandtransformations (Beta),
streamingtransformations (Alpha)
OnlineLookup
■ store.get_online_features()
■ Latency: <5ms per request
■ Batch: 1000 entity rowsat once
FeastAlternatives
■ Tecton: fullymanaged, real-time features
■ Databricks: FeatureEngineering in Unity
Catalog(WorkspaceFS đã legacy)
■ VertexAI FS:GCPmanaged service
■ Hopsworks: regulatedindustries, on-prem
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 37 / 56

---

### Onlinevs Offline Store + Point-in-TimeJoin

OfflineStore (training)
■ Parquettrên S3 / Delta /Iceberg
■ Snowflake/ BigQuery / Redshift
■ Workload: historicalbatch, 100GB–TB
■ Latency: seconds–minutes(OK for training)
■ Lưu full history củamọi feature value
OnlineStore (serving)
■ Redis/ DynamoDB / Cassandra /Aerospike
■ Workload: per-entityKV lookup
■ Latency: <10ms P99
■ Lưu current value only (nohistory)
■ Feast materialize() nạpoffline →online
Point-in-Time (PIT) Join — Khi build training set: lấy feature as-
of timestamp của mỗi event — không dùng giá trị tương lai. Feast
get_historical_features(entity_df) thực hiện PIT join trên offline store.
Sai lầm:dùng LATEST value⇒ data leakage ⇒ prod accuracy thấp hơn training
20–30%.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 38 / 56

---

### FeatureStores 2026: Feastvs Tectonvs Hopsworks

Feast(open-source)
■ LFAI&Data, cộng đồng
mạnh
■ PushAPI, on-demand
transformations(Beta)
■ Self-host: nhẹ, kiểm
soáthoàn toàn
■ Bestfor: team
nhỏ–vừa,full control
Tecton(managed)
■ Real-timefeatures,
sub-secondfreshness
■ DAGschedulingtựđộng
■ EnterpriseSLA, RBAC,
lineage
■ Bestfor: ML-heavy
productteams, latency
SLAnghiêm ngặt
Hopsworks
■ On-prem+ cloud, data
governance
■ Tíchhợp Spark + Flink
streaming
■ Lineage,versioning,
GDPR-ready
■ Bestfor: regulated
industries(ngân hàng, y
tế)
Lưuý: DatabricksWorkspaceFeatureStoređãlegacy(2024). Migratesang Feature Engineering in Unity
Catalog—không tạo mới project vớiWorkspaceFS.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 39 / 56

---

### Training-ServingSkew: LỗiThầm Lặng

Skewlà gì?
Featuretính khácnhau giữatrainingvàservingdẫn
đến model hoạt động kém khi deploy mà không có
lỗirõ ràng.
Vídụ 1: Aggregation
■ Training: pd.DataFrame.mean() trêntoàn bộ
dữliệu lịch sử
■ Serving: running_mean(last_N) chỉN bản
ghigần nhất
■ ⇒Giátrị khác nhau, model sailệch
Vídụ 2: DateParsing
■ Training: parsedatetime UTC
■ Serving: parselocal timezone
■ ⇒Feature“giờ trong ngày” lệch 7h(VN)
Lưuý: FeatureStoregiảiquyếtskew: mộtđịnh
nghĩa duy nhấtdùng cho cả training lẫn inference
—không code riêng.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 40 / 56

---

### StreamingFeature Pipelines: Sub-SecondFreshness

OLTPDB
(Postgres)
CDC
(Debezium)
Kafka
topic
Flink/
SparkStream
OnlineStore
(Redis)
Offline
(S3/Delta)
rawevents tumbling/slidingwindow
Streamingpatterns
CDC:mọiUPDATErow →Kafkaevent
Aggregate: txnvelocity 5min / 1h window
Feast Push API:app push trực tiếp event→ online
store
Khinào cần streaming
Có: fraud detection, dynamic pricing, real-time rec-
sys
Không cần: churn prediction (daily batch OK),
creditscoring
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 41 / 56

---

### FeatureStore trong ML Production: 3 Use Cases

FraudDetection (PayPal, Wise)
■ Latency: <10ms (per
transaction)
■ Features: velocity
(txn/min),device
fingerprint,
amount-vs-7d-avg
■ Freshness: streaming
(Kafka →Redisonline
store)
■ Tooling: Tecton+ Redis
cluster;Feast +
Aerospike
RecommendationSystems (DoorDash, Spotify)
■ Latency: <50ms
(homepage
personalization)
■ Features: user
embedding,last-N
interactions,item
popularity
■ Freshness: hybrid(daily
user-batch+ stream last
click)
■ Tooling: Tecton
(DoorDash,Atlassian);
Hopsworks(regulated)
DynamicPricing (Uber,Grab)
■ Latency: <100ms (price
atsearch)
■ Features: demand
surge,supply,competitor
price,time-of-day
■ Freshness: sub-second
(streamingdemand
signal)
■ Tooling: Tecton
end-to-endDAG,
managedtransformations
G Feature Store thắng ở3 dimensions: feature reuse + train/serve consistency + low-latency
lookup— không tool nào khácgiải quyết cả 3.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 42 / 56

---

### HộiTụ: Feature StoreChính Là VectorStore

Feast0.65: online storecó thể là vector DB
■ Onlinestore nay gồm cảQdrant,Milvus,
FAISS—bên cạnh Redis, DynamoDB,
Cassandra,Postgres…
■ Vectorsearch trongFeast: trạng tháiAlpha,
nằmdưới nhánh roadmap “NLP”
■ On-demandtransformations (Beta),
streamingtransformations (Alpha)
Nghĩalà gì với kiến trúccủa bạn?
Mộtregistry phụcvụ đồng thời:
■ featuredạng bảng (txn_count_7d)
■ embeddingfeature view(vectoruser/item)
…cho cùng một model, qua cùng một lần online
lookup — cùng định nghĩa, cùng PIT join, cùng
chốngskew.
D
Hainửacủabàihômnayđangnhậplàmmột: RAGcần ngữ cảnh cá nhân hoá (feature),còn
MLcổđiểnngàycàngdùng embeddinglàmfeature. Đừngdựnghaihệthốngsongsongnếu
mộtcái đủ.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 43 / 56

---

### EmbeddingLà Một Feature:vector_index TrongFeast

# 1) an embedding declared like any other field
document_embeddings = FeatureView(
name= "embedded_documents",
entities=[item],
schema=[
Field(name= "vector", dtype=Array(Float32),
vector_index=True,
vector_search_metric= "COSINE"),
Field(name= "sentence_chunks", dtype=String),
],
source=rag_documents_source,
ttl=timedelta(hours=24),
)
# 2) retrieved by similarity, not by key
ctx = store.retrieve_online_documents_v2(
features=[ "embedded_documents:vector",
"embedded_documents:sentence_chunks"],
query=query_embedding, top_k=3,
).to_df()
Điềugì vừa xảy ra?
Cùng FeatureView API, cùng registry,
cùng TTL — nhưng tra cứu bằngđộ
tươngđồng thayvì bằngkhoá.
RAG corpus giờ là một feature view :
có schema, lineage, versioning, PIT
semantics.
online_store:
type: milvus
vector_enabled: true
Alpha — Milvus, SQLite, Qdrant,
PGVector.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 44 / 56

---

### VectorSearch: ProductionOptimization

Caching& Batching
■ Embeddingcache: RedisTTL 24h
■ Hitrate 60–80%, giảm embedding cost
■ Batchembedding: 1000texts/request
■ Throughput50 ×,cost giảm 90%
MonitoringSearch Quality
■ Trackrelevance score distribution theo tuần
■ Nếuavg similarity giảm: điều tra embedding
drift,data quality,query distribution
■ P99latency + index size growth
Multi-tenancy
■ Namespaceisolation (Pinecone)
■ Collectionper tenant (Qdrant)
■ Security+ billing separation
■ Cảnhbáo: lọcbằng metadata = isolation
mềm;1 bug filter⇒ròdữ liệu chéo tenant
(OWASPLLM08 — xem slide Security)
IndexLifecycle Management
■ CreateV1 →ingest →serve
■ Update: build V2 offline→validatequality
■ Blue-greenswitch →retireV1
■ Rollbackngay nếu quality giảm
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 45 / 56

---

### RetrievalEvaluation & Observability

OfflineMetrics (Golden Set)
■ Recall@k: tỷ lệ relevantdocs trong top-k
■ MRR:vị trí trung bình củakết quả đúng đầu
tiên
■ nDCG@k: xếp hạng chấtlượng có weight
■ Build200-querygoldenset—regression-test
mỗilần đổi embedding hoặc chunkstrategy
OnlineMetrics (Production)
■ P99search latency + embedding latency
■ Embeddingcache hit rate (target>60%)
■ Querydistribution drift (alert nếu avg
similaritygiảm)
■ Indexsize growth rate (trigger re-balancekhi
>120%)
RAG-specific: LLM-as-Judge
■ ContextRelevance: retrievedchunkscóliên
quankhông?
■ AnswerRelevance: câu trả lờicó trả lời
querykhông?
■ Groundedness: câu trả lờicó dựa trên
contextkhông?
⇒ RAGAS:faithfulness, answer relevancy,
contextprecision
ObservabilityTooling
■ Langfuse(open-source,OTel): tracing +
evaltích hợp
■ Phoenix/Arize: OpenTelemetry-native,RAG
tracing
■ LangSmith: LangChain-native, prompt +
retrievaldebug
■ Chọn1 tool — instrument từngày đầu tiên
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 46 / 56

---

### BảoMật & TuânThủ: VectorStore LàKho Dữ Liệu Cá Nhân

OWASPLLM08:2025
■ Embeddinginversion: táidựng văn bản gốc
từvector ⇒embeddingkhông phải ẩn danh
hoá
■ Ròchéo tenant: táchbằng metadata filter là
isolation mềm—một bug là rò toànbộ
■ Retrievalpoisoning: tàiliệu độc nhét vào
corpusđể lái câu trả lời
LuậtViệtNam đã có hiệulực
PDPL — Luật 91/2025/QH15 (hiệu lực
01/01/2026), Nghị định 356/2025: quyền chủ thể
dữ liệu,DPO bắt buộc, đánh giá tác động,báo
cáoviphạmtrong72h (24hnếubịtấncônghệ
thống),chếtài hình sự. Ápdụngcảtổchứcnước
ngoàixử lý dữ liệu tạiVN.
LuậtAI—134/2025/QH15 (hiệulực 01/03/2026),
tham chiếu EU AI Act. Chuyển tiếp
đến 01/03/2027 (y tế, giáo dục, tài chính:
01/09/2027).
Lưu ý:Quyền được xoá gặp index ANN bất biến.Một yêu cầu xoá phải lan tớiindex vector + mọi dòng đã
materialize sang online store + semantic cache. Thiết kế đườngxoátrướckhi ingest.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 47 / 56

---

### ChiPhí Một Hệ Retrieval: Cộng Đủ 5 Khoản

5khoản chi
1. Embedding—một lần cho corpus +delta
mỗingày
2. Lưuindex —dims ×bytes ×sốvector, sau
quantization
3. Querycompute —QPS ×tầnglưu trữ
(RAM/SSD/S3)
4. Reranker—mỗi query,cộng thẳngvào P99
5. LLMgeneration —thườnglàkhoản lớn nhất
5đòn bẩy (theo thứ tựhiệu quả)
1. Semanticcache —cắt cả khoản 4 và5
2. Quantization—int8 4×,binary 32×trên
khoản2
3. Chọnđúng tầng—object storage cho
corpusít truy vấn
4. Matryoshka—cắt dims, cắt luôn RAM
5. Top-Knhỏ hơn—ít token vào LLM hơn
Lưu ý:Khoản không ai lập ngân sách:re-index. Đổi embedding model = trả lạitoàn bộ khoản 1 + dựng index
song song (blue-green) = tạm thờigấp đôikhoản 2. Hãy coi nó là chi phí định kỳ, không phải sự cố. (FinOps sâu
hơn: Ngày 25.)
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 48 / 56

---

### EnterpriseCase Studies: ROItừ Vector+ Feature Store

40%
GlassDollar
(Qdrant)
hạ tầng cost↓
3×
GlassDollar
user en-
gagement
1.6M
Alzheimer KG
edges (Mem-
graph)
<10ms
PayPal fraud
feature lookup
Vectorwins
GlassDollar (Qdrant): NL search Siemens/Mahle,
40%cost ↓,3 ×engagement.
Memgraph P3C: KG 1.6M edges, sub-ms multi-hop
traversalcho Alzheimer + diabetes.
FeatureStore wins
PayPal: Tecton+streaming,<10ms/txn fraud lookup.
DoorDash: Tecton DAG, sub-second pricing cho
60M+orders/tháng.
H
ROIđođược: 40%cost ↓+3 ×engagement(GlassDollar)+ <10msfeaturelookup(PayPal).
Khôngphải hype.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 49 / 56

---

### Vector& Feature Store: ML Era vs LLM Era

MLEra (2015–2022)
■ Vectorstore role:candidategeneration cho
recsys;retrieval cho face / imagesearch
■ Embeddings: task-specific(FaceNet,
two-towerrecsys, doc2vec); train per-app
■ Indextooling: FAISS/ Annoy / NMSLIB
embeddedtrong app process
■ Featurestore: tabularfeatures (counts,
ratios,lags) cho XGBoost / DNNtabular
■ Freshness: daily/ hourly batch là mặcđịnh;
streamingchỉ cho fraud
LLMEra (2023–2026)
■ Vectorstore role:RAGretrieval, agent
memory,semantic cache
■ Embeddings: foundationmodels (OpenAI,
BGE,Voyage);một model nhiềuuse case
■ Indextooling: managedmulti-tenant
(Pinecone,Zilliz Cloud, VertexVector)
■ Featurestore: tabular plusembedding
views;on-demand transforms cho prompt
context
■ Freshness: sub-secondstreaming là
baselinecho fraud, pricing, real-time recsys
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 50 / 56

---

### Wiki/CodeWiki/ DocWiki: RAG TrênChính Repo Của Bạn

Wiki(repo →trang)
Sinh tài liệutự động từ source
code.
DeepWiki (Cognition): đổi
github.comthành deepwiki.com
là có wiki. Hơn 50.000 repo
đã index (2026), kèm sơ đồ
Mermaid và MCP server để
agenttruy vấn (Ngày 9).
CodeWiki(hỏivề code)
Hỏibằngngônngữtựnhiên,trả
lờikèm tríchdẫn file + dòng.
“Hàm nào xử lý retry?”→ đoạn
codethật, không phải đoán.
Chínhlà2-stageretrieval+cita-
tioncủa §4, áp lên code.
DocWiki(docscho agent)
Tài liệu được viết đểmáy đọc,
khôngchỉ người.
llms.txt, docs-as-code, mark-
downthay HTML.
Mintlify: gầnmộtnửa lưulượng
vào trang tài liệu nay đến từ
agent.
E
Cả bakhông phải sản phẩm mới— chúng là đúng những mảnh của hôm nay: chunk→
embed →index →hybridsearch →rerank →agenticretrieval →sinhcâutrảlờicótríchdẫn.
Bạnđã đủ kiến thức đểtự dựng một cái.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 51 / 56

---

### CodeWiki: Vì Sao Chunk CodeKhác Chunk Văn Bản

Chiatheo ký tự = hỏng
Textsplitter cắt theo số ký tựsẽcắtđôi một hàm:
■ Embeddingcủa nửa hàm không mangnghĩa
gì
■ Mất import,mất signature, mất scope
■ Retrievevề một mảnhkhông chạy được
Vănbảnchịuđượccắtgiữacâu. Codethìkhông—
nghĩanằm ởkhối,không ở dòng.
Chiatheo AST = đúng
Cắt tại ranh giới cú pháp(hàm, class, method)
bằng tree-sitter; mỗi chunk mang theo scope
chain,imports, signature.
cAST (CMU, arXiv 2506.15655): chunk theo AST
cho +4,3 điểm Recall@5trên RepoEval và+2,67
Pass@1trênSWE-bench.
Nốilạivới§5GraphRAG — Code vốn dĩ làmộtđồthị: hàmgọihàm,moduleimportmodule,classkế
thừa class. Câu hỏi “đổi hàm này thì hỏng chỗ nào?” là câu hỏimulti-hop — đúng loại mà vector RAG kém và
graphtraversal mạnh. NênCodeWiki tốt = vector (tìm đoạnliên quan)+callgraph (lần theo phụ thuộc).
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 52 / 56

---

### DocWiki: Tài Liệu Giờ ĐượcĐọc Bởi Agent

llms.txt —sitemap cho LLM
Một file markdown ở/llms.txt chỉ cho agent biết nội
dungnằm ở đâu, thay vìbắt nó crawl HTML.
■ Phâncấp: file gốctrỏ tới index từng mục⇒
agentchỉ lấy phần cần,tốnít token hơn
■ Mặcđịnh trên Mintlify,Fern,GitBook, Vercel,
Supabase
■ Chưaphải chuẩnIETF/W3C— vẫn là đề xuất
cộngđồng
Viếtdocs khác đi thế nào?
■ MarkdownthayHTML nặng
■ Mỗitrang tựđứng được—agent hiếm
khiđọc trang trước đó
■ Vídụ codechạyđược,có import đầy đủ
■ Tiêuđề mô tảnhiệm vụ,không phải
marketing
Lưu ý:Đây làchunking chiến lượcở tầng tổ chức: bạn đang quyết định trước hệ thống retrieval của người
khác sẽ cắt tài liệu của bạn thế nào. Trangviết rời rạc, phụ thuộc ngữ cảnh trang khác⇒chunk vô nghĩa⇒agent
trảlời sai về sản phẩm của bạn .
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 53 / 56

---

### Demo: Semantic Search vớiWeaviate

1. Ingest10,000documents VietnamesevàoWeaviatevớibge-m3embeddings
(multilingual,tiếng Việtprod 2026)
2. Semanticsearch: “tìmtài liệu về cloud computing”→top5 results với
similarityscores
3. Sosánh: keywordsearch vs semantic vs hybrid —semantic thắng trên
paraphrasedqueries
4. FeatureStore: Feastmaterialize user features→onlinelookup trong Jupyter
notebook
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 54 / 56

---

### Glossary: Vector&Feature Store Terminology

VectorStore
■ Embedding: densevector biểu diễn nghĩa
■ Chunk: đoạntext trước khi embed
■ Index: cấutrúc ANN (HNSW,IVF,DiskANN)
■ Recall@k: %relevant docs trong top-k
■ Quantization: fp32 →int8/binary
■ Hybridsearch: BM25+ Vector →RRF
merge
■ Reranker: cross-encoderrerank top-N
■ Re-index: rebuildkhi đổi embedding model
■ Filtered-ANN:indexbiết filter,tránh sập
recall
■ Lateinteraction: giữvector từng token,
chấmMaxSim
■ Embeddinginversion: dựnglại text gốc từ
vector
FeatureStore
■ Entity: primarykey (user_id, item_id)
■ Featureview: schema+ entity + source
■ Online/ Offline store:KV <10ms/ full
history
■ Materialize: batchload offline →online
■ PITjoin: as-oftimestamp, no leakage
■ Train-serveskew: featuremismatch bug
■ PushAPI: streamevent →onlinestore
■ Featureservice: bundledfeatures cho 1
model
■ Registry: Feastmetadata catalog
■ Embeddingfeature view: vectorlàm
feature
■ Agentmemory: onlinestore + vector store
choagent
■ Semanticcache: táidùng câu trả lời cho
querygần
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 55 / 56

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
1 Hybrid Search (BM25 + Vector + RRF,k = 60) là mặc định production 2026 — nhưngtầng
lưutrữ (RAM/SSD/objectstorage) mới là quyết địnhchi phí lớn nhất.
GraphRAG khi câu trả lời làrelationship(multi-hop, cross-document), không phải đoạn text.
Kiếntrúc layered: vector→KG.
3 Feature Store thắng cùng lúc3 dimensions: feature reuse, train/serve consistency, low-
latencyonline lookup — không toolnào khác giải quyết cả 3.
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 55 / 56

---

### Tiếptheo & Bài tập

Ngày 20: Model Serving & Infer-
enceOptimization
“Model accuracy 95% nhưng latency
3 giây — user đợi không nổi. Quiz +
Milestone 1.”
■ Hoànthành Lab 19: Vector&
FeatureStore
■ Đọctrước: vLLM docs—
PagedAttentionpaper
■ Ôntập Chương 4 cho Quiz N20
Giảngviên (VinUni) AICB· Ngày 19 Tuần4 56 / 56

---

### Hỏi& Đáp

Câu hỏi về Vector DB, Hybrid Search, GraphRAG, hay Feature Store?

---

### Cảmơn!

AICB-P2T2 · Ngày 19
Vector Store & Feature Store
lms.vinuni.edu.vn · Slide & template trên LMS