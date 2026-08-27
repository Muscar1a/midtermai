# day12 deployment dua agent len cloud

**File gốc:** `Phase_1_COMP2010\D25_Day12-cloud-services-and-deployment\day12-deployment-dua-agent-len-cloud.md`

---

### Deployment — Đưa Agent Lên Cloud

AICB-P1 · Ngày 12 · Từ localhost đến production URL
TênGiảng Viên
VinUniversity · Phase 1 · 2026

---

### “Bạn demo cho sếp thấy agent chạy trên laptop.

Sếp hỏi: khi nào 100 người dùng được? —
và liệu nó có ngốn hết ngân sách không?”
Giữcâu hỏi này trong đầukhi học bài hôm nay

---

### NộiDung Bài Học

1. Từlocalhost đến production
2. Agentvs deploy truyền thống
3. Docker& containerization (2026)
4. Tháchthức riêng của agent
5. Agentchạy ở đâu:
server/client/on-device
6. Cloudoptions + managed runtimes (Tier
0)
7. HostingMCP servers
8. APIgateway & security
9. Scaling+ frontier-scale serving
10. CI/CD& eval gates
11. Nângcao: production-grade(tùychọn)
12. Checklist+ phụ lục lệnh/code
13. Lab12 + preview Day 13
Giảngviên (VinUni) AICB· Deployment 2026 1/ 84

---

### MụcTiêuNgày 12

■ Hiểugapgiữa dev và production: dependencies, config, secrets,networking
■ ViếtDockerfilehiệnđại (multi-stage +uv+slim/distroless) để đóng gói agent
■ Nắm3thứ agent phá vỡ webinfra thông thường: long-running, stateful, cost
■ Sosánh cloudoptions theotrục quan trọng nhất vớiagent:requesttimeout
■ Biếtvề managedagent runtimesmới(Bedrock AgentCore, VertexAgentEngine)
■ Thiếtkế APIgateway +cost protection và deploy agentcópublicURL hoạtđộng
Giảngviên (VinUni) AICB· Deployment 2026 2/ 84

---

### DeliverableCuối Ngày

Artifactpack cần nộp
Agent đã được containerize và deploy lên cloud, có health check endpoint, basic
authentication,cost guard, và accessible qua publicURL
■ 1Dockerfile (multi-stage, uv, <500MB)+ docker-compose cho agent +
dependencies
■ 1deployed instance trên Railway hoặc Render
■ 1health check endpoint (/health)+ streaming endpoint (SSE)
■ 1public URL mà bất kỳ aicũng có thể truy cập vàdùng agent
Giảngviên (VinUni) AICB· Deployment 2026 3/ 84

---

### 01

Từ Localhost Đến Production
Agent chạy trên máy mình khác rất xa với agent chạy cho 100
người — gap đó không chỉ là “copy code lên server”

---

### Recap: Agent Đã HoànChỉnh Nhưng Chỉ Ở Local

11ngày đã build
■ LLMAPI + prompt engineering
■ RAGpipeline grounded
■ Multi-agent+ MCP
■ UX+ trust layer
■ Guardrails+ safety
Nhưngđang chạy trên
■ localhost:8000
■ APIkeys trong .env file
■ Chỉ1 user (chính mình)
■ Khônghealth check
■ Tắtlaptop = agent chết
Lưu ý: “It works on my machine” là câu nói nổi tiếng nhất trong lịch sử software
engineering. Day 12 giảiquyết đúng vấn đề này.
Giảngviên (VinUni) AICB· Deployment 2026 4/ 84

---

### DevEnvironment ̸=ProductionEnvironment

Khíacạnh Dev(localhost) Production
Dependencies “pipinstall” thủ công Đónggói cùng container
Config .envfile trên máy Environment variables, secrets
manager
Networking localhost:8000 HTTPS,domain, load balancer
Users 1(chính mình) Nusers đồng thời
Failure Restartthủ công Auto-restart,health check
Nguyêntắc
Environmentparity: dev/staging/prod cànggiống nhau càng ít bugkhideploy.
Giảngviên (VinUni) AICB· Deployment 2026 5/ 84

---

### AgentKhông Phải WebApp BìnhThường

MộtCRUDapptrảlờitrong <1s. Agentthìkhácvềbảnchất—vàđólànguồngốccủamọithách
thứcdeploy hôm nay.
1. Long-running
Reasoning loop chạy
10–60s+ (có khi vài
phút). Phá vỡ timeout
29–60s của gate-
way/proxy.
2. Stateful
Có conversation mem-
ory + tool history. Mâu
thuẫnvớiquytắc“state-
less process” của 12-
factor.
3. Costly
Mỗicallgửilạicảhistory
→ cost tăngsiêu tuyến
tính(50–1000×tokenso
vớichat).
Lưuý: Giữ3tínhchấtnàytrongđầusuốtcảbài. Mỗisectionsaugiảiquyếtmộthệquảcủa
chúng.
Giảngviên (VinUni) AICB· Deployment 2026 6/ 84

---

### 12-FactorApp — Áp Dụng ChoAI Agent

4nguyên tắc quan trọng nhất
1. Configinenv: khônghardcodeAPI
keys
2. Statelessprocesses: agentkhông
giữstate trên instance
3. Portbinding: exportservice via
port
4. Dev/prodparity: giữgap nhỏ nhất
Deploymentchecklist
□ Secretsmanagement
□ Healthcheck endpoint
□ Structuredlogging
□ Monitoringendpoint
□ Gracefulshutdown
Lưu ý:Factor VI (stateless) nói “không dùng sticky session”. Agent có memory→
externalize state (mục Thách Thức Riêng Của Agent ),không bỏ nguyên tắc.
Giảngviên (VinUni) AICB· Deployment 2026 7/ 84

---

### 02

Agent Deploy vs Deploy Phần
Mềm Truyền Thống
Tin tốt: bạn ship agent bằngđúng cỗ máyđã có (CI/CD, con-
tainer, load balancer). Tin cần nhớ: có 3 thứ bịđịnh nghĩa lại —
và đó là nơi agent khác biệt

---

### CùngCỗ Máy Ship, Khác CáiHộp Bên Trong

Giữnguyên (đừng phát minh lại)
■ CI/CDpipeline, build artifact
■ Immutableimage, canary/rolling
■ IaC(Terraform)
■ Loadbalancer,health check
■ 12-factor,stateless web tier
Bịđịnh nghĩa lại (cái mới)
■ Test: evalgate, không phải
exact-match
■ Hoáđơn: tokenruntime, không
CPU-hour
■ Dependency: modelngoài, rate-limit,
deprecate
■ State: hộithoại, không DB row
■ GPUeconomics: khôngCPU/RAM
Câuthần chú
Cùngcái hộp;cáibên trongvàcáchquyết định “đạt”mớilà phần khác.
Giảngviên (VinUni) AICB· Deployment 2026 8/ 84

---

### Before/ After — Monolith CRUDvs Agent

AppCRUD truyền thống AIAgent
Kiểmthử Unittest, assert chính xác Eval gate(golden set, LLM-judge),
gatetheo điểm
Chiphí CPU/RAM-hour, đoán trước
được
Token/request,chỉbiếtsaukhichạy
Latency Mili-giây,đồng bộ Giây–phút, streaming (SSE) +
async
State DBrows Hộithoại / memory (checkpointer)
Dependency Bạnkiểm soát & tự version Modelbênngoài : rate-limit,bịdep-
recate
Scalingunit CPU/RAM GPU+ VRAM
Lưu ý: Luận điểm: dùngcùng machinery(CI/CD, canary, immutable image, IaC, LB) —
nhưngđịnh nghĩa lạithetest, the bill, the dependency.
Giảngviên (VinUni) AICB· Deployment 2026 9/ 84

---

### HarnessMới Là Sản Phẩm —Sáu Lớp Bọc Quanh Lời GọiModel

Lớp Harnessphải cung cấp Trongcoding agent 2026 Mục
Vònglặp + tools Loop,toolschema,retry,giớihạnlượt Cùng một loop, ba mặt: CLI / SDK /
hosted
§1
Côlập FS + network làhai lớp bật-tắt độc
lập,ép ở tầng OS
Seatbelt (macOS), bub-
blewrap+seccomp(Linux)
§13
Chínhsách quyền allow / ask / deny, cưỡng chếngoài
model
opencode chỉ có lớp policy, không
sandboxOS
§13
Cấu hình theo
repo
Fileđi cùng git, thứ tựưu tiên rõ ràngAGENTS.md (gần nhất thắng) /
CLAUDE.md
§12
Phiên(state) Session ID, resume, lưungoài pro-
cess
Transcripttrênđĩa;hostedlưuserver-
side
§4
Cổng không
tươngtác
Exit code + JSON + chi phí mỗi lần
chạy
claude -p ; opencode serve + Ope-
nAPI
§12
Điểmmấu chốt
Lờigọimodelchỉlà mộtdòngtrongsáu . Promptkhôngphải biêngiớibảomật: chỉ
dẫntrong prompt/CLAUDE.md “khôngthay đổi những gì Claude Codecho phép”.
Giảngviên (VinUni) AICB· Deployment 2026 10/ 84

---

### ModelLà Dependency Bạn Không KiểmSoát

Khácthưviệnbạnpintrong requirements.txt: modelsốngtrênservercủangườikhác,cóthểbị
khaitử vàcó trầnthông lượngdonhà cung cấp đặt.
Pin& deprecation là việc củadeploy
■ PinmodelID +tắt auto-upgrade (như
deployartifact)
■ Providerbáo trước ≥60ngày rồi
requestfail
■ Thựctế: AssistantsAPI gỡ
26/8/2026; gpt-4o/4-turbo/3.5tắt
23/10/2026
Ratelimit = trần thông lượng
■ RPM/ TPM theotiercủanhà cung
cấp
■ VDGPT-4o: rate-limit tier 1= 500
RPM →tier5 = 10k
■ Trầndo vendorđặt,không phải
autoscalercủa bạn
■ →retry/backoff+ nhiều key (mục
Scaling)
Lưu ý:Lịch khai tử modelcủa nhà cung cấp là một forcing function lên release calendar
củabạn.
Giảngviên (VinUni) AICB· Deployment 2026 11/ 84

---

### 03

Docker — Đóng Gói Agent
Thành Container
Container giải quyết “it works on my machine” bằng cách đóng
gói mọi thứ agent cần thành 1 unit chạy được ở bất kỳ đâu

---

### ContainerLà Gì?

