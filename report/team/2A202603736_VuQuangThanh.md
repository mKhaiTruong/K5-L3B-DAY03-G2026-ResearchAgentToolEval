# Báo cáo cá nhân — Vũ Quang Thanh (2A202603736)

## 1. Thông tin thành viên

- Họ tên: Vũ Quang Thanh
- MSSV: 2A202603736
- Email: 26ai.thanhvq@vinuni.edu.vn

## 2. Phần việc phụ trách

- CP1: chạy và kiểm tra baseline v0 bằng provider OpenRouter, xác nhận bộ eval đủ 20 case và không có provider error.
- CP2: thực hiện các vòng cải tiến prompt/tool declaration v1–v3 song song, tập trung vào hỏi lại khi thiếu thông tin, routing `lookup` (topic news/general) và xác nhận trước khi gửi.
- CP3: xây dựng 2 tool local `extract_claims` và `deduplicate_items`, đăng ký `TOOL_FUNCTIONS` + `tools.yaml`, viết 6 unit test.
- CP4: viết 6 eval case cho 2 tool mới (3 case/tool); sau merge, nội dung 2 case được viết lại thành G09/G10 trong bộ 10 case của nhóm.

## 3. Đóng góp cụ thể

- `extract_claims`: lấy claim từ `summary`/`claim`, giữ `source`/`url`, bỏ item rỗng; không gọi mạng, không xác minh nội dung. Trả `claim_count` để agent tự kiểm tra.
- `deduplicate_items`: loại item trùng theo `url` hoặc `title` (không phân biệt hoa thường), giữ lần xuất hiện đầu tiên, trả `removed_count`; `key` ngoài enum trả error dict thay vì raise.
- Unit test: 6 test (mỗi tool 3: happy path, input xấu từ model, nhánh lỗi/malformed). Sau merge, 6 test này bị mất khỏi `tests/test_tools_todo.py` do conflict được resolve bằng cách giữ một bên; nhóm đã khôi phục đủ 6 test (tên `test_extract_claims_*`, `test_deduplicate_items_*`, có thêm case item không phải dict).
- Eval case: 6 case ban đầu (G01–G06 cho 2 tool local) bị ghi đè khi merge; nội dung được viết lại thành 2 case multi-turn **G09_extract_claims_multiturn** và **G10_deduplicate_items_multiturn** — case G10 từng FAIL ở v4 vì model gọi thêm `fetch`, đã PASS ở v5 sau khi nhóm siết rule.
- Góp ý thiết kế: tool local không fetch để tránh biến "gộp kết quả" thành một cuộc gọi mạng ngoài ý muốn, và luôn trả error dict vì model là người gọi không tin cậy.

## 4. Bằng chứng

- File:
  - `starter_v0/tools/extract_claims/tool.py`, `starter_v0/tools/extract_claims/TOOL.md`
  - `starter_v0/tools/deduplicate_items/tool.py`, `starter_v0/tools/deduplicate_items/TOOL.md`
  - `starter_v0/tests/test_tools_todo.py` — `test_extract_claims_keeps_claim_and_source`, `test_extract_claims_bad_model_input_returns_error_dict`, `test_extract_claims_empty_and_non_dict_items_do_not_crash`, `test_deduplicate_items_by_url_keeps_first_occurrence`, `test_deduplicate_items_by_title_is_case_insensitive`, `test_deduplicate_items_bad_model_input_returns_error_dict`
  - `starter_v0/data/eval_group.json` — G09, G10
  - `starter_v0/runs/v5_B_group_openrouter_20261111T121840551842.json` — G09/G10 PASS trong bộ 10 case
- Commit: `d5db877` (extract_claims & deduplicate_items), `1365270`, `dc8502a` (6 test case), `f9ac8e8` (báo cáo cá nhân).
- Ghi chú bằng chứng: bản nháp báo cáo trước của tôi dẫn 3 run (`v0_…183148622701`, `v3_…222138486571`, `v3 group …221155467525`) nhưng các file này **không có trong repo** sau merge; tôi không dùng các số đó làm bằng chứng. Bằng chứng được tính là code tool, test và case eval còn trong repo.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng trợ lý AI để soạn test và rà lỗi; tự kiểm tra bằng `pytest -q -k "extract_claims or deduplicate_items"` và đọc kết quả run group.

## 5. Tự đánh giá

- Hoàn thành CP3 (2 tool local + test) và đóng góp case eval; tool chạy offline, không cần API key, mọi lỗi trả error dict.
- Hạn chế: các run base v0–v3 tôi chạy không được commit vào repo nên không còn làm bằng chứng; 6 case ban đầu bị ghi đè trong merge và chỉ còn 2 case sau khi viết lại. Tôi chưa có bằng chứng đo riêng cho 2 tool local ngoài 2 case multi-turn ở trên.
