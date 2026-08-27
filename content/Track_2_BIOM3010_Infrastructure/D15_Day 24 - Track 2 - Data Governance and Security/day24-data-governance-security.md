# day24 data governance security

**File gốc:** `Track_2_BIOM3010_Infrastructure\D15_Day 24 - Track 2 - Data Governance and Security\day24-data-governance-security.md`

---

### Data Governance & Security

AICB-P2T2 · Ngày 24 · Chương 5: Vận Hành
Giảng viên
VinUniversity · Phase 2 · Track2· Tuần5

---

### “Tháng 7/2026, IBM công bố: chi phí trung bình

một vụ data breach đạt $4.99 triệu — mức
kỷ lục, tăng 12% so với năm trước. Nhưng
con số đáng chú ý hơn nằm ở dòng kế tiếp: 1
trong 4 vụ tấn công có chủ đích giờ đã dùng
AI, tăng 56%, và mỗi vụ như vậy tốn thêm $1
triệu. Nguyên nhân hàng đầu không phải thuật
toán bí hiểm — mà là API/plugin bị chiếm
quyền (27%) và cấu hình cloud sai (27%) .
Nói cách khác: hệ thống AI của bạn thất thủ
ở phần hạ tầng, không phải phần model.”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### Nội Dung Bài Học

1. Vìsao governance quyết định sốphận AI
2. Framework: catalog, phân loại,lineage
3. TừRBAC đến ABAC
4. Row-levelsecurity & column masking
5. Danhtính cho máy: workload identity
6. Danhtính cho agent & tokenvaulting
7. Encryption: at rest, intransit
8. Confidentialcomputing: mã hoákhi đang tính
9. Secrets& thời gian thu hồi
10. PIIdetection & thực tế tiếngViệt
11. Thangẩn danh đến differentialprivacy
12. RAGcó phân quyền: ACL trong vector store
13. Ròrỉ qua agent: egress control
14. Chuỗicung ứng model
15. Compliance →technicalcontrol
16. Vậnhành, Demo & Tổng kết
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 1 / 49

---

### Mục Tiêu

Saubuổi học này,bạnsẽ:
1. Thiếtkế access control gắn vàotag(ABAC)thay vì gắn vào từng bảng
2. Cấpdanh tính & phạm vi quyềnchoagentvàtool credentials
3. Xâypipeline PII detection tiếng Việtvàbáocáo recall trung thực theo từngentity
4. Bảovệ retrieval: ACLđi theo chunk vào vector store,lọctrướckhitìm kiếm
5. Ánhxạ Luật BVDLCN 2025 vàEU AI Act thành technical controlcụ thể
Trục xuyên suốt
Governance cho AI = kiểm soátđường đi của dữ liệu: ai đọc được, ở dạng gì, đi
đâuđược, và chứng minh lại được.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 2 / 49

---

### Deliverable Cuối Ngày

Artifact cần nộp
Agentđã bị contain+bằngchứng chứng minh được nó đãbị contain
– Tấn công: attack-before.log —PII thật sự ra tớisink. Phải phá đượctrước khi được vá
– 5 biến thể injection: ẩnchữ · giả mạo thẩmquyền · chia payload 2 file· tiếng Việtkhông
dấu
– 4 control tự viết: PIIgate · PEP tại toolcall · trifecta split+egressallowlist · audit ledger
– Chứng minh: attack-after.log sạch + ledger.jsonl khôngdòng nào thiếureason
– Hồ sơ: compliance-mapping.md + dpia-lite.md
Lưu ý: Ba điều kiện trượt, bất kể tổng điểm:(1)ledger có dòng thiếureason; (2)attack sau
contain vẫn lọt PII;(3)agent vẫnđọchồ sơ khách do attacker chỉ định.Chặn chặng gửi mà
vẫn đọc = mitigation, chưa phải containment.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 3 / 49

---

### 01

Vì Sao Governance Quyết Định
Số Phận Hệ Thống AI
Hệ thống AI thất thủ ở phần hạ tầng, không phải phần model. Số
liệu 2026 nói rõ điều đó.

---

### Chi Phí Thực Tế — IBM Cost of a Data Breach 2026

$4.99M
Chi phí TB một
vụ breach —
kỷ lục, +12%
25%
Vụ tấn công có
chủ đích dùng
AI (+56%)
$6M
Chi phí một
vụ AI-enabled
breach
37%
Tổ chức bị
breach có
mã hoá cả
rest và transit
Ponemon/IBM,602 tổ chức, sự cốtừ 03/2025 đến 02/2026. “AI-enabled” =kẻ tấn công dùngAI — không phải “AIlàm lộ
dữliệu”.
Đọc kỹ con số 37%: encryptionlà control được dạy nhiềunhất và triển khai ít nhất. Chỉ 34% có khảnăngnhìn thấy tài
sảnmã hoá của mình.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 4 / 49

---

### Hệ Thống AI Hỏng Ở Đâu?

Nguyên nhân vụ breach liên quan AI Tỷ lệ Đây là bài của ai?
API/ ứng dụng / pluginbị chiếm quyền 27% Accesscontrol, agent scope (hôm nay)
Cấuhình cloud sai 27% IAM,encryption default (hôm nay)
Cácnguyên nhân còn lại phầndư Hạtầng, con người, quy trình
– Hơn 20%tổchức đã gặp sự cốtrên chínhmodel hoặc ứng dụng AI củamình
– Khôngcó dòng nào ghi “thuậttoán bị phá” — toàn bộlàplumbing: quyền, cấu hình,credential
Hệ quả cho cả ngày hôm nay
Nếu bạn chỉ có 1 ngày để làm hệ thống AI an toàn hơn, đừng bắt đầu từ model. Bắt đầu từai được đọc gì và
credential nằm ở đâu.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 5 / 49

---

### AI Làm Tan Biến Ranh Giới Của Bảng Dữ Liệu

Governancecổ điển dừng lại ở ranhgiới bảng: mộtvai trò đượcSELECThoặckhông. Hệ
thốngAI phá vỡ ranh giới đótheoba đường:
Training hấp thụ
Dữ liệu tan vào trọng số.
Xoá không còn làDELETE —
nó là bài toán nghiên cứu.
Retrieval phục vụ lại
Vector index kế thừa — hoặc
đánh mất — ACL của nguồn.
Index sai quyền = rò rỉ im lặng.
Agent hành động
Agent cầm credential.
Một câu prompt trở thành
một đặc quyền.
Cả ba đều nằm NGOÀI phạm vi của một câu GRANT — đó là lý do governance cho AI cần kiểm soát ĐƯỜNG ĐI, không chỉ điểm truy cập
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 6 / 49

---

### Con Số Nói Về Chính Căn Phòng Này

