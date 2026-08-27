# batch02 day12 cloud services and deployment 16.31.52

**File gốc:** `Phase_1_COMP2010\D25_Day12-cloud-services-and-deployment\batch02-day12-cloud-services-and-deployment 16.31.52.md`

---

### AICB-P1  ·  NGÀY 12  ·  VINUNIVERSITY 2026

Cloud Infrastructure & Deployment
Đưa Agent Lên Cloud

---

### "Bạn demo cho sếp thấy agent chạy trên laptop.

Sếp hỏi: khi nào 100 người dùng được?
Giữ câu hỏi này trong đầu khi học bài hôm nay.

---

### Nội Dung Bài Học

01 Hạ Tầng Cloud có những gì?
02 Từ LocalHost đến Production
03 Docker & Containerization
04 API gateway & security
05 Scaling & reliability
06 Cloud deployment options
07 Lab 12 + deliverable
08 Preview Day 13

---

### Mục Tiêu Ngày 12

2 Hiểu gap dev → production: dependencies, config, secrets, networking
3 Viết Dockerfile đúng cách: đóng gói agent thành container < 500 MB
4 So sánh cloud options: Railway, Render, AWS ECS, Serverless
5 Thiết kế API gateway: authentication, rate limiting, cost protection
6 Deploy lên cloud: agent có public URL hoạt động được
1 Hiểu về Cloud Infrastructure: Cloud Services, AI Architecture

---

### Deliverable Cuối Ngày

Agent đã được containerize và deploy lên cloud, có health check endpoint, basic authentication, và accessible qua public URL
Container
·  Dockerfile (multi-stage, < 500 MB)
·  docker-compose.yml + .dockerignore
·  Health check endpoint /health
Deployment
·  Deployed instance: Railway / Render
·  Env vars đúng cách (không hardcode)
·  Basic auth (API key header)
Demo
·  Public URL ai cũng truy cập được
·  Request → Response hoạt động
·  Production readiness check
✅

---

### 01HẠ TẦNG CLOUD

CÓ NHỮNG GÌ?

---

### Cloud Infrastructure là gì?

---

### Cloud Infrastructure gồm những gì?

---

### Cloud Infrastructure gồm những gì?

---

### 3 Tầng Cloud Services

---

### High Level Architecture của AI Agent

6 Layer của 1 Ứng dụng AI hiện đại

---

### High Level Architecture của AI Agent

6 Layer của 1 Ứng dụng AI hiện đại

---

### Big 3 Cloud Providers

AWS, Google Cloud và Azure chiếm hơn 65% thị phần cloud toàn cầu. Mỗi nhà
cung cấp có điểm mạnh riêng nhưng core services đều tương đương nhau.

---

### 2 Cloud Providers Nổi Bật

Railway & Render là hai nền tảng nổi bật trong thế hệ PaaS mới — đơn giản
hơn AWS, nhanh hơn Heroku, phù hợp cho startups, MVPs và AI apps.

---

### 02TỪ LOCALHOST

ĐẾN PRODUCTION
Agent chạy trên máy mình ≠ Agent chạy cho 100 người

---

### Recap: "It Works On My Machine"

✅  11 Ngày Đã Build
·  LLM API + prompt engineering
·  RAG pipeline grounded
·  Multi-agent + MCP
·  UX + trust layer
·  Guardrails + safety
⚠  Nhưng Đang Chạy Trên...
·  localhost:8000
·  API keys trong .env file
·  Chỉ 1 user (chính mình)
·  Không health check
·  Tắt laptop = agent chết
📌  "It works on my machine" — câu nói nổi tiếng nhất lịch sử software engineering. Day 12 giải quyết đúng vấn đề này.

---

### 6 Giai Đoạn từ Localhost đến Production

---

### 6 Giai Đoạn từ Localhost đến Production

---

### 6 Giai Đoạn từ Localhost đến Production

---

### 6 Giai Đoạn từ Localhost đến Production

---

### So Sanh Môi Trường

---