Container
Application
code
Dependencies
(Python,libs)
Runtime
config
MinimalOS layer (Debian slim /distroless)
Laptop CloudVM Kubernetes
Ýchính: Container= app + deps +runtime đóng gói thành 1 unit.Build1 lần, chạy ở mọinơi.
Giảngviên (VinUni) AICB· Deployment 2026 12/ 84

---

### Dockerfile2026 — Multi-Stage +uv

# Stage 1: build deps with uv (Rust-fast, ~10x pip)
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
RUN --mount= type=cache,target=/root/.cache/uv \
--mount= type= bind,source=uv.lock,target=uv.lock \
--mount= type= bind,source=pyproject.toml,target=pyproject.toml \
uv sync --locked --no-install-project --no-editable
FROM python:3.12-slim # Stage 2: slim runtime
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH= "/app/.venv/bin:$PATH"
RUN useradd -m app && chown -R app /app
USER app # non-root
CMD [ "fastapi", "run", "main.py", "--host", "0.0.0.0"]
Lưuý: Target <500MB: uv+cache, --locked,non-root, .dockerignore.
Giảngviên (VinUni) AICB· Deployment 2026 13/ 84

---

### BaseImage Showdown — Đừng ChọnSai

Baseimage Size(giảinén,
trênđĩa)
Ghichú cho AI agent
python:3.12 ∼1.0GB Full— thừa toolchain, attack surfacelớn
python:3.12-slim ∼150MB Defaulttốt choMLPython(glibc,manylinuxwheels)
distroless ∼66MB Gọnnhất + an toàn; khôngshell (debug khó)
python:3.12-alpine ∼55MB TRÁNHcho ML—xem cảnh báo
Lưu ý đơn vị: size “nén khi pull” nhỏ hơn ∼3–4× con số trên đĩa (vd python:3.14-slim-trixie ≈41 MB khi tải). Đừng so
hai đơn vị với nhau.
Lưuý: Alpinedùng musllibc →packagekhôngcówheel musllinuxphảicompiletừsource
(benchmark cũ pandas+matplotlib: slim 30s vs Alpine 26 phút).2026 đã đỡ hơn: numpy
2.5.1 / pandas 3.0.5 / matplotlib 3.11.1 đều đã có wheelmusllinux cho CPython 3.12–3.14
—nhưng matplotlib chưa có aarch64, nên Alpine trên Apple Silicon/Gravitonvẫnbuild từ
source. Vẫn nên chọnslim.
Giảngviên (VinUni) AICB· Deployment 2026 14/ 84

---

### ImageSecurity — Scan, Non-Root, SBOM

3việc bắt buộc
1. ScanCVE: Trivy/ Docker Scout /
Grypetrước khi deploy
2. Non-root: USER app ,không chạy
roottrong container
3. Pindigest: FROM ...@sha256:...
thayvì tag mềm
SBOM— giấy tờ thành phần
SBOM (SPDX/CycloneDX): liệt kê mọi
packagetrong image.
Sinhbằng syft/ docker buildx --sbom .
Giờ làyêu cầu pháp lý(US EO 14028,
EUCRA).
Mốc gần nhất: 11/9/2026— CRA buộc
báo ENISAtrong 24h. Nghĩa vụ đầy đủ
+SBOM: 11/12/2027.
Lưu ý:Distroless ít CVE hơn nhưngkhông phải zero. Scan là việc lặp lại, không
phảimột lần.
Giảngviên (VinUni) AICB· Deployment 2026 15/ 84

---

### DockerCompose — Multi-Service Setup

Agentstack điển hình
■ Agentservice: FastAPI+ LLM logic
■ Vectorstore: Qdrant(6333/6334)
■ Cache: Redis(6379) cho
session/ratelimit
■ Reverseproxy: Nginx(optional)
Compose2026
■ docker compose up (V2,không
gạchnối)
■ Bỏkey version: (đãobsolete)
■ depends_on: condition:
service_healthy
■ Servicegọi nhau bằng tên (DNS):
qdrant:6333
Cholab
Bắt đầu với 2 services:agent + vector store. Thêm Redis và Nginx khi hệ thống
cầnscale.
Giảngviên (VinUni) AICB· Deployment 2026 16/ 84

---

### HìnhHài Một Agent Service TốiThiểu

from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
app = FastAPI()
@app.get("/healthz") # health check for LB / Cloud Run
def healthz():
return {"status": "ok"}
@app.post("/chat") # streaming is the default, not the exception
async def chat(req: ChatRequest):
async def gen():
async for chunk in run_agent(req.messages):
yield { "event": "token", "data": chunk}
yield { "event": "done", "data": "[DONE]"}
return EventSourceResponse(gen())
Lưuý: /healthz chohạ tầng biết agent sống;/chatstreamtokenqua SSE.
Giảngviên (VinUni) AICB· Deployment 2026 17/ 84

---

### 04

Thách Thức Riêng Của Agent
Long-running + stateful = web infra thông thường “gãy”. Đây là
phần mà một bài deploy bình thường bỏ qua — nhưng agent thì
không thể

---

### VấnĐề Timeout— Agent ChạyLâu Hơn Gateway Cho Phép

Reasoningloop của agent thường lâuhơn timeout mặc định của hạtầng. Request bị cắtgiữa
chừng →userthấy lỗi 504.
Hạtầng Timeoutmặc định Ghichú
AWSAPI Gateway 29s →504 Cóthể nâng (từ 6/2024)
Herokurouter 30s(initial byte) Khôngchỉnh được
AWSALB (idle) 60s Cắtstream im lặng
nginx proxy_read_timeout 60s Giữa2 lần đọc
Fly.ioproxy (idle) 60s Streamingreset timer
Railwaypublic HTTP 15phút Privatenetwork: vô hạn
Lưuý: 2cáchvượt: (1) streamtừngtoken;(2)routequa privatenetwork hoặcasyncjob.
Bảng đầy đủ theo platform: mục Cloud Deployment Options.
Giảngviên (VinUni) AICB· Deployment 2026 18/ 84

---

### StreamingBằng SSE — Chuẩn De-FactoCho LLM

Tạisao SSE, không phải WebSocket?
■ Tokenstreaming mộtchiều
(server→client),chạy trên HTTP/1.1
thường
■ EventSource tựreconnect +
Last-Event-ID
■ OpenAI& Anthropic đều dùng SSE
(stream:true)
Lưuý: 2cái bẫy proxy hay gặp:
■ nginx proxy_buffering on (mặcđịnh) gom
tokenlại →tắtnó, hoặc header
X-Accel-Buffering: no
■ Agentim lặng >60s →heartbeat : ping
mỗi ∼15sđể không bị cắt idle
Streamđứt giữa chừng?
BuffertokenvàoRedistheo streamId →reloadthì replaytừchỗđứt . Giớihạn: chỉ
cứureload trang.
Giảngviên (VinUni) AICB· Deployment 2026 19/ 84

---

### KhiQuá Lâu — Chuyển SangAsync Job

Client API
(submit)
JobQueue
(Redis/Celery)
Worker
(agentloop)
POST
job_id
poll/ webhook
■ Submit-and-poll: APItrả job_idngay,client hỏi kết quảsau (hoặc nhận webhook)
■ Tool:Celery(broker),RQ(Redis),CloudTasks (managed)
■ Batchlớn không gấp?BatchAPI rẻhơn 50%: OpenAI trả trong24h;Anthropic cũng 50%
nhưngphần lớn xongdưới1 giờ
Giảngviên (VinUni) AICB· Deployment 2026 20/ 84

---

### Statefulness— Mâu Thuẫn Với “Stateless”

12-factornói agent phải stateless đểscale. Nhưng agentcómemory. Giải pháp:externalize
state,không giữ trên instance.
Externalizeở đâu
■ Conversation/session →Redis/
Postgres
■ LangGraphcheckpointer
(PostgresSaver)keyed bằng
thread_id
■ Bấtkỳ instance nào cũng phụcvụ
đượcrequest →scaletự do
Durableexecution (2025–26)
Cho agent chạy nhiều bước/nhiều ngày,
resumesau crash:
■ Temporal(replay)· DBOS(MIT,
Postgres)
■ Inngest(stepmemoization)
■ LangSmithDeployment (têncũ
LangGraph Platform)— managed
persistence
Lưuý: “Stickysession”chỉlà best-effort—CloudRunphávỡnókhiinstancebịkill. Exter-
nalizestate mới chắc.
Giảngviên (VinUni) AICB· Deployment 2026 21/ 84

---

### Concurrency& Cold Start

Concurrency: dùng async
Mỗi request giữ workerrất lâu → dễ cạn
workerpool.
■ async def : 1 worker phụcvụ nhiều
requestkhi awaitI/O
■ Bẫy: blockingcall trong async def
làmnghẽncả event loop
■ CloudRun concurrency: mặcđịnh 80,
max1000/instance
Coldstart: ML depsnặng
Load model/embeddings lúc khởi động→
coldstart chậm.
■ Mininstances (CloudRun) /
provisionedconcurrency (Lambda)
giữinstance ấm
■ Lazy-loadobjecthiếm dùng ra khỏi
coldpath
Nguyêntắc agent
AgentI/O-bound(đợiLLM) →tăngconcurrencytiếtkiệminstance;giữblockingcode
trong defthường.
Giảngviên (VinUni) AICB· Deployment 2026 22/ 84

---

### 05

Agent Chạy Ở Đâu? Server /
Client / On-Device
Một trục kiến trúc deploy mà nhiều người bỏ qua: vòng lặp agent
+ tools + API key thực sựchạy ở đâu? Câu trả lời quyết định
bảo mật, chi phí, và quyền riêng tư

---

### PhổVị Trí— LoopChạy Ở Đâu

Vịtrí Loopchạy ở APIkey Cost/token Nănglực
Server-side Backendcủa bạn Antoàn (server) Bạn trả hết Frontier
Client(chỉ UI) Trình duyệt, call qua
proxy
Vẫncần proxy Bạntrả hết Frontier
Local-first(BYOK) Máyuser (CLI/IDE) Keycủauser Usertrả Frontier
In-browsermodel Trìnhduyệt (WebGPU) Khôngcần Bằng0 ∼1–3B
On-device NPU/GPUthiết bị Khôngcần Bằng0 ∼3B
Edge Nodebiên (WorkersAI) Ở provider Pay-per-call ∼7B+
Hybrid On-device → escalate
cloud
Cloudtin cậy Rẻ→đắt Nhỏ→frontier
Mặcđịnh
Đa số agent production làserver-side: loop + tools + key ở backend, client chỉ là lớp mỏng gửi message. Đổi lại:
mọitoken đi vòng qua serverbạn, bạn trả toàn bộ compute.
Giảngviên (VinUni) AICB· Deployment 2026 23/ 84