Secrets rò rỉ trong kỷ nguyên AI-assisted
– ∼28 triệu credentiallộ trên GitHub trong
2025
– Commitcó AI hỗ trợ ròrỉ secret ở mức
∼3,2%—khoảng 2×mứcnền của người
viếttay
– Tỷ lệ trúng khôngtăng vọt —sản lượng
tăng. Cùng một tỷlệ lỗi, nhiều code hơn gấp
đôimỗi tuần
Vì sao slide này nói về bạn
– Mọingười trong phòng này đềuđang commit
codecó AI hỗ trợ
– Nghĩalà: bạn chính là mẫu thống kê ,
khôngphải một nhóm trừu tượngnào đó
– Controltương ứng nằm ở phầnSecrets —
vàchỉ tiêu không phải “pháthiện” mà là
time_to_revoke
Nguồn: GitGuardian State ofSecrets 2026 (qua Snyk); tổng hợpcông cụ quét secret 2026.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 7 / 49

---

### 02

Framework: Catalog, Phân Loại,
Lineage, Glossary
Bốn trụ cột vẫn đúng. Điều đã đổi từ 2026: phân loại trở thành
TỰ ĐỘNG và MANG THEO CHÍNH SÁCH.

---

### Bốn Trụ Cột Của Data Governance

Data Catalog
DataHub/ OpenMetadata
UnityCatalog
Tìmđược & mô tả được
Classification
Public/ Internal /
Confidential/ Restricted
Sinhra chính sách
Lineage
Source →Transform
→Train →Predict
Bằngchứng & phạm vi xoá
Business Glossary
“Kháchhàng”, “Churn”,
“Giaodịch”
Thuậtngữ nhất quán
Thay đổi 2026: Classification không còn do người gắn tay — nó được PHÁT
HIỆN tự động, gắn thành governed tag, và chính sách BÁM VÀO TAG đó
Nguyên tắc: mộtnhãn phân loại phải dongười gắn tay là một nhãnsẽ sai trong vòng một quý.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 8 / 49

---

### Phân Loại Dữ Liệu & Vai Trò Của Lineage

4 cấp độ — ví dụ trong AI
Cấp Ví dụ
Public Benchmark,tài liệu
Internal Codefeature engineering
Confidential Trainingdataset
Restricted PII, hồ sơ y tế,CCCD
Phânloại quyết định chính sách: Restricted→mã
hoá +ABAC +auditlog +cấmexport.
Lineage — dùng cho đúng việc
– Ngày24 dùng lineage chohai việc: xác định
phạm vi phải xoá,và tạo bằng chứng cho
audit
– “Modeldự đoán sai — nóđã học từ dữ liệu
nào?” là câu hỏilineage trả lời
– Chitiết kỹ thuật (OpenLineage, eventmodel,
column-level)thuộc về Ngày 27
Lưu ý: Lineagekhôngphảicôngcụbảomật. Nókhông ngănròrỉ—nóchobạnbiết
ròrỉ đã lan tới đâusau khi đãxảy ra.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 9 / 49

---

### Bức Tranh Catalog 2026 — Chọn Gì Để Chạy?

Công cụ Vị thế Auto-classify PII? Ghi chú thực dụng
DataHub OSS dẫn đầu
(∼11k⋆)
Có—auto classification Datacontracttừ2025;cộngđồnglớn
nhất
OpenMetadata OSS( ∼8k⋆) Có Contract dạng schema máy đọc kèm
SLA
Unity Catalog Managed
(Databricks)
Có—kèmcảnhbáochủ
động
Bản OSS tồn tại nhưng tài liệu còn
mỏng
Apache Atlas Ổnđịnh, ngách Không — chỉ gắn tay+
lantruyền tag
Disản Hadoop; vẫn dùng được
Apache Polaris Đang ươm ( <1
năm)
Chưa Còn rất sớm — theo dõi, chưa cược
vào
Tiêu chí chọn duy nhất đáng quan tâm hôm nay: côngcụ có tự phát hiện PII và gắn tag không? Vì toàn bộphần
accesscontrol tiếp theo bám vàotag đó.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 10 / 49

---

### 03

Từ RBAC Đến ABAC: Bài Toán
Bùng Nổ Vai Trò
Least privilege đúng về nguyên tắc nhưng vỡ về quy mô. ABAC
lật ngược bài toán: chính sách bám vào thuộc tính, không bám
vào từng bảng.

---

### Least Privilege Cho Đội AI — Điểm Xuất Phát

Vai trò Đọc Ghi Không được phép
Admin Toànbộ Toànbộ —(nhưng phải có audit log)
ML Engineer Trainingdata Modelartifact Xoádữ liệu production
Data Analyst Chỉsố tổng hợp Báocáo PIIthô
Intern Chỉsandbox Chỉsandbox Mọithứ thuộc production
Agent Theo phiên Có cổng duyệt Giữcredential dài hạn
Sai lầm phổ biến: cấpadmin cho toàn bộ MLengineer “cho nhanh” — một lầnxoá nhầm là hết.
Hàngcuối là hàng mới của2026: agent không phảimột vai trò con người. Nó cần danh tính riêng— xem phần Danh tính
choagent.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 11/ 49

---

### Vì Sao Chỉ RBAC Thì Không Đủ Ở Quy Mô

Phép nhân khiến RBAC vỡ
– RBACcần một grant cho mỗi cặp (vai trò
× đối tượng)
– Thêmmột chiều nhạy cảm (PII/ vùng / mục
đích)là nhânmatrận lên
– Bảngmới →cần Ngrantmới. Vaitrò mới
→cần Mgrantmới
– Kếtquả quen thuộc:
analyst_vn_pii_readonly_v2 — bùng nổ
vai trò
Lưu ý: Triệu chứng nhận biết: không ai dám
xoámộtvaitrònàocả,vìkhôngaibiếtnócònđược
dùngở đâu.
ABAC lật ngược bài toán
– Chínhsách bám vàothuộc tính / tag,không
bámvào tên bảng
– “Cộtnào mang tagpiithìche, trừ khi người
dùngthuộc nhóm privacy-cleared”
– Bảngmới mang tagpii → được quản trị
ngay khi vừa tạo,không cần grant nào
– Chínhsách gắn ởcatalog / schema và lan
xuốngbảng,cột
Câu chốt
RBAC trả lời“ai là bạn”. ABAC trả lời“dữ liệu này là
loại gì”. Hệ thống AI sinh bảng mới liên tục — nên
câuhỏi thứ hai mới làcâu mở rộng được.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 12 / 49

---

### 04

Row-Level Security & Column
Masking
Chính sách gắn vào tag, không gắn vào bảng. Từ 2026 đây là
tính năng GA chứ không còn là kiến trúc tự dựng.

---

### Hai Nguyên Thuỷ Cần Nắm

Row Filter
Quyết định người dùngthấy dòng nào.
Hàm trả về điều kiện lọc,
gắn vào bảng, chạy trong query plan.
Column Mask
Quyết địnhgiá trị hiện ra thế nào .
Che tại chỗ:0123**…
Cột vẫn tồn tại, giá trị thì không.
Điểm mấu chốt — cả hai đều bám vào GOVERNED TAG, không bám vào tên bảng.
Data classification tự phát hiện PII→ gắn tagpii → policy đã viết sẵn tự áp dụng.
Bạn viết chính sách MỘT LẦN, nó quản trị mọi bảng sẽ được tạo ra trong tương lai.
ABACrow filter,column mask,governed tag và data classification trongUnity Catalog đạt trạng tháiGAtrong2026.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 13 / 49

