# Day18 Track02 Data Lakehouse Architecture

**File gốc:** `Track_2_BIOM3010_Infrastructure\D03_Day18 - Track2 - Data Lakehouse Architecture\Day18-Track02-Data_Lakehouse_Architecture.md`

---

### Data Lakehouse Architecture

AICB-P2T2 · Ngày 18 · Chương 4: Hạ Tầng
Giảngviên
VinUniversity · Phase 2 · AI Infrastructure Track· Tuần4

---

### ““Đổ tất cả vào S3” — works ở 10GB, ác

mộng ở 10TB, production outage ở 10PB.
Lakehouse = ACID + cheap
storage + AI workloads.
Câu trả lời cho 3 era: Traditional, ML, LLM.”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### NộiDung Bài Học

1. Evolution+ 3 Eras (Trad/ML / LLM)
2. DeltaLake: ACID +Deletion Vectors
+CDF
3. TimeTravel& Data Versioning
4. ApacheIceberg: Hidden Partitioning,
v3
5. QueryEngines (Spark/Trino/DuckDB)
6. StorageOptimization & Anti-Patterns
7. FormatInternals & Performance
Tuning
8. Lakehousecho AI/ML Workloads
9. Streaming& CDC Ingestion
10. IndustrialDeep Dive (AI Thực Chiến)
11. ProductionOps (Catalog, DQ,
Lineage,Security,FinOps)
12. Demo+ Lab repo (notebooks 01–04)
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 1 / 35

---

### Mụctiêu bài học

Saubuổi học này,bạnsẽ:
1. Hiểuevolution storage qua 3 era:Traditional →ML →LLM
2. Triểnkhai Delta/Iceberg: ACID,time travel, deletion vectors, CDF
3. Sosánh Delta vs Iceberg vs Hudi→chọntheo workload (append / mutate /
multimodal)
4. Thiếtkế medallion Bronze/Silver/Gold cho LLM observability+ RAG corpus
5. Ápdụng production ops: catalog, data contracts, lineage, FinOps
Evolution+3Eras →Delta+Iceberg →Storage&Performance →AI/LLMWorkloads
→IndustrialCases →ProductionOps →Demo
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 2 / 35

---

### DeliverableCuối Ngày

LakehouseBronze/Silver/Gold+DeltaACID+timetravel+benchmark—1-to-1với
notebookstrong lab repo.
■ NB1—Delta Lake table với schemaenforcement + transaction log
■ NB2—OPTIMIZE + Z-ORDER benchmark: query time trước/sau (chứng minhsmall-file
problem)
■ NB3—Timetravel: restoreToVersion +MERGE upsert
■ NB4—Medallion pipeline Bronze→Silver →Goldcho LLM observability hoặc RAGcorpus
Labrepo: github.com/VinUni-AI20k/
Day18-AIInfrastructure-Lakehouse-Lab
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 3 / 35

---

### Evolutionof Data Platforms

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
Key Innovation:metadata layer biến S3 object storage thành transactional
store.
Enablers: Open table formats (Delta/Iceberg/Hudi) + cheap object storage
(S3) + query engines (Spark/DuckDB/Trino).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 4 / 35

---

### 3Eras of Software: WorkloadDrives Storage

Aspect Traditional(1990s–2010) ML Era ( ∼2012–2022) LLMEra (2022+)
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
Storagestack mởrộng,không thay thế.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 5 / 35

---

### StorageTech ×EraFit + LLM Demands

Tech Traditional MLEra LLMEra
OLTPDB (Postgres) Primarysystem Appbackend; CDC source for
ML
Appbackend; CDC; user
feedback
Warehouse(Snowflake) BIreporting Featureaggregation + serving BIdashboards on LLM
telemetry
DataLake (S3 + Hive) — Rawevents, training datasets Rawcrawls, multimodal blobs
Lakehouse
(Delta/Iceberg)
— UnifiedBI + ML feature store Trainingcorpus + RAG +
eval+ prompt logs
VectorDB
(Qdrant/Milvus)
— Recommendation(rare) OnlineRAG (sub-100ms)
Multimodal(Lance) — — Video/image/audio+
embeddings
LLM-erademands trên Lakehouse:
■ Trillion-tokendedup (MinHashLSH)
■ Multimodalblobs (Lance/ Iceberg)
■ Embeddingversioning (doc_v ×model_v)
■ Trainingdata provenance(Icebergv3)
■ Licensegovernance (per-doctag)
■ Evalgolden sets(Icebergtags)
■ Prompt+ trace logs→Bronze
LLMera thêmtầng (vectorDB, multimodal) vàéplakehouse =dataset-of-recordcho compliance.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 6 / 35