---

### ĐiểmMấu Chốt: “Client-Side”Hiếm Khi Là Keyless

Browser
(UIagent)
Backendproxy
(BFF)
LLMprovider
(OpenAI/Claude)
request +API key
keythêm ở đây,
KHÔNGbao giờ xuống browser
Lưu ý:Build toolnhúngbiến VITE_/NEXT_PUBLIC_ thẳng vào JS bundle→key ship
xuốngtrìnhduyệtvà bịlấycắp . Vìvậyngaycảagent“client-side”vớimodelfrontier
vẫn cần backend proxy(Backend-for-Frontend) + rate limit. Chỉon-device / in-
browsermodel mớithật sự keyless.
Giảngviên (VinUni) AICB· Deployment 2026 24/ 84

---

### On-Device& Edge — Keyless ThậtSự

On-device(2025–26)
■ AppleFoundation Models(∼3B,
on-device,offline,free)
■ ChromeGemini Nano/Prompt API
(Chrome138, không gửi data đi)
■ MSPhi Silica(NPU,Copilot+ PC)
■ WebLLM/ transformers.js
(WebGPUtrong browser)
Edge
Cloudflare Workers AI: inference trên GPU
ở 200+ thành phố, pay-per-call, OpenAI-
SDKcompatible.
Đánhđổi: privacy+offline+cost0,nhưng
năng lực ∼1–3B, tốn pin, và cold load
weightslần đầu.
Hybrid(mẫu hay nhất)
Modelnhỏon-deviceloviệcthường →escalatelênmodellớntrêncloudkhikhó(VD
Apple: ∼3B →PrivateCloudCompute). Tiêuchíđịnhtuyếnthường không công bố.
Giảngviên (VinUni) AICB· Deployment 2026 25/ 84

---

### 06

Cloud Deployment Options
Không có 1 platform đúng cho mọi trường hợp — và với agent,
trục quan trọng nhất làrequest timeout, không phải giá

---

### 4TierDeployment (2026)

Tier0
Managedagent
runtime
Tier1
Railway/ Render
Fly.io
Tier2
CloudRun /
ECSFargate
Tier3
Kubernetes
self-managed
Khôngquản infra
AgentCore/Vertex
(Tier0)
<10phút deploy
MVP/ demo
Auto-scale
Production
Fullcontrol
Large-scale
Chokhoá học
Bắt đầu Tier 1 (Railway/Render). Hiểu flow deploy trước, migrate lên Tier 2/3 khi
businesscần, hoặc Tier0 nếumuốn bỏ qua việc quản hạtầng.
Giảngviên (VinUni) AICB· Deployment 2026 26/ 84

---

### SoSánh Platform — Theo TrụcTimeout

Platform Maxrequest/runtime Scale-to-0 GPU Agentfit
Railway 15phút / ∞private Không Không OK(route nội bộ)
Render ∼100phút (?) Freetier Không OK
Fly.io 60sidle (stream reset) Có Có OK+ streaming
CloudRun 60phút Có(cả GPU) L4 Mạnh
AWSApp Runner ∼120s Provisioned Không Deprecated
ECSFargate Khônggiới hạn Không — Mạnh(always-on)
Modal 24h(mặcđịnh 5phút) Có(snapshot) H100/A100 Mạnh (GPU)
Vercelfunctions 5 phút Hobby · 800s GA
(Pro)
Có Không Kém
Lưuý: Cậpnhật2026: Railwaybỏfreetier (giờ $5trialcredit);AWSAppRunner deprecated(Mar2026) →ECS
Express Mode; Cloud Run GPUGA (6/2025, scale-to-zero,∼5s start). Con số∼100 phút của Renderkhông có
trongdocs chính thức(chỉtrong bài so sánh marketing)— đừng thiết kế dựa vàonó.
Giảngviên (VinUni) AICB· Deployment 2026 27/ 84

---

### ServerlessFunctions — Tại Sao KhôngHợp Agent

Vercel/ Lambda functions
■ Hardcap 5phút (Hobby/mặc
định);GA 800s, beta 1800s→rồi
504
■ Bodycap 4.5 MB
■ Stateless— mất context giữa các
invoke
Container-basedhợp hơn
■ Giữđược connection cho
streamingdài
■ Min-instancegiữ ấm, tránh cold
start
Lưuý: Câucũ“serverlesscoldstart5–15s”giờ lỗithời: CloudRunGPUstart ∼5s,
Modalsnapshotnhanh ∼10×. Vấnđềthậtcủaserverlessvớiagentlà timeoutcap,
khôngphải cold start.
Giảngviên (VinUni) AICB· Deployment 2026 28/ 84

---

### Railway— Deploy Trong5Phút

Cácbước
1. Kếtnối GitHub repo
2. Railwaytự detect Dockerfile (builder
Railpack2026)
3. Setenvironment variables
4. ClickDeploy
5. Nhậnpublic URL
Tạisao chọn cho lab
■ Auto-detectDockerfile
■ Environmentvariables UI
■ Customdomain + SSL miễn phí
■ Logsreal-time
■ $5trialcredit (đủ cho lab)
Lưuý: Hếtfreetier: Railwaytínhtheousage;newusercó $5trialcredit(khôngcần
thẻ)hếthạnsau30ngày . Hếttrial →vềgóiFree: chỉ $1credit/tháng(khôngcộng
dồn),vàRailway xoávolume củatàikhoảntrial30ngàysauđó → sao lưu trước khi
hết hạn. Bind đúng0.0.0.0:$PORT.
Giảngviên (VinUni) AICB· Deployment 2026 29/ 84

---

### KhiRequest/Response Không Còn Là MôHình

Chạydài, không qua HTTP
■ CloudRun WorkerPools (GA
4/2026): instance chạy dàipull từ
queue— khôngcó trần request
timeout. Cột “60 phút”không áp
dụng.
■ VercelWorkflows: durable execution
—resume đúng điểm cũ, sốngqua
deploy/crash.
■ OpenAIResponses APIbackground
mode.
Trầncũ vẫn còn nguyên
■ AWSLambda: trần cứng vẫn900s.
APIGateway 29schặthơn, nằm phía
trướcnó.
■ Lambdaresponse streaming: native
chỉchoNode.js —Python khôngcó.
Ýchính
2026 platform mở lối thoát ở tầng hạ tầng:bỏ hẳn mô hình request/response. Chọn plat-
formgiờ là chọnmode.
Giảngviên (VinUni) AICB· Deployment 2026 30/ 84

---

### 07

Managed Agent Runtimes (Tier
0)
Danh mục mới hẳn của 2025–26: deploy agent màkhông phải
quản container— runtime, memory, identity đều managed

---

### Tier0 — Bạn Chỉ MangAgent, Cloud Lo Phần Còn Lại

Bạnkhông viết Dockerfile, không loscaling. Platform cấp sẵnruntime + session + memory +
identity,tính theo tiêu thụ.
Sảnphẩm GA Điểmnhấn
AWS Bedrock Agent-
Core
Oct2025 8giờ/session,microVMcôlậpmỗisession
Agent Runtime (tên
mới của Vertex AI
AgentEngine)
Mar2025 Sessions +Memory Bank+ Code Execu-
tion+ Example Store
Azure AI Foundry
Agent
May2025 No-code+hosted; miễnphíservice (trảto-
ken)
OpenAIAgentKit Oct2025 Agent Builder đóng 30/11/2026→ Agents
SDK;ChatKit vẫn còn
Đặcđiểm chung
Framework-agnostic(LangGraph,CrewAI,ADK...),hỗtrợMCP/A2A(A2Anaylàchuẩn v1.0
doLinuxFoundation quản,150+ tổ chức), session isolation.Cách tính tiền: slide sau.
Giảngviên (VinUni) AICB· Deployment 2026 31/ 84

---

### Frameworkvs Runtime — Hai TầngBạn Đang Chọn

“Framework-agnostic”ở slide trước nghĩa làgì? Mọi hãng lớnshiphaitầng riêng biệt—và bạn
chọntừng tầng độc lập.
Hãng Tầngframework (bạnviết agent) Tầngmanaged runtime(họchạy)
Anthropic ClaudeAgent SDK (Python/TS) ClaudeManaged Agents (public beta)
OpenAI AgentsSDK AgentKit;ChatKit là surface UI
Google ADK(5 ngôn ngữ, OSS) Agent Runtime(tên mới của Vertex AI Agent
Engine)
AWS StrandsAgents (Apache-2.0) BedrockAgentCore
Microsoft Agent Framework (AutoGen + Semantic
Kernel)
AzureAI Foundry Agent Service
LangChain deepagents(MIT) LangSmith Deployment · Managed Deep
Agents
Vìsao phải tách
Frameworkquyếtđịnh codebạnviết ;runtimequyếtđịnh aibịđánhthứclúc3hsáng . Đổi
framework = refactor. Đổi runtime = re-deploy. So sánh nhầm tầng là lỗi phổ biến nhất khi
đọctài liệu vendor.
Giảngviên (VinUni) AICB· Deployment 2026 32/ 84

---

### SessionLà Đơn Vị Vận HànhCủa Tier0

ỞTier0, requestkhôngcòn là đơn vị —sessionmớilà. Và sessioncó trần riêng.
Trầnsession từng platform
■ AWSAgentCore: tối đa8giờ,chết
khiidle15 phút;mỗi session một
microVMriêng, huỷ = wipe sạch.
■ ModalSandbox: mặc định5phút —
phải timeout= mớilên 24h.
■ ClaudeManaged Agents: session tự
chủhàng giờ, không công bố trần
cứng.
Khicần vượt trần
■ ModalFilesystemSnapshot →
restorevào Sandbox mới.
■ AgentCoremanagedsession
storagegiữstate qua session.
■ Nguyêntắc cũ vẫn đúng: state nằm
ngoàiruntimethì trần nào cũng vượt
được.
Lưu ý:Idle timeout là bẫy chi phí lẫn bẫy đúng-đắn:agent chờ human approval 20 phút
→sessionchết, state mất nếu chưaexternalize.
Giảngviên (VinUni) AICB· Deployment 2026 33/ 84

---