---

### Row Filter & Column Mask — Trông Như Thế Nào

-- 1. Column mask bound to a TAG,
-- not to a specific table
CREATE FUNCTION mask_pii(v STRING)
RETURN CASE
WHEN is_account_group_member(
'privacy_cleared')
THEN v
ELSE '***REDACTED***'
END;
-- 2. Attach at CATALOG level:
-- cascades to every schema,
-- table and column beneath it
ALTER CATALOG prod SET
COLUMN MASK mask_pii
ON COLUMNS TAGGED ( 'pii');
Vì sao phải gắn ở cấp catalog
– Gắnở bảng=quay lại bài toán bùng
nổ: mỗi bảng mộtlần gắn
– Gắnở catalog/schema=chính sách
lan xuống,bảng tương lai đã đượcbảo
vệsẵn
Bẫy thường gặp
– Maskkhông thay đượcquyền cột:
ngườidùng vẫn biết cột tồntại
– Rowfilter chạy trong query plan—hiệu
nănglàbài toán thật, hãy đo
– Cẩnthận rò rỉ quaCOUNT(*): che giá trị
nhưngvẫn lộ số lượng
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 14 / 49

---

### Cùng Một Kỹ Thuật, Bốn Nền Tảng

Nền tảng Row-level Column-level Gắn chính sách vào
Unity Catalog Rowfilter policy Columnmask policy Governed tag (ABAC, GA
2026)
Snowflake Rowaccess policy Maskingpolicy Taghoặc gán trực tiếp
BigQuery Row-levelaccess Policytag trên cột Taxonomycủapolicy tag
Apache Ranger Rowfilter Columnmasking Rangerpolicy (Hive/Trino)
Cách đọc bảng này
Đừngnhớtênsảnphẩm—hãynhớ kỹ thuật: mọienginenghiêmtúcđềucó(1)lọcdòng,(2)checột,(3)mộtcách
đểchính sách bám vào phân loại thayvì bám vào tên bảng. Khi đánh giá mộtnền tảng mới, hỏi đúng bacâu đó.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 15 / 49

---

### Policy-as-Code Với OPA — Và Giới Hạn Thật Của Nó

OPA làm tốt việc gì
– Chínhsách dạng code (Rego) trongCI/CD
—review được, test được, versionđược
– Thựcthi ở ranh giới dịch vụ: API gateway,
Kubernetesadmission controller
– Phủđược bề mặtkhông phải SQL —nơi
enginekhông có row filter
Lưu ý: OPA quản trị REQUEST , không quản
trị ROW. Rego quyết định “principal này có được
gọi endpoint này không”. Nókhông tự viết lại câu
queryđể che một cột.
Sinh viên thường cố làm row-level security bằng
Regorồi thất bại — đólà dùng sai tầng.
Kiến trúc đúng là kết hợp
Row/column policy ngay trong engine dữ liệu +
OPA ở ranh giới dịch vụ . Hai tầng, hai nhiệm vụ
khácnhau.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 16 / 49

---

### 05

Danh Tính Cho Máy: Từ Static
Key Đến Workload Identity
Chính sách xoay vòng khoá tốt nhất là không có khoá nào để
xoay vòng.

---

### Cái Thang Ba Bậc Của Machine Credential

Bậc 1 — Khoá tĩnh dài hạn. AWS_SECRET_ACCESS_KEY trong .env.
Đây chính là thứ bị rò rỉ trong 28 triệu credential trên GitHub. Bí mật tồn tại⇒ bí mật rò rỉ được.
Bậc 2 — Khoá tĩnh có xoay vòng. Tự động đổi hằng tuần.
Tốt hơn: thu hẹp cửa sổ tấn công. Nhưng bí mật VẪN tồn tại giữa hai lần xoay.
Bậc 3 — Workload identity federation (OIDC). Không lưu bí mật nào cả.
Nền tảng phát hành token ngắn hạn từ danh tính workload xác minh được. SPIFFE/SPIRE là chuẩn trung lập; mọi
cloud có bản tương đương.
Trưởng
thành
Lưu ý: Deckcũghiđồngthời“xoayvòngcredentialhằngtuần” và“khôngdùngkhoá
dài hạn — dùng OIDC”. Đó là hai bậc khác nhau, và bậc 3 làm bậc 2 trở nên không
cầnthiết. Đừng dạycả hai như thể chúng nganghàng.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 17 / 49

---

### 06

Danh Tính Cho Agent & Token
Vaulting
Agent giờ cầm credential thật. Một MCP server thường giữ khoá
của nhiều hệ thống cùng lúc — và xin nhiều quyền hơn nó cần.

---

### Vì Sao Agent Phá Vỡ Mô Hình Danh Tính Cũ

Rủi ro cốt lõi
– MộtMCP server thường giữ credentialcho
nhiều hệ thống cùng lúc
– Vàthường xin scope rộng hơn nhu cầu
thật
– Hệquả: một serverbị chiếm hoặc một token
ròrỉ trở thànhđường vào mọi hệ thống nó
chạmtới
Lưu ý: Lỗi auth phổ biến nhất: agent chỉ cần
đọcmộtlịchnhưngxin read:allhoặcquyềnadmin.
Leastprivilege vỡ ngay tại nềnmóng.
Mô hình uỷ quyền nên dùng
– OAuth 2.1 + PKCE
– Consent theo từng client
– Khớp redirect-URInghiêmngặt
– Audience-bound token: token phát cho
serverA khôngdùnglại được với server B
– Scope hẹp và cụ thể,ưu tiên tokenngắn
hạnhơnbí mật dài hạn
Nguyên tắc quản trị: mỗiagent phải có một danhtính bạnliệt kê được và tắt được trong một thao tác . Agent không
liệtkê được là agent khôngthu hồi được.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 18 / 49

---

### Token Vaulting — Agent Không Bao Giờ Cầm Khoá Mạnh

Agent
token mờ, quyền thấp
Gateway
token exchange
Token Vault
theo user × provider
Hệ thống đích
Gmail, DB, CRM…
tokenmờ
đổilấy
tokenthật, scope hẹp
Access token và refresh token được cất trong vault, mã hoá,
phân vùng nghiêm ngặt theo từng người dùng và từng provider.
Agent bị chiếm quyền chỉ cầm được một token mờ vô dụng — không phải chùm chìa khoá.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 19 / 49

---

### 07

Encryption: At Rest, In Transit
— Và In Use
Chỉ 37% tổ chức bị breach có mã hoá cả hai đầu. Đây là control
được dạy nhiều nhất và triển khai ít nhất.

---

### Ba Trạng Thái Của Dữ Liệu

