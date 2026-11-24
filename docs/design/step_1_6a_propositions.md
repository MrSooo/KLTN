# Bước 1.6A: tách mệnh đề (`src/propositions.py`)

Trạng thái: đang thay bằng bản v2 (A59, A60), xem mục 9. Mục 1-8 tả bản cũ (A38, A39, lời nhắc đến `menh-de-12`), còn là khuôn dữ liệu mà 1.6B, 1.8 đọc. Chưa nối vào `run_all`. Bước này thay phần gạch cụm cũ (`src/concepts.py`, lời nhắc `concepts-2`), vốn đã chạy xong nhưng cho kết quả không dùng được (lý do ở `docs/design/steps_1_6_to_1_8.md`, mục 3).

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
| `bo_ngu` | (cũ, chỉ đọc) cụm bổ nghĩa đã tách khỏi mệnh đề; từ `menh-de-9` (A55) không dùng nữa, cụm bổ nghĩa thành dòng `dieu_kien` | danh sách `{original_text, scope}`; `scope`: `this_clause`, `group`, `unknown`. Giữ trong mã để đọc cache đến `menh-de-8`; từ `menh-de-9` khác rỗng là lỗi cổng |
| `liet_ke` | danh sách liệt kê từ 3 mục của tân ngữ hoặc phạm vi, mỗi mục chép nguyên văn | danh sách chuỗi |
| `nhom_hoac` | các điều kiện cùng một nhóm "hoặc" trong một đơn vị | mã nhóm hoặc rỗng (rỗng nghĩa là nối bằng "và") |
| `quy_tac` | gom điều kiện và kết luận của cùng một quy tắc trong một đơn vị | `q1`, `q2`, ... |
| `cac_muc_con` | (chỉ ở dòng `bo_qua` loại câu dẫn) các mục con nối thế nào | `va` (phải đủ hết), `hoac` (một là đủ), `danh_sach` (liệt kê quyền hay nội dung, không phải điều kiện) |
| `chua_ro` | chỗ chưa xác định | danh sách `{thanh_phan, nguyen_nhan, cau_hoi}`; `nguyen_nhan`: `pham_vi_bo_ngu`, `tach_hay_giu_chung`, `phuong_thuc`, `chu_the`, `khac`; mỗi chỗ một mục |
| `trich` | bằng chứng nguyên văn | danh sách chuỗi liền, chép từ tiêu đề, câu dẫn hoặc chữ đơn vị; chủ thể hay phương thức kế thừa thì phải có cả mẩu chứa nó |
| `targets` | đích dẫn chiếu (ở `con_tro`) | mã đơn vị từ bước 1.2 hoặc 1.5; rỗng kèm `chua_ro` nếu 1.2 không giải được |
| `gan_vao` | chỉ số dòng (từ 0, trong cùng đơn vị) mà một `con_tro` bổ nghĩa | số, hoặc rỗng nếu chặn cả quy tắc |
| `ly_do_llm` | vì sao quyết như vậy, chỉ ở ca khó và mọi dòng `bo_qua` | `{ma, giai_thich}`; `ma`: `tach`, `giu_chung`, `gan_bo_ngu`, `chua_ro`, `ke_thua`, `cau_dan`, `dan_chieu_mo`, `dan_chieu_ngoai`, `khong_quy_pham` |

### 3.1. Khuôn gọn của LLM, từ `menh-de-12` (A57; lệch A38 và bảng trên)
Bảng trên vẫn là khuôn dữ liệu mà bước sau đọc. Từ `menh-de-12`, LLM KHÔNG viết khuôn đó: nó viết khuôn gọn, máy (`propositions.expand_unit`) dựng lại khuôn trên, rồi cổng chạy như cũ (`propositions.check_unit` là đường nhập duy nhất).