### Tier0 Tính TiềnThế Nào— TrụcChi Phí ThứBa

Tier0 thêmđồnghồ thứ haibêncạnh token: thờigian thựccủasession.
Platform Đồnghồ tính tiền
AWSAgentCore $0,0895/vCPU-giờ + $0,00945/GB-giờ — chỉ tính computeactive;
idle& I/O-waitmiễnphí. Gateway $0,005/1.000 invocation
Claude Managed
Agents
Giátoken chuẩn+$0,08/session-giờ,chỉ tính khi status =running
Cloudflare ActiveCPUpricing —chỉtínhchukỳCPUthựcchạy;thờigiannằm
chờLLM miễnphí
Azure AI Foundry
Agent
Servicekhôngtính phí riêng—chỉ trả cho model +tài nguyên nền
Rútra
Agent là workloadidle-heavy (phần lớn thời gian là đợi LLM). Chọn Tier 0 chỉ cần hỏimột
câu: đồng hồ có chạy khi agent đang chờ không? (Tốiưu chi phí ở quymô→Day25.)
Giảngviên (VinUni) AICB· Deployment 2026 34/ 84

---

### RuntimeCũng Là Dependency Bạn KhôngKiểm Soát

Bằngchứng trong chính bài này
■ OpenAIAgent Builderđóng
30/11/2026—vòng đời13tháng. Lối
thoát: Agents SDK.
■ OpenAIEvals cùnglịch →trỏsang
Promptfoo.
■ AWSApp Runner →ECSExpress
Mode.
■ LangGraphPlatform →LangSmith
Deployment: đổi tên cũnglà rủi ro —
docs/IaCcủa bạn trỏ tên cũ.
Bacâu hỏi trước khi chọn
■ Pincái gì? SDKversion, API version,
imagebase.
■ Thoátbằng đường nào?Export
đượcstate/config không?
■ Mấtbao lâu? Ướclượng thật.
Lưuý: Cùngcâuhỏibạnđãhỏivề model,giờhỏivề runtime: pin cái gì, thoát bằng đường
nào, mất bao lâu?
Giảngviên (VinUni) AICB· Deployment 2026 35/ 84

---

### Tier0 vs Tự Deploy —Khi Nào Chọn Gì

ChọnTier0 khi
■ Muốnship nhanh, không có team
infra
■ Cầnsession isolation + memory
sẵn
■ Agentchạy rất lâu (AgentCore 8h)
■ Đãở sẵn hệ sinh thái
AWS/GCP/Azure
Tựdeploy (Tier1–3) khi
■ Cầnkiểm soát đầy đủ stack
■ Tránhvendor lock-in
■ Tốiưu cost ở quy môlớn
■ Yêucầu compliance/networking
riêng
Lưu ý:Cho lab 12, ta vẫntự containerize + deploy(Tier 1) để hiểu cơ chế. Tier 0
làlựa chọn production khi không muốnquản hạ tầng — biết làđủ.
Giảngviên (VinUni) AICB· Deployment 2026 36/ 84

---

### DeepAgents — Thang 3 BậcCủa Chính LangChain

LangChainmô tả sản phẩm củahọ như mộtthang,không phải lựa chọn nhịphân — và nó ánh
xạgần 1–1 vào Tier0–3ở đầu mục này.
Bậc Bạnsở hữu Đánhđổi
OSSdeepagents(MIT) Toànbộ hosting Kiểm soát tối đa;tự cấu hình persis-
tence
LangSmithDeployment Application+ server code Choteamcầnrouteriêng,authnângcao,
scalelớn
ManagedDeep Agents Chỉ agent code, tools, middleware, in-
structions
LangChain lo backend, store, check-
pointer,memory,skills, sandbox,identity
Lưuý: ManagedDeepAgentsđangPRIVATEBETA :vàobằng waitlist,chỉchạyởregion
UScủa LangSmith Cloud,CLI-first, docs ghi rõ “behavior may change before general avail-
ability”,và chưacông bố giá. Biết là đủ— đừng thiết kế kiến trúcquanh nó.
Giảngviên (VinUni) AICB· Deployment 2026 37/ 84

---

### DeployDeep Agents — Bốn QuyếtĐịnh Hạ Tầng

Filesystembackend = quyết định infra
■ StateBackend(mặcđịnh): theo
thread,khôngchiasẻ cross-thread
■ StoreBackend/
CompositeBackend: chia sẻ
cross-thread
■ FilesystemBackendvà
LocalShellBackendtruycập thẳng
host— docs: đừngdùng trongagent
đãdeploy
Sandbox& secret
■ Thread-scoped: sandbox mới mỗi
hộithoại, dọn khi hết TTL
■ Assistant-scoped: dùng chung→
tíchtụ file & package→phảiđặtTTL
■ Authproxy chèncredential vào
requestđi ra →secretkhôngvào
sandbox
Lưu ý:Hai bẫy còn lại:(1) LangSmith Deploymenttự cấu hình persistent checkpointer —
self-hostthìbạnphảitựlàm,đâylàdeltalocal →prodlớnnhất. (2) Sharedmemory làvector
promptinjection —scope namespace theo user (Day11).
Giảngviên (VinUni) AICB· Deployment 2026 38/ 84

---

### “OpenSource” Không Có Nghĩa LàTự Host Được Miễn Phí

Bạntự host để tránh lock-in. Nhưng licence củaserverthườngkhác licence củalibrary.
Thànhphần Giấyphép Ràngbuộc khi self-host
LangGraph(library lõi) MIT Tựdo
langgraph-api (server) Elastic-2.0 Cầnlicensekey+egresstới beacon.langchain.com
(cóchế độ air-gapped)
n8n Sustainable Use Li-
cense
Chỉnội bộ / phi thươngmại
Dify Apache2.0 sửađổi Cấmchạy multi-tenant SaaS; cấm gỡlogo
ClaudeCode Proprietary Anthropic Commercial ToS —không phải open
source
CodexCLI · opencode · goose Apache-2.0 · MIT ·
Apache-2.0
Khôngràng buộc
Crush FSL-1.1-MIT Đọc được mã nhưngcấm dùng cạnh tranh; MIT
sau2 năm
Lưu ý:Ba câu hỏi khi thấy chữ “open source”:licence củaserver có giống licence của
library? Cóthưmục ee/? Cóphảigọivềnhà đểxácthựclicence? —VàOSS cóthểđóng
lại: Daytona đóng mãlớp sandbox ngày11/6/2026.
Giảngviên (VinUni) AICB· Deployment 2026 39/ 84

---

### 08

Hosting MCP Servers
Day 9 dạy agent gọi MCP tools. Khi MCP server cần chạyre-
mote cho nhiều client, nó cũng là một service phải deploy — và
phải bảo mật đúng

---

### stdiovs Streamable HTTP — HaiTransportCủa MCP

stdio(local)
Client spawn server làm subprocess,
nóichuyện qua stdin/stdout.
■ Chạycùng máy với agent
■ Khôngcần OAuth — lấy credential
từenv
■ Hợpdev / desktop
StreamableHTTP (remote)
Mộtendpoint(vd /mcp),POST+GET,SSE
bên trong.
■ Processđộc lập, phục vụ nhiều
client
■ Thaythế transportHTTP+SSE cũ
(2024-11-05)
■ Phảihost + bảo mật nhưAPI thật
Lưu ý: Remote MCP server (spec2026-07-28) phải dùngOAuth 2.1. stdio thì
KHÔNGcần. Ba cái bẫy spec gọi tên: slide sau.
Giảngviên (VinUni) AICB· Deployment 2026 40/ 84

---

### MCP2026-07-28 — Protocol TrởThành Stateless

Thayđổi lớn nhất
■ Babản: 2025-06-18 →2025-11-25 →
2026-07-28.
■ “MakeMCP stateless”: bỏ handshake
initialize +header Mcp-Session-Id.
■ TransportHTTP+SSEcũdeprecated
(12tháng chuyển tiếp).
■ Header Mcp-Method/Mcp-Name: router
khỏiparse JSON body.
Hệquả deploy
Mọi request rơi vàobất kỳ instance
nào sau LB round-robin thường:
không sticky session, không session
store,scale-to-zero thoải mái.
Đúng bài học mục Statefulness: ex-
ternalize state → tự do scale.
Lưuý chuyển tiếp
Server đã deploy vẫn phảitương thích ngượcvới client bản 2025 trong suốt giai đoạn
chuyểntiếp — đừng xoá codecũ ngay.
Giảngviên (VinUni) AICB· Deployment 2026 41/ 84

---

### OAuth2.1 Cho MCP — BaCái Bẫy Spec Gọi Tên

Bẫy1 — Tokenpassthrough
ServerMUSTNOT nhậntokenkhôngđược
cấpriêng cho nó. Speccấmrõ ràng.
Vìsaonguyhiểm: nó vôhiệuhoáratelim-
itingvà audit trailởservice phía sau.
Bẫy2 — Confused deputy
Proxyphảigiữregistry client_idđãduyệt
theotừng user,kiểm tra trước mỗi flow.
Xácthực đúng user ̸=uỷquyền cho client.
Bẫy3 — Discovery đã đổi
Từ 2025-11-25 theo RFC 9728 :
WWW-Authenticate nay tuỳ chọn, fall-
backvề .well-known.
Siếtthêm ở bản 2026-07-28
■ Validate isstheoRFC 9207
■ Khai application_type lúcđăng ký
■ DCRđangbị khai tử→CIMD
Lưu ý:stdio không cần OAuth. Nhưng khoảnh khắc bạn đưa server ra remote, nó làmột
APIcông khai với đầy đủnghĩa vụ.
Giảngviên (VinUni) AICB· Deployment 2026 42/ 84

---

### ServerMCP Là API Thật —Ba CVE Đã Chứng Minh

CVE Bàihọc deploy
CVE-2026-33032
nginx-ui,CVSS 9,8
đang bị khai thác
/mcp có AuthRequired(), /mcp_message thì không → 12 tool
khôngcần credential, chiếm server trong2request.
→ Xác thực MỌI route.Lỗi deploy kinh điển, không phải lỗi
protocol.
CVE-2025-6514
mcp-remote,9,6
Command injection trong chínhOAuth proxy: chỉ cần kết nối
tớiserver độc hại là RCEtrên máy client.
→Lớpproxy cũnglàattack surface.
CVE-2025-68143/4/5
GitMCP server (Anthropic)
Pathtraversal + argument injection;git_init bịgỡ hẳn.
→Ngaycảserverthamchiếucủa người tạo protocol cũngcólỗ
hổng.
Lưu ý:Rất nhiều MCP server chỉ làlớp bọc mỏng quanh một CLI. Deploy remote = phơi
CLIđó ra Internet→container,non-root, egress allowlist.
Giảngviên (VinUni) AICB· Deployment 2026 43/ 84

