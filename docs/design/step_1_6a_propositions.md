# Bước 1.6A: tách mệnh đề (`src/propositions.py`)

Trạng thái: thiết kế đã chốt (quyết định A38, A39). Lời nhắc `menh-de-3` đã đóng băng. Chưa chạy đủ 204 lô; chưa nối vào `run_all`. Bước này thay phần gạch cụm cũ (`src/concepts.py`, lời nhắc `concepts-2`), vốn đã chạy xong nhưng cho kết quả không dùng được (lý do ở `docs/design/steps_1_6_to_1_8.md`, mục 3).

## 1. Mục đích
Biến chữ của mỗi đơn vị luật thành danh sách **mệnh đề**: mỗi dòng nói đúng một điều có thể đúng hoặc sai, kèm chủ thể, phương thức (được, phải, cấm), cực (khẳng định hay phủ định) và bằng chứng nguyên văn. Mệnh đề phải đủ ngắn và tự đủ nghĩa để hai điều luật khác nhau cùng nói một ý thì ra cùng một vị từ ở bước 1.6B, vì chính sự trùng vị từ nối các điều luật rời rạc lại với nhau.

## 2. Đầu vào
881 đơn vị của BLLĐ thuộc Điều có nhãn `substantive` hoặc `definition` (bước 1.4), chia 204 lô, mỗi lô một Điều (Điều dài hơn 20 đơn vị thì cắt). Mỗi đơn vị kèm ngữ cảnh: tiêu đề Điều, câu dẫn của khoản hoặc Điều cha, chữ chính của đơn vị, và các dẫn chiếu đã giải ở bước 1.2 (kèm mã đích). Nút điều kiện của bước 1.5 (ngoại lệ chung) chưa được đưa vào bước này trong mã hiện tại; bản gạch cụm cũ có làm việc đó, nên khi nối vào `run_all` phải quyết cách giữ lại.

## 3. Đầu ra
`data/processed/concepts/concepts_spans_<doc_id>.jsonl` (tên file giữ nguyên từ bản cũ), mỗi dòng một mệnh đề hoặc một chỗ bỏ qua. Phản hồi thô của LLM lưu ở `data/llm_cache/propositions/`.

Bốn loại dòng (`loai`):

| Giá trị | Nghĩa | Bước sau dùng |
|---|---|---|
| `menh_de` | một điều đúng/sai được | 1.6B đặt tên vị từ; 1.8 viết quy tắc |
| `con_tro` | dẫn chiếu đã giải ("trừ trường hợp quy định tại ..."), không đặt tên | 1.8 |
| `bo_qua` | không thành mệnh đề; có `ly_do_llm.ma` | báo cáo, truy vết (không xoá khỏi dữ liệu) |
| `chua_ro` | cả dòng không xác định được; có `cau_hoi` | người đọc |

Trường của dòng:

| Trường | Nghĩa | Giá trị |
|---|---|---|
| `unit` | đơn vị chứa dòng | mã Điều, khoản, điểm |
| `vai` | vị trí trong quy tắc | `ket_luan`, `dieu_kien`, `ngoai_le`; rỗng với `bo_qua` |
| `menh_de` | lõi của mệnh đề: động từ hoặc tính chất cộng tân ngữ chính; đã bỏ chủ thể, chữ phương thức, chữ phủ định, bổ ngữ, danh sách liệt kê | chuỗi; mọi âm tiết phải có trong `trich` của chính dòng |
| `chu_the` | ai làm hoặc ai mang tính chất | `{chu, loai, nguon}` hoặc rỗng. `loai`: `W` người lao động, `E` người sử dụng lao động, `C` hợp đồng, `J` công việc, `G` vùng, `D` ngày, `A` số tiền, `?` chưa biết (hoặc danh sách mã khi chủ thể chung). `nguon`: `chinh`, `cau_dan`, `tieu_de` |
| `doi_so` | đối số khác, theo thứ tự | danh sách `{loai}` cùng tám mã trên |
| `phuong_thuc` | sức ép pháp lý | `duoc` (được, có quyền), `phai` (phải), `cam` (cấm, không được làm), `khong_ap_dung` (tuyên bố một quy định không áp cho một nhóm trường hợp; chặn quy tắc chứ không cấm hành vi), `khong` (chỉ mô tả, điều kiện, định nghĩa) |
| `cuc` | khẳng định hay phủ định `menh_de` | `khang_dinh`, `phu_dinh`. `cuc` chỉ phủ định mệnh đề, không bao giờ phủ định phương thức: "được + phủ định X" là "được không bị X", không phải "cấm X" |
| `bo_ngu` | cụm bổ nghĩa đã tách khỏi mệnh đề | danh sách `{original_text, scope}`; `scope`: `this_clause`, `group`, `unknown` |
| `liet_ke` | danh sách liệt kê từ 3 mục của tân ngữ hoặc phạm vi, mỗi mục chép nguyên văn | danh sách chuỗi |
| `nhom_hoac` | các điều kiện cùng một nhóm "hoặc" trong một đơn vị | mã nhóm hoặc rỗng (rỗng nghĩa là nối bằng "và") |
| `quy_tac` | gom điều kiện và kết luận của cùng một quy tắc trong một đơn vị | `q1`, `q2`, ... |
| `cac_muc_con` | (chỉ ở dòng `bo_qua` loại câu dẫn) các mục con nối thế nào | `va` (phải đủ hết), `hoac` (một là đủ), `danh_sach` (liệt kê quyền hay nội dung, không phải điều kiện) |
| `chua_ro` | chỗ chưa xác định | danh sách `{thanh_phan, nguyen_nhan, cau_hoi}`; `nguyen_nhan`: `pham_vi_bo_ngu`, `tach_hay_giu_chung`, `phuong_thuc`, `chu_the`, `khac`; mỗi chỗ một mục |
| `trich` | bằng chứng nguyên văn | danh sách chuỗi liền, chép từ tiêu đề, câu dẫn hoặc chữ đơn vị; chủ thể hay phương thức kế thừa thì phải có cả mẩu chứa nó |
| `targets` | đích dẫn chiếu (ở `con_tro`) | mã đơn vị từ bước 1.2 hoặc 1.5; rỗng kèm `chua_ro` nếu 1.2 không giải được |
| `gan_vao` | chỉ số dòng (từ 0, trong cùng đơn vị) mà một `con_tro` bổ nghĩa | số, hoặc rỗng nếu chặn cả quy tắc |
| `ly_do_llm` | vì sao quyết như vậy, chỉ ở ca khó và mọi dòng `bo_qua` | `{ma, giai_thich}`; `ma`: `tach`, `giu_chung`, `gan_bo_ngu`, `chua_ro`, `ke_thua`, `cau_dan`, `dan_chieu_mo`, `dan_chieu_ngoai`, `khong_quy_pham` |