---

### DeltaLake TransactionLog

_delta_log/
000.json
001.json
002.json
003.json
addpart-001, part-002
addpart-003
removepart-001
addpart-004
ParquetFiles
part-001 part-002
part-003 part-004
ACID: Atomicity + Consistency + Isolation + Durability trên S3 ·Concurrency: optimistic con-
flict detection ·Metadata layer:JSON log biến object store→ transactional table.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 7 / 35

---

### DeltaLake: Thao TácQuan Trọng

■ df.write.format("delta") —basic
write
■ MERGE INTO ... =upsert. Workshop
100K ∼2×;prod 100M+ →10–50×vs
overwrite
■ Schemaevolution: mergeSchema=true
■ Compact →target128MB–1GB
■ 10,000 ×1MB →10 ×1GB
■ Z-ORDER:3–10 ×typical;100 ×bestcase
■ VACUUM table RETAIN 168 HOURS
■ Dài =nhiềucost, audit tốt
■ Ngắn =ítcost, mất rollback window
■ Regulated30+ ngày; startup 7 ngày
■ Successorcho Z-ORDER: incremental
re-cluster
■ Khôngcần rewrite toàn bộ table
■ GADatabricks; OSS Delta 3.3+ đangmở
rộng
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 8 / 35

---

### DeletionVectors& Change DataFeed

Vấnđề: DELETE1row →rewritecảfile(writeam-
plification1000 ×).
Cáchhoạtđộng: Lưubitmapđánhdấurowsbịxoá
trong sidecar file. Reader skip rows theo bitmap.
Khôngrewrite Parquet.
Lợiích:
■ DELETE/UPDATE/MERGE10–100 ×nhanh
hơn
■ GDPR DELETE FROM ... WHERE user_id=X
từgiờ →phút
■ Compact-on-read;physical removal khi
OPTIMIZE
Bật: ALTER TABLE ... SET
TBLPROPERTIES('delta.enableDeletionVectors'=true)
Use case: downstream consumer cần biếtcái gì
thayđổi,không phải full snapshot.
Cách bật: TBLPROPERTIES
(delta.enableChangeDataFeed = true)
Đọcdeltas:
spark.read.format("delta")
.option("readChangeFeed","true")
.option("startingVersion", 5)
.table("silver.users")
Output columns: _change_type (insert / up-
date_pre / update_post / delete) + version + times-
tamp.
Pattern: BronzeCDF →SilverMERGE →Goldin-
crementalrefresh =streaming-likebatch.
Kếthợp: Deletion Vectors+ CDF + MERGE =canonical CDC sink pattern. Không cần custom apply logic.Giảngviên (VinUni) AICB· Ngày 18 Tuần4 9 / 35

---

### TimeTravel: API

# Version-based
df = spark.read. format("delta") \
.option("versionAsOf", 5).load(path)
# Timestamp-based (point-in-time query)
df = spark.read. format("delta") \
.option("timestampAsOf", "2025-01-15 00:00:00") \
.load(path)
# Restore (rollback) --- creates new version ớvi same data as v10
DeltaTable.forPath(spark, path).restoreToVersion(10)
# Audit trail
spark.sql("DESCRIBE HISTORY delta.`{}`".format(path)).show()
3cách query history:versionAsOf (sốversion), timestampAsOf (point-in-time), restoreToVersion (rollback).
DESCRIBE HISTORY =compliance-grade audit log đi kèmbuilt-in.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 10 / 35

---

### TimeTravel: UseCases & Limits

■ Modelreproducibility — pin training set
version
■ Rollbackbad ingestion — instant vs2+ giờ
manualfix
■ A/Btest datasets — timestamp queries
■ Regulatoryaudit — DESCRIBE HISTORY=
compliancelog
■ Bịgiới hạn bởi VACUUMretention (default 7
ngày)
■ Schema-incompatibleold versions có thể fail
■ Khôiphục ̸=GDPRDELETE — VACUUM
mớixoá vĩnh viễn
Lưuý: Timetravel + schema registry=DataContracts.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 11/ 35