---

### DeployMCP Ở Đâu — Registry,Gateway,Runtime

Lớp Vaitrò Côngcụ 2026
Registry Để tìm Official MCP Registry: server.json + namespace
reverse-DNS.Chỉlàmetadata—KHÔNGphảihost-
ing;giải quyết discovery,không giải quyếttrust
Gateway Để gom& kiểm soát Docker MCP Gateway(mỗi server một container cô
lập,secrettậptrung); AWSAgentCoreGateway (gom
Lambda/REST/MCPvề một endpoint có governance)
Runtime Để chạy Cloudflare Workers + OAuth 2.1 qua
workers-oauth-provider; hoặc chính container
bạnđã học ở mục Docker
Mẫu2026
Registryđểtìm →Gatewayđểgom+kiểmsoát →Runtimeđểchạy. Đừngđểmỗiagent
tựcắm thẳng vào 20 serverrời rạc.
Giảngviên (VinUni) AICB· Deployment 2026 44/ 84

---

### 09

API Gateway & Security
Agent trên cloud cần lớp bảo vệ trước khi request đến logic —
authentication, rate limiting, vàcost protection(nơi nhiều startup
đã “cháy túi”)

---

### APIGateway Architecture

Client
Request
Auth
Check
Rate
Limiter
Input+
Budget Agent
Reject
Nguyêntắc
Mỗirequestphảiqua auth →ratelimit →validate+budgetcheck trướckhiagent
xửlý. Reject sớm= tiết kiệm tokens và tiền.
Giảngviên (VinUni) AICB· Deployment 2026 45/ 84

---

### AuthenticationPatterns

APIKey
Đơngiản nhất.
Header: X-API-Key
Dùng khi:internal, MVP,
B2B(M2M)
JWTToken
Statelessauth.
Bearertoken + expiry
Dùng khi: user-facing
app,microservices
OAuth2.1
Delegatedauth + PKCE.
Chuẩn cho MCP/agent
remote
Dùng khi: platform, re-
moteMCP
Lưu ý:Cho MVP:API keylà đủ. Đừng over-engineer auth trước khi có user thật.
Nhưngnếu hostremoteMCP server,OAuth 2.1 là bắt buộc theospec.
Giảngviên (VinUni) AICB· Deployment 2026 46/ 84

---

### CostProtection — Đừng Để AgentĐốt Hết Tiền

Rủiro (có thật)
■ $47.000trong 11ngày: 4agent retry vô
hạn,có log nhưng không cóhard limit
■ $96.000Vercel: appCara tăng
100k→900kuser trong vài ngày
■ Promptinjection →tokenexplosion
■ APIkey bị lộ→hackerxài
Bảovệ
■ Pre-calladmission control: check
budgetcòn lại trước khi gọiLLM, từ chối
nếuvượt
■ Per-tenantbudget: keytheo (tenant,
workload,model)
■ Ratelimiting: tokenbucket (rate + burst)
■ Circuitbreaker: tắtkhi anomaly
Lưuý: Bẫylớn: “spend alert”chỉ thôngbáo,KHÔNGchặn . Hardcaplàtínhnăng
riêng, phảibật thủ công. Alert của provider làphản ứng sau → vẫn phải tự build
admissioncontrol chặn trước.
Giảngviên (VinUni) AICB· Deployment 2026 47/ 84

---

### HTTPS,Secrets & OWASP

Securitybasics
■ HTTPS:Railway/Rendercấp SSL tự động
■ CORS:chỉlà kiểm soáttrình duyệt —
KHÔNGphải authz, API vẫn cầnauth
■ Secrets: dùngsecret manager (Doppler,
Infisical...) thay.env—có rotation + audit
■ GitHub: pushprotectionmặcđịnh;keylộbị
auto-revoke
OWASPLLM Top10(2026)
■ LLM01Prompt Injection
■ LLM02Sensitive Info Disclosure
■ LLM06Excessive Agency
■ LLM10Unbounded Consumption
(cost/DoS)
→ Agentcó tool: AgenticApps 2026—
ASI03(Identity)+ ASI04(Supply
Chain). Đầy đủ: Day 11
Lưu ý:Kiểm tra ngay:.env có trong .gitignore? Key có lỡ commit lên GitHub?
Nếucó →revokevà tạo key mới ngay lậptức.
Giảngviên (VinUni) AICB· Deployment 2026 48/ 84

---

### DữLiệu Chạy Ở Đâu —Residency,ZDR & Compliance

Gatewaylo auth, rate limit, cost. Còn một trục nữanhiều team chỉ phát hiện lúcký hợp đồng:dữ
liệunằm ở đâu và tồntại bao lâu.
OpenAI
■ 11region lưutrữ at-rest, nhưng chỉ
US/ EU / UAExửlý inference trong
vùng
■ Bậttheo project bằngprefixdomain
(eu.api.openai.com);phụphí 10%
■ ZDRloạinội dung khỏi log,ép
store=false ,phải duyệt trước
Anthropic
■ ClaudeManaged Agents KHÔNG
đủđiềukiệnZDRlẫnHIPAABAA —
vìnó cố ý lưuhistory,sandbox state,
outputở server
■ ClaudePlatform on AWS̸=
Bedrock: hạ tầng doAnthropicvận
hành;ZDR xin được
Lưu ý:Việt Nam không nằm trong danh sách region→ mặc định dữ liệurời lãnh thổ.
Nếu hồ sơ pháp lý buộc dữ liệu ở lại, lựa chọn còn lại làself-host — chính là quyết định ở
mụcsau.
Giảngviên (VinUni) AICB· Deployment 2026 49/ 84

---

### HardCap Thật Sự Nằm ỞĐâu?

Nhàcung cấp Hard cap native? Cơ chế Bẫy
OpenAI Có, phải bật thủ
công
HardSpendLimitở cảorglẫnproject,
trả429
“Spend alert” và trường monthly-
budgetcũ chỉbáo, không chặn
Anthropic Có,thật sự cứng Trần theo tier ($500 / $1.000 /
$200.000); chạm trần → API tạm
dừngtới tháng sau
Có spend limittheo Workspace, rút
từhạn mức chung của org
AWSBedrock KHÔNG Tự ráp: Budgets + CloudWatch →
Lambdathu hồi IAM
Circuitbreaker phảnứngsau ,không
phảiadmission control
LiteLLM Cótheothiết kế Virtual key max_budget → 429
BudgetExceededError
Đãcóissue bypasshoàntoàn ởmột
bảnrelease
Kếtluận
Enforcement của providerkhông đồng nhấtvà không phải lúc nào cũng hoạt động
→admissioncontrolphíabạnlàlớpduynhấtbạnkiểmsoát. “Cứng theo thiết kế” ̸=
“cứng ở version bạn đang deploy” — hãy tự test.
Giảngviên (VinUni) AICB· Deployment 2026 50/ 84

---

### 10

Scaling & Reliability
Agent MVP không cần Kubernetes — nhưng cần hiểu cơ bản về
scaling và reliability để hệ thống không chết khi có nhiều user
hơn

---

### HorizontalScaling — Scale Theo Concurrency,Không Phải CPU

Users Load
Balancer
Instance1
Instance2
Instance3
Shared
State(DB)
Lưu ý: Agent làI/O-bound: một instance có thể đầy request đang chờ LLM mà
CPUvẫnthấp. →Autoscaletheo concurrency/queuedepth (Knative,KEDAtheo
tínhiệuvLLM num_requests_running,RayServe target_ongoing_requests),không
theoCPU. Điều kiện tiên quyết: agentstateless,state ở DB/Redis.
Giảngviên (VinUni) AICB· Deployment 2026 51/ 84

---

### HealthChecks — 3 Loại Probe

3loại probe
■ Liveness—“còn sống?” Fail→
restartcontainer( GET /health )
■ Readiness—“sẵn sàng nhận
request?” Fail→gỡkhỏi LB,
KHÔNGrestart
■ Startup—cho boot chậm (load
weights);gate 2 probe kia đếnkhi
pass
Healthendpoint mẫu
GET /health trảvề:
■ status: “ok” / “degraded”
■ uptime: seconds
■ version: app version
■ dependencies: DB, vector store,
LLMreachable?
Lưuý: Livenessrestart,readinesschỉngắttraffic—cấuhìnhnhầmreadinessthành
liveness= restart loop vô ích.
Giảngviên (VinUni) AICB· Deployment 2026 52/ 84

---

### Zero-DowntimeDeploy & Graceful Shutdown

Step1
Startnew
instancev2
Step2
Healthcheck
passes
Step3
Routetraffic
tov2
Step4
Drain+ stop
v1(SIGTERM)
Lưu ý: Graceful shutdown cho agent:khi nhận SIGTERM, phảidrain request
đangchạydở(mộtagentturncóthểdài). Đặt terminationGracePeriodSeconds lớn
hơnworst-case agent turn,nếu không request bị cắt giữachừng.
Nângcao
Rainbow deployment(Anthropic): dịch traffic dần sang version mới nhưnggiữ cả
hai cùng chạy, để không cắt ngang agent đang chạy dở — vì agent là hệ thống
stateful chạy gần như liên tục. Argo Rollouts: shift traffic + AnalysisRun tự rollback.
Railway/Renderhỗ trợ rolling sẵn.
Giảngviên (VinUni) AICB· Deployment 2026 53/ 84

---

### LLMGateway / Router — MộtCửa, Nhiều Provider

Agent LLMGateway
(LiteLLM)
OpenAI
Anthropic
Local/ OSS
■ 1endpoint, format OpenAIchohàng trăm model —LiteLLM(tựhost, không markup) vs
OpenRouter(managed,phí nạp credit 5,5%)
■ Fallback& failover: modellỗi / rate-limit→tựnhảy nhóm dự phòng; load-balancenhiều
key,retry/backoff,cost tracking mộtchỗ
Vìsao cần
Router vượt trầnrate-limit của vendor bằng nhiều key/nhiều provider, và sống sót
khimột provider hỏng.
Giảngviên (VinUni) AICB· Deployment 2026 54/ 84

---

### CacheĐể Cắt Cost & Latency