IN USE — Confidential computing / GPU TEE (phần tiếp theo)
IN TRANSIT — TLS 1.3 bắt buộc, certificate pinning cho dịch vụ nội bộ
AT REST — AES-256 cho object store, block store, database (khoá do KMS quản lý)
COLUMN-LEVEL — mã hoá riêng từng trường PII (họ tên, email, CCCD)
ENVELOPE — DEK được mã hoá bởi KEK; xoay DEK hằng tháng, KEK hằng năm
Phòng thủ
nhiều lớp
Quy tắc bất di bất dịch: khôngbao giờ lưu khoá dạngplaintext trong code hay biến môitrường — dùng KMS / Vault.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 20 / 49

---

### Envelope Encryption — Vòng Đời Một Data Key

import boto3
kms = boto3.client( "kms")
# KMS returns the SAME key twice:
# once usable, once wrapped by KEK.
resp = kms.generate_data_key(
KeyId= "alias/ai-training-data",
KeySpec= "AES_256",
)
dek = resp[ "Plaintext"]
wrapped = resp[ "CiphertextBlob"]
ciphertext = encrypt_aes(data, dek)
# Persist the WRAPPED key beside the
# data -- never the plaintext one.
store(ciphertext, wrapped)
del dek
Vì sao phải qua hai lớp khoá
– XoayKEK khôngcầnmã hoá lại toàn
bộdữ liệu — chỉ bọclại các DEK
– KMSkhông bao giờ nhìn thấydữ liệu
củabạn; nó chỉ bọc vàmở bọc khoá
– Lộmột DEK chỉ ảnh hưởngđúng phần
dữliệu nó mã hoá
Checklist triển khai
– Objectstore: bật mãhoá mặc định ở
cấpbucket
– Blockstore: volume mãhoá theo mặc
định
– Database: TDE+mãhoá cột cho PII
– Ghi log mọi lần dùng khoá —đây là
bằngchứng audit
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 21 / 49

---

### 08

Confidential Computing: Mã Hoá
Khi Đang Tính
Câu trả lời kỹ thuật duy nhất cho “chúng tôi không thể dùng GPU
cloud vì phải giao dữ liệu ở dạng plaintext”.

---

### GPU TEE — Mở Rộng Vùng Tin Cậy Tới Bộ Tăng Tốc

Cơ chế
– H100 (Hopper) làGPU đầu tiên có
confidentialcomputing — ra mắt 07/2023,
GA2024
– Mãhoá VRAM +mãhoá bus PCIe +
attestationbằngphần cứng
– Trọngsố và activation trung gianđược giữ
mãhoá trong lúc đang tính
– Blackwell B200 bổsung mã hoáNVLink
choworkload nhiều GPU
Lưu ý: Giới hạn thật trên H100 — đây là phần
táchbài giảng khỏi quảng cáo:
– Cóchỗ bộ nhớ được bảovệ bằngkiểm soát
truy cập,không phải mã hoá lúcchạy
– MetadataRPC và cấu trúc đồngbộ vẫn
plaintext
– Hopper khônghỗtrợ CC cho training quy
môlớn
Chi phí hiệu năng
Overhead dưới 5% với phần lớn truy vấn LLM, tiệm cận 0 khi model lớn / chuỗi dài
—lúcđóworkloadbịchặnbởitínhtoán. Số liệu nhà cung cấp công bố — hãy tự đo.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 22 / 49

---

### Khi Nào Confidential Computing Đáng Tiền?

Tình huống Có cần? Lý do
Inference trên dữ liệu nội bộ, hạ tầng tự
quản
Không Bạnđã kiểm soát vật lýlẫn phần mềm
DùngGPUcloudbênthứbachodữliệu
Restricted
Có Biếnràocảnpháplýthànhmộtphépkiểmtra
attestation
Xử lý dữ liệu y tế / tài chính bên ngoài
biêngiới tin cậy
Có Nhàcungcấphạtầngnằmngoàivùngtincậy
Trainingquy mô lớn trên Hopper Chưađược Hopper không hỗ trợ CC cho training lớn —
chờBlackwell
Giá trị thật cho đội governance
Attestationchobạnmột bằng chứng kiểm tra được bằng máy rằngworkloadchạytrongmôitrườngđãđượcxác
thực. Đó là thứđưa được vào compliance evidence —khác hẳn một dòng cam kếttrong hợp đồng.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 23 / 49

---

### 09

Secrets: Quản Lý, Quét, Và Thời
Gian Thu Hồi
Chỉ tiêu đúng không phải “phát hiện được bao nhiêu” mà là “bao
lâu thì khoá bị vô hiệu”.

---

### Bộ Công Cụ Quét Secret 2026

Công cụ Vị trí trong pipeline Điểm mạnh riêng Dùng khi
gitleaks pre-commit +CI Nhanh, chặn được trước
khipush
Tuyếnphòng thủ số một
TruffleHog Quétlịch sử repo Xác minh khoá còn sống
haykhông
Ràsoát toàn bộ lịch sử
Push protection Tầngnền tảng Chặn ở phía server,
khôngbỏ qua được
Lướian toàn cuối
GitGuardian Nềntảng quản lý Dashboard quản trị, báo
cáotuân thủ
Môitrường bị quản chế
Lưu ý: git-secrets(AWS)đãcũvàgầnnhưkhông
còn được bảo trì. Deck cũ khuyến nghị nó —hãy
thay bằng gitleaks ởcả bài giảng lẫn lab.
Nghịch lý chuỗi cung ứng
Năm2025,kẻtấncông đóng gói chính TruffleHog
làm payload trong một package NPM bị chiếm —
dùng năng lực quét của công cụ bảo mật để tìm và
tuồnsecret ra ngoài.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 24 / 49

---

### Chỉ Tiêu Duy Nhất Đáng Đưa Lên Dashboard

Secret lọt
vào commit Scanner phát hiện Xác minh khoá
còn sống
Thu hồi &
xoay khoá
time_to_revoke — đo bằng PHÚT , không phải NGÀY
Khác biệt giữa “khoá bị lộ, không thiệt hại gì ” và “khoá bị lộ, kẻ tấn công có ba tiếng để dùng ”
nằm trọn trong khoảng thời gian này.Phát hiện mà không tự động thu hồi chỉ là diễn kịch.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 25 / 49

---

### 10

PII Detection & Thực Tế Của
Tiếng Việt
Presidio không có sẵn tiếng Việt. Đoạn code chạy được và đoạn
code trông có vẻ chạy được khác nhau ở đúng một dòng cấu
hình.

---

### Kiến Trúc Presidio — Hai Nửa Rất Khác Nhau

Recognizer theo luật
regex / checksum
Bắt thực thểcó cấu trúc:
CCCD, SĐT, email, số tài khoản
Không cần model. Không phụ thuộc ngôn ngữ.
NLP engine (NER)
spaCy hoặc Stanza
Bắt thực thểtheo ngữ cảnh:
PERSON, LOCATION, ORG
Cần model đúng ngôn ngữ. Đây là chỗ tiếng Việt vỡ.
Presidio mặc định nạp model tiếng ANH. Gọi
analyze(language="vi") trên engine mặc định sẽ LỖI —
không phải trả về kết quả kém, mà là không chạy.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 26 / 49