## 4. Luật tách (nằm trong lời nhắc)
1. **Tách** khi từng phần kiểm được đúng/sai độc lập và vi phạm từng phần có ý nghĩa pháp lý riêng. **Giữ chung** khi các phần tạo thành một yêu cầu tập thể. Không tách chỉ vì có nhiều danh từ. Mỗi quyết định tách hoặc giữ chung ở ca khó có lý do (`ly_do_llm`).
2. `menh_de` chỉ giữ lõi, càng ngắn càng tốt; danh sách từ 3 mục đưa vào `liet_ke`.
3. Chữ dùng chung đứng đầu chuỗi ("không" trong "không A, B, C") được hiểu cho từng mục. Bổ ngữ đứng cuối phải xác định phạm vi trong `bo_ngu`; không xác định được thì `chua_ro` với `nguyen_nhan` là `pham_vi_bo_ngu`.
4. `bo_ngu` chỉ cho cụm mà bỏ đi thì vẫn cùng loại hành vi (nơi chốn, căn cứ, cách thức phụ). Cụm làm nên chính hành vi giữ trong `menh_de`. Dẫn chiếu không bao giờ là bổ ngữ.
5. Câu dẫn: nếu danh sách là tân ngữ ("có các nghĩa vụ sau đây") thì câu dẫn ra `bo_qua` loại `cau_dan`, mục con là `ket_luan` kế thừa chủ thể và phương thức. Nếu danh sách là điều kiện ("trong trường hợp sau đây") thì phần nội dung của câu dẫn ra một `ket_luan` (một lần, ở câu dẫn), phần dẫn ra `bo_qua`, mục con là `dieu_kien`.
6. Định nghĩa "X là Y": các dấu hiệu của Y là `dieu_kien`, thêm một `ket_luan` "là X". Câu nêu giá trị hoặc mức ("thời hạn ... là N ngày") ra một `ket_luan`.
7. "Hoặc" giữa các điều kiện trong một quy tắc dùng chung `nhom_hoac`. "Hoặc" mà một vế có "và" thì tách thành nhiều quy tắc.
8. Bẫy "không được": "không được + động từ" là `cam` (không được làm X) hoặc bị động phủ định (không được người khác làm cho: `khong` cộng `phu_dinh`). "Không phải X" (không có nghĩa vụ) ghi `duoc` cộng `phu_dinh`.
9. Chủ thể là đối số, không nằm trong tên vị từ; chữ phương thức và chữ phủ định không nằm trong `menh_de`.
10. Bước 1.6B đặt tên theo `menh_de`, không tính `bo_ngu`; bước 1.8 phải dùng `bo_ngu` như một điều kiện, không được bỏ sót.

## 5. Cổng máy kiểm
Cổng chặn (sai thì hỏi lại lô đó một lần, vẫn sai thì loại dòng): khuôn dòng và giá trị trường đúng; mỗi chuỗi `trich` là chuỗi con liền của ngữ cảnh; **cổng âm tiết**: mọi âm tiết của `menh_de` phải có trong các mẩu `trich` của chính dòng đó (chủ thể hoặc phương thức kế thừa từ câu dẫn thì mẩu câu dẫn phải nằm trong `trich`); `menh_de` không kết thúc bằng "sau đây" hoặc dấu ":" (chặn câu dẫn lọt); `con_tro` có `targets` nằm trong dẫn chiếu của bước 1.2; `bo_qua` có lý do; mọi đơn vị có ít nhất một dòng.

