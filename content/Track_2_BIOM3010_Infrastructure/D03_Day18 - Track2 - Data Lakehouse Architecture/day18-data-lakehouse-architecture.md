# day18 data lakehouse architecture

**File gốc:** `Track_2_BIOM3010_Infrastructure\D03_Day18 - Track2 - Data Lakehouse Architecture\day18-data-lakehouse-architecture.md`

---

### Data Lakehouse Architecture

AICB-P2T2 · Ngày 18 · Chương 4: Hạ Tầng
Giảng viên
VinUniversity · Phase 2 · AI Infrastructure Track· Tuần4

---

### ““Đổ tất cả vào S3” — works ở 10GB, ác

mộng ở 10TB, production outage ở 10PB.
Lakehouse = ACID + cheap
storage + AI workloads.
Câu trả lời cho 3 era: Traditional, ML, LLM.”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### Nội Dung Bài Học

1. Evolution +3Eras (Trad/ ML /LLM)
2. DeltaLake: ACID, DV,CDF,
catalog-managed(4.1/4.2)
3. TimeTravel& Data Versioning
4. Iceberg: hidden partitioning,
metadata,v3 →v4
5. QueryEngines +nativeexecution
kernels
6. StorageOptimization +Table
Maintenance
7. FormatInternals & Performance
Tuning
8. Lakehousecho AI/ML Workloads
9. Streaming: CDC, vật lýđộ trễ,
dưới-giây
10. Industrialcases + AI 2026:
multimodal,vector-trong-bảng,
semanticlayer,MCP,agent memory
11. ProductionOps: catalog =control
plane,DQ, lineage, agentic DE,
governance,FinOps
12. Demo +Labrepo (notebooks 01–04)
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 1 / 50

---

### Mục tiêu bài học

Saubuổi học này,bạnsẽ:
1. Hiểuevolution storage qua 3 era:Traditional → ML → LLM
2. Triểnkhai Delta/Iceberg: ACID,time travel, deletion vectors, CDF
3. Sosánh Delta vs Iceberg vs Hudi→chọntheo workload (append / mutate /
multimodal)
4. Thiếtkế medallion Bronze/Silver/Gold cho LLM observability+ RAG corpus
5. Ápdụng production ops: catalog, data contracts, lineage, FinOps
6. Giảithích catalog = control plane (Iceberg1.11scan planning, Delta4.1
catalog-managed)và chọn được băng độ trễstreaming phù hợp
7. Thiếtkế tầng dữ liệu choagent: semantic layer,embedding trong bảng, trajectory,
provenancetheo EU AI Act
Mạch lecture
Evolution → Delta + Iceberg → Engines & Maintenance→ AI/LLM Workloads →
Streaming →AI2026 (multimodal, agent)→ProductionOps →Demo
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 2 / 50

---

### Deliverable Cuối Ngày

Artifact cần nộp
8 notebook đã chạy. Mỗi notebook tự kết thúc bằng khốiasserttrên tiêu chí đậu —
make run-all làđúngcổng giảngviên chấm.
Phần A — Nền tảng (44đ)
■ NB1Deltalog +schemaenforcement +
schema_mode="merge"
■ NB2OPTIMIZE +Z-ORDER:speedup ≥3×hoặc
files-pruned ≥10×
■ NB3MERGE100K +RESTORE; history() ≥5
versions
■ NB4Medallion: Silver<Bronze +Gold
p50/p95/cost ≥7ngày
Phần B — Lakehouse 2026 (50đ)
■ NB5Iceberg +catalog: hidden-partition pruning≥
5×;field-ID bền qua rename
■ NB64job maintenance: compaction≥10×,
clusteringskip ≥50%,orphan +expiry
■ NB7Vectortrong bảng: int8 nhỏ 4×;táihiện
lifecyclebug
■ NB8Trajectory +MCP +4rổ provenance thành
partition
Labrepo: github.com/VinUni-AI20k/Day18-Track2-Lakehouse-Lab —chạy offline hoàn toàn
(Python3.10–3.14, không key/Docker/JVM). Còn 6đchomake test + make run-all xanhtừ máy sạch.
Bonus (optional, không tính điểm): BONUS-CHALLENGE.md —thiết kế lakehouse cho 1hard problem của riêng
bạn.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 3 / 50

---

### Evolution of Data Platforms

Data
Warehouse
Data
Lake
Data
Lakehouse
2000s 2010s 2020s
Structured, SQL
· Fast queries
Đắt, kém flexible
Cheap, flexible
· Any format
“Data swamp”
ACID + cheap
storage
Open formats
· Best of both
Key Innovation: metadata layer biến S3 object storage thành transactional
store.
Enablers: Open table formats (Delta/Iceberg/Hudi) + cheap object storage
(S3) + query engines (Spark/DuckDB/Trino).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 4 / 50

---

### 3 Eras of Software: Workload Drives Storage

Aspect Traditional (1990s–2010) ML Era ( ∼2012–2022) LLM Era (2022+)
Workload OLTPtxn, BI reports Featureeng,batchtrain/infer Pretraining(T tokens), fine-tune,
RAG,eval
Datashape Tabular,3NF normalized Tabular+ semi-structured
(JSON)
Text+ multimodal + embeddings
Volume GB–TB TB–PB PB+raw, 1012+tokens, billions
vectors
Latency ms(txn), hours (BI) Min–hours(batch ML) Hours(train) + sub-100ms (RAG)
Schema Schema-on-write(rigid) Schema-on-reador hybrid Hybrid+ lineage + contracts +
provenance
Compliance SOX,PCI, GDPR +biasaudit, fairness +trainingdata provenance,
copyright,hallucination
Failuremode Schemadrift, deadlock Datadrift, train/serve skew Dedupleak, license violation,
hallucination
Pattern: mỗiera thêmmộtclass data mớimàera trước không có (semi-structured→multimodal+embeddings).
Storagestack mở rộng,không thay thế.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 5 / 50

---

### Storage Tech × Era Fit + LLM Demands

Tech Traditional ML Era LLM Era
OLTPDB (Postgres) Primary system Appbackend; CDC source for
ML
Appbackend; CDC; user
feedback
Warehouse(Snowflake) BIreporting Featureaggregation + serving BIdashboards on LLM
telemetry
DataLake (S3 + Hive) — Rawevents, training datasets Rawcrawls, multimodal blobs
Lakehouse
(Delta/Iceberg)
— UnifiedBI + ML feature store Training corpus + RAG +
eval + prompt logs
VectorDB
(Qdrant/Milvus)
— Recommendation(rare) Online RAG (sub-100ms)
Multimodal(Lance) — — Video/image/audio +
embeddings
LLM-era demands (deduptrillion-token, multimodal blobs, embedding versioning,training-data provenance,
license/evaltags, prompt+trace logs→Bronze)thêmtầng (vectorDB, multimodal) vàéplakehouse =
dataset-of-recordcho compliance — chi tiếtở §8 (AI/ML) + §11(Governance).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 6 / 50

---

### Delta Lake Transaction Log