---

### Cấu Hình Presidio Cho Tiếng Việt — Đúng Cách

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import (
NlpEngineProvider)
# A Vietnamese NLP engine must be
# declared EXPLICITLY. Without this,
# language=" vi" fails -- the default
# engine is English-only.
engine = NlpEngineProvider(
nlp_configuration={
"nlp_engine_name": "stanza",
"models": [{ "lang_code": "vi",
"model_name": "vi"}],
}).create_engine()
analyzer = AnalyzerEngine(
nlp_engine=engine,
supported_languages=[ "vi"])
Ba điểm khác biệt
– Phảikhaibáo NLP engine chovi—
Stanzacó tiếng Việt,spaCy thìkhông
sẵn
– CCCD/ SĐT / email đăngký bằng
PatternRecognizer — regex thuần,
khôngcần model
– PERSON/ địa chỉ dựa vàoNER —
thựctế dùng undertheseahoặc
PhoBERT
Lưu ý: Trong Lab 24, đường được
chấm là regex-first — đủ vượt ngưỡng re-
call trong 2h. Slide này cho bạn biết đường
Presidio-tiếng-Việt tồn tạivàcấuhìnhrasao;
nólà stretch goal,khôngphảiđườngchính.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 27 / 49

---

### Báo Cáo Recall Trung Thực Theo Từng Entity

Nhóm thực thể Phương pháp Recall thực tế Vì sao
CCCD,SĐT,email, số TK regex/ checksum Rất cao Cócấu trúc cố định
PERSONtrong văn bản tự do NERtiếng Việt Thấp hơn rõ rệt Dấu, thứ tự họ tên, tên
trùngtừ thường
Địachỉ tiếng Việt NER +luật Thấp hơn nữa Định dạng không chuẩn
hoá
Lưu ý: Không bao giờ báo cáo một con số accu-
racy gộp. Một detector “95%” chạy trên 1 triệu bản
ghivẫn để lọt50.000bảnghi.
Hai quy tắc sống sót
– Recalllà một control bảo mật,không phải
mộtchỉ số đẹp
– Cântrọng số theomức thiệt hại: bỏ sót một
CCCDtệ hơn bỏ sót mườitên thành phố
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 28 / 49

---

### 11

Thang Ẩn Danh: Từ Masking
Đến Differential Privacy
Băm không phải ẩn danh. k-anonymity không đủ một mình. DP
là câu trả lời hình thức duy nhất.

---

### Thang Ẩn Danh — Sáu Bậc

Kỹ thuật Cơ chế Đảo ngược? Dùng cho
Masking Nguyễn*** (chetại chỗ) Không Hiểnthị, log
Pseudonymization Thaybằng bí danh nhất quán Có(quabảng tra) Analyticsnội bộ, A/B test
Hashing Hàmbăm một chiều Trên thực tế: CÓ Xem cảnh báo bên dưới
Generalization Tuổi32 →nhóm30–39 Không Thốngkê, báo cáo
k/l/t k-anonymity → l-diversity → t-
closeness
Không Chiasẻ dataset
DP Nhiễu hiệu chỉnh, có cận chứng
minh được
Không Training,thống kê công bố
Lưu ý: Băm không phải ẩn danh. CCCD chỉ có1012 giá trị và có cấu trúc — vét cạn một bảng băm CCCD là
chuyệncủa vài phút trên mộtGPU. Đây là lỗi phổ biếnnhất của sinh viên trong bàilab này.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 29 / 49

---

### k-anonymity Không Đủ — Vì Sao Cần l Và t

k-anonymity
Mỗi bản ghi giống ít nhấtk −
1 bản ghi khác trên cácquasi-
identifier.
Vỡ khi: cả kngườitrongnhóm
có cùng một giátrịnhạycảm—
kẻtấncôngkhôngcầnbiếtbạn
là ai. Đây là tấn công đồng
nhất.
l-diversity
Yêu cầu mỗi nhóm có ít nhấtl
giátrị nhạy cảmkhác nhau.
Vỡ khi: phân bố trong nhóm
lệch hẳn so với tổng thể — “đa
dạng” nhưng 90% vẫn rơi vào
mộtgiá trị.
t-closeness
Yêu cầu phân bố giá trị nhạy
cảm trong nhómgần với phân
bố toàn cục (khoảng cách≤ t).
Giá phải trả: mấtnhiềutiệních
dữ liệu hơn hẳn. Càng chặt
càngít dùng được.
Cách đọc cái thang này
Mỗi bậc vá đúng lỗ hổng của bậc trước, và mỗi bậc lấy đi thêm một phần tiện ích.
Khôngcó bậc nào “đúng” — chỉcó bậc phù hợp với mứcthiệt hại bạn đang phòng.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 30 / 49

---

### Differential Privacy & Dữ Liệu Tổng Hợp

DP-SGD — DP cho training
– Cắtngưỡng gradient rồicộng nhiễu hiệu
chỉnhtronglúc train
– Cho cận chứng minh được vềảnh hưởng
củabất kỳ bản ghi đơnlẻ nào
– Đâylà bảo đảmtoán học,không phải nỗ lực
“tốtnhất có thể”
Lưu ý: Cái giá: mất tiện ích — và DPcó thể
khuếch đại thiên lệch khi fine-tune mô hình ngôn
ngữ. Phải đo cảhai.
Dữ liệu tổng hợp có DP
Sinh một corpus tương đương về mặt ngữ nghĩa
nhưng không chứa bản ghi thật nào . Chia sẻ và
trainthoải mái.
Cảnh báo quan trọng nhất phần này
LọcPII khôngchốngđược membership inference.
Mỗi mẫu chỉ có vài token PII — model vẫn ghi nhớ
phần còn lại củabản ghi.
Lọc PII và DP giải hai bài toán khác nhau. Đừng
dùngcái này để biện minhcho việc bỏ cái kia.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 31 / 49

---

### 12

RAG Có Phân Quyền: ACL
Trong Vector Store
Cách governance thất bại phổ biến nhất năm 2026: ACL ở hệ
nguồn hoàn toàn đúng, còn vector index thì vui vẻ phớt lờ chúng.

---

### Vấn Đề: Index Không Kế Thừa Quyền

Hệ nguồn
ACL đúng, chặt chẽ
Ingest & embed
ACL rơi ở đây
Vector index
chỉ còn vector + text
Mọi người dùng
đọc được mọi thứ
Không có cảnh báo nào phát ra. Pipeline chạy xanh, chất lượng câu trả lời tốt, không log lỗi nào.
Bảng lương của giám đốc chỉ đơn giản là bắt đầu xuất hiện trong câu trả lời cho thực tập sinh.
Nguyên tắc: mọichunk trong index phải mangtheometadata ACL —danh sách user / group/ role được phép thấy nó.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 32 / 49