---

### DataVersioning& MLflow Integration

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
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 12 / 35

---

### DeltaLake vs Iceberg vs Hudi

Feature DeltaLake Iceberg Hudi
ACIDTransactions ✓ ✓ ✓
TimeTravel ✓ ✓ ✓
DeletionVectors ✓(2.3+) ✓(v3) ✓(MOR)
HiddenPartitioning × ✓ ×
Branching/Tagging Tagonly ✓+Nessie ×
Multi-enginenative viaUniForm ✓(default) ✓
Row-levelUpdates MERGE+ DV MERGE+ DV MOR(fastest)
Ecosystem(origin) Databricks(2017) Netflix,Apple (2018) Uber(2016)
Icebergmetadata: metadata.json → manifest list → manifests →Parquet. Apache XTableconvert
Delta ↔Iceberg ↔Hudi.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 13 / 35

---

### IcebergHidden Partitioning (Game Changer)

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
Vấnđề: ts_dayduplicatedữliệu,userdễquênfilter
→fullscan.
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
Tạisao quan trọng:đasố performance regression trong productionlakehouse là vì userquênpartition column. Hidden
partitioningloại bỏ cả class bugsnày.LinkedInciteđây là lý do chínhmigrate Hive→Iceberg.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 14 / 35

---

### KhiNào Chọn Iceberg vs DeltaLake?

■ Databricksecosystem heavy
■ Spark-firstworkloads
■ Zerofriction với Databricks Runtime
■ Teamquen thuộc Delta API
■ Multi-engine: cùng 1 tablequery từ Spark,
Trino,Flink, Snowflake
■ Vendorneutrality + partition evolution
■ RESTCatalog: Polaris (SnowflakeOSS),
Nessie(git-like branching cho data!)
■ GDPRrow-level deletes
Adoption2026: Netflix· Apple · LinkedIn ·Adobe at scale. AWSAthena/EMR default. Snowflakenative (Polaris).
DatabricksIceberg v3 GA Apr 2026. Iceberg = de factoopen standard.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 15 / 35

---

### QueryEngines cho Lakehouse

Engine Sweet Spot Scale FormatSupport
SparkSQL ETL,batch ML pipelines TB–PB Delta,Iceberg, Hudi (native)
Trino FederatedBI, ad-hoc SQL GB–PB Iceberg(native), Delta (connector)
DuckDB Single-nodeanalytics, dev MB–100GB Parquet/Delta/Icebergvia extensions
Photon Databricks-onlyfast SQL TB–PB Delta,Iceberg
Athena Serverlessad-hoc on S3 GB–TB Icebergnative, Delta read-only
■ <100GB, 1 dev:DuckDB—zero infra
■ ETLSpark-native: SparkSQL
■ BImulti-source: Trino
■ AWS-onlyserverless: Athena
ĐừngchạySparkclustercho5GBquery—DuckDB
nhanhhơn,rẻgầnnhư 0. Chỉscale-upkhidata >1
nodeRAM.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 16 / 35

---

### Columnarvs Row Storage

Row-oriented(Avro/JSON)
Row1 id name age city
Row2 id name age city
Row3 id name age city
Columnar(Parquet/ORC)
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
Readonly age!
SELECT 5/100 columns→ đọc ∼5% data (Parquet) vs
100% (JSON). Compression: Snappy (default, fastest),
ZSTD (3× smaller, hơi chậm), GZIP (chậm nhất).
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 17 / 35

---

### PartitionStrategy cho AI Workloads

■ Target: 100MB –1GB mỗi partition file
■ Partitionby low-cardinality: date, region
■ Khôngpartitiontheo user_id (high-card)
■ Over-partition →smallfiles →slow
■ Under-partition →largescans →wasteIO
■ Partition: physical directory separation
■ Z-ORDER:co-locate within files
■ Kếthợp: partition bydate + Z-ORDER by
user_id
■ DuckDB:query Parquet trực tiếp từS3
■ Zeroinfra, ấn tượng cho<100GB
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 18 / 35

---

### ParquetInternals: Tại SaoNhanh?