| Ai ghi | Trường |
|---|---|
| LLM, mỗi dòng | `doan` (danh sách đoạn chép nguyên văn, liền; nối lại là lõi), `vai`, `phuong_thuc`, `cuc`, `quy_tac`, `nhom_hoac`, `chu_the{chu, loai}` (bỏ khi không có chủ thể), `doi_so`, `liet_ke`, `chua_ro` |
| LLM, mỗi đơn vị (tuỳ chọn) | `cac_muc_con`; `ngoai_le` (đích dẫn chiếu là ngoại lệ); `bo_qua` (`khong_quy_pham`, `dan_chieu_mo`, `dan_chieu_ngoai`, khi đơn vị không có dòng) |
| Máy | `loai`; `menh_de` (nối `doan`); `trich` (`doan`, cộng chữ chủ thể khi chủ thể lấy từ câu dẫn hay tiêu đề); `chu_the.nguon` (chỗ chữ chủ thể xuất hiện); một dòng `con_tro` cho mỗi dẫn chiếu (vai `ngoai_le` theo trường `ngoai_le`, còn lại `dieu_kien`; `gan_vao` rỗng); dòng `bo_qua cau_dan` từ `cac_muc_con`; `ly_do_llm` của dòng máy dựng; `bo_ngu` rỗng |

Kiểm thêm của khuôn gọn (`compact_checks`): `doan` rỗng, `doan` chứa chữ dẫn chiếu, `bo_qua` ngoài tập đóng, đơn vị không có dòng, giữa hai đoạn liên tiếp cùng nguồn có chữ "không / chưa / hoặc" bị bỏ (lỗi); chữ "và" bị bỏ (cờ). Khoá lạ ở dòng, ở đơn vị hay trong `chu_the` là lỗi; máy không sửa giá trị LLM ghi.

## 4. Luật tách (nằm trong lời nhắc)
1. **Tách** khi từng phần kiểm được đúng/sai độc lập và vi phạm từng phần có ý nghĩa pháp lý riêng. **Giữ chung** khi các phần tạo thành một yêu cầu tập thể. Không tách chỉ vì có nhiều danh từ. Mỗi quyết định tách hoặc giữ chung ở ca khó có lý do (`ly_do_llm`).
2. `menh_de` chỉ giữ lõi, càng ngắn càng tốt; danh sách từ 3 mục đưa vào `liet_ke`.
3. Chữ dùng chung đứng đầu chuỗi ("không" trong "không A, B, C") được hiểu cho từng mục. Bổ ngữ đứng cuối phải xác định phạm vi: chỉ một quy tắc (`this_clause`) thì một dòng `dieu_kien` trong quy tắc đó; chung cho cả nhóm (`group`) thì một dòng `dieu_kien` nguyên văn trong MỖI `quy_tac` của nhóm; không xác định được thì `chua_ro` với `nguyen_nhan` là `pham_vi_bo_ngu` (giữ tên mã). Đến `menh-de-8`: phạm vi ghi trong `bo_ngu` (A55).
4. Bổ ngữ là cụm mà bỏ đi thì vẫn cùng loại hành vi (nơi chốn, căn cứ, cách thức phụ): tách khỏi `menh_de` thành một dòng `dieu_kien` riêng, chép nguyên văn, cùng chủ thể với dòng nó bổ nghĩa (A55; đến `menh-de-8` là trường `bo_ngu`). Cụm làm nên chính hành vi giữ trong `menh_de`. Dẫn chiếu không bao giờ là bổ ngữ.
5. Câu dẫn: nếu danh sách là tân ngữ ("có các nghĩa vụ sau đây") thì câu dẫn ra `bo_qua` loại `cau_dan`, mục con là `ket_luan` kế thừa chủ thể và phương thức. Nếu danh sách là điều kiện ("trong trường hợp sau đây") thì phần nội dung của câu dẫn ra một `ket_luan` (một lần, ở câu dẫn), phần dẫn ra `bo_qua`, mục con là `dieu_kien`.
6. Định nghĩa "X là Y": các dấu hiệu của Y là `dieu_kien`, thêm một `ket_luan` "là X". Câu nêu giá trị hoặc mức ("thời hạn ... là N ngày") ra một `ket_luan`.
7. "Hoặc" giữa các điều kiện trong một quy tắc dùng chung `nhom_hoac`. "Hoặc" mà một vế có "và" thì tách thành nhiều quy tắc.
8. Bẫy "không được": "không được + động từ" là `cam` (không được làm X) hoặc bị động phủ định (không được người khác làm cho: `khong` cộng `phu_dinh`). "Không phải X" (không có nghĩa vụ) ghi `duoc` cộng `phu_dinh`.
9. Chủ thể là đối số, không nằm trong tên vị từ; chữ phương thức và chữ phủ định không nằm trong `menh_de`.
10. Bước 1.6B đặt tên theo `menh_de`. Từ `menh-de-9` bổ ngữ là dòng `dieu_kien` nên 1.6B và 1.8 dùng nó như mọi điều kiện. Cache đến `menh-de-8` còn `bo_ngu` mà 1.6B, 1.8 KHÔNG đọc (luật cũ "1.8 phải dùng `bo_ngu` như một điều kiện" chưa từng được làm; A55).