---

### Pre-filter Hay Post-filter — Không Phải Lựa Chọn

Cách làm Cơ chế Kết luận
Post-filter ANN trả về top-k, ứng dụng loại bỏ
chunkkhông được phép sau đó
Hỏng. Trảvềíthơn kkếtquả;ngườiquyềnhẹp
có thể nhận câu trả lờirỗng dù dữ liệu tồn tại.
Cònlộ sự tồn tại quasố lượng và độ trễ
Pre-filter Điều kiện ACL được đánh giátrước /
bên trong phéptìm kiếm tương tự
Đúng. Vector không được phép không bao giờ
nổi lên — tầng ứng dụng không hề nhìn thấy
chúng
Phân vùng Indexđượcchiavùngvậtlýtheomẫu
truycập
Hiệunăngtốtnhấtởquymôlớn,đổilạivậnhành
phứctạp hơn
Ví dụ nhỏ gọn nhất để xem
Row Level Security đặt thẳng trên bảng vector: điều kiện phân quyền trở thành một phần của câu truy vấn, cơ sở
dữliệu không bao giờ trảvề dòng không được phép.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 33 / 49

---

### Lỗi Không Ai Lên Kế Hoạch: ACL Cũ

ACLởhệnguồnthayđổi—mộtngườirờinhóm. Indexvẫngiữmetadatacủahômqua.
Độ trễ đồng bộ trở thành một cửa sổ lỗ hổng phân quyền.
Thiết kế Cửa sổ lỗ hổng Cái giá
Đồngbộ ACL theo lịch = chu kỳ đồng bộ Rẻ,đơn giản — nhưng cửasổ là thật
Lưu group ID,phângiảithànhviên
tại thời điểm truy vấn từIdP
≈ 0 Thêmmột lần join mỗi truyvấn
Câu hỏi để tranh luận trong lab
Nhómbạnchọnchukỳđồngbộbaolâu? 5phút,1giờ,hay1ngày? Hãytrảlờibằngcâunày: “chúng tôi chấp nhận
một người vừa bị thu hồi quyền vẫn đọc được dữ liệu trong nữa”. Nếu câu đó nghe không ổn, bạn cần
phângiải tại thời điểm truyvấn.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 34 / 49

---

### 13

Rò Rỉ Dữ Liệu Qua Agent:
Egress Control
Ngày 11 dạy phòng thủ prompt injection theo chiều sâu. Ở đây
ta chỉ lấy đúng một góc: chặn đường DỮ LIỆU ĐI RA.

---

### Bộ Ba Chết Người — Và Chân Nào Ta Chặt Được

Truy cập dữ liệu riêng
Agent đọc được email, tài liệu, database
Nội dung không tin cậy
Email, tài liệu truy hồi,
output từ tool khác
Đường thoát ra
Gọi API, render ảnh, sinh link
+ +
Đủ cả ba⇒ hệ thống có lỗ hổng.Chặt bỏ bất kỳ chân nào thì đòn tấn công không thành.
Ngày 11 chặt chân giữa (lọc nội dung).Ngày 24 chặt chân phải — đường thoát.
Phầnlớninjection khôngđếntừônhậpcủangườidùng—chúngđếntrongnộidungagenttựđọc: email,tàiliệutruyhồi,
outputcủa tool khác (injection gián tiếp). Nghiên cứu côngbố 04/2026 ghi nhận số lượtthử tăng32%trongba tháng.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 35 / 49

---

### Bốn Control Thuộc Về Ngày Hôm Nay

Egress allowlist
Chặt đứt chân “đường thoát”: agent chỉ gọi được
host đã duyệt. Hướng dẫn NSA 2026:kiểm soát
ranh giới mạng thay vì tin vào prompt .
Capability token theo tác vụ
Tokenchỉđủquyềnchođúngviệcđanglàm,hếthạn
ngaysau đó — thu hẹpbán kính thiệt hại.
Cổng duyệt hành động
Bắt người xác nhận với hành động không đảo
ngược được hoặc gửi ra ngoài —khôngphảimọi
bước.
Dual-LLM: lập kế hoạch rồi thực thi
Model có đặc quyềnlậpkếhoạchnhưng không bao
giờ đọc văn bản thô. Model đọc văn bản thô thì
khôngcóđặc quyền.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 36 / 49

---

### OWASP Top 10 Cho Ứng Dụng Agentic (2026)

Bộkhung ASI01–ASI10 mô tả rủi rokhimodel trở thành một tác nhân : có mục tiêu,có
credential,có tool, có bộ nhớ, vàtự chuỗi hành động qua nhiềubước.
Vài mục đáng chú ý
– Chiếmquyền mục tiêu của agent
– Lạmdụng tool
– Đầu độc bộ nhớ & ngữ cảnh (ASI06)
– Agentlừa đảo (rogue agent)
– Quyềnhạn quá mức
Vì sao ASI06 đáng chú ý nhất hôm nay
Kẻ tấn công đầu độc bộ nhớ agent, embedding và
cơsở dữ liệu RAG.
Đó là cơ chếgiữ cho mục tiêu đã bị chiếm tồn
tại qua nhiều phiên —tấncôngkhôngkếtthúckhi
phiênkết thúc.
Hệ quả kiến trúc
Bộ nhớ agent và vector indexlà kho dữ liệu được quản trị , không phải cache —
cần đúng bộ control như mọi kho khác: phân loại, kiểm soát truy cập, ghi log, và có
đườngxoá.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 37 / 49

---

### Filter Là Mitigation — Split Là Containment

Mitigation — phát hiện rồi từ chối gửi
Vẫn ĐỌCdữ liệu nạn nhân, chỉ chặnchặng cuối —
dữliệu đã bị chạm.
Filter chuỗi còn yếu hơn: không dấu, teencode là
qua. Nó đòi bạnbiếtmọi cách viết lại.
Containment — split
KHÔNG BAO GIỜ đọc. Attacker vẫn chọn được
mụctiêu, nhưng mục tiêu đókhông với tới được.
Bất biến: Run đọc dữ liệu riêng không đọc văn
bản tự do để quyết định — nên không cần biết
payload.
customer_id suy từ nguồn tin cậy (ticket_id →
related_tickets).
Lab 24 chấm chỗ này: test_split.py trượt nếu
agent đọc hồ sơ attacker chỉ định, kể cả khi không
gửi.
PEP — Policy Enforcement Point
Đặt tại lời gọi tool : check(ctx) trả về (allow,
reason). reason không bao giờ rỗng — kể cả khi
allow. Quyết định không giải thích được là không
auditđược.
Audit ledger append-only
Chỉ ghi thêm,tamper-evident (mỗi dòng móc hash
dòng trước). Đây là file bạn mở khi regulator hỏi
“chứngminh dữ liệu chưa từngra khỏi hệ thống”.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 38 / 49

---

### 14

Chuỗi Cung Ứng Model: Pickle,
Safetensors, Ký Số
torch.load trên một file không tin cậy là thực thi mã tuỳ ý. Đây
không phải ẩn dụ.