File Header (PAR1 magic) + Schema
RowGroup 1
128MB
RowGroup 2
128MB
RowGroup 3
128MB
Footer: Schema + Stats (min/max/null) + Page Index + Bloom Filters
Readerstrategy (4 levels of skip):(1)đọc footertrước (∼KB) →skipRow Groups bằng min/max stats→(2)đọc
PageIndex →skippages →(3)dùng BloomFilter skipvalues chắc chắn không có→(4)đọc chỉcolumns trong
SELECT.
Compression: Snappy(default, fastest) · ZSTD (3×smaller,hơi chậm) · GZIP(chậm nhất).Quytắc:
Bronze=Snappy(fast write); Gold=ZSTD(slow write OK, fast read).
Practicalimpact: WHERE user_id=42 trên1TB Parquet với bloomfilter→đọc ∼50MB. Cùng query CSV/JSON
→full1TB. 20,000×I/Oreduction.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 19 / 35

---

### SchemaEvolution Playbook

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
Patternan toàn: (1)Deploy reader code biết columnmới NULL-able→(2)Add column →(3)Backfill →(4)Update
writer. Đảo thứtự=productionoutage.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 20 / 35

---

### MedallionArchitecture cho AI

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
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 21 / 35

---

### Medallion: Schema Cụ Thể(LLM Observability)

Layer Bronze(raw) Silver(clean) Gold(analytics)
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
Quytắc: Bronzeappend-only (immutable audit), Silver upsert(MERGE), Gold rebuild-from-Silver (idempotent).
Schemarõ ràng mỗi layer=datacontract giữa teams.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 22 / 35

---

### Lakehouse+ AI: Production Patterns

■ Raw →processed →model →deploy
versionchain
■ RAG:doc chunks + embeddings lưuGold
■ Embeddinggắn doc version=fullytraceable
■ PinDelta version trong MLflow runcho
reproducibility
■ S3Intelligent-Tieringcho cold Bronze data
■ Glaciersau 90 ngày→ −60%storage cost
■ Unity/Polaris: fine-grained access +audit
■ Inferencereq/resp →Bronze(raw JSON,
30d)
■ Dedup+ parse tokens/latency→Silver
■ Aggregate(date, model) metrics→Gold
■ LLMgenerate →Bronze(output + prompt)
■ Qualityfilter + MinHash dedup→Silver
■ Curatedset + license tags→Gold
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 23 / 35

---

### CDCPattern: Postgres →Lakehouse

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
Vietnamcontext: chuẩncho fintech VN (MoMo, VNPay,Cake) — Postgres OLTP→Iceberg/Deltaanalytics.
End-to-endfreshness 1–5 phút, không impactOLTP.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 24 / 35

---

### CaseStudies: Lakehouse ởQuy Mô Production

Côngty Format & Scale Sốliệu công khai
Uber Hudi· 350 PB 6T rows/day · 19,500 datasets· freshness 24h
→1h
Netflix Iceberg+ Lance Atlasquery planning 9.6 min→42sec · Media
DataLake multimodal
Apple Iceberg “Foundationcho lakehouse on all divisions”(MB
→PB)
LinkedIn Iceberg MigrateHive →Icebergvì hidden partitioning +
queryplanning
Shopify Iceberg+ Trino Openlakehouse, multi-engine BI + ML
■ Append-mostly(logs, events) →
Delta/Iceberg
■ Mutation-heavy(orders, sessions) →Hudi
■ Multimodal(video, embeddings) →Lance+
Iceberg
MoMo,Zalo,ShopeeVN →TB–PB.Patternchuẩn:
Postgres → Debezium → Kafka → Iceberg/MinIO.
Decree13 →on-premMinIO khả thi.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 25 / 35

---

### FormatWar2024–2026: Đã Kết Thúc

Delta Lake
+UniForm
Apache
Iceberg v3
Apache
Hudi
UniForm XTable
Key events:Databricks acquires Tabular $1B+ (2024) · Snowflake→ Iceberg native + Polaris catalog
· Iceberg v3 GA on Databricks (Apr 2026): deletion vectors + row lineage + VARIANT · Result:30%
giảm DE workload.
■ AWSGlue (∼39%share) — default AWS
■ UnityCatalog — Databricks OSS 2024
■ ApachePolaris — top-level 2025
■ ProjectNessie — git-like branching
■ Lakekeeper— Rust, K8s-native
RESTCatalog spec =linguafranca 2026.
nessie tag create v1-prod
nessie branch create exp-2026
# ...train + evaluate on branch...
nessie merge → main
“ModelXdùngdatanào?” → nessie tag list :
trảlời 1 command, thay vìConfluence rotting.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 26 / 35

