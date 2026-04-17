# Day 12 — Deployment Submission Repository

> **AICB-P1 · VinUniversity 2026**  
> Repository này đã được tinh gọn để tập trung cho phần nộp cuối Day 12.

---

## Cấu Trúc Hiện Tại

```
day12_ha-tang-cloud_va_deployment/
├── 06-lab-complete/               # Production-ready agent (source chính để chấm)
├── DEPLOYMENT.md                  # Thông tin deploy cloud
├── MISSION_ANSWERS.md             # Bài làm mission answers
├── DAY12_DELIVERY_CHECKLIST.md    # Checklist nộp bài
└── README.md
```

---

## Yêu Cầu Môi Trường

```bash
python 3.11+
docker + docker compose
```

---

## Chạy Local (Docker)

```bash
cd 06-lab-complete
docker build -t my-agent .
docker run --rm -p 8000:8000 my-agent
```

Kiểm tra:

```bash
curl http://localhost:8000/health
```

---

## Deploy Cloud

- Deploy chính: Render
- Public URL hiện tại và test command được ghi trong `DEPLOYMENT.md`

---

## Ghi Chú Nộp Bài

- Source code dùng để chấm nằm trong `06-lab-complete/`.
- Các section học mẫu (`01` đến `05`) đã được loại bỏ khỏi repo nộp để tránh nhiễu.