---

### Pickle Là Thực Thi Mã Từ Xa

Lưu ý: torch.load()trênfile .bin/.ptkhôngtin
cậysẽ giải tuần tự mã Python tuỳ ý —tứclàchạy
codecủakẻtấncông,vớiquyềncủatiếntrìnhtrain-
ingcủa bạn.
Trọngsốmodeltảitừinternetlà mã thực thi,không
phảidữ liệu.
Cách sửa: safetensors
Định dạng tuần tự hoákhông thể thực thi mã khi
nạp. Đãlàđịnhdạngcôngbốmặcđịnhcủacácnhà
cungcấp lớn.
Lưu ý: Bài học tháng 12/2025: PickleScan —
côngcụOSSchínhđểpháthiệnpickleđộchại—bị
phát hiện cóba lỗ hổng zero-day cho phép vượt
qua,mỗi lỗ hổng CVSS 4.09,3.
Bài học rút ra:một scanner không phải một bảo
đảm về định dạng. Hãy chọn safetensors thay vì
quétpickle.
Đăng ký extension cũng là bề mặt tấn công
Tháng02/2026: 341 skill độc hại bịpháthiệntrong
một registry skill cho agent, phát tán mã đánh cắp
thông tin. Registry skill giờ là bề mặt chuỗi cung
ứngy hệt npm/PyPI.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 39 / 49

---

### Chứng Minh Model Đến Từ Đâu

Control Cho bạn điều gì Trạng thái 2026
safetensors Nạpfile không chạy được mã Mặc định của nhà cung cấp lớn — hãy bắt
buộcnó
Ký số model Bằngchứngmậtmã: modeldođúngbên
pháthành, chưa bị sửa
Sigstore +cosign;đượcmôtảlà yêu cầu tối
thiểutrongRFP 2026
AIBOM Kiểmkê thành phần của hệthống AI OWASP AIBOM đạt v0.1 (11/2025); Cy-
cloneDX& SPDX 3.0 mở rộngcho AI
Quy tắc một dòng cho pipeline của bạn
Chỉ nạp modelsafetensors + đã ký số + có trong AIBOM. Ba điều kiện này viết được thành một bước kiểm tra
trongCI — và đó chínhlà bài lab hôm nay.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 40 / 49

---

### 15

Compliance → Technical Control
Ngày này ánh xạ nghĩa vụ thành control chạy được. Phân tích
pháp lý chi tiết thuộc về Track 1 — Ngày 22.

---

### Bối Cảnh Pháp Lý — Bản Cập Nhật 2026

Quy định Phạm vi Ràng buộc kỹ thuật cụ thể
Luật BVDLCN 2025 Dữliệu cá nhân tại VN Hiệu lực01/01/2026; kèm NĐ 356/2025. Đồng ý, DPI-
A/CTIA,chuyển dữ liệu xuyên biêngiới
GDPR Kháchhàng EU Quyền xoá → xoá lan truyền trong khovà câu hỏi về
trọngsố model
EU AI Act Hệthống AI ở EU 02/08/2026: áp dụng chung + minh bạch Điều 50+
quyềncưỡng chế GPAI
ISO 27001 Khách hàng doanh
nghiệp
Khungquản lý ATTT,audit hằngnăm
SOC 2 Dịchvụ SaaS/Cloud Bảomật, sẵn sàng, toàn vẹnxử lý
Lưu ý: Nghị định 13/2023 đã HẾT HIỆU LỰC từ 01/01/2026. Nhiềutàiliệuvàslidevẫntríchdẫnnónhưluậthiện
hành— kể cả phiên bảntrước của chính bài giảng này. Hãy kiểm tralại mọi checklist tuân thủ bạnđang dùng.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 41 / 49

---

### Luật BVDLCN 2025 — Điều Đội Kỹ Thuật Phải Biết

Thế nào là chuyển dữ liệu xuyên biên giới?
– Chuyểndữ liệu đang lưu tạiVN ra hệ thống
lưutrữ ở nước ngoài
– TổchứctạiVNtraodữliệucánhânchobênở
nướcngoài
– Dùng nền tảng đặt ngoài lãnh thổ VN để xử
lý dữ liệu cá nhân thu thập tại VN
Lưu ý: Đọc kỹ gạch đầu dòng thứ ba:gọi API
LLM nước ngoài với dữ liệu cá nhân người Việt là
một hành vi chuyển dữ liệu xuyên biên giới. Đây
làlý do phần này nằmtrong một bài giảngkỹ thuật.
Chế tài
Mức phạt hành chính tối đa với vi phạm chuyển
dữ liệu xuyên biên giới:5% doanh thu năm liền
trước. Nếu không có doanh thu năm trước hoặc
5% thấp hơn mức trần thì áp dụng sàn3 tỷ đồng.
Hiệulực 01/01/2026.
Hồ sơ DPIA / CTIA
– Lập một lần chosuốt thời gian hoạt động,
cậpnhật theo quy định
– Gửi 01 bản chính chocơ quan chuyên
tráchtrong 60 ngày kểtừ lần chuyển đầu
tiên
Phântích pháp lý đầy đủ: Track1 —Ngày 22. Ở đâyta chỉ lấy phần ràng buộckiến trúc.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 42 / 49

---

### EU AI Act — Mốc Thời Gian Đã Thay Đổi

Cấm một số thực
hành + nghĩa
vụ AI literacy
Nghĩa vụ GPAI+
quy tắc quản trị
02/08/2026
Áp dụng chung
+ minh bạch
Điều 50+ quyền
cưỡng chế GPAI
Nghĩa vụ rủi ro
cao — Phụ lục III
Rủi ro cao nhúng
trong sản phẩm
— Phụ lục I
Lưu ý: Mốc rủi ro cao đã bị lùi lại bởi thoả thuận chính trị sơ bộ “Digital Omnibus”
(05/2026): Phụ lục III lùi tới02/12/2027, Phụ lục I tới02/08/2028. Nhiều tài liệu vẫn
ghi “rủi ro cao áp dụng 08/2026” — điều đó không còn đúng.Đây là thoả thuận sơ
bộ; hãy kiểm tra lại trước khi đưa vào cam kết hợp đồng.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 43 / 49

---

### Quyền Được Xoá Gặp Trọng Số Model

Xoálan truyền trong kho dữ liệugiải quyếtnơi lưu trữ. Nókhônggiảiquyết model.
Phương án Bảo đảm Chi phí Kết luận
Trainlại toàn bộ Phươngpháp duy nhất cóbảo
đảmchứng minh được
Hàng triệu đô cho
modellớn
Đúng,nhưnghiếmkhikhả
thi
SISA(chiamảnh) Tương đương train lại, chi phí
O(1/k) — chỉ train lại mảnh
chứabản ghi
Phải thiết kếngay từ
đầu; không áp dụng
ngượcđược
Câutrảlờikỹthuậtthậtsự
Unlearningxấp xỉ Giảm ảnh hưởng nhưng không
loạibỏ
Rẻ Dưới góc nhìn GDPR:
không phải là xoá
Câu chốt — và là lý do RAG là một quyết định về quyền riêng tư
Chiếnlượcxoárẻnhấtlà không bao giờ hấp thụ dữ liệu . Ẩndanh trướckhiingest,vàgiữdữliệucánhânở tầng
truy hồi —nơi xoá là một câuDELETEthật— thay vì trong trọngsố, nơi xoá là một bàitoán nghiên cứu.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 44 / 49