_delta_log/
000.json
001.json
002.json
003.json
addpart-001, part-002
addpart-003
removepart-001
addpart-004
Parquet Files
part-001 part-002
part-003 part-004
ACID: Atomicity + Consistency + Isolation + Durability trên S3 ·Concurrency: optimistic
conflict detection ·Metadata layer: JSON log biến object store→ transactional table. Aha:
reader đọc003.json trước → danh sách file hợp lệatomic → không bao giờ thấy trạng thái
dở-dang (part-003 có, part-004 chưa).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 7 / 50

---

### Delta Lake: Thao Tác Quan Trọng

Write & MERGE
■ df.write.format("delta") —basic
write
■ MERGE INTO ... =upsert. Workshop
100K ∼2×;prod 100M+ →10–50×vs
overwrite
■ Schemaevolution: mergeSchema=true
OPTIMIZE + Z-ORDER
■ Compact →target128MB–1GB
■ 10,000 ×1MB →10 ×1GB
■ Z-ORDER:sort/co-locate theo cột→
min/maxchặt →skipcả file (3–10×;§6)
■ LiquidClustering (3.2+) =kếnhiệm
Z-ORDER,re-cluster tăng dần
VACUUM & Retention
■ VACUUM table RETAIN 168 HOURS
■ Dài =nhiềucost, audit tốt
■ Ngắn =ítcost, mất rollback window
■ Regulated30+ ngày; startup 7 ngày
Delta 4.1 (3/2026) & 4.2 (16/4/2026)
■ Catalog-managed: commit rời filesystem→
catalog(§11)
■ CTAS/RTASatomic; VARIANTGA; UniForm
đồngbộ
■ BậtDV/column mapping không cần
maintenance window
■ Breaking: Java17 +,bỏ Spark 3.5
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 8 / 50

---

### Deletion Vectors & Change Data Feed

Deletion Vectors (Delta 2.3+, Iceberg v3)
Vấn đề: DELETE1row →rewritecảfile(writeam-
plification1000 ×).
Cách hoạt động: bitmap đánh dấu rows xoá trong
sidecar;readerskiptheobitmap,khôngrewritePar-
quet.
Lợi ích:
■ DELETE/UPDATE/MERGE10–100 ×nhanh
hơn
■ GDPR DELETE FROM ... WHERE user_id=X
từgiờ →phút
■ Compact-on-read;physical removal khi
OPTIMIZE
Bật trên table có sẵn: ALTER TABLE ... SET
TBLPROPERTIES('delta.enableDeletionVectors'=true)
— từ Delta 4.1 việc bật nàykhông chặn transac-
tion đang chạy.
Change Data Feed (CDF)
Use case: downstream consumer cần biếtcái gì
thayđổi,không phải full snapshot.
Cách bật: TBLPROPERTIES
(delta.enableChangeDataFeed = true)
Đọc deltas:
spark.read.format("delta").option("readChangeFeed","true")
.option("startingVersion",5).table("silver.users")
Output columns: _change_type (insert / up-
date_pre / update_post / delete) + version + times-
tamp.
Pattern: BronzeCDF →SilverMERGE →Goldin-
crementalrefresh =streaming-likebatch.
Kếthợp: Deletion Vectors+ CDF + MERGE =canonical CDC sink pattern. Không cần custom apply logic.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 9 / 50

---

### Time Travel: API

# Version-based
df = spark.read. format("delta") \
.option("versionAsOf", 5).load(path)
# Timestamp-based (point-in-time query)
df = spark.read. format("delta") \
.option("timestampAsOf", "2025-01-15 00:00:00").load(path)
# Restore (rollback) --- new version, same data as v10
DeltaTable.forPath(spark, path).restoreToVersion(10)
spark.sql("DESCRIBE HISTORY delta.`{}`".format(path)) # audit
versionAsOf (sốversion) · timestampAsOf (point-in-time)· restoreToVersion (rollback)· DESCRIBE
HISTORY =audit log built-in. KHÔNG phải backup —sống trong VACUUMretention(7 ngày).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 10 / 50

---

### Time Travel: Use Cases & Limits

4 Use Cases
■ Modelreproducibility — pin training set
version
■ Rollbackbad ingestion — instant vs2+ giờ
manualfix
■ A/Btest datasets — timestamp queries
■ Regulatoryaudit — DESCRIBE HISTORY=
compliancelog
Limits cần biết
■ Bịgiới hạn bởi VACUUMretention (default 7
ngày)
■ Schema-incompatibleold versions có thể fail
■ Khôiphục ̸=GDPRDELETE — VACUUM
mớixoá vĩnh viễn
Lưu ý: Timetravel + schema registry=DataContracts.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 11/ 50

---

### Data Versioning & MLflow Integration

v0 v1 v2 v3 v4 v5
Initial
load
Add
columns
Upsert
100K
Bad
data
RESTORE
tov2
New
ingest
MLflowrun-1
data_version=1
MLflowrun-2
data_version=3
MLflow run_id ↔Deltatable version =reproducibletraining. Full lineage: data→features →model →deploy.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 12 / 50

---

### Delta Lake vs Iceberg vs Hudi

Feature Delta Lake Iceberg Hudi
ACIDTransactions ✓ ✓ ✓
TimeTravel ✓ ✓ ✓
DeletionVectors ✓(2.3+) ✓(v3) ✓(MOR)
HiddenPartitioning × ✓ ×
Branching/Tagging Tagonly ✓+Nessie ×
Multi-enginenative viaUniForm ✓(default) ✓
Row-levelUpdates MERGE+ DV MERGE+ DV MOR(fastest)
Ecosystem(origin) Databricks(2017) Netflix,Apple (2018) Uber(2016)
Iceberg metadata: metadata.json → manifest list → manifests →Parquet. Apache XTableconvert
Delta ↔Iceberg ↔Hudi. MOR(Merge-On-Read) =ghidelta, merge lúc đọc (ghinhanh nhất).UniForm =1bản
Parquet,nhiều format metadata.Hudi 1.x: secondaryindex + partial update +non-blocking concurrency.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 13 / 50

---

### Iceberg Hidden Partitioning (Game Changer)

Hive/Delta cách cũ
-- Need extra partition column
CREATE TABLE events (
ts TIMESTAMP,
ts_day DATE, -- duplicate!
user_id BIGINT)
PARTITIONED BY (ts_day);
-- User MUST filter ts_day
SELECT * FROM events
WHERE ts_day = '2026-04-01';
-- Forgot ts_day = full scan!
SELECT * FROM events
WHERE ts > '2026-04-01'; -- BAD
Vấn đề: ts_dayduplicatedữliệu,userdễquênfilter
→fullscan.
Iceberg cách mới
-- Partition is a transformation
CREATE TABLE events (
ts TIMESTAMP,
user_id BIGINT)
PARTITIONED BY (days(ts));
-- User filters natural column
SELECT * FROM events
WHERE ts > '2026-04-01';
-- Iceberg AUTO-prunes!
Transforms: years / months / days /
hours(ts), bucket(N, col) , truncate(N,
col).
Partition Evolution: đổi days(ts) →
hours(ts) khôngcần rewrite data.
Tại sao quan trọng: đasố performance regression trong productionlakehouse là vì userquênpartition column. Hidden
partitioningloại bỏ cả class bugsnày.LinkedInciteđây là lý do chínhmigrate Hive→Iceberg.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 14 / 50

---

### Khi Nào Chọn Iceberg vs Delta Lake?