### 6 Giai Đoạn từ Localhost đến Production

---

### Pre Production Checklist

---

### 12-Factor App — Áp Dụng Cho AI Agent

1Config in env
Không hardcode API keys.
Dùng os.getenv() cho mọi config.
2Stateless processes
Agent không giữ session
trên instance memory.
3Port binding
Đọc PORT từ env var.
Railway/Render inject tự động.
4Dev/prod parity
Giữ gap nhỏ nhất giữa
dev, staging, production.
Production Checklist (MVP)
✅  Secrets trong env vars (không trong code)
✅  Health check endpoint: GET /health
✅  Structured logging (JSON format)
✅  Graceful shutdown (handle SIGTERM)
Đừng cố học hết 12 factors ngay. 4 cái trên đủ cho MVP deployment.

---

### 03DOCKER - ĐÓNG GÓI AGENT THÀNH

CONTAINER
Build once — run anywhere

---

### Docker & Docker Compose

---

### Docker & Docker Compose

---

### Docker & Docker Compose

---

### Docker Commands

---

### Docker & Docker Compose

---

### 04API GATEWAY

& SECURITY
Bảo vệ agent trước khi request đến được logic

---

### API GATEWAY & SECRITY

---

### API GATEWAY CORE FEATURE

---

### API GATEWAY CHỌN TOOL NAO

---

### 05SCALING

& RELIABILITY
Agent không chết khi có 100 người dùng cùng lúc

---

### SCALING & RELIABILITY

---

### SCALING & RELIABILITY

---

### SCALING & RELIABILITY

---

### SCALING & RELIABILITY

---

### SCALING & RELIABILITY

---

### SCALING & RELIABILITY

---

### 04CLOUD

DEPLOYMENT OPTIONS
Chọn platform dựa trên traffic, cost, control, compliance

---

### 3 Tier Deployment

Tier 1
Railway  /  Render  /  Fly.io
·  < 10 phút deploy
·  Free tier có sẵn
·  Zero config
·  MVP / Demo / Học
BẮT ĐẦU ĐÂY
Tier 2
AWS ECS  /  GCP Cloud Run
·  Enterprise-grade
·  Auto-scaling
·  CI/CD pipeline
·  Production ready
KHI CẦN SCALE
Tier 3
Kubernetes  (Self-managed)
·  Full control
·  Complex ops
·  Large-scale
·  Multi-cloud
KHI LỚN HƠN

---

### So Sánh Platform

Railway
Render
Cloud Run
Lambda
Deploy time
< 5 phút
✅
< 10 phút
10-15 phút
15-20 phút
Pricing
Usage-based
Free tier
Per-request
Per-invoke
Scaling
Auto
✅
Auto
✅
Auto
✅
Auto
✅
Complexity
🟢 Thấp
🟢 Thấp
🟡 Trung bình
🟡 Trung bình
Best for
MVP, demo
Side project
Production
Low-traffic
⚠  Serverless cold start 5-15s. Với AI agent cần response nhanh, container-based (Railway/Render) thường tốt hơn Lambda.

---

### Railway — Deploy Trong 5 Phút

1 Kết nối GitHub repo
railway login && railway init
2 Railway tự detect Dockerfile / Nixpacks
3 Set environment variables
railway variables set OPENAI_API_KEY=sk-...
4 Click Deploy (hoặc railway up)
railway up
5 Nhận public URL
🎉
railway domain  →  your-app.up.railway.app
railway.toml
[build]
builder = "NIXPACKS"
[deploy]
startCommand = "uvicorn app:app
--host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"
Đặt PORT=8000 trong env vars. Railway inject PORT tự động — agent PHẢI đọc os.getenv('PORT').

---

### 06GITHUB PROJECT

WALKTHROUGH
Ví dụ cơ bản + chuyên sâu cho từng section

---

### Project Structure — day12-agent-deployment/