---

### Kiểm Soát Dữ Liệu Khi Gọi API LLM

Lưu ý: Từ chối train ̸= Zero Data Retention.
Từ chối train chỉ ngăn dữ liệu được dùng để huấn
luyện. Nhàcungcấp vẫn có thể lưu tạm payload.
Đâylà hai control riêng biệt. Mộtsốnhàcungcấp
gộpchung,mộtsốthìkhông—phảikiểmtracảhai.
Ba điều sinh viên hay nhầm
– ZDRcần hợp đồng doanh nghiệp đàm
phán riêng — khôngcótrên gói API trả theo
lượtdùng
– Có ngoại lệ thật: vệt suy luậnmở rộng và
mộtsố model mới có thểnằm ngoài điều
khoảnZDR chuẩn, lưu tới∼30ngày
– Data residency làcấu hình ghim vùngriêng,
thườngphải qua kênh bán hàng
Nối lại với Luật BVDLCN
Với một công ty Việt Nam, câu hỏi về residency và ZDR không phải chuyện vệ sinh
kỹ thuật — nóquyết định một lệnh gọi API có phải là hành vi chuyển dữ liệu
xuyên biên giới hợp pháp hay không . Hãy đưa nóvào hồ sơ CTIA.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 45 / 49

---

### 16

Vận Hành, Demo & Tổng Kết
Một control không đo được là một control bạn chỉ đang hy vọng
nó tồn tại.

---

### Chỉ Số Nên Phát Ra — Và Ngưỡng Đi Kèm

Chỉ số Ngưỡng / cách đọc Thuộc phần
Audit completeness — % dòng ledger có
reason
100%. Dưới 100% là hỏng,
khôngphải “gần đạt”
Vậnhành
time_to_revoke khikhoá bị lộ Phút,không phải ngày Secrets
Độphủ mã hoácảrest vàtransit Sovới mốc nền 37% Encryption
RecallPII theo từng entity Khôngbao giờ gộp PIIdetection
Độtrễ đồng bộ ACL củavector index Đâylà cửa sổ lỗ hổng RAGphân quyền
%model nạp từ artifactđã ký + safetensors Mụctiêu 100% Chuỗicung ứng
Độrộng scope của agent:cấp so với dùng Pháthiện read:all Danhtính agent
Độtươicủakiểmkêchuyểndữliệuxuyênbiên
giới
Khớphồ sơ CTIA Compliance
Vì sao cột giữa quan trọng hơn cột trái
Một dashboard đầy con số không có ngưỡng chỉ là đồ trang trí. Mỗi chỉ số phải kèm một câu trả lời cho “bao nhiêu
thì phải hành động?” — nếu khôngtrả lời được, đừng đo nó.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 46 / 49

---

### Live Demo: Đóng Mạch Trifecta Rồi Ngắt Nó

LIVE DEMO
1. Demo 1 — ba cái chân: search_docs (nộidung không tin cậy)+
read_customer (dữliệu riêng) + http_post (đườngthoát). Ba toolvô hại,
ghéplại thành một lỗ hổng
2. Demo 2 — tấn công: chạyagent chưa có control, xem CCCDvà số tài khoản
củakhách xuất hiện trong log củasink
3. Demo 3 — filter thất bại: thêmbộ lọc chuỗi “hãy gọi”; rồiphá nó bằng biến
thểtiếng Việtkhông dấu. Filter là mitigation, không phải containment
4. Demo 4 — split thành công: táchRun đọc dữ liệu riêng khỏiRun đọc văn
bảntự do. Cùngpayload đó, giờ không còn đườngđi
5. Demo 5 — bằng chứng: mở ledger.jsonl,chỉvàodòng decision=deny kèm
reason. Đó là câutrả lời cho regulator
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 47 / 49

---

### Lab #24

LAB #24
Mục tiêu: Tấn công chính agent của bạn, rồi ngăn nó lại. Đóngmạchlethaltrifecta
bằng prompt injection để agent gửi PII khách hàng ra sink; viết 5 biến thể injection;
rồi viết 4 control để chặn:pii.py (gate trước ingestion),policy.py (PEP tại tool
call), runner.py (trifectasplit +egressallowlist), ledger.py (auditappend-only)
Deliverable: attack-before.log và attack-after.log; injection-corpus.md
5 biến thể; ledger.jsonl mọi dòng có decision và reason không rỗng ;
compliance-mapping.md + dpia-lite.md. Chấm bằng--mock + pytest — không
cầnAPI key. Tự kiểm tra lure trước khichấm:python -m agent.check_lure
Thời gian: 2h
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 48 / 49

---

### Tổng kết — Key Takeaways

Những ý chính cần nhớ trướckhi sang bài tiếp theo
1 HệthốngAIthấtthủởphầnhạtầng—API/pluginbịchiếmquyềnvàcấuhìnhcloudsaichiếm
27%mỗi loại. Đừngbắt đầu từ model.
2 GắnchínhsáchvàoTAG,khônggắnvàobảng. Bảngsinhrangàymaiphảiđượcquảntrịmà
khôngcần ai nhớ cấp quyềncho nó.
3 ACLphảiđitheochunkvàovectorstorevàlọcTRƯỚCkhitìmkiếm—đâylàcáchgovernance
thấtbại phổ biến nhất vàim lặng nhất.
4 Chiếnlượcxoárẻnhấtlàkhônghấpthụdữliệu. Ẩndanhtrướcingest;giữPIIởtầngtruyhồi
nơixoá là một câu DELETEthật.
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 48 / 49

---

### Tiếp theo & Bài tập

Ngày 25: GPU FinOps & Cost Opti-
mization + Quiz + Milestone 2
“Làm chủ chi phí GPU, hoàn thành
Chương 5 với quiz tổng hợp và Mile-
stone 2”
■ Hoànthành Lab 24: ABAC, PII
pipelinetiếng Việt& RAG phân
quyền
■ Ôntập Chương 5: CI/CD,
LLMOps,Monitoring,
Governance
■ Chuẩnbị Milestone 2: tổng hợp
artifacttừ Ngày 21–24
Giảngviên (VinUni) AICB· Ngày 24 Tuần5 49 / 49

---

### Hỏi & Đáp

Câu hỏi nào về ABAC, danh tính agent, PII tiếng
Việt, RAG phân quyền, hay Luật BVDLCN 2025?

---

### Cảm ơn!

AICB-P2T2 · Ngày 24
Data Governance & Security
lms.vinuni.edu.vn · Slide & template trên LMS