Chọn Delta Lake khi
■ Databricksecosystem heavy
■ Spark-firstworkloads
■ Zerofriction với Databricks Runtime
■ Teamquen thuộc Delta API
Chọn Iceberg khi
■ Multi-engine: cùng 1 tablequery từ Spark,
Trino,Flink, Snowflake
■ Vendorneutrality + partition evolution
■ RESTCatalog: Polaris (SnowflakeOSS),
Nessie(git-like branching cho data!)
■ GDPRrow-level deletes
Adoption 2026: Netflix· Apple · LinkedIn· Adobe ở quymô lớn. AWSAthena/EMR mặc định. Snowflake native (Horizon
chạytrên Polaris). Icebergv3 GA H1 2026 (spec 6/2025;Snowflake 7/5, Databricks 28/5 · DBR18+);stable line 1.11
(19/5/2026)thêmREST scan planning. Iceberg=chuẩnmở de facto.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 15 / 50

---

### Iceberg Metadata: 3 Tầng & Cái Giá Của Planning

Catalog
con trỏ
metadata.json
schema, snapshots
manifest list
1 / snapshot
manifests
N files
Parquet
data files
Đổi con trỏ= commit atomic Lịch sử snap-
shot → time travel
Partition stats mỗi manifest min/max, row count mỗi file Dữ liệu thật
Planning = đọc metadata TRƯỚC khi đọc 1 dòng data. Client tải manifest list→ tải N manifests→ lọc theo min/max
→ mới biết đọc file nào. Bảng lớn→ hàng trăm manifests→ planning chiếm phần lớn thời gian query. Đây là lý do Net-
flix: 9,6 phút→ 42 giây khi tối ưu tầng này.
Iceberg 1.11 (19/5/2026): planning ở server
■ Engine POST .../plan →catalogduyệt
manifests,trả FileScanTask
■ Scanlớn →trả plan-id đểpoll; scan
khổnglồ →parallel plan-tasks
■ Clientnhẹ RAM hơn, job khởiđộng nhanh
hơn
Hệ quả lớn hơn: bảo mật
Catalog plan hộ⇒ catalog có thể áprow filter +
column maskngaylúcplanning ,chỉtrảvềfile/dòng
đượcphép.
Đây là nền chocross-engine access control —
mộtchính sách, mọi engine. Chi tiết §11.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 16 / 50

---

### Iceberg v4: Metadata Được Thiết Kế Lại ( chưa ship)

Đề xuất Giải quyết gì Trạng thái 8/2026
Adaptivemetadata trees Thaycây manifest bằng node columnar(Parquet)
phẳnghơn →planningtiệm cậnO(1)
Specphase
Single-filecommits CommitI/O từO(manifests) → O(1)—mở khoá
streaming
Đikèm adaptive trees
Relativepaths Bảngportable qua bucket/region, không rewrite
metadata(DR, migration)
Độclập, có thể ship sớm
Columnfamilies Nhómcột tiến hoá độc lập— bảng feature ML
rộng,backfill 1 nhóm
Draftgần xong (có thể v3.x)
Vì sao phải làm lại
CâymetadataIceberg thiết kế cho batch;writeam-
plification tạo commit latency màstreaming không
chịunổi.
Chốt: 1 commit/giây= 86.400 snapshots/ngày —
bất khả thi trên v3. (Extensible statistics — index
cắmthêm — còn xa hơn,Q1/2027+.)
Timeline — đừng nhầm với sản phẩm
Hiện chỉ là design doc+ IEP + dev-list. Chưa có
spec draft, chưa có implementation.
■ Specdraft: cuối 2026
■ Bảnthử nghiệm: giữa2027
■ Production: cuối 2027sớmnhất
Hôm nay: stable line= 1.11 (v3). Commit quá dày
→batching +compaction(§6, §9),khôngchờ v4.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 17 / 50

---

### Query Engines cho Lakehouse

Engine Sweet Spot Scale Format Support
SparkSQL ETL,batch ML pipelines TB–PB Delta,Iceberg, Hudi (native)
Trino FederatedBI, ad-hoc SQL GB–PB Iceberg(native), Delta (connector)
DuckDB Single-nodeanalytics, dev MB–100GB Parquet/Delta/Icebergvia extensions
Photon Databricks-onlyfast SQL TB–PB Delta,Iceberg
Athena Serverlessad-hoc on S3 GB–TB Icebergnative, Delta read-only
Quy tắc chọn
■ <100GB, 1 dev:DuckDB—zero infra
■ ETLSpark-native: Spark SQL
■ BImulti-source: Trino
■ AWS-onlyserverless: Athena
Anti-pattern
ĐừngchạySparkclustercho5GBquery—DuckDB
nhanhhơn,rẻgầnnhư 0. Chỉscale-upkhidata >1
nodeRAM.
Cảnh báo phân loại: bảngtrên trộn 2 trục. Spark SQL / Trino/ Athena làinterface(bạnviết SQL vào đó); Photonlà
execution kernel (chạybên dưới Spark). Slide sau tách 2 trục nàyra.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 18 / 50

---

### Native Execution: Engine Không Còn Là Một Khối

Interface — SQL / DataFrame (Spark SQL, Trino, DuckDB)
Plan — logical → physical, trao đổi qua Substrait
Execution kernel — vectorized C++/Rust (Photon, Velox, DataFusion)
Memory — Apache Arrow columnar batches
Storage — Parquet + Delta/Iceberg trên object storage
Kernel Nguồn Cách hoạt động Khi nào
Photon Databricks,đóng VectorizedC++, tương thích Spark
API
Đãở Databricks
Gluten +Velox OSS, ASF TLP
5/3/2026
Dịchphysical plan →Substrait →
JNI →C++;JVM vẫn điều phối
Sparktự quản, muốn phủ rộng
plan
DataFusionComet OSS(Rust +
Arrow)
Nhắmlátmỏng: scan+filter;bật
nhẹ,không đổi code
Workloadnặng scan Parquet
FabricNEE Microsoft,
managed
Gluten-based,vận hành hộ Đãở Fabric
Cùng một cơ chế: DataFusionvàVeloxđều vectorizedcolumnar —dữliệuchảytheo batch cột Arrow,khôngphải
từngdòng. Arrow (bộnhớ) +Substrait(plan) +kernel → đổi kernel mà không đổi SQL .Bản Iceberg Rustnay
chạynative scan operator của Comet.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 19 / 50

---

### Columnar vs Row Storage

Row-oriented (Avro/JSON)
Row1 id name age city
Row2 id name age city
Row3 id name age city
Columnar (Parquet/ORC)
id
v1
v2
v3
name
v1
v2
v3
age
v1
v2
v3
city
v1
v2
v3
Read only age!
SELECT 5/100 columns→ đọc ∼5% data (Parquet) vs
100% (JSON). Compression: Snappy (default, fastest),
ZSTD (3× smaller, hơi chậm), GZIP (chậm nhất).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 20 / 50

---

### Partition Strategy cho AI Workloads

Partition Rules
■ Target: 100MB –1GB mỗi partition file
■ Partitionby low-cardinality: date, region
■ Khôngpartitiontheo user_id (high-card)
■ Over-partition →smallfiles →slow
■ Under-partition →largescans →wasteIO
Z-ORDER vs Partitioning
■ Partition: physical directory separation
■ Z-ORDER:co-locate within files
■ Kếthợp: partition bydate + Z-ORDER by
user_id
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 21 / 50

