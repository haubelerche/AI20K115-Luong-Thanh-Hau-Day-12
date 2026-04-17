# Deployment Information

## Public URL
https://ai-agent-production-nn44.onrender.com

## Platform
Render (primary), Railway (alternative config available).

## Deployment Status
- [x] `06-lab-complete/render.yaml` available
- [x] Render env vars aligned with app config (`MONTHLY_BUDGET_USD`, `RATE_LIMIT_PER_MINUTE`)
- [x] Containerized app verified locally (`my-agent`, `GET /health` returns 200)
- [x] Public service URL generated from cloud platform

## Test Commands

### Health Check
```bash
curl https://ai-agent-production-nn44.onrender.com/health
# Expected: {"status":"ok", ...}
```

### API Test (with authentication)
```bash
curl -X POST https://ai-agent-production-nn44.onrender.com/auth/token \
  -H "X-API-Key: <AGENT_API_KEY>"

curl -X POST https://ai-agent-production-nn44.onrender.com/ask \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

## Environment Variables Set (Required)
- `PORT` (auto-injected by Render)
- `REDIS_URL`
- `AGENT_API_KEY`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_EXP_MINUTES`
- `RATE_LIMIT_PER_MINUTE`
- `MONTHLY_BUDGET_USD`
- `OPENAI_API_KEY` (optional if using mock in learning mode)

## Final Deploy Steps
```bash
# 1) Push latest code to GitHub
# 2) Render Dashboard -> New -> Blueprint
# 3) Select repository root, Render reads 06-lab-complete/render.yaml
# 4) Set secret env vars (OPENAI_API_KEY if needed)
# 5) Deploy and copy public domain from Render service page
```

## Screenshots
- [ ] Deployment dashboard
- [x] Service running (`sucessful-deploy-render.png`)
- [ ] Health/API test results
