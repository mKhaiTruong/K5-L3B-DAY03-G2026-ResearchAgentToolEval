# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Vũ Quang Thanh
- MSSV: 2A202603736
- Email: 26ai.thanhvq@vinuni.edu.vn

## 2. Phần việc phụ trách

- CP1: chạy và kiểm tra baseline v0 bằng provider OpenRouter, xác nhận bộ eval có đủ 20 case và không có provider error.
- CP2: thực hiện các vòng cải tiến prompt/tool declaration từ v1 đến v3, tập trung vào hỏi lại khi thiếu thông tin, routing `lookup` và xác nhận trước hành động gửi.
- CP3: xây dựng 2 tool local mới `extract_claims` và `deduplicate_items`, đăng ký vào hệ thống và viết unit test.
- CP4: viết 6 eval case cho hai tool mới, gồm 3 case cho mỗi tool, và chạy group eval.

## 3. Đóng góp cụ thể

- CP1 baseline v0 đạt 15/20 case, case accuracy 0.75, tool routing accuracy 0.80 và argument accuracy 0.75.
- CP2:
  - v1 sửa system prompt để hỏi lại khi thiếu thông tin.
  - v2 làm rõ `lookup`: `topic=news` cho tin tức và `topic=general` cho tra cứu thông thường; accuracy tăng từ 0.75 lên 0.85.
  - v3 bổ sung guardrail cho account/URL bị thiếu, bắt buộc `clarify.response_type`, và yêu cầu xác nhận trước `send`; accuracy tăng từ 0.85 lên 1.00.
- CP3:
  - `extract_claims`: lấy claim từ `summary`/`claim` và giữ `source`/`url`, không gọi mạng hay xác minh nội dung.
  - `deduplicate_items`: loại item trùng theo `url` hoặc `title`, giữ lần xuất hiện đầu tiên, không fetch hay xếp hạng.
  - Mỗi tool có `tool.py`, `TOOL.md`, registry trong `tools/__init__.py` và declaration trong `artifacts/tools.yaml`.
  - Viết 3 test cho mỗi tool: happy path, input sai và dữ liệu lỗi/malformed.
- CP4 viết 6 case trong `eval_group.json`: G01–G03 cho `extract_claims`, G04–G06 cho `deduplicate_items`. Group eval đạt 6/6, case accuracy 1.0, routing accuracy 1.0 và argument accuracy 1.0.

## 4. Bằng chứng

- File/commit/PR:
  - [version_log.csv](../../starter_v0/artifacts/version_log.csv): log v0–v3, hash artifact, giả thuyết, metric trước/sau.
  - [v0 baseline run](../../starter_v0/runs/v0_B_base_openrouter_20261110T183148622701.json): 15/20 case pass.
  - [v3 base run](../../starter_v0/runs/v3_B_base_openrouter_20261110T222138486571.json): 20/20 case pass.
  - [v3 group run](../../starter_v0/runs/v3_B_base_openrouter_20261110T221155467525.json): 6/6 case pass, không có provider error.
  - [eval_group.json](../../starter_v0/data/eval_group.json): 6 case CP4, chia đều cho 2 tool.
  - [extract_claims](../../starter_v0/tools/extract_claims/): implementation và TOOL.md.
  - [deduplicate_items](../../starter_v0/tools/deduplicate_items/): implementation và TOOL.md.
  - [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py): 6 unit test cho 2 tool mới.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Python/OpenRouter để chạy `run_eval.py`; dùng pytest cho unit test và contract test.
  - `pytest -q tests/test_tool_contract.py`: 65 passed.
  - `pytest -q tests/test_tools_todo.py -k "extract_claims or deduplicate_items"`: 6 passed.
  - `pytest -q`: 78 passed, 14 skipped; các test skipped là stub challenge có sẵn, không thuộc 2 tool mới.
  - Kiểm tra JSON của `eval_group.json` có đúng 6 case, đúng 3 case cho mỗi tool và mọi case đều có `phase`, `failure_type`, `expect`, `metadata.what_it_tests`.

## 5. Tự đánh giá

- Hoàn thành các phần CP1, CP2, CP3 và CP4 theo yêu cầu.
- Kết quả tốt nhất là v3 base đạt 20/20 case với provider error bằng 0; group eval cho 2 tool mới đạt 6/6.
- Hạn chế: các unit test challenge của những tool có sẵn vẫn còn 14 test skip; hai tool mới là local formatter nên chưa kiểm chứng việc model sử dụng chúng trong một workflow nhiều bước thực tế ngoài 6 group case.