---

### Table Maintenance: 4 Job Bắt Buộc (Không Phải Tuỳ Chọn)

Job Không chạy thì sao Delta Iceberg
Compaction Smallfiles →querychậm, cost
phituyến
OPTIMIZE rewrite_data_files
Clustering/ sort Statslỏng →khôngskip được
file
ZORDER BY /Liquid sort/ zorder
Hếthạn snapshot Metadataphình, list chậm,
storagerác
VACUUM RETAIN n
HOURS
expire_snapshots
Xoáorphan files Trảtiền cho rác vô hìnhtừ job
fail
VACUUM (cùnglệnh) remove_orphan_files
Job thứ 5 cho streaming/CDC
■ Rewrite manifests —manifest vụn →
planningchậm (§4)
■ Nén delete files —Flink CDC sinhequality
deletes;không gộp →mỗiread phải merge
thêm
Small-file problem làfailure mode phổ biến nhất
củalakehouseproduction—nhiềuhơnmọinguyên
nhânkhác cộng lại.
Ai chạy: tự quản vs managed
■ Tự quản: cron/Airflowgọi các thủ tục trên—
rẻ,nhưng phải nhớ
■ Managed: S3Tablesauto-compaction,
Databrickspredictive optimization — tiện,
nhưngcó hoá đơn riêng(§11FinOps)
Bẫy: “fullymanaged” ̸=miễnphí—compactiontính
tiềntheo GBvàtheomỗi 1.000 object.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 22 / 50

---

### Parquet Internals: Tại Sao Nhanh?

File Header (PAR1 magic) + Schema
RowGroup 1
128MB
RowGroup 2
128MB
RowGroup 3
128MB
Footer: Schema + Stats (min/max/null) + Page Index + Bloom Filters
Reader strategy (4 levels of skip): (1)đọc footer trước (∼KB) →skipRow Groups bằng min/max stats→(2)đọc
Page Index →skippages →(3)dùng Bloom Filter skipvalues chắc chắn không có→(4)đọc chỉ columns trong
SELECT.
Compression: Snappy(default, fastest) · ZSTD (3×smaller,hơi chậm) · GZIP(chậm nhất).Quytắc:
Bronze=Snappy(fast write); Gold=ZSTD(slow write OK, fast read).
Practical impact: WHERE user_id=42 trên1TB Parquet với bloomfilter→đọc ∼50MB. Cùng query CSV/JSON
→full1TB. 20,000× I/O reduction.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 23 / 50

---

### Schema Evolution Playbook

Change Safe? How Notes
Addcolumn (nullable) ✓ ADDCOLUMN;
mergeSchema=true
Existingrows =NULL
Addcolumn (with default) ✓ Icebergv3 native Delta: backfill MERGE
Renamecolumn ∼ Iceberg: RENAME (field ID) Delta: cần column mapping
Dropcolumn ∼ DROPCOLUMN OPTIMIZEphysical remove
Typewiden (int →bigint) ✓ ALTERCOLUMN TYPE Compatiblecast
Typenarrow(double →int) × —không cho phép DATALOSS
Changepartition column ∼ Icebergpartition evolution Delta: rewrite
Movecolumn position ✓ ALTERCOLUMN ... AFTER Cosmetic,an toàn
Pattern an toàn: (1)Deploy reader code biết columnmới NULL-able→(2)Add column →(3)Backfill →(4)Update
writer. Đảo thứtự=productionoutage.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 24 / 50

---

### Medallion Architecture cho AI

Bronze
Raw / Ingested
Silver
Cleaned / Validated
Gold
Aggregated /
Feature-ready
deduplicate,PII-scrub aggregate,feature eng.
Raw LLM outputs
User inputs (JSON)
Synthetic data
Deduplicated, validated
PII removed
Schema enforced
Feature tables, metrics
Doc chunks + embeddings
RAG-ready datasets
Streaming
Ingestion
RAGPipeline
Embeddings
MLTraining
FeatureStore
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 25 / 50

---

### Medallion: Schema Cụ Thể (LLM Observability)

Layer Bronze (raw) Silver (clean) Gold (analytics)
Schema request_id, ts,
raw_json
request_id, ts,
model, prompt_tokens,
completion_tokens,
latency_ms, user_id,
status
date, model,
p50/p95_latency,
total_tokens,
cost_usd, error_rate
Cardinality 1row per LLM call 1row per call (validated) 1row per (date, model)
Partition ingest_date date date(Z-ORDER model)
Retention 30ngày 1năm 5năm
Consumer Replay/ debug Featurestore, RAG corpus Dashboards,alerts, FinOps
Quy tắc: Bronzeappend-only (immutable audit), Silver upsert(MERGE), Gold rebuild-from-Silver (idempotent).
Schemarõ ràng mỗi layer=datacontract giữa teams.Tổng quát hoá cho AGENT trajectories: Bronze =raw
steps/tool-callJSON; Silver =parsed(tool, latency,status, cost,trajectory_id); Gold =per-agent
success_rate/cost/step_count. Lakehouse=system-of-record;vector store + LangGraph checkpoint=derived
memory.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 26 / 50

---

### Lakehouse + AI: Production Patterns

Data Lineage & RAG
■ Raw →processed →model →deploy
versionchain
■ RAG:doc chunks + embeddings lưuGold
■ Embeddinggắn doc version=fullytraceable
■ PinDelta version trong MLflow runcho
reproducibility
Cost Optimization
■ S3Intelligent-Tieringcho cold Bronze data
■ Glaciersau 90 ngày→ −60%storage cost
■ AWSS3 Tables =managedIceberg
(auto-compaction),v3 từ 11/2025
■ Unity/Polaris: fine-grained access +audit
LLM Observability Pipeline
■ Inferencereq/resp →Bronze(raw JSON,
30d)
■ Dedup+ parse tokens/latency→Silver
■ Aggregate(date, model) metrics→Gold
Synthetic Data Pipeline
■ LLMgenerate →Bronze(output + prompt)
■ Qualityfilter + MinHash dedup→Silver
■ Curatedset + license tags→Gold
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 27 / 50

---

### CDC (Change Data Capture): Postgres → Lakehouse

Postgres
MySQL
Debezium
WAL reader
Kafka
+ Schema Reg.
Hudi/Delta
Streamer
Bronze
Table
binlog/WAL Avromsg durablebuffer MERGEupsert
Source DB CDC connector Decouple uptime Apply CDC Lakehouse
3 failure modes phổ biến:
(1) Kafka full→ Postgres WAL fills→ DB outage.Fix: alert on Debezium lag + Kafka retention dài.
(2) Source schema change breaks pipeline.Fix: Schema Registry +mergeSchema=true ở sink.
(3) Out-of-order events tạo bad updates.Fix: MERGE ... WHEN MATCHED AND src.ts > tgt.ts .
Vietnam context: chuẩncho fintech VN (MoMo, VNPay,Cake) — Postgres OLTP→Iceberg/Deltaanalytics.
End-to-endfreshness 1–5 phút, không impactOLTP.(WAL/binlog=Write-AheadLog: nhật kýthay đổi DB đọc lại
được.) Flink-native streaming →ApachePaimon (LSM-tree, sub-minute mutable streams,output
Iceberg-compatible).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 28 / 50

