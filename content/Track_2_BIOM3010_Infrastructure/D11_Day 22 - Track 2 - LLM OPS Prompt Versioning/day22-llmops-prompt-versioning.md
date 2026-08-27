# day22 llmops prompt versioning

**File gốc:** `Track_2_BIOM3010_Infrastructure\D11_Day 22 - Track 2 - LLM OPS Prompt Versioning\day22-llmops-prompt-versioning.md`

---

### LLMOps & Prompt Versioning

AICB-P2T2 · Ngày 22 · Chương 5: Vận Hành
Giảngviên
VinUniversity · Phase 2 · Track2· Tuần5

---

### “Prompt thay đổi = behavior thay đổi. Bạn

có đang version control prompts như code
không? Case study: Team sửa một dòng trong
system prompt — latency tăng 3x vì output
dài hơn, cost tăng 200%. Không ai biết, vì
prompt không có version, không có owner,
không có rollback. Hôm nay ta biến prompt
từ string literal thànhartifact có vòng đời .”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### NộiDung Bài Học

1. MLOps →LLMOps: artifact đổi
2. Promptlà Artifact, không phải String
3. PromptRegistry: version &label
4. Git-nativevs Registry & rủi rovendor
5. Runtime: fetch mà khôngphụ thuộc cứng
6. Environments& Promotion
7. Testprompt trong CI: regression gate
8. Release: A/B & canarycho prompt
9. Rollback& Incident drill
10. ModelDeprecation Treadmill
11. PromptCaching: version LÀcache prefix
12. CostTracking& Attribution
13. Guardrailconfig như artifact
14. LLMOpsStack 2026
15. Đónggói bundle thành file
16. Phântầng context: luônnạp vs lười
17. Contrỏ có quản trị: tên & quyền
18. Demo,Lab & Tổng kết
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 1 / 52

---

### MụcTiêu

Saubuổi học này,bạnsẽ:
1. Môtả đượcđầyđủ mộtprompt artifact gồm những gì (khôngchỉ chuỗi text)
2. Viếtđượcfile artifact cho prompt của mình,vàphântầng contextđể không huỷ
cacheoan
3. Thiếtkế promptregistry: immutable version+ movablelabel +rollback trongvài giây
4. Wiremột evalgate vàoCI để chặn prompt regression trướckhi merge
5. Sốngsót quamodeldeprecation màkhông phải viết lại prompt library
6. Đođược costper prompt versionvàper user — trước khi hoáđơn về
Ranhgiới bài học
Hômnayhọc vòngđời củaartifact. Cáchchấmđiểm chấtlượng →Day14. Cáchtrace/dashboard →Day13&23.
Guardrails →Day11. CI/CDtổng quát →Day21.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 2 / 52

---

### DeliverableCuối Ngày

Artifactcần nộp
Mộtpromptartifactcóversion,cóevalgatetrongCI,cólabel prodrollbackđược,và
cóbáo cáo cost theo từng version
■ Promptregistry (Langfuse hoặc LangSmith) với≥3versions + commit message rõràng
■ CIjob chạy regression suite,failPR khiđiểm tụt quá ngưỡng
■ Label prodtrỏversion đã pass; demo rollback<60giây
■ Bảngcost/latency theoprompt version+cache hit rate
Ngưỡngchất lượng & cách chọnmetric: dùng lại khungDay 14 — hôm nay talo phần gate, không lo phầnchấm.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 3 / 52

---

### 01

Từ MLOps Đến LLMOps: Arti-
fact Đổi Thì Vòng Đời Đổi
Khi artifact chính không còn là weights mà là prompt + context,
mọi quy trình vận hành phải viết lại — không phải vì công cụ
mới, mà vì thứ bạn version hoá đã khác

---

### MLOpsvs LLMOps: SoSánh

Khíacạnh MLOpstruyền thống LLMOps
Artifactchính Modelweights + dataset Prompt + context + model pin
(thườngkhôngtrain)
Tracking Hyperparams,train/eval metrics Tracetừng LLM call, token cost
Output Deterministic,reproducible Non-deterministic, chất lượng chủ
quan
Versioning Modelweights, data +Prompts,toolschema,modelsnap-
shot
Evaluation Accuracy,F1, AUC Faithfulness,relevance,hallucination
Cost Train-heavy,inference rẻ Inference/token-heavy
Drift Datadrift, concept drift + Prompt / embedding / model-
versiondrift
Điểmmấu chốt: MLOps
sởhữu toàn bộ vòng đờihuấnluyện. LLMOps giả địnhđã có foundation model — việccủa bạn làquảntrị thứ bạn gửi
vàomodel,chứ không phải trọng sốbên trong nó.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 4 / 52

---

### ĐơnVị Vận Hành Mới: Compound AI System

Hệthống >model
BAIR (Zaharia et al., 02/2024): kết quả SOTA đến từ
hệ thốngnhiều thành phần — nhiều lần gọi model +
retriever+ tools — chứ khôngtừ một model đơn lẻ.
Hệ quả vận hành: đơn vị để version hoá, để test, để
rollbacklàcả pipeline,không phải một model.
∼60%ứng dụng LLM dùng mộtdạng RAG nào đó (số liệu
BAIR2024).
Câu hỏi tự kiểm — “Phiên bản hiện
đangchạy trên production là gì?”
Nếu câu trả lời chỉ là một git SHA củacode, bạn
đang thiếu 80% thông tin: prompt nào, model
snapshot nào, index version nào, tool schema
nào.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 5 / 52

---

### BẫyNền Tảng: temperature=0 KhôngPhải Reproducible

Lưu ý:Bẫy: temperature=0 không đảm bảo cùng output. Thay đổibatch size⇒
thứtựcộngfloating-pointđổi ⇒kếtquảkhác. Đâykhôngphảilỗiseed,vàbạnkhông
“sửa”được từ phía application.
Quy tắc Ops— Pin ngưỡng eval, đừng
pin output.
Gate trên “% pass ≥ X” kèm khoảng tin cậy —
không gate trên so khớp chuỗi. Một test so sánh
string bằng nhau sẽ đỏ ngẫu nhiên và team sẽ học
cáchbỏ qua nó.
Vìsao điều này thuộc Day22
Non-determinism là lý do prompt cầnversion chứ
không chỉ cần diff. Bạn không thể chứng minh
“promptmớitốthơn”bằngcáchchạymộtlần—bạn
cần một artifact cố định để chạy lại nhiều lần trên
cùngmột bộ dữ liệu.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 6 / 52

---

### 02

Prompt Là Artifact, Không Phải
String Literal
Nếu prompt của bạn là một chuỗi nằm trong ba file và một lời
cầu nguyện, thì bạn không có hệ thống — bạn có một quả bom
hẹn giờ