---

### Lakehousecho AI/LLM Workloads

RedPajama-V2: 30Ttokens · MinHashLSH dedup
Dolma(Ai2): 3Ttokens · two-stage Bloom filter
Pipeline: 64CPU cores, ∼1.4TB peak RAM
Lakehouse: Bronze(raw) →Silver(dedup) →Gold
(train-ready). Timetravelrevert dedup mistakes.
Embedding version= doc_v × model_v → pin via
Iceberg/Deltaversion + MLflowrun_id.
Vector DB (Qdrant/Milvus) = derived index, re-
buildable,không phải system of record.
■ Randomaccess ∼2000×fasterthanParquet
■ NativeHNSW vector index; first-class blobs
■ Built-inversioning
Netflix Media Data Lake:Parquet → Lance cho
videoframes.
■ Iceberg/Delta →tabularfeatures + lineage
■ Lance →embeddings+ multimodal blobs
■ VectorDB →onlineANN (sub-100ms)
Bổtrợ, không thay thế nhau.
AIThực Chiến VN:fine-tunecorpus (Wiki-VI + ZNews)→applyRedPajama-style MinHash trước. Repo:
togethercomputer/RedPajama-Data.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 27 / 35

---

### CatalogLayer: REST Standard2026

Catalog Origin Killerfeature Khinào dùng
AWSGlue AWS,2017 DefaultAWS, ∼39%share Đãở AWS
UnityCatalog Databricks,OSS
2024
Fine-grainedgovernance Databricks-native
ApachePolaris Snowflake,top-level
2025
Vendor-neutralREST Multi-cloud
ProjectNessie Dremio,2020 Git-likebranching/tagging MLversioning
Lakekeeper OSS2024 (Rust) Lightweight,K8s-native Self-hosted
Standard HTTP API cho Iceberg metadata (cre-
ateTable,loadTable,commit, listNamespaces).
Lợi: engine (Spark, Trino, Flink, Snowflake,
DuckDB)plug-and-playvớibấtkỳcatalogimplement
spec. 2026 default.
Catalog-levelcommit =atomicupdatenhiềutables.
Use case:Bronze + Silver + Gold update phải all-
or-nothing.
Nessienative(gitcommit);Polarisđangimplement.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 28 / 35

---

### DataQuality & Contracts: 3-ToolStack

Where: Bronzeingestion
What: validateraw data
Strength: 50+expectations
expect_column_values_to_be_in_set(
column="status",
value_set=["ok",
"rate_limited","error"])
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
Where: Prodmonitoring
What: continuous,anomaly
Strength: SodaCLDSL
checks for gold.metrics:
- row_count >= 1000
- freshness < 1h
- anomaly_score
< 0.7 for cost_usd
DataContract: schema+ constraints + freshness SLA+ ownership; run trong CI (pre-merge)vàruntime(per-batch). Bể
contract →blockpipeline.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 29 / 35

---

### DataLineage: OpenLineage +Marquez

Bronze.events Sparkjob
clean+dedup Silver.events dbtmodel
aggregate Gold.metrics
Dashboard
MLfeature
OpenLineage: OSS standard — Spark/Airflow/dbt/Flink emit lineage events tự động.Mar-
quez: reference server (graph DB + UI). Trả lời: “Drop column X→ ai bị ảnh hưởng?” ·
“Gold metric Y sai→ truy ngược về Bronze nào?”
Pattern: bậtOpenLineage từngày1 . Spark: spark.openlineage.transport.type=http +MarquezURL.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 30 / 35

---

### Security& Governance cho Lakehouse