---

### Streaming → Lakehouse: Vật Lý Của Độ Trễ

Băng trễ Đường đi Đánh đổi
10–30giây Flinktinh chỉnh, checkpoint dày Cầnexpertise phân tán; CDC sinhequality
deletesphải nén
30giây–2 phút Flinkchuẩn; Spark Streaming trigger dày Trigger60s =1.440commit/ngày,file còn
hợplý
1–15phút Sparkthoải mái; Iceberg Kafka Connect
sink
No-code,ít small file; transform hạnchế
Phút Tableflow;Firehose +S3Tables Bậtbằng checkbox; khoá vendor,tiền theo
scale
Giây–phút Broker-native: Redpanda, AutoMQ, Ursa Bỏtầng ingest riêng; có thểchậm producer
3 định luật không thể lách
1. Dữliệu vôhình tớikhi commit vào metadata
2. Committốn thời gian thật (vàigiây,tuỳ object
store)
3. Commitdày →smallfiles →bắtbuộc
compaction
Máy dò nói phét
1 commit/giây = 86.400 snapshot/ngày — không
vậnhành nổi trên v3.
“ĐưaIcebergwritervàobroker khôngbãibỏ commit
floor.”
Ai hứa freshness queryable dưới 10 giây → soi
kỹ.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 29 / 50

---

### Khi Giây Là Chưa Đủ: 3 Kiến Trúc

Hot/Cold Split
OLAP realtime + Iceberg
Streaming Database
view tăng dần
Stream–Table Federation
union đuôi chưa commit
Pinot / StarRocks / ClickHouse / Druid giữ dữ
liệu mới; Iceberg giữ lịch sử; query trải cả hai
RisingWave / Materialize giữ view cập nhật
liên tục, sink kết quả xuống Iceberg để bền
Query layer nối đuôi stream chưa
commit với thân Iceberg đã commit
Phổ biến nhất production Sạch về mặt logic Chưa chín 2026
Câu trả lời của vendor
Databricks LTAP (Lake Transactional/Analytical
Processing): workload giao dịch và phân tích
đọc/ghi cùng một bản ở format mở, thay vì 2 bản
đồngbộ bằng ETL/CDC.
Lakehouse//RT (engine Reyden): serving trực tiếp
trên Delta/Iceberg. Databricks công bố sub-100ms
@12.000 QPS, thấp nhất∼10ms.
Đọc con số vendor thế nào
Chưacóbenchmarkđộclậpchocácsốtrên →coilà
địnhhướngkiếntrúc ,khôngphảicamkếthiệunăng.
Điều có thật: tầng serving đang gộp vào chính
bảng lakehouse thay vì đứng cạnh nó — hướng
đichung của cả Databricks lẫnSnowflake.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 30 / 50

---

### Case Studies: Lakehouse ở Quy Mô Production

Công ty Format & Scale Số liệu công khai
Uber Hudi· 350 PB 6T rows/day · 19,500 datasets· freshness 24h
→1h
Netflix Iceberg +Lance Atlasqueryplanning9,6phút →42giây·Media
DataLake: Parquet →Lancecho video frame
Apple Iceberg “Foundationcho lakehouse on all divisions”(MB
→PB)
LinkedIn Iceberg MigrateHive →Icebergvì hidden partitioning +
queryplanning
Shopify Iceberg+ Trino Openlakehouse, multi-engine BI + ML
Bài học chọn format
■ Append-mostly(logs, events) →
Delta/Iceberg
■ Mutation-heavy(orders, sessions) →Hudi
■ Multimodal(video, embeddings) →Lance+
Iceberg
Vietnam Context
MoMo,Zalo,ShopeeVN →TB–PB.Patternchuẩn:
Postgres → Debezium → Kafka → Iceberg/MinIO.
PDPL91/2025 →on-premMinIOkhảthichodữliệu
nhạycảm.
Khảosát 2026 (N=252lãnh đạo dữ liệu): 58% dùng Iceberg cho analyticstrọng yếu, 95% dùng/định dùng choAI/ML —
dovendor tài trợ, đọc nhưxu hướng chứ không phải thịphần.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 31 / 50

---

### Format War 2024–2026: Đã Kết Thúc

Delta Lake
+UniForm
Apache
Iceberg v3
Apache
Hudi
UniForm XTable
Key events: Databricks mua Tabular $1B+ (2024) · Delta 4.0 GA 9/2025 · Iceberg v3 GA H1 2026
(Snowflake 7/5, Databricks 28/5 · DBR 18+): DV + row lineage+ VARIANT + default + geo ·Ice-
berg 1.11 (19/5/2026) ·Delta 4.2 (16/4/2026). Vì sao kết thúc: cùng primitives→ chọn theocatalog
+ ecosystem. Mặt trận mới: cả hai dành 2026 ship tính năngphía catalog— cạnh tranh dời lên
tầng trên (§11).
Catalog Layer
■ AWSGlue — default cho AWSanalytics
(Athena/EMR/Redshift)
■ UnityCatalog — Databricks OSS 2024
■ ApachePolaris — top-level Feb 2026
■ ProjectNessie — git-like branching
■ Lakekeeper— Rust, K8s-native
RESTCatalogspec =linguafranca2026. +Apache
Gravitino (TLP 2025): metadata federation + MCP
choagents.
Branching cho ML reproducibility
nessie tag create v1-prod
nessie branch create exp-2026
# ...train + evaluate on branch...
nessie merge → main
“ModelXdùngdatanào?” → nessie tag list :
trảlời 1 command, thay vìConfluence rotting.
Frontier 2026: DuckLake(v1.0prod4/2026) =metadatatrongSQLDBthaymetadata-files →giải“small-metadata-files”;
ecosystemcòn mỏng — counter-design, khôngphải default.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 32 / 50

---

### Lakehouse cho AI/LLM Workloads

Training data prep at scale
FineWeb (HF): ∼15T tokens · per-snapshot Min-
Hashbeatglobaldedup·ODC-By(siêusetRedPa-
jama30T / Dolma 3T)
Lakehouse: Bronze(raw) →Silver(dedup) →Gold
(train-ready);time travel revert dedup sai.
Embeddings as 1st-class citizen
Embedding version= doc_v × model_v → pin via
Iceberg/Delta + MLflowrun_id. Vector DB= de-
rived index (rebuildable), không phải system-of-
record(rebuild từ Iceberg authoritative).
Provenance của training corpus
Mỗidòngtrainingphảiquyđượcvềđúng mộtnhóm:
licensed · public domain · scraped đã kiểm opt-
out· synthetic có ghi nguồn sinh .
Trộn scraped với licensed trong cùng một bucket
khônggắnnhãn =trượtaudit. Nhãnnàylàmột cột
+partitionkey,khôngphảimộtfileConfluence. Chi
tiết§11.
Multimodal(Lance): xem slideriêng ngay sau.
Stack bổ trợ, không thay thế: Iceberg/Delta(tabular) + Lance (multimodal) +VectorDB (online ANN). VN:corpus
Wiki-VI/ZNews →MinHashdedup trước.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 33 / 50

---

### Agentic Lakehouse: Agents Là Consumer Mới