Promptcaching (provider)
Tái dùng KV-cache củaprefix chung (sys-
temprompt, RAG context).
■ Anthropic: cache read∼0.1×(∼90%
rẻhơn), cần khai báo breakpoint;ghi
cache1.25 ×–2×
■ OpenAI:tựđộng vớiprefix ≥1024
token,cache read ∼0.1×(∼90%rẻ
hơn);từ GPT-5.6có thêmphíghi
cache1.25×
Semanticcache (của bạn)
Trả lại câu trả lời cũ cho câu hỏitương tự
vềnghĩa (soembedding).
■ GPTCache: lưu embedding query
trongRedis
■ Tránhgọi LLM lặp→cắtcả cost lẫn
latency
■ Cẩnthận: trả lờicũ có thể lỗi thời
Lưu ý:Prompt cacheso khớp prefix từng byte;semantic cacheso khớp ý nghĩa
—mạnh hơn nhưng có thể trảcâu cũ đã lỗi thời.
Giảngviên (VinUni) AICB· Deployment 2026 55/ 84

---

### 11

Deploy Model — Gọi API Hay Tự
Phục Vụ?
Trước hết: có tự host model không? Nếu có, phần sau giải thích
vì sao cost & latency lại như vậy— một sợi chỉ đỏ duy nhất:
giữ GPU bận, đừng phí KV cache

---

### Model: Gọi API HayTự Phục Vụ? —Quyết Định Deploy Thứ Hai

Bốnlực đẩy sang tự host
■ Residency/ compliance: dữ liệu
khôngđược rời lãnh thổ hoặcVPC
■ Sởhữu adapterfine-tune(Bedrock
CustomModel Importlàmmờ ranh
giới)
■ Kinhtế theo volume: chỉ thắng khi
GPUđủ bận (hoà vốn: Day 25);trần
nănglực khôngcòn là rào — slide
sau
Balực giữ ở hosted API
■ Khôngcó GPU-hour rảnh: hosted
trảtheotoken;tựhosttrảtheo giờ,kể
cảkhi rảnh
■ Bậcmua năng lực: Fastmode (2×),
ScaleTier (SLA99,9%)
■ Ngượclại: AzurePTUtínhtheogiờ
dùkhôngcótoken —đúngcáiTier0
tránhđược
Balớp, không phải hai
Hosted API → managed self-hosting(bạn mang weight, họ lo serving stack)→ tự dựng.
Câu hỏi không phải “model nào giỏi hơn” (Day 14) mà “tôi có muốn vận hành thêm một
serviceGPU không”.
Giảngviên (VinUni) AICB· Deployment 2026 56/ 84

---

### NếuTự Host: ChọnModel Mở Nào, Engine Nào

Modelmở đáng deploy (8/2026)
■ gpt-oss-120b —117Btổng / 5,1Bactive
(MoE),Apache-2.0, vừamộtGPU 80GBnhờ
MXFP4
■ gpt-oss-20b —chạy trong16GB:tầng phần
cứngphổ thông
■ Qwen3-235B-A22B—235B/22B, Apache-2.0
■ DeepSeek-V3.2-Exp—685B, MIT
■ KimiK2 —1T/32B, Modified MIT,thiết kế cho
agentictool-use
MoE: VRAM quyết bởi active params , không phải
tổng.
Enginechọn theo hình dạng tải
■ vLLM—mặc định đa phần cứng
(NVIDIA/ROCm/Intel/TPU),server
OpenAI-compatible
■ SGLang—khi prefix được dùng lạinhiều
(RadixAttention) →rấtđúng với agent
■ TensorRT-LLM—đỉnh trên NVIDIA, đổi lại
phảicompile engine riêng
■ llama.cpp+ GGUF—CPU/edge/consumer,
quantize1,5–8 bit
Quantization không thay nhau:GGUF (CPU/edge)
̸=AWQ/GPTQ(GPU) ̸=FP8(H100/Blackwell).
Lưu ý: Ship fine-tune bằngmulti-LoRA trên một base, không phải một GPU cho mỗi
adapter. Cơ chế bên trong engine, benchmark, sharding đa GPU: Day 20.
Giảngviên (VinUni) AICB· Deployment 2026 57/ 84

---

### TựHost = Bạn Có ThêmMột Service Phải Deploy

Vậnhành đổi luật
■ Coldstart không còn tính bằng
giây: nạp weight hàngchục GB→
phút
■ Readinessprobe phảiđợi weight
nạpxong, không chỉ đợi portmở
■ Autoscaletheo queuedepth,không
theoCPU
■ GPUrảnh vẫn tính tiền—ngược
hẳnđồng hồ idle-free của Tier0
Artifactdeploy có thêm trục thứtư
NhớbaartifactrollbackởmụcCI/CD— im-
age · prompt · model ID? Tự host thêm:
weight(repo+revision) ·địnhdạng/quan-
tization ·phiên bản engine. Hỏi trước khi
deploy: “rollback” ở đây nghĩa là rollback cái
nào?
Lưuý: Tựhostkhôngphảilà“bỏvendor”—là đổivendorlock-inlấycôngviệcvậnhành .
Mọi mục hôm nay (health check, scaling, rollback, cost guard) đều phải làm lại cho service
GPUnày.
Giảngviên (VinUni) AICB· Deployment 2026 58/ 84

---

### SợiChỉ Đỏ: GiữGPU Bận + Continuous Batching

Staticbatching
Cả batch chờ requestdài nhất xong →
GPU ngồi không khi các request ngắn đã
xong.
Continuous(in-flight) batching
Lên lịch lại batchmỗi bước decode: re-
questxongthìthayngayrequestmớivào.
Tácđộng
Orca(OSDI’22)giớithiệuiteration-levelscheduling,báocáotới 36.9×throughputso
với baseline ở cùng latency. Đây là “unlock” lớn nhất của GPU utilization khi serve
LLM.
Lưuý: Mọikỹthuậtsauphụcvụmộtý: khôngphíKVcache,GPUkhôngbaogiờ
rảnh—vì GPU-hourquyếtđịnh cost serve agent.
Giảngviên (VinUni) AICB· Deployment 2026 59/ 84

---

### PagedAttention— Quản KV Cache NhưOS Quản RAM

Mỗitoken sinh ra cần lưuKey/Value(KV cache). Cấp phát liền mạch→phânmảnh, phí bộ nhớ.
PagedAttention(vLLM,SOSP’23) chia KV cache thànhblockcố định, không liền mạch—y
nhưvirtual memory paging của hệđiều hành.
■ Gầnzerolãngphí KV →batchlớn hơn trong cùng VRAM
■ Chiasẻ KV giữa request (parallelsampling, beam) qua copy-on-write
■ vLLMbáo cáo2–4×throughputso với hệ trước ởcùng latency
Vìsao bạn quan tâm
KV cache là lý do context dàitốn bộ nhớvà vì sao prompt caching (slide trước) tiết kiệm
được— nó tái dùng đúngnhững block KV này.
Giảngviên (VinUni) AICB· Deployment 2026 60/ 84

---

### PrefixCaching + Speculative Decoding

Prefix/ prompt caching
Prefill của prefix chung tínhmột lần, dùng
lạicho nhiều request.
■ Prefillcủa prefix tínhmộtlần rồitái
dùng →đặtphần tĩnh(system,
few-shot,RAG) lênđầuprompt. (Giá
cache: mục Cache ở slide trước.)
Speculativedecoding
Model nháp nhỏ đề xuất 5–8 token, model
đíchxácminh song song.
■ Tậndụng GPU đang rảnh,khôngđổi
phânphối output
■ ∼2–3×giảmlatency; EAGLE-3 báo
cáotới ∼4.8×(Llama-3.3-70B)
Liênhệ thực tế
Haikỹthuậtnàylàlýdocùngmộtcâuhỏigửilần2(cachehit) rẻvànhanhhơn hẳn
—thiết kế prompt để tận dụng.
Giảngviên (VinUni) AICB· Deployment 2026 61/ 84

---

### DisaggregatedPrefill / Decode

Prefillpool
compute-bound
(xửlý prompt)
Decodepool
memory-bound
(sinhtoken)
KVcache
Prefill(đọc cả prompt, song song→
compute-bound)và decode (sinh từng token→memory-bandwidth-bound)có hồ sơ tài
nguyênkhác nhau →táchra 2 pool GPUscaleđộc lập.
■ DistServe(OSDI’24): tới 7.4×nhiềurequest hơn trong cùng SLO
■ Mooncake(Kimi, FAST’25): KV-cache-centric,>100Btoken/ngày
■ NVIDIADynamo (GTC 3/2025): prefill/decode là first-class, KV-awarerouter
Giảngviên (VinUni) AICB· Deployment 2026 62/ 84

---

### 12

CI/CD & Eval Gates
Deploy bằng tay sẽ quên bước, sẽ sai. Tự động hoá
build→push→deploy — và thêm lớpeval gateriêng của AI: chặn
deploy nếu chất lượng tụt

---

### Pipeline: Build→Push →Deploy →EvalGate

# .github/workflows/deploy.yml
steps:
- uses: actions/checkout@v4
# build + push image to GHCR (needs packages: write)
- uses: docker/build-push-action@v6
# scan image for CVEs, fail the build on high severity
- uses: aquasecurity/trivy-action@master
- run: promptfoo eval --fail-on-error # <- EVAL GATE
- run: railway up # deploy iff evals pass
Evalgate — lớp đặc trưngcủa AI
Agent non-deterministic → không thể chỉ dựa unit testexit 0 . Gate deploy theo
điểmeval ≥ngưỡng(promptfoo/DeepEval/Braintrust). ĐâylàcầunốitớiDay14
(Evaluation).
Giảngviên (VinUni) AICB· Deployment 2026 63/ 84

---

### EvalGate TrongThực Tế— Bốn Công Cụ, Một Khuôn

Côngcụ Cơchế gate Kếtquả trên PR
promptfoo promptfoo eval --fail-on-error ; chặt hơn: fail khi
stats.failures > 0
promptfoo-action comment pass/fail +
linkviewer
DeepEval assert_test()(khôngphải evaluate())—raisekhi
score <threshold
pytest-native,fail như test thường
Langfuse experiment-action chạytrên dataset có version Commentkết quả lên PR
Braintrust eval-action chặnmerge khi dưới ngưỡng Diffview sovới run của nhánh baseline
Lưu ý:Đừng pintemperature=0 : Anthropic deprecatetemperature/top_p/top_k từ Opus
4.7trởđi—setkhácmặcđịnhtrả 400. Mọiharnessđangpin temperature=0 sẽgãythẳng.
Mẫuđã hội tụ
Cả bốn công cụ đi tới cùng một chỗ: so vớirun của nhánh baseline, không chỉ so với một
ngưỡng tuyệt đối — ngưỡng tuyệt đối không phát hiện được “tụt 4 điểm nhưng vẫn trên
ngưỡng”. Phương pháp đánh giá → Day 14; quan sát production → Day 13.
Giảngviên (VinUni) AICB· Deployment 2026 64/ 84