01
01-localhost-vs-production/
basic/: Anti-patterns  ·  advanced/: 12-Factor compliant
02
02-docker/
basic/: Single-stage  ·  advanced/: Multi-stage + Compose + Nginx
03
03-cloud-deployment/
railway/  ·  render/  ·  advanced-cloud-run/ (CI/CD)
04
04-api-gateway/
basic/: API Key  ·  advanced/: JWT + Rate Limiter + Cost Guard
05
05-scaling-reliability/
basic/: Health checks  ·  advanced/: Stateless + Redis + 3 replicas
06
06-lab-complete/
Production-ready agent  ·  check_production_ready.py

---

### Key Files — Localhost vs Production

Section 4: API Gateway
basic/app.py
→ API Key auth (30 lines)
→  nâng cấp
advanced/auth.py + rate_limiter.py + cost_guard.py
→ JWT + Sliding Window + Budget cap
Section 5: Scaling
basic/app.py
→ /health + /ready + graceful shutdown
→  nâng cấp
advanced/app.py + docker-compose.yml
→ Redis sessions + 3 replicas + Nginx LB
utils/mock_llm.py  →  Dùng chung cho tất cả sections (không cần API key thật)

---

### LABLAB 12

CONTAINERIZE & DEPLOY
Mục tiêu: agent có public URL ai cũng truy cập được

---

### Lab 12 — Các Bước Thực Hiện

1 Viết Dockerfile
Multi-stage build, non-root user, HEALTHCHECK. Target < 500 MB.
2 Build & Test Local
docker build -t my-agent .  →  docker run -p 8000:8000 my-agent
3 Deploy Railway / Render
Connect GitHub → Set env vars → Deploy → Nhận public URL
4 Health Check Endpoint
GET /health trả về: status, uptime, version, dependencies
5 Basic Authentication
API Key header: X-API-Key. Reject 401 nếu thiếu hoặc sai key.
6 Demo Request → Response
curl -H 'X-API-Key: ...' -X POST https://your-url/ask -d '{"question":"..."}'

---

### Blueprint Cần Nộp

Không cần enterprise-grade. Cần chứng minh: biết đưa agent từ localhost lên cloud và nó hoạt động.
📦  Container
☁  Deployment
✅  Dockerfile
Multi-stage build, < 500 MB, non-root user
✅  docker-compose.yml
Agent + dependencies
✅  .dockerignore
Loại bỏ .env, __pycache__, venv/
✅  GET /health
Trả về status + uptime + version
✅  GET /ready
Readiness check
✅  Public URL
https://your-app.up.railway.app
✅  Env vars
Secrets trong env, không hardcode
✅  API Key auth
X-API-Key header, 401 nếu thiếu
✅  Demo
Request → Response qua public URL
✅  check_production_ready.py
20/20 checks pass
✅

---

### Key Takeaways

1 Container = "ship anywhere"
Docker giải quyết "it works on my machine". Multi-stage + slim image → agent < 500 MB.
2 Start simple, migrate later
Railway/Render cho MVP (< 10 phút). Migrate AWS/GCP khi business thật sự cần scale.
3 Security from day 1
Secrets management + HTTPS + rate limiting + spending caps. Setup trước khi có user thật.
4 Health check + rolling deploy = always available
Stateless design + Redis cho phép scale bằng cách thêm instances bất kỳ lúc nào.

---

### Preview — Day 13: Monitoring & Observability

"Agent deploy xong, 3 ngày sau: latency tăng gấp đôi, cost tăng 300%.
Bạn không biết cho đến khi user phàn nàn."
📊 Metrics
Latency, throughput, error rate, token usage
📝 Logging
Structured logs → Loki / Datadog / CloudWatch
🔍 Tracing
LangSmith / Langfuse cho LLM traces
🚨 Alerting
PagerDuty / Slack alert khi anomaly detected
Chuẩn bị: Đọc LangSmith hoặc Langfuse quickstart (20 phút) trước buổi sau.

---

### Từ hôm nay, agent không còn chỉ chạy trên máy bạn.

Nó đã là một service thật sự.
AICB-P1  ·  Ngày 12  ·  VinUniversity 2026