MCP trên Lakehouse (2026)
Managed MCP servers expose lakehouse cho
agentsqua catalog:
■ Genie →UCtables (NL query,
on-behalf-of-user,UC permissions enforced)
■ AISearch →vectorindex · UC Functions→
governedtools
■ Snowflakeđối xứng: CortexAnalyst MCP→
SQLqua semantic view
Agent KHÔNG query raw table — query qua
semantic layer (entities, named metrics, joins)→
khôngđoán PK/FK.
Governance + Maturity
AI Gateway = control plane: mỗi tool-call check
policy trước, log sau thành catalog system tables
(= Bronze-tier agent telemetry). 2026:contextual
service policies—duyệt/chặnhànhđộngagentlúc
chạytheouser,agent,model hoặcnộidungrequest.
Catalog nay quản cả model, MCP service, agent,
skill.
Thực tế text-to-SQL:ReAct ∼91%trênfamiliarDB,
nhưng Spider 2.0 SOTA chỉ ∼45%; rớt 14–40%
trên heterogeneous DB.Mitigation: semantic layer
+query linting + constrained joins.
Lakehousepassive(chờquery) →agentic(semanticlayer =não);cùng 1 ACID table, thêmgovernance +
observability.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 34 / 50

---

### Multimodal Lakehouse: Khi Một Dòng Nặng 10 MB

3 giả định của Parquet/Iceberg bị lật
Parquet + Iceberg thiết kế chodòng cỡ KB, đọc
tuần tự, theo batch. Multimodal lật cảba:
■ Dòngthành MB(ảnh,clip, audio)
■ Truycập thành random: hàng nghìn
clip/vectormỗi giây
■ GPUphảinạpliêntục—đóidatalàcháytiền
Lance thay đổi gì
■ Randomread ∼3–35×Parquet;vectorquery
tới ∼10×(sốbáo cáo,chưa benchmark độc
lập)
■ Gộp3 tầng: filelayout +tổchức bảng +
namespace
■ Logkiểu Delta →streaminginsert, append
cột,delete, time travel
■ Blobhạng nhất +HNSWindex sẵn
Ai đang chạy
■ Netflix Media Data Lake —Parquet →
Lancecho video frame; Ray chạybatch
inferenceco giãn ở quy môPB
■ Runway—chống GPU starvation khi
training
■ CodeRabbit—gộp Pinecone +Postgresvề
mộtLanceDB
2026: Lance-native SQL qua DuckDB (5/2026),
multi-bucketquy mô Uber,LanceNamespace.
Stack tham chiếu: PyTorch +Ray +Lance/Arrow +K8s
—Lance giữ media thô, embedding,feature; Ray phân
tán;PyTorchtrain.
Bổ trợ, không thay thế: Iceberg/Delta =
system-of-recorddạng bảng · Lance=multimodal·
VectorDB =indexANN online.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 35 / 50

---

### Embedding Đi Thẳng Vào Bảng (Xu Hướng 2026)

Nơi Làm gì Trạng thái
ApacheHudi 1.2 Cột VECTOR(dim, type) hạngnhất;
hudi_vector_search quaSQL
Quét brute-forcephântán; ANN
(IVF-PQ)mới là kế hoạch
DatabricksLakebase Vectorngay trong tầng
OLTP-trên-lakehouse
Sảnphẩm
AWSS3 Vectors Vectorbucket native trên objectstorage GA12/2025
Iceberg/ Delta Lưuembedding nhưdatasetcó version +
lineage
Dùngđược ngay hôm nay
Lý do thật: vòng đời, không phải tốc độ
Khi một dòng bị xoá, hết hạn, sửa hay xử lý lại thì
embedding phải đi theo đúng vòng đời đó .
Mọipipelineđồngbộwarehouse →vectorDBlàmột
bug lệch vòng đời đangchờxảyra—gặp right-to-
forgetthìthành bug tuân thủ.
Đọc kỹ trước khi bỏ vector DB
Brute-force trong bảngkhông phải đường serving
sub-100ms — nó hợp semantic queryphân tíchvà
đorecall offline.
Số học: VECTOR(768, FLOAT) =3.072B/dòng;
INT8 =768B/dòng (nhỏ hơn 4×).
Quy tắc: vectorDB =indexpháisinhdựnglạiđược;
lakehouse =system-of-record. (Ngày 19)
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 36 / 50

---

### Semantic Layer Là Hợp Đồng: Apache Ossie

Vì sao agent cần tầng ngữ nghĩa
Câuchốt của cả ngành 2026:
“Khiagentquerydữliệuthô,nótrảlời sai một cách
tự tin, ở tốc độ máy .”
Bằng chứng định lượng: ReAct đạt∼91% trên DB
quen, nhưng SOTA trênSpider 2.0 chỉ ∼45%; rớt
14–40%khi DB không đồng nhất.
Semanticlayerlàcâutrảlời kỹthuật: thuhẹpkhông
giantìmkiếmcủaagent,thayvìhyvọngmodelđoán
đúngkhoá join.
Apache Ossie (Incubating)
Tên mới của Open Semantic Interchange (OSI)
saukhi vào Apache Incubator.
■ Spec v1.0 công bố 27/1/2026
■ Chuẩnhoá trung lập:dataset, metric,
dimension, relationship, context
■ Snowflake,Salesforce, dbt Labs, Databricks,
BlackRock +30+tổchức; 50+contributor
■ Phase2 (Q2–Q4 2026): hỗ trợ native ở 50+
nềntảng
Ý nghĩa thực tế: địnhnghĩametric mộtlần,dashboardBIvàagenttrảvề cùngmộtconsố . Khôngcóchuẩnnày,mỗi
côngcụ có một định nghĩa“doanh thu” riêng — và agentsẽ chọn nhầm. Semanticlayer từmiddlewaretuỳ chọn
thành hạ tầng bắt buộc.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 37 / 50

---

### MCP 2026-07-28: Giao Thức Agent ↔ Lakehouse

Thay đổi Nội dung Vì sao data team quan tâm
Statelesscore Bỏhandshake initialize và
Mcp-Session-Id;mỗi request tự
môtả trong _meta
MCPserver trên catalog chạy sauload
balancer round-robin,không cần
sessionstore
MultiRound-Trip
Requests
Tươngtác giữa chừng qua
resultType:
input_required
Chốthuman-in-the-loop trước DELETE
/xuất dữ liệu xuyên biêngiới
Headerrouting Header Mcp-Method, Mcp-Name Gatewayđịnh tuyến + đo tiền theo
toolmàkhông parse JSON
Cacheablelists tools/list, resources/read
kèm ttlMs, cacheScope
Catalog50.000 bảng thôi tự liệtkê lại
mỗilượt agent
Authzsiết chặt RFC9207 issuer validation; DCR→
CIMD;token gắn với server phát
hành
Tokencủa agentkhôngreplayđược
sangcatalog khác
Extension tasks Poll-based tasks/get /
tasks/update
Đúnghình dạng cho một Sparkjob 40
phút
Hai giao thức khớp nhau: agentbắn một scan petabyte thìphải nhậntaskhandle rồipoll (MCP Tasks)— và
lakehousetrả plan-id rồipoll (Iceberg 1.11scanplanning, §4). Cùng mộthình dạng. Ngoàira: chính sách
deprecationtối thiểu 12 tháng →đủổn định để xây governancelên trên.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 38 / 50

---