Cờ cảnh báo (không chặn): `menh_de` còn chữ phương thức; `menh_de` dài từ 15 âm tiết (`LONG_SYL`).

Máy không kiểm được: nghĩa của `menh_de` có đúng không; bẫy "không được"; bổ ngữ có bị rải sai không; quyết định tách hay giữ chung. Cổng âm tiết yếu hơn cổng chuỗi con: LLM vẫn có thể đảo thứ tự chữ.

## 6. Cách chạy
Phần LLM chạy bằng phiên Claude Code trong thư mục làm việc ngoài repo (xem `docs/operations/llm_sandbox.md`), không gọi API. Đường chạy đã chốt (A39): Sonnet 5.5, effort `high`, mỗi subagent một khối tối đa 20 lô, song song tối đa 4, lời nhắc `menh-de-3`. Luật dừng: sau 3 khối đầu (60 lô), nếu có câu dẫn lọt thành `menh_de` hoặc lỗi cổng còn lại vượt 5% số dòng thì dừng và báo.

```
python -X utf8 -I src/propositions.py xuat <thư mục mới> [model] [effort] --tat-ca   # dựng thư mục làm việc (204 lô)
python -X utf8 -I src/propositions.py nhap <thư mục>                              # kiểm và ghi vào data/llm_cache/propositions/
python -X utf8 -I src/propositions.py kiem-dap-an [file]                          # chạy cổng trên file đáp án
python -X utf8 -I src/propositions.py so [file llm] [file báo cáo]                # so đầu ra LLM với đáp án thí điểm
```

## 7. Thí điểm và đánh giá
Bộ thí điểm gồm 30 đơn vị BLLĐ chọn theo nhóm khó: câu dẫn thuần và câu dẫn có nội dung; danh sách quyền; "và" so với "hoặc"; phủ định và bẫy "không được"; định nghĩa "X là Y"; dẫn chiếu rõ và dẫn chiếu mờ. Dữ liệu ở `data/pilot_propositions/`:
- `gold_draft.json`: đáp án nháp (97 dòng), chưa phải đáp án chuẩn vì chưa được người có thẩm quyền xác nhận;
- `llm_output*.json` và `comparison*.md`: đầu ra và so sánh của các lần thử (Sonnet qua Claude Code, hai model Gemini);
- `gold_template.json`, `gold_first_draft.json`: khung đơn vị và bản nháp đầu.

Kết quả thử 16 lô (30 đơn vị) với lời nhắc `menh-de-3` trên Gemini, so với Sonnet qua Claude Code ở lời nhắc `menh-de-1`:

| Cách chạy | Lỗi cổng | Nhận xét |
|---|---|---|
| Sonnet qua Claude Code (`menh-de-1`) | 0 / 100 dòng | chính xác nhất, tốn token |
| Gemini 3.5 flash-lite (`menh-de-3`) | 26 / 79 dòng | rẻ, nhanh; có bịa đích dẫn chiếu và chủ thể |
| Gemini 3.8 flash (`menh-de-3`) | 17 / 79 dòng | không bịa; lỗi chủ yếu là thiếu mẩu câu dẫn trong `trich`; hạn mức 20 lượt mỗi ngày |

Nghiệm thu sau khi chạy đủ 204 lô (A39): số cặp ứng viên cho bước 1.7 (bản cũ: 108), tỉ lệ tái dùng ở 1.6B (bản cũ: 3%), tỉ lệ mệnh đề lặp nguyên văn ở từ 2 Điều trở lên (bản cũ: 9/318). Các số này đo độ kết nối giữa các Điều, không đo nghĩa đúng hay sai. Cả ba không hơn bản cũ thì coi là không cải thiện và dừng.

## 8. Giới hạn đã biết
- `menh-de-3` chưa có số so đáp án đầy đủ trên Sonnet; đóng băng lời nhắc là một lựa chọn có rủi ro (A39 (6)).
- Đáp án nháp do LLM soạn nên chỗ đáp án và LLM cùng sai sẽ không lộ.
- Đoạn văn không có ký hiệu điểm nằm giữa hai điểm bị bước 1.1 gắn vào khoản cha thay vì điểm đứng trước (ví dụ `D36.K1`): ngữ cảnh của một số đơn vị còn dính câu thừa.
- Dẫn chiếu tới Mục hoặc Chương chưa được bước 1.2 nhận dạng (BLLĐ có một ca, `D3.K1`): `con_tro` ở đó có `targets` rỗng kèm `chua_ro`.
- `liet_ke` là trường thêm việc cho bước 1.8: danh sách là một đối số, chưa thiết kế cách dùng.
- `khong_ap_dung` cần bước 1.8 dịch khác `cam` (chặn quy tắc, không cấm hành vi); cách dịch chưa thiết kế.