---

### Shadow →Canary →100%— Ramp Cho Agent

Shadow
mirrortraffic, output BỎ ĐI
Canary5%
outputTHẬT tới user
Ramp
10 →25 →100%
■ Shadow(mirror): nhânđôitrafficsangversionmới, khôngbaogiờ trảoutputchouser. Rủi
rouser = 0.
■ Canary: địnhtuyến một% traffic thậtvà có trảoutput — bán kính thiệthại giới hạn.
■ Auto-rollbacklàprimitive có thật: Argo RolloutsAnalysisRun queryPrometheus theo lịch,
tựrollback khi metric fail.
Lưu ý: Thuế riêng của agent:shadow chạy cả hai version cho mọi request →
nhân đôi hoá đơn token. Với agent: shadowmột mẫu 5–10%, không phải 100%.
Vàshadowchỉantoànkhitoolcallcủaversionmới bịchặnsideeffect —nếukhông,
“khôngtrả output” vẫntrừtiền thật.
Giảngviên (VinUni) AICB· Deployment 2026 65/ 84

---

### RollbackKhông Nhất Thiết Là MộtLần Deploy

Baartifact, ba vòng đời
Một“bảndeploy”củaagentthựcragồm ba
thứrollback độc lập:
■ Container image
■ Promptversion
■ ModelID
Ba đường rollback khác nhau — đừng gộp
làmmột.
Mẫuđã hội tụ ở 6vendor
Prompt version là artifact bất biến,
content-addressed; một label di động
(prod) được trỏ lại để promote hoặc roll-
back.
→Rollbackprompt/modelxấu= dichuyển
một label, tính bằnggiây: không deploy,
khôngchạy CI.
Giới hạn: label chỉ cứu prompt/config —
codevà image vẫn đi quapipeline.
Lưuý: Nếupromptcủabạnnằmtrong .pyvàđicùngimage,bạn khôngcó rollbacknhanh
—bạn có một lần deploy.Táchprompt ra khỏi code làmột quyết định deploy.
Giảngviên (VinUni) AICB· Deployment 2026 66/ 84

---

### AgentLà Một Job TrongCI — Hợp Đồng Tối Thiểu

Hợpđồng gọi (callable contract)
■ Exit 0/khác 0đểscript rẽ nhánh;
--output-format json trả
total_cost_usd mỗilần chạy
■ Chếđộ bare: bỏ auto-discovery
hook/skill/MCP →CIchạy giống
nhaumọi máy
■ Đừngparse transcript nội bộ —
formatkhôngổn định
Aiđược kích hoạt, với quyềngì
■ Gatedanhtính người kích hoạt
trướcgate tool: writeaccess + phải là
người
■ Bẫy: trigger schedule khôngcó tác
giả → bỏ qua checkwrite-access
■ Automationmode: zerotool mặc
định;OIDCfederation thaysecret
APIkey tĩnh trong repo
Lưu ý: Job agent cóhai trục chi phí độc lập— compute-minute và token — phải chặn
cứngcảhai( --max-turns,workflowtimeout,concurrencylimit). Vàtách pha: cấpsecretcho
setupscript rồigỡtrước khivònglặp agent đọc nội dungkhông tin cậy.
Giảngviên (VinUni) AICB· Deployment 2026 67/ 84

---

### 13

Nâng Cao — Deploy Cấp Pro-
duction (tùy chọn)
Đưa 1 agent lên URL an toàn mới là 20% dễ. 80% khó là khi
agent bền bỉ, lặp lại, và hành động không hoàn tác được—
phần này phác qua những vấn đề đó

---

### AgentCó Nhiều “Hình Dạng” —Mỗi Cái Deploy Khác Nhau

Hìnhdạng Trigger Vòngđời Scale State
Chatbotđồng bộ userrequest giây(timeout) per-request sessionstore
Cron/ nền scheduler phút thấp,định kỳ jobstate
Batch dataset/queue dài,async fan-out per-item idempo-
tent
Autonomous“chạy mãi” loop liên tục vôhạn 1actor/goal phải sống qua
restart
Copilotnhúng in-appevent giây theoapp app/session
Ambient/ sự kiện webhook/event bursts,ngủ lâu scale-to-zero bềnqua giấc ngủ
Lưu ý:State-durability là trục phân biệt chính.“Autonomous chạy mãi” phá vỡ mô hình request/response→
buộc dùng durable runtime. Multi-agent: tốn∼15× token; nguyên tắc vàng “read thì song song được, write thì
không”— scale 1 agent trước,chỉ tách khi chạm trần thật.
Giảngviên (VinUni) AICB· Deployment 2026 68/ 84

---

### “JustRetry” Rất Nguy Hiểm VớiAgent

Webapp thường: lỗithì retry. Nhưng agent cósideeffect thật(gửimail, trừ tiền, đặt vé). Retry
mù= làmhai lần.
AgentA AgentB
(chargecard)
1. charge
2. reply chậm
3. timeout→retry →CHARGELẦN 2
Lưuý: Timeoutkhôngphânbiệt được“thấtbại”với“thànhcôngnhưngreplychậm” →caller
bắn lại side effect. Sự thật phũ phàng:không có “exactly-once”cho hành động ngoài hệ
thống— chỉ cóat-least-once+ consumer idempotent.
Giảngviên (VinUni) AICB· Deployment 2026 69/ 84

---

### IdempotencyKey — Và Cái BẫyRiêng Của Agent

Mẫuchuẩn (Stripe)
Client gửi headerIdempotency-Key (UUID)
kèmrequest mutating.
■ Serverlưu kết quả lầnđầutheokey
■ Retrycùng key →trảlại y nguyên (kể
cảlỗi đã cache)
■ Stripelà chuẩn de-facto,khôngphải
RFC(IETFdraft đã hết hạn)
Bẫyvới LLM agent
LLM không sinh lại tham số y hệtcho
cùngmộtýđịnh →hashnộidungthô trượt.
■ Cầndeduptheo ngữ nghĩa / ýđịnh
■ “Cùngintent”,khôngphải“cùngbytes”
■ Ailà trọng tài quyết 2hành động là
“một”?
Thựchành
Mọitoolcallcósideeffectnênmangmộtidempotencykeyổnđịnh(vd order_id),và
backenddedup bằng RedisSET NX +TTL.
Giảngviên (VinUni) AICB· Deployment 2026 70/ 84

---

### DurableExecution — Ghi Lại QuyếtĐịnh, Đừng Chạy Lại Model

Agentcrash ở bước 7 (sau4 tool call). Chạylại từ đầu =trảtiền LLM lần nữa+lặp tool đã ghi
đĩa. Durable execution giảiquyết bằng một mẹo tinh tế:
Journal+ replay
Temporal / Restate / Inngest: ghioutput của
LLMvàojournalởlầnđầu;khireplaythì đọc
lạibản ghi,KHÔNGgọi lại model.
■ “Phầnthông minh” không bao giờchạy
lại
■ Bướcđã xong được memoize, bỏqua
Lưu ý:LangGraph là ngoại lệ:check-
point ở mứcnode, không phải từng call
→ node chưa xong sẽchạy lại cả LLM
call. “Checkpoints̸=durableexecution”.
Lưu ý:“Exactly-once” của các framework thực ra là “exactly-oncetrên datastore của họ ”.
Hànhđộngrahệthốngngoàivẫncầnidempotent. Câuhỏihay: agentđược resumecócòn
“suynghĩ” không, hay chỉ đangđọclại quákhứ?
Giảngviên (VinUni) AICB· Deployment 2026 71/ 84

---

### Saga& Hành Động Không ThểHoàn Tác

Giữchỗ Trừtiền Gửivé
(pivot) Ghilog
compensate(undo)
■ Saga: mỗibước có một bướcbùtrừ (undo)— không có rollback tựđộng, phải tự code
■ Bướckhônghoàn tác được(gửimail/vé) =pivot: đặtcuối+gate bằnghumanapproval
■ Vấnđề: agent tựchọn thứ tự hành động —runtime có nêncấmnóxếp việc bất khả hoàn
trướcpivot?
Lưu ý:HITL nghịch lý: Temporal cho agentchờ 3 tuần tốn 0 compute— nhưng
giữ chỗ / báo giá / tokenvẫn hỏng dầnngoài đời. Resume một quyết định đã cũ =
durabilitythành gánh nặng.
Giảngviên (VinUni) AICB· Deployment 2026 72/ 84

---

### Security: Egress Là ĐiểmKiểm Soát

Đâylàmặt hạtầng củaantoàn(khácDay11—mặthànhvi). Toolcủaagentgọirangoài=kênh
ròrỉ.
Lethaltrifecta (Willison)
Ròrỉ data cần 3 thứcùnglúc:
■ datariêng tư
■ +nội dung không tin cậy
■ +kênh gửi ra ngoài
Bỏmột cái = chặn được.
4sự cố 2025, cùng 1cơ chế
EchoLeak · CamoLeak · GitLab Duo ·
AgentFlayer — đềurender ảnh/HTML tới
URLkẻtấncông vàđềufixbằng chặnren-
der/ giới hạn egress.
Lưu ý:Egress allowlist là phòng thủ mạnh nhất — nhưngkênh rò rỉ thường là kênh tin
cậy: CamoLeak tuồn data qua chính proxy Camo của GitHub. Không thể allowlist khỏi nhà
cungcấp bạn đang tin.
Giảngviên (VinUni) AICB· Deployment 2026 73/ 84

---

### Sandbox& Bài Học “Fail-Open”