### Agent Memory & Trajectory: Lakehouse Là System-of-Record

Loại bộ nhớ Kiểu truy cập Tầng lưu trữ
Working/ state (checkpoint,
rule,profile)
Trakhoá chính xác, nhanh, hay
đổi
TầngOLTP
(Postgres-trên-object-storage)
Episodic/ semantic (kinh
nghiệmcũ)
Tươngđồng ngữ nghĩa Vectorindex —pháisinh
Bản ghi bền (hộithoại +
trajectory)
Append,replay,audit, tổng hợp Bảng lakehouse —
system-of-record
Trajectory: workload mới của LLM era
Một trajectory (rollout) = chuỗi (observation,
action, reward) từ trạng thái đầu tới khi kết
thúc— nhiên liệu để RLcập nhật policy.
Kháccơbảnvớisupervised: phân phối dữ liệu đổi
khi policy tốt lên →datasettĩnhkhôngdùngđược.
Bảngtrajectoryvìthế append-heavy,cóversion,cắt
đượctheo policy.
Áp vào medallion (§8)
Bronze =step/tool-callJSONthô·Silver =đãparse
(tool, latency, status, cost, trajectory_id) ·
Gold =success_rate/cost/step_counttheoagent.
Thêm 2 quy tắc: partition theoagent_version
(hoặc policy version); vàpin version bảng trajec-
tory vào training run — đúng hợp đồng repro-
ducibilitynhư MLflow ↔Deltaversion (§3).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 39 / 50

---

### Catalog Layer: REST Standard 2026

Catalog Origin Killer feature Khi nào dùng
AWSGlue AWS,2017 DefaultAWSanalytics
(Athena/EMR/Redshift)
Đãở AWS
UnityCatalog Databricks,OSS
2024
Governance+ ML models / feature
tables/ agent functions
Databricks-native
ApachePolaris Snowflake,TLP
18/2/2026
RESTtrung lập; remote signing Multi-cloud
ApacheGravitino Datastrato,TLP
2025
Metadatafederation + AI Model
Catalog+ MCP Server
Heterogeneous+ agent
ProjectNessie Dremio,2020 Git-likebranching/tagging MLversioning
Lakekeeper OSS2024 (Rust) 1binary,K8s-native, authz
OpenFGA +OPA
Self-hosted
REST Catalog spec
HTTPAPIchuẩnchometadataIceberg;mọiengine
plug-and-play.
1.11 thêm: POST /plan (planning phía server)+
signerproperties →remotesigning.
Multi-table transactions
Catalog-levelcommit =atomicupdatenhiềutables.
Use case: Bronze + Silver + Gold update phải all-
or-nothing.
Nessienative(gitcommit);Polarisđangimplement.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 40 / 50

---

### Catalog = Control Plane: Chuyển Dịch Lớn Nhất 2026

TRƯỚC
Engine
tự duyệt manifest
Catalog
chỉ tra tên bảng
Credential rộng phát thẳng cho en-
gine; mỗi engine tự áp policy riêng
NAY
Engine
gửi yêu cầu scan
Catalog
plan + filter + cấp quyền
Trả về đúng file được phép
+ credential scoped, tạm thời
Hai phe, cùng một nước đi
Iceberg 1.11 (19/5/2026) — RESTscan planning:
catalogduyệtmanifest,trả FileScanTask;áprow
filter +columnmask lúcplan.
Delta 4.1(3/2026)— catalog-managedtables: com-
mit coordination chuyểntừ filesystem sang cata-
log; uỷ quyền planning cho Unity Catalog+ push-
down +credentialscoped.
Hệ quả cho kiến trúc
■ Một policy, mọi engine —không còn nhân
bảnquyền ở Spark, Trino,Snowflake
■ Remote signing thayvì phát credential thô
(Polaris,Lakekeeper theo signer properties
của1.11)
■ Snowflake: Horizon chạy trênPolaris+
ExternalEngine Access Management
■ Chọncatalog nay làquyếtđịnh kiến trúc,
khôngphải chi tiết cấu hình
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 41 / 50

---

### Data Quality & Contracts: 3-Tool Stack

Great Expectations
Where: Bronzeingestion
What: validateraw data
Strength: 50+expectations
expect_column_values_to_be_in_set(
column="status",
value_set=["ok",
"rate_limited","error"])
dbt tests
Where: Silver/Goldtransforms
What: structuralcorrectness
Strength: SQL-native
# schema.yml
- name: customer_id
tests:
- unique
- not_null
- relationships:
to: ref('dim_customers')
Soda
Where: Prodmonitoring
What: continuous,anomaly
Strength: SodaCLDSL
checks for gold.metrics:
- row_count >= 1000
- freshness < 1h
- anomaly_score
< 0.7 for cost_usd
Data Contract: schema+ constraints + freshness SLA+ ownership; run trong CI (pre-merge)vàruntime(per-batch). Bể
contract →blockpipeline.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 42 / 50

---

### Agentic Data Engineering: Pipeline Tự Chữa

Observe Reason Act Learn
null rate, schema,
outlier, freshness phân loại mức nghiêm trọng
vá trong ngưỡng,
hoặc escalate
ghi kết quả để
lần sau tốt hơn
Ranh giới: agent được làm gì
Tự vá(đảongượcđược,cóbiên): retry,backfillmột
partition,cáchlydònglỗi,nớimộtcộtthànhnullable.
Phải escalate (không đảo ngược được): thu hẹp
schema, VACUUM,xoádữliệu,chuyểndữliệuxuyên
biêngiới.
Agent đề xuất — data contract quyết định cócho
áphay không.
Vì sao chuyện này thuộc bài Lakehouse
Mọihànhđộngcủaagenttrênbảngđềulàmột com-
mit →nằmtrongtablehistory → revert được bằng
time travel.
ChínhACIDloglàthứkhiếnremediationtựđộngtrở
nênantoàn. Timetravellànútundocủaagent(§3).
Đọc số cẩn thận: cácconsố“giảm70–80%triage”,
“ROI 10×” đều từ blog vendor, không có phương
phápđo — đừng mang vàobusiness case.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 43 / 50

---

### Data Lineage: OpenLineage + Marquez

Bronze.events Sparkjob
clean+dedup Silver.events dbtmodel
aggregate Gold.metrics
Dashboard
MLfeature
OpenLineage: OSS standard — Spark/Airflow/dbt/Flink emit lineage events tự động.Mar-
quez: reference server (graph DB + UI). Trả lời: “Drop column X→ ai bị ảnh hưởng?” ·
“Gold metric Y sai→ truy ngược về Bronze nào?”
Pattern: bậtOpenLineage từ ngày 1. Spark: spark.openlineage.transport.type=http +MarquezURL.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 44 / 50

---

### Security & Governance cho Lakehouse