---

### PhảnVí Dụ: “StringLiteral TrongBa File”

Lưuý: Câuchuyệncóthật: chiếnlược
deploy cho prompt và model là“một
stringliteralnằmtrongbafilevàmột
hyvọng” —vàchỉbịpháthiệnkhinhà
cung cấp thông báo khai tử model với
thờihạn 60 ngày.
Triệuchứng nhận biết trong codebasecủa bạn:
■ grepra3 bản copy hơi khácnhau của cùng một
systemprompt
■ Khôngai biết bản nào đangchạy thật
■ Sửaprompt = deploy lại toànbộ app
■ Rollbackprompt = revert commit +chờ CI 20 phút
Bốncâu hỏi kiểm tra độtrưởng thành
1. Promptđang chạy trên prod cóIDkhông?
2. Aiđổi nólầncuối,và vì sao?
3. Rollbackmất bao lâu?
4. Versiontrước có cònchạyđược không?
Câu4 là câu khó nhất— và là lý do có§10.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 7 / 52

---

### MộtPrompt Artifact Thật Sự GồmNhững Gì

CONTEXTBUNDLE = đơn vị đượcversion hoá
Systemprompt Few-shotexamples Tool/ function schema
Outputschema ModelID + snapshot Decodingparams
Retrievalconfig Guardrailconfig VersionID + owner
Sailầm phổ biến nhất:versionhoá ôđầu tiênrồiđể tám ô còn lạitrôi tự do. Đổimodel snapshot mà không đổi version
ID ⇒haihệ thống khác nhau mangcùng một cái tên.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 8 / 52

---

### VìSao “Model ID” Phải NằmTrongArtifact

Promptkhông tồn tại độc lập
Mộtpromptđược tunechomộtmodelcụthể. Cùng
chuỗitextđógửisangmodelkháclàmột thínghiệm
chưatừng chạy,không phải “cùng một prompt”.
Vì vậy cặp (prompt_version, model_snapshot)
mớilàđơnvịcóýnghĩa—khôngphảiriêngcáinào.
Hệquả trực tiếp—
■ Kếtquả eval chỉ có giátrịtrênđúng cặpđó
■ Rollbackprompt mà model đã bịkhai tử⇒
khôngrollback được
■ Đổimodel ⇒mấttoàn bộ prompt cache
(§11)
Bahệ quả này là basection riêng phía sau — chúngđều bắt nguồn từ đúng mộtquyết định thiết kế ở đây.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 9 / 52

---

### 03

Prompt Registry: Immutable Ver-
sion + Movable Label
Một ý tưởng duy nhất giải quyết cả versioning lẫn rollback: bản
ghi thì bất biến, còn cái tên “production” chỉ là một con trỏ

---

### MôHình Chuẩn: VersionBất Biến, Label Di Động

v1
a3f9c2
v2
7b1e04
v3
c8d5a1
v4
e2f770
append-only
production staging
rollback= dời con trỏ
Mỗilần sửatạomột versionbấtbiến vớiID tự sinh.Label(production, staging)là contrỏ màSDK phân giải lúc fetch.
Deploy= trỏ label sang versionmới.Rollback= trỏ ngược lại—không build lại, không deploylại code.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 10 / 52

---

### HaiHiện Thực Phổ Biến

LangSmithPrompt Hub—commit hash + tag
from langsmith import Client
client = Client()
# Pin an exact version (commit hash)
prompt = client.pull_prompt(
"my-org/rag-system:c8d5a1")
# Or resolve through a tag
prompt = client.pull_prompt(
"my-org/rag-system:prod")
# New version = new commit
client.push_prompt(
"my-org/rag-system",
object=new_prompt_template)
Langfuse(OSS) — label pointer
■ Versionbất biến + autoversion ID
■ Protectedlabels: chỉ admin đổiđược
production
■ Versiondiff viewđểreview
■ GitHubsync qua webhook→triggerCI
Lưuý: Promptđổi khôngcầndeployapp —đó
là ưu điểm lớn nhấtvà là rủi ro quản trị lớn nhất.
Xem§6.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 11/ 52

---

### CommitMessage Cho Prompt: ViếtGì Mới Hữu Ích

