# Team

## Thông tin nhóm

- Tên nhóm: G2026
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-G2026-ResearchAgentToolEval`
- URL repo: https://github.com/mKhaiTruong/K5-L3B-DAY03-G2026-ResearchAgentToolEval
- Nhánh nộp bài: `trinhtuanphong` (đã merge `main` vào ngày 11/11; PR về `main` sau khi sửa xong merge)
- Commit chốt: commit cuối trên nhánh `trinhtuanphong` (xem `git log -1 --oneline`); commit merge mốc là `ec89ecf`

## Thành viên

| STT | Họ tên                | MSSV        | Email                       | GitHub                                      | Vai trò |
| --: | --------------------- | ----------- | --------------------------- | ------------------------------------------- | ------- |
|   1 | Trương Đặng Minh Khuê | 2A202603785 | 26ai.khuetdm@vinuni.edu.vn  | https://github.com/mKhaiTruong              | CP2 (prompt v1–v3), CP3 (`date_calc`, `cite_format`), test challenge 0 skipped |
|   2 | Trịnh Tuấn Phong      | 2A202603781 | 26ai.phongtt2@vinuni.edu.vn | https://github.com/trinhtuanphong123        | CP1 (baseline + failure analysis), CP2 (`artifacts/tools.yaml`), CP3 (`wiki`, `hackernews`), CP4 (case multi-turn), CP5 (UI + transcript), hợp nhất merge |
|   3 | Vũ Quang Thanh        | 2A202603736 | 26ai.thanhvq@vinuni.edu.vn  | https://github.com/thanhvu101               | CP1 (baseline), CP2 (prompt song song), CP3 (`extract_claims`, `deduplicate_items`), CP4 (case multi-turn local tool) |
|   4 | Nguyễn Ngọc Ninh      | 2A202603774 | 26ai.ninhnn@vinuni.edu.vn   | https://github.com/sevenminutes2311-creator | Chưa có báo cáo cá nhân trong repo tại thời điểm hợp nhất — nhóm cần bổ sung trước khi nộp |

## Cá nhân

Mỗi thành viên có báo cáo riêng trong `report/team/`:

- `report/team/2A202603781_TrinhTuanPhong.md`
- `report/team/2A202603785_TruongDangMinhKhue.md`
- `report/team/2A202603736_VuQuangThanh.md`

## Đóng góp theo checkpoint

| Checkpoint | Bằng chứng chính |
|---|---|
| CP1 — baseline v0 | `starter_v0/runs/v0_B_base_openrouter_20261110T172631463565.json` (0.75, 15/20), `starter_v0/analysis/base_runs.csv`, bảng B2 trong group report |
| CP2 — prompt + tool declaration v1–v3 | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, run v1/v2/v3 trong `starter_v0/runs/` |
| CP3 — tool mới + unit test | `starter_v0/tools/wiki/`, `starter_v0/tools/hackernews/`, `starter_v0/tools/date_calc/`, `starter_v0/tools/cite_format/`, `starter_v0/tools/extract_claims/`, `starter_v0/tools/deduplicate_items/`, `starter_v0/tests/test_tools_todo.py` (36 test), `pytest` 128 passed / 0 failed / 0 skipped |
| CP4 — 10 case eval nhóm | `starter_v0/data/eval_group.json`, run `v4_B_group_*` trong `starter_v0/runs/` |
| CP5 — UI + live chat | `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/transcripts/v3_openrouter_20261110T232722798444.transcript.json` |