Access Control Models
■ RBAC:role-based(admin/analyst/eng)
■ ABAC:attribute-based(region,
classification)— Unity/Polaris
■ Row-level security: dynamicfilter
■ Column masking: hash/redactPII
PII Handling
■ TokenizePII at Bronze landing
■ Encryptat field level (Iceberg v3native)
■ Right-to-forget: DELETE + VACUUMsau
30dgrace
■ Auditlog mọi PII column access
Vietnam Compliance
PDPL Law 91/2025/QH15 (hiệu lực 2026-01-01,
Decree 356/2025 hướng dẫn) chồng lênDecree
13/2023(khôngthay thế):
■ Residency: dữ liệu nhạycảm ở VN
■ Cross-border: Mẫu 09 nộp Bộ Công an
■ Right-to-forget: 72h SLA
■ ND356 có điều khoản riêngcho tài
chính–ngânhàng, dữ liệu lớn,AI,blockchain
Impact: lakehousephục vụ AIbịgọi tên.
Auditing pattern
■ Everyread/write →Bronzeaudit table
■ Iceberg: system.snapshots table
■ Retention365+ ngày cho regulated
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 45 / 50

---

### Provenance Dữ Liệu Huấn Luyện: Hạn Chót Đã Tới

EU AI Act — áp dụng từ 2/8/2026
Nghĩavụchohệthống high-riskcóhiệulực 2/8/2026
—tức đãcóhiệu lực.
■ Điều 10 gắnvào tậptrain/ validation / test:
nguồngốc, cách chuẩn bị (labelling,cleaning),
kiểmbias, khoảng trống dữ liệu
■ Phụ lục IV:tài liệu kỹ thuật môtả dữ liệu đã
dùng
■ GPAI:chính sách tôn trọng opt-outmáy đọc
được +côngbố “bản tóm tắt đủchi tiết” về nội
dunghuấn luyện
4 rổ — và chúng là một CỘT
Mỗidòng training phải quy vềđúng một rổ:
1. Licensed(cóhợp đồng)
2. Public domain
3. Scraped đã kiểm opt-out
4. Synthetic +ghinguồn sinh
Trộnscrapedvớilicensedtrongmộtbucketkhông
gắnnhãn =trượtaudit 2026.
Tin tốt: luật đang đòi đúng thứ bài học này dạy bạn xây. “Chuẩnbị, làm sạch, dedup, kiểmbias” của Điều 10
chínhlà bướcBronze →Silver. “Mô tảdữ liệu đã dùng” của Phụlục IV=lineage +pinversion bảng. Câuhỏi “model
Xhuấn luyện trên corpus phiênbản nào?”→ DESCRIBE HISTORY +MLflow run_id (§3). 4 rổ trên=mộtcột
governed +partitionkey,không phải mộttrang Confluence.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 46 / 50

---

### Cost & FinOps cho Lakehouse

Component (100
TB/tháng)
Snowflake Iceberg + Trino / S3 Databricks
Storage $4,000 $2,300(S3) $2,300(S3)
Compute(BI) $15,000 $8,000(TrinoEC2) $11,000(DBU)
Compute(ETL) $5,000 $2,000(Spark EMR) $4,000(DBU)
Catalog/gov included $500(Polaris OSS) included(Unity)
Total $24,000 $12,800 (–47%) $17,300 (–28%)
FinOps Practices
■ Per-layerbudget: Bronze →Glaciersau 30d
■ Auto-OPTIMIZEnightly cron
■ Tagclusters: team, purpose,
expires_at
■ Spotcho ETL, on-demand cho BI
■ Managedcompaction tính $/GB + $/1.000
object →lêndashboard
Real benchmarks
■ Cloudera: TPC-DS 24s→1.8s(13 ×),
storage −36%
■ ClickHousevs Snowflake: ∼4×lowerTCO
■ NetflixIceberg: planning9.6min →42s(14 ×)
■ NoOPTIMIZE: 10×moreexpensivethan
DW
Quy tắc: savingschỉ có nếu chủ độngoptimize — và “fully managed” vẫncó hoá đơn:hãyđo, đừng giả định.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 47 / 50

---

### Top 5 Lakehouse Anti-Patterns

# Anti-pattern Hậu quả & Fix
1 “Đổ tất cảvào S3” (raw
JSON,no schema)
Dataswamp →enforceschema từ Bronze; dùng
Delta/Icebergngay từ đầu
2 Partition theo
high-cardinality(vd.
user_id)
Triệupartition nhỏ →partitionby date/region,
Z-ORDER user_id
3 Bỏ qua OPTIMIZE →
small-fileproblem
10Kfiles ×1MB →query10 ×chậm →daily
OPTIMIZEcron
4 VACUUM 0 HOURS để“tiết
kiệmstorage”
Mấttime travel + concurrent readersfail→giữtối
thiểu168h (7 ngày,default)
5 Spark cluster choquery
5GB
Lãngphí 10×chiphí →DuckDB/ Athena cho
<100GB; chỉ scale-up khi>1node RAM
80%lakehouse pain trong production=mộttrong 5 anti-patterns này. Audit checklist trước khideploy.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 48 / 50

---

### Demo: Delta Lake Time Travel & MERGE

LIVE DEMO — 4 tasks ( ∼5 phút mỗi task)
■ Small-file problem —200appends → compact()+ z_order() →stats-basedpruning:
∼1of ∼50files chứa target user (files-pruned≥10×;speedup phụ thuộc RAM, thường
<3×ởmáy nhỏ)
■ Time travel rollback —inject bad rows→ restoreToVersion(N) <30svs ∼2h
manual;verify score<0count =0
■ MERGE upsert —100K rows trong<1s(lightweight); production 100M+ scale→
10–50×vsoverwrite
■ Audit trail — history() sauRESTORE =5versions (gồm cả RESTOREitself)
Lab: VinUni-AI20k/Day18-Track2-Lakehouse-Lab —lightweight (make setup , ∼15s)hoặc
Spark/Docker( make spark-up ).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 49 / 50

---

### Tổng kết — Key Takeaways

Những ý chính cần nhớ trướckhi sang bài tiếp theo
1 Lakehouse = ACID + object storage + open formats —nền chung cho cả 3era.
Mặt trận dời lên catalog: Iceberg 1.11 scan planning và Delta 4.1 catalog-managed làcùng
mộtnước đi—catalog =queryplanner +ranhgiới bảo mật.
3 Maintenance là hạ tầng, không phải dọn dẹp. Streaming cócommit floor— nghi ngờ lời
hứadưới 10 giây.
4 Agent là consumer mới: semantic layer là hợp đồng, embedding về cùng bảng với dữ liệu,
ACIDlog là nút undo.
5 Provenance = hạn chót pháp lý (EUAI Act 2/8/2026; PDPL 91/2025).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 49 / 50

---

### Tiếp theo & Bài tập

Ngày 19: Vector Store & Feature
Store
“SQL trả exact match. AI cần tương
tự — semantic search thay đổi mọi
thứ. S3 Vectors (GA 12/2025): na-
tive vector buckets,∼90% rẻ hơn —
nhưng vector DB vẫn thắng online
sub-100ms.”
■ Hoànthành Lab 18: 8 notebooks
(xemrepo URL trên Deliverable)
■ Đọctrước: case studies(Netflix,
Uber,Apple Iceberg) + Lance
multimodaldocs
■ Càisẵn Docker + Qdrant image
choNgày 19 (VectorStore +
ANN)
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 50 / 50

---

### Hỏi & Đáp

Câu hỏi về Lakehouse, Delta/Iceberg, Medallion,
Catalog, Data Contracts, hay AI/LLM workloads?

---

### Cảm ơn!

AICB-P2T2 · Ngày 18
Data Lakehouse Architecture
lms.vinuni.edu.vn · Lab repo + slides trên LMS