Lưuý: Vôdụng:
"update prompt"
"fix"
"try again"
Sáu tháng sau không ai biết vì sao dòng đó tồn tại
—và sẽ không ai dámxoá.
Hữuích
"Thêm ràng buộc JSON-only vì
3% output làm h￿ ng parser
(ticket #4412). Eval: faithfulness
0.81→0.83, cost +4%."
Khuônmẫu 3 phần— (1)Đổi gì—(2)Vì sao / bằng chứngnào—(3)Đánh đổi đo được.
Promptlàcode,nhưngkháccodeởmộtđiểm: bạn khôngđọcrađược ýđịnhtừdiff. Mộtdòng“Answerconcisely.”
khôngtự nói rằng nó tồntại để cắt 40% token cost.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 12 / 52

---

### 04

Git-native Hay Registry? Và Rủi
Ro Nhà Cung Cấp
Không có lựa chọn đúng tuyệt đối — nhưng có một tiêu chí
không được nhân nhượng: bạn phải xuất được dữ liệu ra

---

### MaTrậnQuyết Định

Tiêuchí Git-native(YAMLtrong repo) Registry (SaaS/OSS)
Reviewflow PRreview sẵn có, quen thuộc UIriêng, cần dạy lại team
Aisửa được Chỉngười biết git PM/SMEsửa được
Đổiprompt Cầndeploy lại app Khôngcần deploy
Rollback Revert+ CI (phút) Dờilabel (giây)
Audit Gitlog Auditlog + protected label
Rủiro vendor Không Có— phải xuất được
Phùhợp Monorepo,team engineer Teamđa vai trò, đổi nhanh
Lựachọn thực tế phổ
biếnnhất là lai:promptsốngtrongregistry để PM sửa nhanh,nhưng đượcsyncngược về gitquawebhook — git là
bảnsao lưu và là nơiCI đọc. Bạn đượccả tốc độ lẫn khả năngthoát.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 13 / 52

---

### RủiRo Nhà Cung Cấp LàCó Thật

Nềntảng Điềuđã xảy ra Đườngditrúdo chínhvendorđềxuất
Humanloop Đóng cửa 08/09/2025
(Anthropicacqui-hiređội
ngũ)
W&BWeave
OpenAIEvals Read-only 31/10/2026,
tắt30/11/2026
Cookbook chính chủ: chuyển sang
Promptfoo
OpenAI Prompt Objects
(/v1/prompts)
Tắt30/11/2026 “Đưa nội dung prompt vào applica-
tioncode”
OpenAIAgent Builder Tắt30/11/2026 AgentsSDK / WorkspaceAgents
Đọckỹdòngthứba—rồirútraquytắc — LờikhuyênditrúcủachínhOpenAIchoprompttrên
platform là“đưa prompt vào code ứng dụng của bạn”— thừa nhận bởi đúng nhà cung cấp hưởng lợi nhất từ
việckhoáchân. Suyra: mộtregistrybạnkhông exportđượcrafilephẳnglàmộttìnhhuốngcontin. Hãythử
xuấtprompt+version+labelraJSON/YAMLvàdựnglạihệthống chỉtừfileđó. Nghịchlý: OpenAImuaPromptfoo
(09/03/2026,vẫnOSS)rồichỉngườidùngEvalssangđó— côngcụOSSsốnglâuhơnnềntảnghosted (bảnđồ
côngcụ: §14).
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 14 / 52

---

### 05

Runtime: Fetch Prompt Mà
Không Tạo Phụ Thuộc Cứng
“Registry sập thì app sập” là một lỗi kiến trúc tự gây ra — và nó
có lời giải chuẩn, chỉ vài dòng cấu hình

---

### VấnĐề: Một NetworkCall TrênĐường Đi CủaRequest

NAIVE— registry nằm trên criticalpath
Request Fetchprompt
+80–300ms LLMcall Response
registrysập ⇒appsập
ĐÚNG— cache cục bộ +revalidate nền
Request Localcache
∼0ms LLMcall Response
Registry
revalidatenền
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 15 / 52

---

### BaLớp Phòng Vệ

# 1) Local cache (default 60s TTL)
prompt = langfuse.get_prompt(
"rag-system",
cache_ttl_seconds=300)
# 2) Fallback when cache is empty
# AND registry is unreachable
prompt = langfuse.get_prompt(
"rag-system",
fallback=BUILTIN_PROMPT)
# 3) Pre-fetch at startup
# -> first request never waits
def on_startup():
langfuse.get_prompt("rag-system")
Cơchế
■ TTLmặc định60giây
■ HếtTTL: trảbản cũ ngay lập tức,revalidate
ởbackground (stale-while-revalidate)
■ ⇒userkhôngbao giờchờnetwork
■ cache_ttl_seconds=0 tắtcache—dùngởdev
đểluôn lấy bản mới nhất
Đánh đổi cần nói rõ— TTL càng dài, prompt mới
lan ra càng chậm. TTL= thời gian tối đađể một
lầnrollbackcóhiệulựctoàncụm. ChọnTTLchínhlà
chọnRTOcủa bạn.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 16 / 52

---

### 06

Environments, Promotion & Ai
Được Pushprod
Khi prompt đổi được mà không cần deploy, con đường tới pro-
duction vừa mất luôn mọi chốt kiểm soát mà code đang có

---

### ĐườngThăng Cấp Của Một Prompt

dev
cacheTTL = 0
eval
gate
staging
shadowtraffic
canary
+review
production
protectedlabel
rollback: dời label
Dùngresourcetag (Environment: dev | prod )thay vì tách workspace riêng— để artifactdùngchung và thăng cấpđược
giữacác môi trường.Committag quyếtđịnh version nào code đangtham chiếu.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 17 / 52

---

### PromptSupply Chain: ChốtKiểm Soát Đã Biến Mất

Lưu ý: Prompt đổikhông qua CI, không qua code review, không qua deploy.
Nếuregistrychophépbấtkỳaidờilabel production,bạnvừatạoramộtđườngđẩy
codethẳng lên prod mà không aigác.
Kiểmsoát tối thiểu
■ Protectedlabel: chỉ role đượccấp mới dời
production
■ Bắtbuộc evalgate passtrướckhi dời
■ Auditlog: ai, khi nào,version nào, lý do
■ Cảnhbáo khi labelprodđổi
Câu hỏi diễn tập— “Một người vừa nghỉ
việctuầntrước. Họcònquyềndờilabel production
không?”
Với code, offboarding đã có quy trình. Với prompt
registry — thường là chưa. Đây là khoảng trống
quảntrị mới mà LLMOps tạora.
ChitiếtRBAC/IAM,phânquyềnvàtuânthủ: Day24. Ởđâytachỉchỉrarằngpromptregistrylàmộtbềmặtquyềnmớicần
đượcđưa vào cùng khung.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 18 / 52

---

### 07

Test Prompt Trong CI: Regres-
sion Gate
Prompt là code, nên nó phải có test chạy tự động và chặn được
merge — phần khó không phải chấm điểm, mà là nối dây

---

### EvalGate Nằm Ở Đâu TrongPipeline

Sửaprompt MởPR Chạyeval
trêngolden set
Sovới
baseline
Merge
pass
fail ⇒chặnmerge
+comment điểm số lên PR
Điểmmấuchốt: gatechạytrên mọiPRchạmvàoprompt,model,hoặcretrievalconfig—khôngchỉPRchạmcode. Đólà
lýdo prompt phải nằm ởnơi CI đọc được (git, hoặcregistry có webhook sync).
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 19 / 52

---

### Promptfoo: Regression Suite KhaiBáo

prompts: [file:// prompts/rag_v3.txt]
providers:
- openai:gpt-4o-mini
- anthropic:claude-sonnet-4-6
tests:
- vars: {question: "Refund policy?"}
assert:
- type: contains-json
- type: llm-rubric
value: "Answer grounded in context,
no invented figures"
- type: latency
threshold: 2000
- type: cost
threshold: 0.01
Vìsao chọn dạng khai báo
■ Testlà data,không phải code→PM
reviewđược
■ Chạynhiềuprovider cùnglúc →chuẩnbị
sẵncho §10
■ GitHubAction failjob khitụt điểm và
commentdiff lênPR
Bốicảnh: OpenAImua Promptfoo (09/03/2026); công
cụvẫnopen source. DeepEval là lựachọn kiểupytest
(assert_test,ngưỡng chặn deploy).
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 20 / 52

---

### GoldenSet: Ít MàTinh

Côngthức 2026
■ Bắtđầu ∼100case,tối đa ∼500
■ Gánnhãn tay,tin được
■ 3–5metric tươngquanvớihànhvisảnphẩm
■ Bổsung từtraceproduction thật
Lưuý: Chấtlượng >sốlượng. Sinhhàngloạt
case bằng LLM rồi không lọc= “AI slop”: suite to,
chạy lâu, tốn tiền, vàkhôngphát hiện được regres-
sionthật.
Ranh giới với Day 14— Cách chọn metric, cách thiết kế benchmark, LLM-as-judge, độ tin cậy
thống kê→ Day 14.Hôm nay ta chỉ quan tâm: bộ eval đó đượcgắn vào cổngnào, chặn được cái gì, và ai có
quyềnbỏ qua nó.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 21 / 52

---

### 08

Release: A/B & Canary Cho
Prompt Version
Eval offline nói prompt mới tốt hơn trên 100 case bạn tự chọn
— production nói nó tốt hơn hay không trên phần còn lại của thế
giới

---

### CơChế Định TuyếnTheoVersion

Router
hash(user_id)— sticky
prompt :c8d5a1
control— 90%
prompt :e2f770
canary— 10%
Mọitrace gắn tagprompt_version
90% 10%
Sosánh quality · latency ·cost · cache hit ratetheo version
Stickytheouser ,khôngrandomtheorequest—nếukhông,cùngmộtngườisẽthấygiọngvănđổigiữachừngtrongmột
hộithoại. Đây làkhác biệt so với A/B testmột nút bấm.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 22 / 52

---

### BaĐiều Kiện Để Con SốSo Sánh Có Nghĩa

1. Chỉđổi một biến.Đổiprompt vàmodelcùng lúc thì kết quảkhông quy được cho cái nào.
Đâylà lý do model IDphải nằm trong artifact (§2).
2. Tagđủ chiều ngay từcall site.Thiếutag prompt_version trêntrace ⇒khôngthể tách số
liệuvề sau. Dữliệu không tag được thìvĩnhviễn mất.
3. Đocả cost và latency,không chỉ chất lượng.Prompt“tốt hơn” mà dài gấpđôi có thể vẫn
làmột bước lùi — đúngnhư case study mở đầu buổihọc.
Ranhgiới — ToánhọccủaA/B (Welch’st-test,CUPED,SPRT,bandit)vàcác mẫushadow/canary →Day
23§14vàDay14. Hômnaytalophần nốidây: làmsaomộtrequestbiếtnóđangdùngversionnào,vàlàmsaosố
liệuquay về đúng version đó.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 23 / 52

---

### 09

Rollback & Diễn Tập Sự Cố
Rollback không phải là một nút bấm — nó là một tính chất của
hệ thống, và nó hỏng âm thầm nếu bạn không diễn tập

---

### RollbackNhanh — Nhưng Chỉ KhiBạn Đã Chuẩn Bị

Điềukiện đủ để rollback được
1. Versioncũ còntồn tại(immutable,không bị
ghiđè)
2. Modelsnapshot củanó còn phục vụ
3. Toolschema / output schema cũ còntương
thíchvới code đang chạy
4. TTLcache đủ ngắn để labelmới lan ra kịp
Lưu ý: Điều kiện(2) là cái hỏng thường xuyên
nhất và ít ai kiểm tra. Prompt v2 của bạn vẫn nằm
nguyêntrongregistry—nhưngmodelnóđượctune
chođãbịkhaitửbathángtrước. Rollbackthấtbại
đúnglúc bạn cần nó nhất.
Thờigian rollback thực tế=thờigian dời label+TTL
cache. Nếu TTL là300s, RTOcủa bạn là5 phút, không
phải“tức thì”.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 24 / 52

---

### DiễnTập: Bốn Bước,Làm TrướcKhi Cần

1. Pháthiện —alert nào sẽ kêu? (chất lượng tụt, cost vọt,JSON parse fail, cache hit raterơi
về0)
2. Quytrách nhiệm—trace có tagprompt_version không? Bạn có biếtversion nào gây ra
không?
3. Rollback—dời label. Bấmgiờ. So với consố bạntưởng.
4. Xácnhận —metric có thực sự trởlại mức cũ không? Nếu không, nguyên nhân không phải
prompt.
Bàitậptạichỗ — Đẩymộtpromptcốýtệlên staging,rồibấmgiờtoànbộbốnbước. Gầnnhưmọiteam
lầnđầu làm việc này đềuphát hiện họ thiếu bước(2)—trace không đủ tag đểbiếtversionnào đanggây lỗi.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 25 / 52

---

### 10

Model Deprecation Treadmill
Model bạn đang chạy sẽ bị khai tử. Câu hỏi không phải “nếu”
mà là “bạn phát hiện lúc nhận email, hay ba tháng trước đó”

---

### VìSao Đây Là ViệcCủaDay 22

Bốicảnh
Khai tử model từng là chuyện phiền mỗi năm một lần;
2026 nó là một mục thường trựctrên roadmap nền
tảng. Thời hạn báo trước dao động từkhoảng một
quýđến một năm.
Lưu ý: Silent behavioral regression: trỏ sang
snapshotmới,endpoint vẫntrả200 ,nhưngđịnhdạng
tool-callđổi,độtuânthủJSONlỏngra,ranhgiớitừchối
dịchchuyển. Khôngcó exception nào trong log.
Trườnghợpđượcbáocáo — Một
nhà cung cấp dịch vụ y tế buộc phải chuyển từ
Gemini1.5 sang 2.5 Flash:
■ outputdài ∼5×sốtoken
■ hạtầng parse JSONhỏnghoàn toàn
■ >400giờ táithiết kế prompt library
Nguồnthứ cấp, không nêu têntổ chức — dùng như mộtgiai thoại minh
hoạ,không phải số liệu chuẩn.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 26 / 52

---

### KỷLuật Phòng Ngừa: Eval Trênn+1

PROD
model n—pinned
nightly: modeln+1
nightly: modeln+2
Bảngchênh lệch
quality· cost · format
Khiemail khai tử đến, bạnđãbiếtcần sửa gì — vàmất bao lâu
Nguyêntắc: mỗicall site production chạy bộeval của nókhôngchỉ trênmodel đang pin, màliêntục trên các ứng viên
n+1. Chiphílàmộtjobnightlytrên ∼100case—rẻhơn400giờtáithiếtkế rấtnhiều. Đâycũnglàlýdobộtestở§7nên
khaibáo nhiều provider ngay từđầu: hạ tầng sosánh chéo model đã sẵn sàngtrước khi bạn cần đến nó.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 27 / 52

---

### 11

Prompt Caching: Version Của
Bạn LÀ Cache Prefix
Prompt versioning và kinh tế học cache là cùng một bài toán —
mỗi lần bạn sửa một chữ trong system prompt, bạn vứt đi toàn
bộ cache phía sau nó

---

### BấtBiến Duy Nhất Cần Nhớ

Nguyênlý — Promptcachinglàsokhớp tiền tố(prefixmatch). Bấtkỳthayđổi
nàoở byte thứ N cũng huỷcache của mọi thứ từ Ntrở đi.
tools system messages
ổnđịnh nhất biếnđộng nhất
thứtự render
sửa1 byte ở đây⇒huỷtoàn bộ bên phải
Vìthứ tự render làtools → system → messages,hãy đặt nội dungổnđịnh trước, biến động sau. Đây là mộtquyết định
thiếtkế prompt,không phải một tuỳ chọncấu hình.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 28 / 52

---

### KinhTế Học: ĐọcRẻ, Ghi Đắt

Thaotác Giá(sovớiinputthường) Ghi chú
Cacheread ∼0.1× CảAnthropic và OpenAI
Cachewrite (5 phút) 1.25× Anthropic,TTL mặc định
Cachewrite (1 giờ) 2× Anthropic,TTL mở rộng
Điểmhoà vốn
TTL5 phút: hoàvốn ở2request
(1.25 + 0.1 = 1 .35×sovới 2×nếukhông cache)
TTL1 giờ: cần ≥3request
(2 + 0.2 = 2 .2×sovới 3×)
Lưuý: Sốliệumultiplierởtrênlàcủa Anthropic.
Mỗinhàcungcấpmộtkhác—OpenAIbậtcache tự
động cho prompt ≥1.024 token, vòng đời 30 phút
(GPT-5.6+), tối đa 24 giờ với extended retention.
Luônkiểm tra pricing hiện hành.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 29 / 52

---

### NgưỡngTối Thiểu Không Tăng ĐềuTheo Đời Model

Model(Anthropic) Prefixtối thiểu
ClaudeOpus 5, Fable 5, Mythos5 512token
Opus 4.8, Sonnet 5, Sonnet 4.6, Sonnet 4.5, Opus 4.1/4,
Sonnet4
1.024token
Opus4.7, Haiku 3.5 2.048token
Opus4.6, Opus 4.5, Haiku 4.5 4.096token
Lưu ý:Ngưỡng không đơn điệu theo thế hệ.Một prompt 3K tokencócache trên
Opus 5 / Opus 4.8 / Sonnet 4.5, nhưngim lặng không cachetrên Opus 4.6 hay
Haiku 4.5. Không có lỗi nào được ném ra — chỉ làcache_creation_input_tokens:
0.
⇒Đổimodel cũngđổingưỡng cache. Mộtlần “tối ưu chi phí” bằngcách hạ cấp model có thểtắtcache hoàn toànvà
làmchi phítăng. Tối đa4breakpoint mỗirequest.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 30 / 52

---

### ThứBậc Huỷ Cache: Cái Gì Huỷ Cái Gì

Thayđổi tools system messages
Tooldefinitions (thêm/bớt/đổi thứ tự) huỷ huỷ huỷ
Đổimodel huỷ huỷ huỷ
Nộidung system prompt giữ huỷ huỷ
tool_choice,images, bật/tắt thinking giữ giữ huỷ
Nộidung message giữ giữ huỷ
Nốingượcvề§10 — Đổimodelkhôngcó
đường thoát— cache gắn theo model. Ngày bạn
buộc phải migrate vì deprecation, bạn mấttoàn bộ
cache cùng lúc: chi phí input tăng vọtđúng lúc bạn
đangchữa cháy.
Tintốt
tool_choicevàbật/tắtthinking khôngphácache
tools+system—đừnglolắngthừavềchúng. Chỉ
tool definitionsvà model mới buộc dựng lại từ
đầu.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 31 / 52

---

### SilentInvalidators: Danh SáchCần grep

# BAD: prefix changes EVERY request
system = f "Today: {datetime.now()}"
# BAD: ID early in the content
system = f "[req {uuid4()}] You are..."
# BAD: non-deterministic dump
system = json.dumps(cfg) # missing
# sort_keys= True
# BAD: per-user prefix
system = f "User: {user.name}..."
# BAD: each flag combo = new prefix
if beta: system += EXTRA_RULES
# BAD: tool set varies per user
tools = build_tools(user)
Cáchkiểm chứng
Đọc usage.cache_read_input_tokens. Nếunó
bằng0 quanhiềurequestcócùngprefix ⇒có
mộtsilent invalidator.
Bẫy đọc số: input_tokens chỉ làphần chưa
cache. Tổng prompt = input_tokens +
cache_creation + cache_read.
Cách sửa — Chuyển phần động ra sau
breakpoint cuối, làm nó xác định (sort keys),
hoặcxoá nếu không thực sựcần.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 32 / 52

---

### HaiCái Bẫy Ít Người Biết

Cửasổ nhìn lại 20 block
Mỗi breakpoint chỉ dò ngượctối đa 20 content
blockđểtìmcachecũ. Mộtlượtagentcónhiềucặp
tool_use/tool_result dễ vượt 20 block⇒request
kếtiếp misstrong im lặng.
Sửa: đặtbreakpointtrunggianmỗi ∼15blocktrong
cáclượt dài.
Requestsong song
Mộtcacheentrychỉ đọcđược saukhiresponseđầu
tiênbắtđầustream . BắnNrequestgiốnghệtnhau
cùnglúc ⇒cảN đều trả giá đầyđủ.
Sửa (fan-out): gửi 1 request, chờ token đầu tiên,
rồimới bắn N−1cái còn lại.
Lưu ý:Kết luận của cả section:một chỉnh sửa “vô hại” về câu chữ trong system
prompt là mộtsự kiện chi phí gấp∼10 lầncho tới khi cache đầy lại. Hãygộp các
thay đổi prompt thành lô, đừng rải rác cả ngày — và đừng bao giờ nhét timestamp
vàosystem prompt.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 33 / 52

---

### 12

Cost Tracking & Attribution
Câu hỏi “vì sao hoá đơn tháng này gấp đôi” chỉ trả lời được nếu
bạn đã gắn tag từ trước — dữ liệu không tag được thì mất vĩnh
viễn

---

### GắnTagTại Call Site: ViệcCó ĐònBẩy Cao Nhất

App
+metadata
Gateway
virtualkey,budget
LLMprovider Spanclose
gen_ai.usage
prompt_version· user · tenant ·feature · agent_run
Chiphí tính lúc đóng span,theo bảng giá có version
Gatewaynằm gần request nhất—nó gắn tag vàcưỡngchế ngânsách theo thời gian thực,tạo dữ liệu attribution sạch
ngaytại biên,trước khi chi phí kịpchạm dashboard.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 34 / 52

---

### BốnQuy Tắc Vận Hành

1. Gắnmetadata ở mọicallsite — ngay hôm nay.Header/fieldmetadata là bước có đòn
bẩycao nhất vàtươngthích tiến: dữ liệu bắtđầu tích luỹ trên trace từđúng thời điểm bạn
bậtnó. Không thểtruy hồi cho quá khứ.
2. Sosánh cost/request và token deltatheopromptVersion trongcùng một cửa sổ thời
gian. Đâychính là thứ phát hiệncase study mở đầu buổi học—trướckhihoá đơn về.
3. Chặntrước, tối ưu sau.Đặthard cap và throttle theouser/tenant trước; tối ưu prompt sau.
Mộtuser vượt ngân sách ngàyphải bị chặn, không phải bịghi nhận.
4. Bảnggiáphảicóversion. Giáthayđổitheothờigian;dữliệulịchsử khôngđược địnhgiá
lạitheo bảng giá hôm nay,nếu không mọi so sánhtheo thời gian đều sai.
Chiphí tầng GPU (MFU/MBU, kinhtế học instance)→Day25. Dashboard vàalerting →Day13 & 23. Ở đây chỉ làquy
nguyên nhân về đúng artifact .
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 35 / 52

---

### ThêmMột Chiều Bắt Buộc: Cache Hit Rate

Vìsao phải đo cùng nhau
Costperrequesttăngcóthể khôngphảivìpromptdài
hơn, mà vìcache hit rate rơi. Hai nguyên nhân này
cầnhai cách chữa hoàn toànkhác nhau:
■ promptdài hơn →sửanội dung
■ hitrate rơi →tìmsilent invalidator (§11)
Khôngtách được hai cái thìbạn sẽ tối ưu nhầm chỗ.
Bảngtối thiểu theo version—
■ cost/ request
■ tokenin / out
■ cacheread %
■ latencyP50 / P95
■ điểmchất lượng
Nămcộtnày,cắt theo prompt_version,trảlời đượcgần
nhưmọi câu hỏi vận hànhcủa một LLM app.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 36 / 52

---

### 13

Guardrail Config Cũng Là Một
Artifact Có Version
Guardrail là một phần của context bundle — nới một ngưỡng
cũng là một thay đổi hành vi cần review, cần eval, cần rollback

---

### GócNhìn Day 22 Về Guardrails

Guardrailconfig phải đi cùng prompt
Ngưỡng toxicity, danh sách PII entity, schema JSON
bắt buộc, hành vion_fail — tất cả đều làtham số
quyếtđịnhhànhvi . Chúngthuộcvềcùngmộtversion
vớiprompt.
Táchrờichúng ⇒promptv3chạyvớiguardrailconfig
củav1, và không ai biết.
Lưu ý: Nới một ngưỡng từ 0.7 xuống 0.5
không phải “chỉnh cấu hình” — đó là mộtthay
đổi hành vi an toàn, phải qua đúng cổng như
một thay đổi prompt: review, eval, audit log, roll-
backđược.
Ranh giới rõ ràng với Day 11— Day 11(20 section) sở hữu toàn bộ nội dung guardrails: attack
vector, prompt injection, jailbreak, defense in depth, tooling, red-teaming, HITL.Day 24sở hữu PII, RBAC và tuân
thủ.
Day22chỉbổsungđúngmộtđiều: nhữngcấuhìnhđólàartifact—vàphảiđượcversionhoá,thăngcấp,rollback
theocùng một vòng đời vớiprompt.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 37 / 52

---

### Defensein Depth — Nhắc LạiMột Slide

User
Input
InputGuards
PII,injection,
jailbreak
LLM
modelpin từ
contextbundle
OutputGuards
toxicity,format,
factualgrounding
Safe
Response
Block Reask/Block
Cảnăm hộp trên đều nằmtrong context bundle của §2.Đổibất kỳ hộp nào màkhông tăng version⇒bạncó một hệ
thốngkhác mang cùng một cáitên.Cơchế củatừng hộp: Day11.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 38 / 52

---

### 14

LLMOps Stack 2026
Bản đồ công cụ — chọn theo ràng buộc của bạn, không theo độ
nổi tiếng

---

### NămTầng Của Stack

Safety— Guardrails AI, Llama Guard,NeMo Guardrails(Day 11)
Evaluation— Promptfoo, DeepEval, Ragas(Day 14)
Tracing— LangSmith, Langfuse, W&BWeave,Phoenix (Day 13, 23)
PromptManagement — Langfuse, LangSmith Hub,MLflow Prompt Registry,Agenta, YAML+Git
Gateway& Cost — Portkey,Helicone, OpenMeter(Day 23, 25)
Tầngđược khoanh đỏ là phầnDay 22 sở hữu.Bốntầng còn lại được dạyở các ngày khác — ởđây chỉ để bạn thấy
promptmanagement ngồiở đâutrongbức tranh, và nó chạmvào cái gì.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 39 / 52

---

### ChọnCông Cụ Theo Ràng Buộc

Ràngbuộc của bạn Hướngchọn
Khôngđược để dữ liệu rangoài Langfuseself-host, hoặc YAMLtronggit
PM/SMEphải sửa được prompt Registrycó UI: Langfuse, Agenta, PromptLayer
Đãdùng LangChain sẵn LangSmith(tracing + Prompt Hub liềnmạch)
Muốngiấy phép rộng nhất Agenta(MIT)
Ưutiên regression suite trong CI Promptfoo(YAML+ GitHub Action)
Đãdùng Databricks / lakehouse MLflowPrompt RegistrytrongUnity Catalog
Sợvendor biến mất Bấtkỳ lựa chọn nào —miễn làexportđược
Lờikhuyênduynhấtkhôngphụthuộccôngcụ — Bắtđầubằng git+mộtfileYAML+một
suite promptfoo. Nó giải quyết 80% nhu cầu, không tốn tiền, không có rủi ro vendor, và dạy team đúng thói quen.
Chuyển sang registrykhibạn có nhu cầu cụ thể: người không biết git cần sửa prompt, hoặc cần rollback trong vài
giây.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 40 / 52

---

### 15

Đóng Gói Context Bundle Thành
File
Sơ đồ chín ô ở §2 chỉ có ích khi nó trở thành một file thật —
và ba nhà cung cấp frontier đã hội tụ về gần như cùng một tập
trường

---

### BaCách Lưu, Gần Như MộtTập Trường

Trườngcần lưu ClaudeCode SKILL.md MLflow Prompt
Registry
YAMLtronggit
Nộidung chỉ dẫn Thânfile Markdown template Khối prompt:
Địnhdanh name catalog.schema.name Đườngdẫn file
Khinào dùng description — description:
Modelpin model Tag model:
Toolschema allowed-tools — tools:
Lýdo thay đổi Commit message của
git
commit_message Commit message
củagit
Phiênbản GitSHA Sốtự tăng GitSHA
Contrỏ deploy Branch/ tag alias Branch/ tag
Ô—khôngphảilời khẳng định rằng sảnphẩm thiếu tính năng; nó chỉcó nghĩa là tài liệu khôngmô tả mộtchỗdành riêng
chotrường đó, nên bạn phảitự chọn nơi lưu. Và đó chính là điểm cầnthấy:mộttrường không có chỗ lưuthì không
biếnmất — nó chuyển thànhtri thức ngầm trong đầu mộtngười.Vìsao không có cột OpenAI:lựa chọn “sống trong platform” đãbị
tắt 30/11/2026,và đường di trú dochính OpenAI đề xuất là “đưanội dung prompt vào application code”— tức là đúng cột thứtư (§4).
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 41 / 52

---

### ĐọcMột Artifact File Thật: Từng TrườngLàm Gì

---

### name: deploy-check

description: Pre-deploy checks. Use
when the user asks about a
release or a rollout.
model: claude-opus-5 # model pin
effort: high
allowed-tools: Read Grep Bash
disallowed-tools: WebFetch
paths: services/** # when to
# activate
license: Apache-2.0
compatibility: needs kubectl

---

### Instruction body goes here...

Đốichiếu với §2
■ model →modelpin
■ allowed-tools →toolschema
■ paths →điềukiện kích hoạt
■ description →khinào dùng
■ license, compatibility →metadatađể
mangđi nơi khác
Điểm cần thấy — Đây không phải “một file
prompt”. Đây là context bundle của §2 dưới
dạngmộtđịnhdạngfile —vànónằmtronggit,
nên nó thừa hưởng miễn phí review, version và
rollbackcủa git.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 42 / 52

---

### TựThiết Kế: TậpTrườngTối Thiểu Của Bạn

# prompts/support-triage.yaml
name: support-triage
version: 7 # immutable
description: Route a ticket to
the right queue.
model: claude-sonnet-5 # pin
temperature: 0
tools: [lookup_order]
output_schema: schemas/triage.json
guardrails: guards/pii-strict.yaml
retrieval:
index: kb-2026-08
top_k: 3
owner: platform-team
commit_message: >
Add queue "billing-dispute":
6% fell through to catch-all
(ticket 4412). Eval 0.88 -> 0.91.
Chínô, mười mấy dòng YAML
Đọc ngược lại sơ đồ §2: nếu một ôkhông có
dòng tương ứng ở đây, hãy hỏi“nó đang nằm
ởđâu?” —câutrảlờigầnnhưluônlà“rảitrong
code”.
Batrường hay bị bỏ quênnhất—
■ model—thiếu nó thì kết quảeval vô
nghĩa(§2)
■ retrieval.index —đổi index là đổi hệ
thống
■ guardrails —xem §13
Filenày chính làđầuvào của Lab 22: thứ bạn push
lênregistry ở bước 1.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 43 / 52

---

### 16

Phân Tầng Context: Luôn Nạp
vs Nạp Lười
Không phải thứ gì trong bundle cũng đáng nằm trong mọi re-
quest — và tầng bạn chọn quyết định luôn cả hoá đơn cache
ở §11

---

### HaiTầng, Hai Hoá Đơn RấtKhác Nhau

TẦNG1 — LUÔN NẠP ·mọi request đều trả tiền ·nằm ở ĐẦU cache prefix
Systemprompt Facts/ memory Toolschema
TẦNG2 — NẠP KHI CẦN· chỉ request liên quan mớitrả tiền
Procedures Tàiliệu tham khảo Few-shottheo loại
Quytắc phân loại: fact(luônđúng, luôn liên quan)→tầng1. Procedure(chỉđúng trong một loại việc)→tầng2.
ClaudeCode hiện thực đúng haitầng này bằngCLAUDE.md (luônnạp) và thânSKILL.md (nạplười) — nhưng phép chiathì
ápcho mọiLLMapp.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 44 / 52

---

### KinhTế Học Của ViệcNạpLười

Nguyêntắc thiết kế
Tài liệu Claude Code nói thẳng:“phần thân của một
skill chỉ được nạp khi nó được dùng, nên tài liệu tham
khảodàigầnnhưkhôngtốngìchotớilúcbạncầnđến.”
Ngaycả phầnmôtả cũngbịgiớihạn 1.536kýtự trong
danhsáchskill—tàiliệughirõlýdolà “đểgiảmdùng
context”.
Áp dụng ngoài Claude Code—
Cùngphép tính đó cho appcủa bạn:
■ Few-shotdài →nạptheo loạitruyvấn
■ Toolschema →chỉnạp tool thật sự dùng
được
■ Chínhsách / quy trình→đưavào
retrieval,đừng nhét hết vào system
prompt
Lưuý: Nốithẳngvề§11: contextluôn-nạpnằmở đầuprefix. Sửamộtdòngởtầng
1 ⇒ đổi prefix⇒ huỷ cache của mọi thứ phía sau. Nội dung tầng 2 không gây ra
điều đó.Phân tầng không chỉ tiết kiệm token — nó quyết định cache của bạn
ổnđịnh đến đâu.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 45 / 52

---

### 17

Con Trỏ Có Quản Trị: Từ Tên
Gọi Đến Quyền
§3 nói label là một con trỏ, §6 nói con trỏ đó phải có người gác
— phần này là cách hiện thực cả hai bằng đúng một hệ định
danh

---

### ĐặtTên Trước,Phân QuyềnSau

Kháiniệm HiệnthựctrongMLflowPromptRegistry Tương ứng §3
Prompt Named entity, định danh ba cấp
catalog.schema.name
Promptrepo
Version Immutablesnapshot,số tự tăng Versionbất biến
Alias Mutable pointer tới một version
(production, staging)
Labeldi động
Tag Key–valuegắn theo từng version Metadataversion
Vì sao “định danh ba cấp” mới là điểm đáng học— catalog.schema.name không phải là
“têndàihơn”. Nóđặtpromptvào cùngkhônggiantênvớitablevàmodel —nêncâuhỏi“aiđượcsửacáinày?”
đượctrả lời bằng hạ tầngquyềnđãcó,chứ không phải một hệquyền thứ hai dựng riêng choprompt.
Tàiliệu nói thẳng về tínhbất biến: “một khiversion đã được tạo, template, commitmessage ban đầu và metadata củanó
khôngthể sửa.” Đâychính xác là mô hình §3,đóng gói thành sản phẩm doanhnghiệp.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 46 / 52

---

### PhânGiải Con Trỏ: Code Không Bao Giờ ChứaSố Version

import mlflow
# 1) Register -> immutable version
mlflow.genai.register_prompt(
name= "main.genai.support_prompt",
template= "Answer: {{question}}",
commit_message= "Initial support prompt")
# 2) Load by alias (no version no.)
p = mlflow.genai.load_prompt(
"prompts:/main.genai.support_prompt@production")
# 3) Deploy / rollback = move alias
mlflow.genai.set_prompt_alias(
name= "main.genai.support_prompt",
alias= "production",
version=2)
Badạng URI
prompts:/name@latest
prompts:/name/3
prompts:/name@production
Kỷ luật cần nhớ— Chỉ dạngthứ bađược
xuấthiệntrongcodeproduction. Haidạngkia
dành cho debug và cho eval — nơi bạncố ý
ghimmột version.
Langfusehiện thực cùng ý tưởngbằnglabel= ;
LangSmithbằng :tag. Cú pháp khácnhau,kỷluật
giốnghệt nhau.
Chúý: biến trongtemplate MLflow dùng ngoặc kép
{{question}}.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 47 / 52

---

### QuyềnLà Quyền Của Bề MặtBạn Đã Có

Táisử dụng, đừng dựng cáithứ hai
Để tạo/xem prompt, bạn cần một Unity Catalog
schemavớiquyền CREATE FUNCTION , EXECUTE, MANAGE.
Nghĩa là câu hỏi “ai được push lênprod?” (§6) trở
thành mộtcatalog grant— cùng bề mặt phân quyền
vớitable, model và feature.
VìsaoTrack2nênchúý — Prompt
trở thành một object có quản trị trong lake-
housecatalog,nằmcạnhtablevàmodel—đúng
tinhthần catalog-as-control-planecủaDay18.
Bạn không phải dựng hệ quyền thứ hai cho
prompt. Bạndùnglạicáiđãcó—kểcảquytrình
offboardingmà§6 đã chỉ ra làhay thiếu.
Đánhđổi: bạnbị buộc vào hệ sinhthái Databricks/Unity Catalog. Nhưngnếu tổ chức đã ở đó(Day 17–19), đây là con
đườngít ma sát nhất đểprompt có audit trail cấp doanhnghiệp mà không phải tự xây.Nguyêntắc mang đi được:chọn
bềmặt phân quyền mà tổchức bạnđãvậnhành tốt.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 48 / 52

---

### BaNơi Artifact Có Thể Sống

Artifact sống ở
đâu
Vídụ Exportđược? Contrỏ dời được?
Trongrepo ClaudeCode (.claude/) Có— là git Có— git revert
Trongcatalog MLflow Prompt Registry
+UC
Có— API + UC Có— alias
Trongplatform OpenAIPrompt Objects Khôngbền Đãtắt
Bàikiểmtrahaicâuhỏi—chạynó trướckhicamkết — (1)Artifactcó exportđượcra
file phẳng không? (2) Con trỏ códờiđược không?Claude Code có cả hai miễn phí nhờ git. Databricks cho cả
hai cộng thêm ACL của catalog. Bản hosted của OpenAI không giữ được cái nào một cách bền vững — và đã bị
khaitử (§4).
Balựa chọn đều hợp lệ. Hãy chọn theo ràngbuộc của bạn (§14) — nhưngđừng chọn cái trượt bài kiểmtra hai câu hỏi
trên.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 49 / 52

---

### 18

Demo, Lab & Tổng Kết
Mục tiêu cuối: một prompt artifact có version, có cổng chặn, roll-
back được, và biết nó tốn bao nhiêu

---

### LiveDemo: Vòng ĐờiĐầy Đủ Của Một Prompt Version

LIVEDEMO
1. Demo1: Pushprompt v2 vào registry→xemversion ID bất biến + diffso với
v1
2. Demo2: MởPR →promptfoochạy trong CI→failvìtụt điểm →xem
commenttrên PR
3. Demo3: Sửaprompt, pass gate→dờilabel staging →canary10% traffic
4. Demo4: Nhét datetime.now() vàosystem prompt →xem
cache_read_input_tokens rơivề 0 và cost/request nhảy vọt
5. Demo5: Sựcố →rollbackbằng cách dời label→bấmgiờ tới khi metric hồi
phục
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 50 / 52

---

### Lab#22

LAB#22
Mụctiêu: PromptArtifact Có Vòng Đời Đầy Đủ
Deliverable:
1. Dựngpromptregistry(Langfuseself-hosthoặcLangSmith): tạo ≥3versioncócommitmessage
theokhuôn mẫu 3 phần
2. Viếtsuite promptfoo (∼20case) + GitHub Action chặnmerge khi tụt điểm; chứng minhbằng
mộtPR bịchặn
3. Wirefetch có cache TTL +fallback prompt; tắt registry và chứngminh appvẫnchạy
4. Gắntag prompt_version vàotrace; xuất bảng cost/latency/cache-hit theotừng version
5. Diễntập rollback 4 bước; ghilại thời gian thực tế từlúc phát hiện tới lúc metrichồi phục
Thờigian: 2giờ
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 51 / 52

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
1 Promptlà artifact,khôngphảistring —gồmcảmodel pin,toolschema,retrieval vàguardrail
config. Thiếu một mảnhlà chưa version hoá.
2 Version bất biến + label di độnglo cả versioning lẫn rollback — nhưng rollback chỉ chạy
đượcnếu model snapshot cũ cònsống.
3 Promptversionchínhlàcacheprefix. Mỗilầnsửalàmộtsựkiệnchiphí—đo cache_read
cùngvới cost.
4 Gắntag ngayhôm nay. Dữ liệu attributionkhông truy hồi được cho quákhứ.
5 Repo,cataloghayplatformđềuđược—miễnlà artifactexportđượcvàcontrỏdờiđược.
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 51 / 52

---

### Tiếptheo & Bài tập

Bàitiếp theo
Ngày 23: Monitoring & Observabil-
ityStack
“Prometheus, Grafana, OpenTeleme-
try và SLO — từ “prompt nào đang
chạy” sang “toàn hệ thống đang khoẻ
đếnđâu””
Bàitập về nhà
■ Hoànthành Lab 22: prompt
artifactcó eval gate + rollback +
costreport
■ Càiđặt Docker Compose cho
Prometheus+ Grafana (pre-lab
N23)
■ Đọctrước: OpenTelemetry
Pythoninstrumentation guide
Giảngviên (VinUni) AICB· Ngày 22 Tuần5 52 / 52

---

### Hỏi& Đáp

Câu hỏi nào về prompt registry, eval gate trong
CI, model deprecation, hay cache economics?

---

### Cảmơn!

AICB-P2T2 · Ngày 22
LLMOps & Prompt Versioning
lms.vinuni.edu.vn · Slide & template trên LMS