■ RBAC:role-based(admin/analyst/eng)
■ ABAC:attribute-based(region,
classification)— Unity/Polaris
■ Row-levelsecurity: dynamicfilter
■ Columnmasking: hash/redactPII
■ TokenizePII at Bronze landing
■ Encryptat field level (Iceberg v3native)
■ Right-to-forget: DELETE + VACUUMsau
30dgrace
■ Auditlog mọi PII column access
Decree13/2023/NĐ-CP (eff. 2023-07-01):
■ Personaldata: basic vssensitive
■ Dataresidency: sensitive ởVN
■ Cross-border: consent + DPI
■ Right-to-forget: 72h SLA
Impact: sensitive data → on-prem MinIO + Ice-
berg.
■ Everyread/write →Bronzeaudit table
■ Iceberg: system.snapshots table
■ Retention365+ ngày cho regulated
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 31 / 35

---

### Cost& FinOps cho Lakehouse

Component(100
TB/tháng)
Snowflake Iceberg+ Trino/ S3 Databricks
Storage $4,000 $2,300(S3) $2,300(S3)
Compute(BI) $15,000 $8,000(TrinoEC2) $11,000(DBU)
Compute(ETL) $5,000 $2,000(Spark EMR) $4,000(DBU)
Catalog/gov included $500(Polaris OSS) included(Unity)
Total $24,000 $12,800(–47%) $17,300(–28%)
■ Per-layerbudget: Bronze →Glaciersau 30d
■ Auto-OPTIMIZEnightly cron
■ Tagclusters: team, purpose,
expires_at
■ Spotcho ETL, on-demand cho BI
■ Top-10query review hàng tháng
■ Cloudera: TPC-DS 24s→1.8s(13 ×),
storage −36%
■ ClickHousevs Snowflake: ∼4×lowerTCO
■ NetflixIceberg: planning9.6min →42s(14 ×)
■ NoOPTIMIZE: 10×moreexpensivethan
DW
Quytắc: savingschỉmaterializenếu actively optimize. Forget OPTIMIZE→small-filetax giết economics.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 32 / 35

---

### Top5 Lakehouse Anti-Patterns

# Anti-pattern Hậuquả & Fix
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
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 33 / 35

---

### Demo: Delta Lake TimeTravel& MERGE

■ Small-fileproblem —ingest 1M rows (200 batches)→OPTIMIZE+ Z-ORDER →
benchmarktrước/sau (target ≥3×)
■ Timetravel rollback—inject bad data→ restoreToVersion() trong30s vs ∼2h
manual
■ MERGEupsert —100K rows (∼2×fasterworkshop; 10–50×productionscale)
■ Audittrail — DESCRIBE HISTORY listmọi operation
Labrepo: VinUni-AI20k/Day18-AIInfrastructure-Lakehouse-Lab
Notebooks01–04 + Docker stack hoặclightweight DuckDB + delta-rs path.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 34 / 35

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
Lakehouse = ACID + object storage + open formats. Foundation chung cho 3 era: Tradi-
tional,ML, LLM.
2 Formatwarkếtthúc . Iceberg+DeltaUniForm=defactostandard. On-diskParquetidentical,
chọntheo tooling fit.
Time travel + branching(Nessie) = “git checkout” cho dataset.OPTIMIZE + Z-ORDER +
DeletionVectors bắtbuộc cho production.
4 LLMeracầnthêmtầng : VectorDB(RAG),Lance(multimodal),embeddingversioning,train-
ingdata provenance.
5 Productionops trifecta: Catalog + DataContracts + Lineage. Bậttừ ngày 1.
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 34 / 35

---

### Tiếptheo & Bài tập

Ngày 19: Vector Store & Feature
Store
“SQLtrảexactmatch. AIcầntươngtự
—semantic search thay đổi mọi thứ.”
■ Hoànthành Lab 18 (4
notebooks): VinUni-AI20k/
Day18-AIInfrastructure-Lakehouse-Lab
■ Đọctrước: case studies(Netflix,
Uber,Apple Iceberg) + Lance
multimodaldocs
■ Càisẵn Docker + Qdrant image
choNgày 19 (VectorStore +
ANN)
Giảngviên (VinUni) AICB· Ngày 18 Tuần4 35 / 35

---

### Hỏi& Đáp

Câu hỏi về Lakehouse, Delta/Iceberg, Medallion,
Catalog, Data Contracts, hay AI/LLM workloads?

---

### Cảmơn!

AICB-P2T2 · Ngày 18
Data Lakehouse Architecture
lms.vinuni.edu.vn · Lab repo + slides trên LMS