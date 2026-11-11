# Báo cáo cá nhân — Trịnh Tuấn Phong (2A202603781)

## 1. Thông tin thành viên

- Họ tên: Trịnh Tuấn Phong
- MSSV: 2A202603781
- Email: 26ai.phongtt2@vinuni.edu.vn

## 2. Phần việc phụ trách

- CP1: chạy baseline v0 và phân tích 5 case FAIL (R08, R10, R11, R12, R13).
- CP2: `artifacts/system_prompt.md` v1–v3 và `artifacts/tools.yaml` v3 (description 10 tool, convention args, boundary `send`).
- CP3: 2 tool mới `wiki` + `hackernews` (`tool.py`, `TOOL.md`, đăng ký `TOOL_FUNCTIONS`, khai báo `tools.yaml`, 7 unit test offline).
- CP4: viết 6 case eval nhóm ban đầu; sau merge phụ trách các case G02, G03, G05, G06, G07, G08 trong bộ 10 case.
- CP5: UI Streamlit `app.py`, live chat 4 lượt, transcript.
- Hợp nhất merge `origin/main` → `trinhtuanphong` (commit `ec89ecf`) và sửa phần dư conflict (v4, v5).

## 3. Đóng góp cụ thể

- Vòng lặp evidence-driven trên base eval: v0 **0.75** → v1 **0.90** (bỏ chỉ dẫn đoán + rule `clarify`) → v2 **1.00** (Scope + Sending boundary) → v3 **1.00** (viết lại description 10 tool, thêm RAPIDAPI cho `social_search`).
- Bảng B2 (failure analysis v0, 5 case R08/R10/R11/R12/R13) trong `report/team/group_report.md`.
- 2 tool mới chạy offline/không cần API key, validate input trước khi gọi mạng, mọi lỗi trả error dict thay vì raise:
  - `wiki`: Wikipedia REST, tóm tắt N câu ≤1200 ký tự, `lang` en/vi.
  - `hackernews`: Algolia HN Search, đổi endpoint theo `sort`, fallback URL item page, bỏ HTML cho Ask HN.
- Hợp nhất sau merge: `tools/__init__.py` đủ 16 tool; `tools.yaml` 16 entry (bỏ key trùng, 2 entry `lookup`, khai báo thêm `extract_claims`/`deduplicate_items`); `tests/test_tools_todo.py` dedupe + bổ sung test của 2 tool bị mất; `data/eval_group.json` chốt 10 case (5 single + 5 multi); `version_log.csv` một chuỗi v0–v5.
- Chạy lại toàn bộ bằng chứng: `pytest` **128 passed, 0 skipped, 0 failed**; base v4/v5 **19/20 = 0.95**; group v5 **10/10 = 1.00**.
- Bắt và sửa 1 bug thật trong `tools/send/tool.py`: khi thiếu `TELEGRAM_BOT_TOKEN`, message lỗi bị chèn `***` vào giữa từng ký tự do `str.replace(token or "", "***")`; sửa thành chỉ mask khi token không rỗng, giữ lại test làm regression test.

## 4. Bằng chứng

- File:
  - `starter_v0/runs/v0_B_base_openrouter_20261110T172631463565.json` … `v3_B_base_openrouter_20261110T183447099371.json`
  - `starter_v0/runs/v4_B_base_openrouter_20261111T121633780906.json`, `starter_v0/runs/v4_B_group_openrouter_20261111T121652684089.json`
  - `starter_v0/runs/v5_B_base_openrouter_20261111T121821609563.json`, `starter_v0/runs/v5_B_group_openrouter_20261111T121840551842.json`
  - `starter_v0/transcripts/v3_openrouter_20261110T232722798444.transcript.json` (4 lượt: tin tức → hỏi lại account → `timeline(screenname="sama")` → `clarify(response_type="yes_no")`)
  - `starter_v0/tools/wiki/`, `starter_v0/tools/hackernews/`, `starter_v0/tools/__init__.py`
  - `starter_v0/tests/test_tools_todo.py` (36 test, trong đó 7 test cho 2 tool của tôi)
  - `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`
  - `starter_v0/analysis/base_runs.csv` (404 dòng, sinh bằng `scripts/parse_runs.py`)
  - `starter_v0/app.py`, `starter_v0/requirements.txt`
- Preflight: `OK provider=openrouter model=openai/gpt-4o-mini` / `tool=timeline` / `args={'screenname': 'sama', 'limit': 1}`.
- Commit: `58866ed` (CP1–CP5), `4e73bcb` (sửa email báo cáo), `ec89ecf` (merge `origin/main`); các commit sửa merge nằm sau `ec89ecf` trên nhánh `trinhtuanphong`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng trợ lý AI để audit TODO, soạn unit test và rà báo cáo; dùng OpenRouter `openai/gpt-4o-mini` để chạy eval/chat. Tự kiểm tra bằng cách đọc trực tiếp `results[*].result.failures` trong run JSON, chạy lại `python -m pytest -q -rs`, chạy `chat.py`/UI và xem tool call thật in ra.

## 5. Tự đánh giá

- Hoàn thành CP1–CP5 với bằng chứng thật (run JSON, transcript, test). Phần hợp nhất merge là phần khó nhất: lần resolve đầu giữ cả hai bên nên sinh trùng lặp và marker lọt vào file `.py`; sau đó phải làm lại theo hướng hợp nhất và chạy lại toàn bộ eval.
- Hạn chế: base eval còn **R12 (wrong_boundary) FAIL** — agent hỏi nội dung cần gửi bằng `clarify(response_type="text")` thay vì xin xác nhận `yes_no`; đã thử ở v2 và v5 nhưng chưa sửa được, ghi nhận là known issue. Transcript live chat chạy trên bản v3 trước merge, chưa quay lại trên v5. Không làm bonus Telegram/local model.
