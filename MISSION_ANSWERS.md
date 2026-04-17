# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. **Hardcoded secrets trong code**  
   `develop/app.py` đặt API key trực tiếp trong source (`OPENAI_API_KEY = "sk-hardcoded-demo-key"`), dễ lộ key khi push GitHub.

2. **Hardcoded hạ tầng (DB URL) trong code**  
   `DATABASE_URL` bị cứng trong file, khó đổi theo môi trường dev/staging/prod.

3. **Không có config management chuẩn**  
   `DEBUG`, `MAX_TOKENS` được gán cứng (`True`, `500`) thay vì quản lý tập trung từ environment/config object.

4. **Log lộ thông tin nhạy cảm**  
   Có `print` key (`print(f"[DEBUG] Using key: {OPENAI_API_KEY}")`) nên có rủi ro bảo mật nghiêm trọng.

5. **Không có health/readiness endpoint**  
   Bản develop không có `GET /health`, `GET /ready`, khiến cloud platform khó kiểm tra trạng thái sống/sẵn sàng.

6. **Bind host chỉ localhost**  
   `host="localhost"` làm app chỉ truy cập được trên máy local, không phù hợp container/cloud.

7. **Port hardcode**  
   `port=8000` không đọc từ biến `PORT`, dễ lỗi khi deploy trên platform inject port động.

8. **Reload/debug mode bật cứng**  
   `reload=True` không phù hợp production (tốn tài nguyên và hành vi không ổn định khi scale).

### Exercise 1.3: Comparison table

| Feature | Develop (❌) | Production (✅) | Why Important? |
|---------|--------------|----------------|----------------|
| Config | Hardcode trực tiếp trong `app.py` | Tập trung ở `config.py`, đọc từ env | Dễ đổi theo môi trường, đúng 12-factor |
| Secrets | Có key cứng trong code, còn log ra màn hình | Đọc từ env (`OPENAI_API_KEY`, `AGENT_API_KEY`) | Tránh lộ secrets, an toàn khi public repo |
| Port/Host | `localhost:8000` hardcode | `HOST` + `PORT` từ env (mặc định `0.0.0.0`) | Chạy được trên Docker/Railway/Render |
| Logging | `print()` tự do, không chuẩn hóa | Structured JSON logging (`logging` + `json`) | Dễ quan sát/trace trên hệ thống log tập trung |
| Health checks | Không có | Có `GET /health` và `GET /ready` | Platform dùng để restart/routing đúng |
| Request handling | `/ask` đơn giản, thiếu guardrails | Validate input + log chuẩn | Giảm lỗi runtime, dễ debug |
| Shutdown behavior | Không xử lý vòng đời rõ ràng | Có lifespan + xử lý SIGTERM graceful | Tránh rớt request khi scale down/redeploy |
| Cloud readiness | "Works on my machine" | Thiết kế sẵn cho production | Đảm bảo deploy ổn định, dễ mở rộng |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. Base image: `python:3.11` (develop image)  
2. Working directory: `/app`  
3. App expose port: `8000`  
4. Start command: `CMD ["python", "app.py"]` (develop) và `CMD ["uvicorn", "app.main:app", ...]` (production-ready)

### Exercise 2.3: Image size comparison

- Develop: `1.66 GB` (image `agent-develop`)  
- Production: `279 MB` (image `my-agent`)  
- Difference: khoảng `83.2%` nhỏ hơn (tính theo công thức `(Develop - Production) / Develop * 100`)

Nhận xét: image production nhẹ hơn rõ rệt nhờ dùng `python:3.11-slim` và multi-stage build, giúp pull/deploy nhanh hơn và tiết kiệm tài nguyên.

## Part 3: Cloud Deployment

_To be completed_

## Part 4: API Security

_To be completed_

## Part 5: Scaling & Reliability

_To be completed_