## 5. Cổng máy kiểm
Cổng chặn (sai thì hỏi lại lô đó một lần, vẫn sai thì loại dòng): khuôn dòng và giá trị trường đúng; mỗi chuỗi `trich` là chuỗi con liền của ngữ cảnh; **cổng âm tiết**: mọi âm tiết của `menh_de` phải có trong các mẩu `trich` của chính dòng đó (chủ thể hoặc phương thức kế thừa từ câu dẫn thì mẩu câu dẫn phải nằm trong `trich`); `menh_de` không kết thúc bằng "sau đây" hoặc dấu ":" (chặn câu dẫn lọt); `con_tro` có `targets` nằm trong dẫn chiếu của bước 1.2; `bo_qua` có lý do; mọi đơn vị có ít nhất một dòng.

Cờ cảnh báo (không chặn): `menh_de` còn chữ phương thức; `menh_de` dài từ 15 âm tiết (`LONG_SYL`).

Máy không kiểm được: nghĩa của `menh_de` có đúng không; bẫy "không được"; bổ ngữ có bị rải sai không; quyết định tách hay giữ chung. Cổng âm tiết yếu hơn cổng chuỗi con: LLM vẫn có thể đảo thứ tự chữ. Từ `menh-de-12` (mục 3.1), cổng âm tiết và kiểm "chủ thể lấy từ câu dẫn/tiêu đề mà `trich` không có mẩu" luôn đúng vì máy dựng `trich`; thay bằng: mỗi `doan` là chuỗi con liền và kiểm chữ bị bỏ giữa hai đoạn.

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

## 9. Bản v2 (A59), lượt 1: tách ranh giới mệnh đề (chốt 24/11, A60)
Mục này thay mục 4 cho lượt 1 của 1.6A-v2. Mục 1-8 còn đúng cho khuôn dữ liệu mà 1.6B, 1.8 đọc (máy dựng lại sau lượt 2).

