# Báo cáo cá nhân — Trương Đặng Minh Khuê (2A202603785)

## 1. Thông tin thành viên

- **Họ tên:** Trương Đặng Minh Khuê
- **MSSV:** 2A202603785
- **Email:** 26ai.khuetdm@vinuni.edu.vn

## 2. Phần việc phụ trách

- CP1: chạy baseline v0 độc lập trên nhánh của mình và phân loại lỗi theo run.
- CP2: vòng lặp prompt v1–v3 tập trung vào (a) boundary `send`, (b) loại clarification `text` vs `yes_no`, (c) convention args của `lookup`.
- CP3: 2 tool mới `date_calc` (tính ngày) và `cite_format` (APA 7), kèm `tool.py`, `TOOL.md`, đăng ký `TOOL_FUNCTIONS` + `tools.yaml`.
- Test challenge: thay toàn bộ 14 stub `pytest.skip(TODO)` trong `tests/test_tools_todo.py` bằng test offline thật → 0 skipped.
- CP4: 6 case eval nhóm ban đầu (G01–G06: 3 case `date_calc`, 3 case `cite_format`); sau merge giữ G01/G04 trong bộ 10 case chung.

## 3. Đóng góp cụ thể

- Chuỗi prompt độc lập của tôi (base eval, `openai/gpt-4o-mini`):
  - v0: **13/20 = 0.65** — `send` bị dùng để trả lời (R08/R14), đoán handle/URL (R10/R11), gửi trước xác nhận (R12).
  - v1: **16/20 = 0.80** — thêm Tool usage boundaries + Safety against assumptions; R08/R14 chuyển PASS, R12 vẫn FAIL.
  - v2: **17/20 = 0.85** — thêm Clarification Rules (phân biệt `text` vs `yes_no`).
  - v3: **19/20 = 0.95** — thêm Search Argument Rules (`topic=news`, query chỉ chứa chủ đề) + rule "luôn đặt `response_type`"; R13 chuyển PASS, R12 vẫn FAIL.
- `date_calc`: `today`, `diff_days`, `add_days`, `weekday`; validate `YYYY-MM-DD`/`"today"`, chặn `bool` cho `days`, overflow và input xấu trả error dict (không raise).
- `cite_format`: APA 7 từ title/authors/year/url; "Last, First" → initials, 2 tác giả dùng `&`, thiếu year → `(n.d.)`, thiếu url thì bỏ phần URL, chỉ hỗ trợ APA.
- Test challenge: 14 stub của tool có sẵn (clarify, format, send, lookup, fetch, timeline, social_search, policy) thay bằng test mock HTTP offline; assert cả request gửi đi lẫn mapping kết quả.
- Phân tích lỗi R10/R12 và các bug nhỏ phát hiện khi viết test (thiếu dấu cuối câu trong citation, `send` chấp nhận chuỗi `"false"` là `confirmed`) ghi lại cho nhóm xử lý.

## 4. Bằng chứng

- File:
  - `starter_v0/runs/v0_B_base_openrouter_20261110T180436912628.json` (0.65)
  - `starter_v0/runs/v1_B_base_openrouter_20261110T182150529339.json` (0.80)
  - `starter_v0/runs/v2_B_base_openrouter_20261110T184052350453.json` (0.85)
  - `starter_v0/runs/v3_B_base_openrouter_20261110T185133364699.json` (0.95)
  - `starter_v0/tools/date_calc/`, `starter_v0/tools/cite_format/` (`tool.py` + `TOOL.md`)
  - `starter_v0/tests/test_tools_todo.py` — `test_date_calc_*` (3) và `test_cite_format_*` (5), cùng toàn bộ test thay stub
  - `starter_v0/artifacts/system_prompt.md` (các rule tôi thêm được giữ trong bản hợp nhất), `starter_v0/artifacts/tools.yaml`
  - `starter_v0/data/eval_group.json` (case G01, G04 sau khi hợp nhất)
- Commit: `a4262b2` (First commit), `2a0453c` (date_calc), `19d92d1` (cite_format), `272022a` (Test challenge: pytest 0 failed, 0 skipped), `da84015` (group report), `fa8ffe0`/`f353731` (báo cáo và tool của thành viên khác).
- Kết quả kiểm tra: `pytest -q tests/test_tool_contract.py` 85 passed; `pytest -q tests/test_tools_todo.py -k "date_calc or cite_format"` 8 passed; sau khi hợp nhất toàn suite **128 passed, 0 skipped, 0 failed**.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng trợ lý AI để giải thích lỗi và soạn test; tự kiểm tra bằng cách đọc `results[*].result.failures` trong run JSON, đối chiếu từng dòng `version_log.csv` với run, chạy `pytest -q -rs` và đọc lại output.

## 5. Tự đánh giá

- Hoàn thành CP1–CP4 và test challenge với bằng chứng run/test thật. Phần tôi yếu nhất là R12 (`wrong_boundary`): đã thêm rule xác nhận trước khi gửi ở v1/v2/v3 nhưng model vẫn chọn `response_type="text"` để hỏi nội dung thay vì `yes_no`; tôi ghi nhận là known issue thay vì sửa mò để giữ kết quả thực nghiệm.
- Hạn chế: chuỗi v0–v3 của tôi chạy song song với chuỗi của Phong, nên khi merge phải chọn một chuỗi làm chuẩn (nhóm chọn chuỗi của Phong) và chuyển chuỗi của tôi về báo cáo cá nhân để tránh trùng `v0–v3` trong `version_log.csv`. 4 case `date_calc`/`cite_format` còn lại của tôi (add_days, negative, reference, negative APA) không nằm trong bộ 10 case cuối vì giới hạn 5 single + 5 multi.