OSnamespace
Docker+seccomp,
bubblewrap
Syscallintercept
gVisor,Modal
microVM
Firecracker· E2B
V8isolate
Cloudflare Workers
côlập mạnh hơn→(startupchậm hơn, gần như ngượclại)
Lưuý: CVE-2025-66479(ClaudeCode): cấuhình allowedDomains: [] (ýđịnh chặt
nhất)lại fail-open(mởtoangegress)vìcodecheck length > 0 . Ýđịnhantoànnhất
không biểu diễn được. → Ngữ nghĩa mặc định CHÍNH LÀ thuộc tính bảo mật
(fail-closed,không phải fail-open).
Nhãn đúng 2026: Cloudflare Sandboxes (GA 13/4/2026) chạy trênContainers,
khôngphải V8 isolate — V8 isolatechỉ đúng choWorkers.
Giảngviên (VinUni) AICB· Deployment 2026 74/ 84

---

### Least-Privilege— Mỗi Agent Một DanhTính

Rủiro
■ OWASPLLM06Excessive Agency:
quánhiều quyền →hànhđộng phá
hoại
■ Confuseddeputy: agent bị lừadùng
quyềncủa nó cho kẻ khác
■ 1“god-key” chung = 1 điểmsụp đổ
Phòngthủ
■ Mỗiagent mộtidentityriêng,scope
hẹp
■ Tokenngắnhạn,theo từng task
■ Audience-boundtoken (MCP OAuth
2.1)
■ VD:Microsoft Entra Agent ID
Lưu ý: Khoảng cách thực tế:∼91% tổ chức chạy agent ở production, nhưng chỉ
∼10% quản chúngnhư một danh tính. Per-agent identity ở quy mô lớn là bài toán
vậnhành chưa được giải tốt.
Giảngviên (VinUni) AICB· Deployment 2026 75/ 84

---

### DanhTính Cho Agent — SPIFFEVà Agent Identity

Cơchế đang thành chuẩn
Service account không đủ: agent phù du,
bán kính lớn, key chung không truy vết
được.
■ SPIFFE(CNCF):X.509SVID ngắn
hạn,có attestation.
■ GoogleAgent Identity(4/2026):
principalhạngnhất,tách khỏi human
lẫnservice account; cert xoay vòng,
hạn24h.
Mộtagent phải xác thực về4 hướng
■ Tớidịchvụ cloud: bound token gắn
cert
■ Tớitool/MCPngoài: API key /OAuth
■ Tớitài nguyêncủauser: 3-legged
OAuth;tới agentkhác: mTLS+
DPoP
Lưuý: OAuth2.1thuần khôngdiễnđạtđược “agent nàohànhđộngthayusernày”. Draft
làdraft —nhớ Idempotency-Key: thiếtkế đểthayđược cơchế uỷ quyền.
Giảngviên (VinUni) AICB· Deployment 2026 76/ 84

---

### 14

Deployment Checklist
Một trang để soi trước khi bấm deploy — gói lại mọi thứ đã học
hôm nay

---

### ProductionReadiness Checklist

Container,Deploy & Agent
□ Multi-stage+ uv, <500MB,non-root
□ .dockerignore +scan CVE (Trivy)
□ PublicURL + HTTPS hoạt động
□ Envvars (không hardcode secret)
□ Streaming(SSE) cho response dài
□ Stateexternalized (Redis/Postgres)
Security,Cost & Reliability
□ Auth(API key / JWT)
□ Ratelimit +spendingcap
(admissioncontrol)
□ Per-project/per-tenantbudget
□ /health(liveness+ readiness)
□ Gracefulshutdown (drain)
□ Rollbackplan <2phút
□ Pinmodel ID+tắt auto-upgrade
□ Router/fallbackkhi provider lỗi
Giảngviên (VinUni) AICB· Deployment 2026 77/ 84

---

### HoạtĐộng: Agent CủaBạn Deploy Ở Đâu? — 20 Phút

Bước1 — Chọn một usecase
■ Chatbotbánhàng—demosau1tuần
■ Agentnghiên cứu — 45 phút/tácvụ
■ Trợlý ngân hàng — datakhông rời
VN
■ Hoáđơn — 10 user,2 lần/ngày
■ Apphọc — 100k user,dồn buổi tối
■ Hoặc: agent của chínhnhóm bạn
Bước2 — Trìnhbày(tự do)
Chỉbắtbuộc 2 điều:
1. Deployởđâu?
2. VÌSAO —ràng buộc nào quyết
định?
Vẽsơđồ,slide,haynóimiệng— không
cómẫu.
Lưuý: “Chúngtôi chọn vì .” Viếtđược câunày là xong.
Giảngviên (VinUni) AICB· Deployment 2026 78/ 84

---

### 15

Phụ Lục Thực Hành — Lệnh &
Code
Gói lại thành thứ gõ được ngay: lệnh deploy thật, và một cost-
guard tối thiểu — để rời lớp học là deploy được

---

### DeployThật — Cloud Run &Railway

# A) Google Cloud Run: build from source, then deploy
gcloud run deploy agent-svc -- source . \
--port 8080 --concurrency 8 --memory 1Gi \
--region asia-southeast1 --allow-unauthenticated \
--set-env-vars MODEL_ID=claude-...,MAX_USD_PER_REQ=0.05 \
--set-secrets ANTHROPIC_API_KEY=anthropic-key:latest
# B) Railway: deploy + set environment variables
railway up # streams build + deploy logs
railway variables -- set "MODEL_ID=... " \
--set "ANTHROPIC_API_KEY= sk-..."
Lưuý: --concurrencyđểthấpchoagent: mỗirequestgiữmộtconnectionstreaming
dài. Secret tiêm qua --set-secrets / Variables tab —không bao giờnhét vào
image.
Giảngviên (VinUni) AICB· Deployment 2026 79/ 84

---

### Cost-GuardTối Thiểu — Chặn TrướcKhi Gọi

MAX_USD = float(os.environ["MAX_USD_PER_REQ"]) # e.g. 0.05
def guard(messages, model, user_id):
in_tok = count_tokens(messages, model) # count tokens
est = in_tok/1e6*IN_PRICE + MAX_OUT/1e6*OUT_PRICE
if est > MAX_USD: # admission control
raise BudgetExceeded(f"${est:.3f} > ${MAX_USD}")
metrics.tag(user=user_id, feature= "chat", usd=est)
return est
3đòn bẩy FinOps
Tag mọi call, đếm token có thẩm quyền,ép budget trước khi gọi LLM. Nhớ: alert
củaprovider là phản ứngsau;admission control chặntrước.
Giảngviên (VinUni) AICB· Deployment 2026 80/ 84

---

### 16

Hands-on & Key Takeaways
Mục tiêu cuối cùng rất cụ thể: agent có public URL, ai cũng truy
cập được, có health check, có basic auth, có cost guard

---

### Lab12: Containerize &Deploy

Mụctiêu lab
Đónggói agent thành container,deploylên cloud, và có public URLhoạt động.
1. ViếtDockerfile (multi-stage +uv,slim base, non-root,<500MB)
2. Build& test container locally:docker build → docker run →scanbằng Trivy
3. Thêmstreaming endpoint (SSE) + healthcheckGET /health
4. Deploylên Railway hoặc Render: connect repo→setenv vars →deploy
5. Thêmbasic auth (API key) +một rate limit / spending guardđơn giản
6. Demo: gửi request tớipublic URL, nhận response streaming từagent
Giảngviên (VinUni) AICB· Deployment 2026 81/ 84

---

### BlueprintCần Nộp

Container
■ Dockerfile(multi-stage, uv,
<500MB)
■ docker-compose.yml+
.dockerignore
■ Healthcheck + streaming endpoint
■ Trivyscan sạch (no high CVE)
Deployment
■ PublicURL hoạt động (HTTPS)
■ Envvars đúng cách (không
hardcode)
■ Basicauth (API key) + costguard
■ Demorequest/response streaming
Lưu ý: Không cần enterprise-grade. Điều cần chứng minh là bạnbiết cách đưa
agenttừ localhost lên cloud,nó hoạt động, vàkhôngđốt tiền.
Giảngviên (VinUni) AICB· Deployment 2026 82/ 84

---

### Tổngkết — Key Takeaways

Nhữngý chính cần nhớtrướckhi sang bài tiếp theo
1 Cùngcỗmáy,kháccáihộp: shipnhưthường—nhưng thetest (evalgate), thebill (token),
thedependency (model)đều bị định nghĩa lại.
2 Container 2026:multi-stage + uv + slim/distroless, non-root, scan CVE; SSE + externalize
state.
3 Chạyởđâu=quyếtđịnhdeploy: server-sidemặcđịnh;“client-side”cầnBFFproxy;keyless
chỉkhi on-device.
4 Platform theo timeout, scale theo concurrency;router failover + cache cắt cost. Budget
KHÔNGtựchặn →admissioncontrol + eval gate trongCI.
5 Đừng mặc định:framework và runtime làhai tầng tách rời; “model là API ngoài” làlựa
chọn,không phải định luật.
Giảngviên (VinUni) AICB· Deployment 2026 82/ 84

---

### Tiếptheo & Bài tập

Monitoring, Logging & Observabil-
ity
“Agent deploy xong, 3 ngày sau: la-
tency tăng gấp đôi, cost tăng 300%.
Bạn không biết cho đến khi user phàn
nàn. ”
■ Đọctrước: LangSmith hoặc
Langfusequickstart (20 phút)
■ Chuẩnbị: agentdeployedtừLab
12cần có endpoint để gắn
monitoring
■ Suynghĩ: metrics nàoquan
trọngnhất cho AI agent trên
production?
Giảngviên (VinUni) AICB· Deployment 2026 83/ 84

---

### TàiLiệu Tham Khảo

1. Astral, Using uv in Docker —docs.astral.sh/uv/guides/integration/docker/. Multi-stage buildhiện đại
choPython.
2. GoogleCloud, Cloud Run request timeout & concurrency —cloud.google.com/run/docs. 60 phútmax,
concurrency80/1000.
3. ModelContext Protocol, Transports & Authorization ( 2026-07-28)—modelcontextprotocol.io.
StreamableHTTP stateless+OAuth 2.1 + security bestpractices.
4. OWASP, Top 10 for LLM Applications 2026 (3/8/2026;75% vote + 25% từ6.639 sự cố thật) &Top 10
for Agentic Applications 2026 —genai.owasp.org. LLM10; ASI03/ASI04.
5. AdamWiggins, The Twelve-Factor App —12factor.net. FactorVI (stateless processes).
Giảngviên (VinUni) AICB· Deployment 2026 84/ 84

---

### Hỏi& Đáp

Từ hôm nay, agent không còn chỉ chạy trên máy bạn. Nó đã là một
service thật sự — có URL, có bảo vệ, và không đốt sạch ngân sách.