**Phần agent thêm và chỗ lệch (đặt lên đầu).** User duyệt các mục [THÊM] và các đề xuất đã gửi ngày 24/11 ("theo đề xuất của bro hết"); các điểm chốt sau lời duyệt đó (D86.K2.c, D73.K1, D46.K3, "Do ...", luật `ap_cho` và ví dụ neo, mốc của luật 5 (c), thứ tự luật 1/luật 3) chỉ advisor soát, theo lời user cho phép; danh sách ở A60. Mọi chỗ khác truy về: lời nhắc `seg-thu-3` (`data/sandbox_runs/seg_thu_3/system.txt`), kiến trúc A59, `gom_loi.md` (E1-E5), quyết định E4 (24/11), A55, A58.
- [THÊM] Chữ nối là tập **đơn vị** đóng, có đơn vị nhiều chữ ("sau khi", "trừ trường hợp"); máy ghép theo khớp dài nhất trước khi kiểm, ranh giới đoạn không được cắt ngang một đơn vị. Vì sao: bắt được E1 dạng "... trước" + "người lao động thôi việc" (D46.K3) mà tập một chữ không bắt. Cái giá: một chữ nối nhiều chữ hiếm khi là hai chữ rời ("trả trước khi ...") sẽ bị coi là một đơn vị.
- [THÊM] Đoạn không được mở đầu bằng một đơn vị nối, và không được kết thúc bằng một đơn vị nối trừ "do", "trừ", "trường hợp" (lỗi máy). Vì sao: E2 ("Trường hợp", "Trước khi" thành đoạn dùng chung) và đoạn dính chữ nối (D113.K4#2 "... để") thành lỗi máy bắt được, gold không có hai cách đúng. Ba chữ được miễn ở cuối vì là âm tiết của từ ghép hay gặp ở cuối đoạn: "lý do" (20 câu), "tự do" (6), "khấu trừ" (5), "các/mọi/từng ... trường hợp" (35). Cái giá: "Khi", "Trường hợp", "để", "trừ" không nằm trong đoạn; lượt 2 phải đọc chúng từ khe giữa các đoạn (xem dòng ghi khoảng token ở mục 9.5).
- [THÊM] Máy ghi kèm mỗi đoạn khoảng token trong câu và các đơn vị nối ở khe ngay trước nó. Vì sao: chữ nối đứng ngoài đoạn mà lượt 2 cần chúng ("trừ" là ngoại lệ, "sau khi" là thời gian); đầu ra của LLM không có vị trí. Cái giá: thêm trường trong khuôn máy dựng (LLM không viết).
- [THÊM] Mở rộng E4 (user chỉ chốt "đối với"): luật 4 gồm cả "trên cơ sở", "theo", "tại", "trong thời hạn" ("trong thời hạn" có trong dòng E4 của `gom_loi.md`). Với "trên cơ sở" đây là lệch `gom_loi.md` E3 (đề xuất có luật tách riêng). Vì sao: cùng loại bổ ngữ A55 (nơi chốn, căn cứ, cách thức), cùng lý do không có chữ đánh dấu. Cái giá: như E4, các cụm này dài ở lượt 1 (D73.K1).
- [THÊM] Mở rộng E3 (gom_loi chỉ nêu "trừ", "trong trường hợp"): luật 5 tách cả vế không động từ mở đầu bằng "nếu", "khi", "sau khi", "trước khi", "trường hợp". Vì sao: một luật chung theo chữ đánh dấu dễ kiểm hơn luật từng chữ. Cái giá: vế không động từ sau "khi" hiếm, chưa đếm.
- [THÊM] "để", "nhằm" vào tập nối và đứng ngoài đoạn. `seg-thu-3` để chúng trong đoạn (D73.K1 m2 "để tiến hành ..."). Vì sao: cùng luật trên. Cái giá: đổi so với lần chạy dò; số liệu `seg_thu_3` không so thẳng được ở điểm này.
- [THÊM] Cách máy cắt E5: khối "trừ (các) trường hợp quy định tại <chuỗi dẫn chiếu>" được thay bằng dấu giữ chỗ `⟦DC1⟧`, `⟦DC2⟧`... trước khi gửi LLM; máy chèn lại thành đoạn `dan_chieu`. A59 và E5 chỉ nói "máy cắt", không nói cách. Cái giá: LLM phải chép đúng dấu giữ chỗ; câu đọc kém tự nhiên hơn.
- [THÊM] Dẫn chiếu khác ("theo quy định tại ...", "người lao động quy định tại ...") giữ trong chữ, nằm trọn trong một đoạn; máy kiểm không ranh giới nào cắt ngang chữ dẫn chiếu của 1.2. Lệch khuôn gọn `menh-de-12` (mục 3.1: `doan` chứa chữ dẫn chiếu là lỗi). Vì sao: 1.2 chỉ ghi cụm danh từ ("khoản 2 Điều này"), không ghi chữ dẫn ("theo quy định tại"); bỏ chữ dẫn chiếu ra ở lượt 1 làm câu cụt nghĩa ("người lao động quy định tại khoản 1" còn "người lao động"). Cái giá: lượt 2 hoặc máy phải tách dẫn chiếu khỏi lõi.
- [THÊM] Luật 3 câu thứ hai (tách tính chất của chính chủ thể) là cách đọc của agent; A58 chỉ nói không tách cụm mô tả đối tượng khác. Cái giá: thêm mệnh đề ở câu có chủ thể dài (D61.K4).
- [THÊM] Thước đo khớp hoàn toàn tính cả `ap_cho`, và gold phải qua máy kiểm (A59 không định nghĩa thước đo). Cái giá: máy kiểm giới hạn gold có thể viết gì (D73.K1, mục 9.7).
- [THÊM] Ngưỡng đạt và thành phần bộ gold ở mục 9.6 do agent đề xuất.

### 9.1. Phạm vi
Đầu vào: một câu (máy cắt, mục 9.2), không kèm tiêu đề hay câu dẫn. Đầu ra: các đoạn theo thứ tự, mỗi đoạn là `menh_de` (một việc đúng/sai được) hoặc `dung_chung` (phần nhiều mệnh đề dùng chung, kèm `ap_cho`). Không gán vai, phương thức, cực, cây AND/OR: việc của lượt 2 (theo nhóm logic, có câu gốc).

### 9.2. Bước 0 (máy, trước LLM)
1. Cắt câu: mỗi dòng của chữ đơn vị, và sau dấu chấm có chữ hoa theo sau (như `do_bo_kho.py`). BLLĐ: 993 câu từ 881 đơn vị.
2. Tách token (chữ, dấu câu); ghép đơn vị nối theo khớp dài nhất (mục 9.4).
3. Đánh dấu chữ dẫn chiếu: mỗi `cum` của 1.2 trong câu là một khối không cắt được. Khối "trừ (các) trường hợp quy định tại" cộng chuỗi dẫn chiếu liền sau (nối bằng ",", "và", "hoặc") thay bằng `⟦DCn⟧` (BLLĐ: 14 câu).

### 9.3. Luật tách (nằm trong lời nhắc)
1. Mỗi việc khác nhau (hành vi, sự kiện, trạng thái) là một mệnh đề. Liệt kê nhiều động từ thì tách từng động từ. Cụm mục đích ("để ...", "nhằm ...") là mệnh đề riêng, trừ khi nó đứng ngay sau một danh từ và trước động từ chính: khi đó nó là phần tên của danh từ, không tách ("Tiền lương để tính trợ cấp thôi việc là ...", D46.K3). Vế "trừ khi" này đứng trước câu thứ hai của luật 3. (`seg-thu-3` luật 1; vế "trừ khi" chốt 24/11)
2. Liệt kê danh từ (đối tượng, thuộc tính, căn cứ, nơi chốn) KHÔNG tách; mục của danh sách có chứa động từ ("vì lý do thành lập, gia nhập công đoàn") vẫn là mục, không tách. (`seg-thu-3` luật 2)
3. Cụm lồng mô tả một đối tượng KHÁC chủ thể KHÔNG tách, kể cả có động từ: "danh mục nghề ... do Bộ trưởng ... ban hành" (mô tả danh mục). (A58) [THÊM] Cụm nói tính chất của chính chủ thể của câu thì tách theo luật 1: "Người học nghề, người tập nghề thuộc danh mục ..." có "thuộc danh mục ..." là một mệnh đề (D61.K4). Luật 4 đứng trước: không tách gì bên trong một bổ ngữ của luật 4 ("đối với người làm công việc ...", "đối với người lao động hưởng lương ngày" giữ nguyên).
4. Bổ ngữ không mở đầu bằng chữ nối của luật 5 ("đối với ...", "trên cơ sở ...", "theo ...", "tại ...", "trong thời hạn ...") KHÔNG tách; để trong đoạn nó bổ nghĩa. (E4, 24/11; lượt 2 đánh span)
5. Vế mở đầu bằng chữ nối điều kiện, thời gian hay ngoại lệ ("nếu", "khi", "sau khi", "trước khi", "trường hợp", "trong trường hợp", "trừ", "trừ trường hợp") là mệnh đề riêng, kể cả khi câu chỉ có một động từ chính và vế đó không có động từ ("trừ lĩnh vực nghệ thuật, thể dục, thể thao", D61.K4). Không áp cho: (a) câu dẫn kết thúc bằng "(các) trường hợp sau đây/như sau" (17 trong 38 câu có "trong (các) trường hợp"), giữ theo luật 8; (b) "trường hợp" theo sau là "quy định tại" mà không có "trừ" đứng trước (6 câu), cụm giữ trong đoạn như dẫn chiếu khác; (c) vế lồng GIỮA một mệnh đề, tức vị ngữ chính đã bắt đầu trước vế và còn tiếp sau vế (D73.K1 "yêu cầu Ủy ban nhân dân ... [vế] thành lập ..."), giữ trong mệnh đề vì đoạn phải liền. Nếu trước vế chỉ có chủ ngữ ("X, khi Y, phải Z") thì tách bình thường, X thành `dung_chung` theo luật 6. "Trong trường hợp này" là một đơn vị nối (mục 9.4). (E3)
6. Phần nhiều mệnh đề dùng chung ghi MỘT lần thành đoạn `dung_chung`, kèm `ap_cho`; gồm cả chủ thể hay cụm mở đầu đứng trước một loạt việc. Chữ nối không bao giờ là đoạn dùng chung. (`seg-thu-3` luật 3; E2)
7. Chép nguyên văn, theo thứ tự. Mọi chữ nằm trong đúng một đoạn, trừ dấu câu, đơn vị nối và `⟦DCn⟧`; đơn vị nối và `⟦DCn⟧` luôn đứng ngoài đoạn khi ở ranh giới. (`seg-thu-3` luật 4; E1)
8. Câu dẫn ("... trong các trường hợp sau đây:") tách như câu thường; ghép câu dẫn với mục con là việc của lượt 2. Định nghĩa dạng công thức ("là tổng ... trừ đi ...") giữ một mệnh đề. (`gom_loi.md`, "không phải lỗi")

### 9.4. Tập đơn vị nối (đóng)
và, hoặc, hay, nhưng, thì, mà, nếu, khi, sau khi, trước khi, trường hợp, trong trường hợp, trong trường hợp này, trừ, trừ trường hợp, do, để, nhằm. (`seg-thu-3` cộng E1, E2, E3; so khớp không phân biệt hoa thường.) "do" có trong tập chỉ để "Do" mở đầu câu (E2) được đứng ngoài đoạn; "do" không thuộc luật 5, và "do X ban hành" theo luật 3. Có trong tập chỉ nghĩa là được đứng ngoài đoạn; chữ đó giữa một đoạn (danh sách "A và B", "các trường hợp sau đây", "do Bộ trưởng ban hành") vẫn nằm trong đoạn. Tần suất trong 993 câu BLLĐ: "khi" (không kể sau/trước khi) 94, "để" 75, "Trường hợp" đầu câu 68, "trừ" 49, "nếu" 42, "trong trường hợp" 34, "sau khi" 19, "trước khi" 17, "nhằm" 14.

### 9.5. Đầu ra và máy kiểm
Khuôn như `seg-thu-3`: `{"doan":[{"id":"m1","loai":"menh_de","chu":"..."},{"id":"c1","loai":"dung_chung","chu":"...","ap_cho":["m1"]}]}`. Máy chèn đoạn `{"id":"d1","loai":"dan_chieu","chu":<khối gốc>}` vào chỗ `⟦DCn⟧`, và ghi kèm mỗi đoạn khoảng token cùng các đơn vị nối ở khe ngay trước nó.

Lỗi (câu hỏng): không phải JSON; đoạn không khớp nguyên văn theo thứ tự; khe giữa hai đoạn có chữ ngoài dấu câu, đơn vị nối, `⟦DCn⟧`; đoạn mở đầu bằng đơn vị nối, hay kết thúc bằng đơn vị nối khác "do", "trừ", "trường hợp"; đoạn chứa `⟦DCn⟧`; ranh giới cắt ngang một đơn vị nối hay chữ dẫn chiếu của 1.2; `ap_cho` rỗng hoặc trỏ id không phải `menh_de`; câu có `⟦DCn⟧` mà đầu ra thiếu nó.
Cờ (không chặn, để đọc tay): `dung_chung` áp cho đúng một mệnh đề; `menh_de` từ 15 chữ.
Máy không kiểm được: tách hay giữ có đúng luật 1-5 không. Phần đó đo bằng gold.

### 9.6. Gold và đo
- 60 câu, user duyệt từng câu (A59): 40 phát triển, 20 kiểm tra. Cả 60 câu lấy từ **đơn vị** chưa dùng để chỉnh lời nhắc (A59), tức loại mọi đơn vị agent đã đọc đầu ra hay đã nêu tên: mẫu đọc tay trong `seg_thu_3/tong_hop.json` (`mau`), 62 câu của `scope_phrase_labels.tsv`, đơn vị nêu tên trong `gom_loi.md`, `decisions.md`, mục này, bộ khó (`data/eval_dev/proposition_panel.json`) và ví dụ lời nhắc. Đếm thô (24/11): loại 253, còn khoảng 628/881 đơn vị.
- [THÊM] Thành phần mỗi nhóm (phát triển, kiểm tra): khoảng 1/3 câu không có đơn vị nối nào của mục 9.4 (câu thường), 2/3 câu có đơn vị nối, trong đó có câu dẫn (ít nhất 2 ở phát triển, 1 ở kiểm tra). Máy chọn ngẫu nhiên có hạt giống cố định trong từng tầng, không chọn tay. Vì sao: tỉ lệ khớp phụ thuộc vào thành phần (376/993 câu chỉ có một mệnh đề theo `seg_thu_3`); bộ toàn câu thường làm ngưỡng dễ đạt giả. Cái giá: tỉ lệ đo được không phải tỉ lệ trên cả kho.
- Gold ghi đúng khuôn mục 9.5 (sau khi chèn `dan_chieu`), chạy qua máy kiểm trước khi user duyệt.
- Duyệt (user chốt 24/11): agent soạn cả 60 câu, chạy máy kiểm, gửi một bảng; câu có ca khó (vế lồng, chủ ngữ, "để", bổ ngữ luật 4) đánh dấu để user đọc kỹ, câu còn lại user đọc lướt. Cái giá: câu đọc lướt mà agent soạn sai có thể lọt.
- Đo: số câu khớp hoàn toàn (cùng ranh giới, `loai`, `ap_cho`); phụ: độ chính xác và độ phủ của ranh giới (vị trí token).
- [THÊM] Ngưỡng: phát triển ≥ 34/40 câu khớp hoàn toàn; kiểm tra chạy MỘT lần, ≥ 16/20. Không đạt thì dừng và báo, không sửa lời nhắc rồi chạy lại trên câu kiểm tra.

### 9.7. Đã chốt (24/11; phần nào user duyệt, phần nào chỉ advisor soát: xem A60)
- D86.K2.c "Không tuân thủ đúng quy trình thương lượng, ký kết thỏa ước lao động tập thể": "thương lượng, ký kết" mô tả "quy trình" (đối tượng khác), luật 3, KHÔNG tách; cả câu một mệnh đề. `seg-thu-3` tách là sai.
- D73.K1: vế "trong trường hợp ..." lồng giữa mệnh đề chính thì giữ trong mệnh đề (luật 5 (c)); không đổi khuôn (user chốt 24/11). Cái giá: mệnh đề dài, lượt 2 phải đánh span điều kiện bên trong. Quy mô: trong 46 `menh_de` của `seg_thu_3` có chữ đánh dấu của luật 5 ở giữa, agent đọc cả 46, chỉ D73.K1 là vế lồng thật; còn lại là vế đứng cuối (luật 5 tách) hoặc trùng âm ("khấu trừ", "trừ đi", "nếu có"). Không thấy được vế lồng mà LLM đã cắt thành mảnh.
- D46.K3: "để tính trợ cấp thôi việc" mô tả "Tiền lương", không tách (luật 1, vế "trừ khi"). Cái giá: ranh giới "mục đích" với "mô tả danh từ" vẫn cần LLM hiểu nghĩa; chưa đếm số câu dạng này.
- "Trong trường hợp này": một đơn vị nối (mục 9.4); lượt 2 nối với câu trước.
- "(trong) trường hợp quy định tại X" không có "trừ": giữ trong đoạn (luật 5 (b)).
- Chủ ngữ dùng chung (user chốt 24/11): tách thành `dung_chung` chỉ khi nó đứng trước từ hai mệnh đề trở lên mà nó là chủ ngữ thật (luật 6); `ap_cho` gồm các mệnh đề SAU nó mà nó là chủ ngữ, kể cả sau chữ nối; không bao giờ gồm mệnh đề đứng trước nó. Ví dụ neo cho gold (`[ ]` là khe):
  - D113.K4#1: c1 "Người sử dụng lao động" → m1, m2, m3; m1 "có trách nhiệm quy định lịch nghỉ hằng năm" [sau khi] m2 "tham khảo ý kiến của người lao động" [và] m3 "phải thông báo trước cho người lao động biết".
  - D113.K4#2: c1 "Người lao động" → m1, m2, m3; m1 "có thể thỏa thuận với người sử dụng lao động" [để] m2 "nghỉ hằng năm thành nhiều lần" [hoặc] m3 "nghỉ gộp tối đa 03 năm một lần".
  - D85.K2: c1 "Doanh nghiệp thành viên của thỏa ước lao động tập thể ngành, thỏa ước lao động tập thể có nhiều doanh nghiệp" → m1, m3; m1 "được rút khỏi thỏa ước lao động tập thể" [khi] m2 "có sự đồng thuận của tất cả ..." [trừ trường hợp] m3 "có khó khăn đặc biệt trong hoạt động sản xuất, kinh doanh".
  - D118.K3: [Trước khi] m1 "ban hành nội quy lao động" [hoặc] m2 "sửa đổi" m3 "bổ sung" c1 "nội quy lao động" → m2, m3; m4 "người sử dụng lao động phải tham khảo ý kiến ... đối với nơi có ..." (chủ ngữ đứng sau m1-m3 và chỉ đứng trước một mệnh đề, nên không tách).
- "Do ..." (user chốt 24/11): hai câu (D36.K1.c, D48.K1.d) đều là "Do <danh sách nguyên nhân> ..." không có "nên"; "Do" đứng ngoài đoạn, phần sau theo luật thường. Không cần thêm "nên".
