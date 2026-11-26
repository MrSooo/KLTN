# Scientific Paper Writing Cookbook

Nov 16, 2026 · @Tú Lê

## 0. Cách dùng tài liệu này

Cookbook này rút cách viết từ ba bài mẫu, kể cả những chỗ ba bài viết chưa tốt. Mỗi kỹ thuật có: khi nào dùng, mẫu câu để thay chữ, và ví dụ chỉ vị trí trong bài.

**Nguồn đã đọc.** Toàn văn bản .md trong Project: `PAPER_02` (Dang et al., *A Practical Approach to Leverage Knowledge Graphs for Legal Query*), `PAPER_03` (Dang et al., *Integrating LLM with Symbolic Reasoning for KG-Driven Legal Query System*), `PAPER_04` (Dang et al., *Neuro-Symbolic Framework for Verified Legal Inference of RAG-based AI*). Số trang lấy theo đầu trang chạy (running header) trong bản .md. Muốn trích vào luận văn thì đối chiếu lại PDF.

**Ký hiệu.** P2/P3/P4 = Paper 2/3/4. §3.2 = mục 3.2. Eq.(5) = công thức số 5. Nhãn: **\[Bài tự nêu\]** là điều bài viết ra; **\[Suy luận\]** là nhận xét của tôi về cách viết.

**Học gì, tránh gì ở từng bài** \[Suy luận\]:

| Bài | Đáng học | Không làm theo |
| --- | --- | --- |
| P2 | Mỗi thuật toán có Input/Output/Steps (§4.3). Nêu ngưỡng α = 0.6 kèm cách chọn (§3.2, tr.5). Thống kê dữ liệu cụ thể (§5.2). | Câu giới thiệu lộ trình ghi sai số section (tr.2). Nói module có 5 thành phần nhưng chỉ liệt kê 4 (§4.4). Câu “các chức năng chính gồm:” bỏ trống (§4.2, tr.7). Gọi Figure 3 là kiến trúc trong khi chú thích hình nói khác. Không có baseline dù phần mở đầu hứa so sánh. |
| P3 | Luôn đi Definition → Example → công thức (Def 3.2 + Ex 3.1; Def 3.4 + Ex 3.2 + Eq.11). Viết cả pipeline thành một chuỗi hàm (Eq.7). Có “where” sau mỗi công thức. | Ngưỡng τ không bao giờ được gán giá trị (Eq.4, 14). Eq.16 định nghĩa Infer bằng chính chữ “inferred”. Có ô 96.36% trên 22 câu, tỷ lệ không thể có (k/22). Tóm tắt nói “vượt trội” trong khi hai loại câu hỏi hoà với baseline (Table 1). |
| P4 | Related Work chia theo hướng tiếp cận; mỗi đoạn kết bằng hạn chế dẫn sang đoạn sau (§2). Mô hình cập nhật tri thức thành biến đổi trạng thái KB\_{t+1} = T\_Δ(KB\_t) (Eq.5–6). Viết điều kiện hợp lệ bằng một biểu thức gọn (Eq.8). Giải thích vì sao bỏ thước đo tương đồng văn bản (§5.3). | Kiểu hàm của δ\_del ghi D × Cla → D nhưng thân hàm lại trừ đi một tập triple (Def 3.3). Không nói ba luật Lex Superior/Specialis/Posterior xếp ưu tiên ra sao khi chúng mâu thuẫn nhau (§4.3). Mô tả thiết lập baseline quá ít (§5.3). |

Nguyên tắc dùng: lấy **khuôn** của phần “Đáng học”; dùng phần “Không làm theo” làm danh sách tự kiểm (Mục 8).

## 1. Paper Structure

Cả ba bài dùng cùng một khung 6 phần cho bài hội nghị 12–14 trang (LNCS). Khoảng một nửa số trang dành cho hai section phương pháp.

| # | Section | Việc phải làm | Tỷ lệ trang (ước từ P3, P4) \[Suy luận\] | Ví dụ |
| --- | --- | --- | --- | --- |
| 1 | Introduction | Bối cảnh → hạn chế của cách hiện có → đề xuất → nơi kiểm chứng → lộ trình bài | \~12% | P4 §1: 3 đoạn (luật cần suy luận; symbolic cứng và LLM ảo giác; hybrid + 2 miền thử) |
| 2 | Related Work | Chia theo hướng tiếp cận, mỗi hướng kết bằng hạn chế | \~10% | P4 §2: 4 tiểu mục Rule-based → NLP → KG → LLM/RAG |
| 3 | Mô hình tri thức / Problem formulation | Định nghĩa đối tượng toán học mà các section sau thao tác lên | \~25% | P3 §3: Def 3.1 KB → Def 3.2 fact → trích xuất → Def 3.4 luật |
| 4 | Phương pháp / cơ chế xử lý | Các giai đoạn xử lý trên đối tượng của mục 3 | \~25% | P3 §4: 4.1 hiểu câu hỏi → 4.2 suy diễn → 4.3 sinh câu trả lời |
| 5 | Experiments | Dữ liệu → xây KB → bộ câu hỏi → cách chấm → kết quả → diễn giải | \~22% | P4 §5.1–5.4 |
| 6 | Conclusion & Future work | 1 đoạn đóng góp, 1 đoạn hướng tiếp | \~5% | P3 §6 |

**Quy tắc tách section 3 và 4.** Section 3 trả lời “dữ liệu/tri thức được biểu diễn thế nào”. Section 4 trả lời “làm gì trên biểu diễn đó”. P3 và P4 đều tách như vậy. Mọi ký hiệu dùng ở section 4 phải được định nghĩa ở section 3.

**Quy tắc subsection.** Mỗi subsection là một bước trong pipeline, đặt tên bằng danh từ chỉ việc làm. Ví dụ P3 §4.1 “Extracting the Main Content of the Question”, §4.2 “Inference on the knowledge graph”. Thứ tự subsection = thứ tự dữ liệu chạy qua hệ thống = thứ tự các khối trong hình tổng quan.

**Câu lộ trình cuối Introduction.** Mẫu:

> The rest of this paper is organized as follows. Section 2 reviews \[hướng A, B\]. Section 3 defines \[đối tượng\]. Section 4 presents \[cơ chế\]. Section 5 reports \[thí nghiệm trên dữ liệu X\]. Section 6 concludes.

Viết câu này **sau cùng**, khi các section đã cố định. P2 viết trước nên số section không khớp (tr.2: nói Section 2 là làm gọn đồ thị, nhưng Section 2 thật là Related work).

## 2. Idea Development

Một ý tưởng thành bài báo khi mỗi hạn chế nêu ở đầu bài có đúng một cơ chế giải quyết nó ở phần phương pháp, và một phép đo chứng minh nó ở phần thí nghiệm. P4 làm tốt nửa đầu của chuỗi này và bỏ nửa sau.

### 2.1 Chuỗi lập luận 5 bước

1. **Yêu cầu của miền.** Một đặc tính bắt buộc của bài toán. P4 §1: truy vấn pháp luật cần liên kết nhiều văn bản và cần suy luận, không chỉ tìm từ khoá.
2. **Hướng A: mạnh ở X, yếu ở Y.** P4 §1 đoạn 2: hệ symbolic minh bạch nhưng cứng và khó mở rộng.
3. **Hướng B: mạnh ở Y, yếu ở X.** Cùng đoạn: LLM linh hoạt nhưng ảo giác và là hộp đen.
4. **Đề xuất = giữ X của A và Y của B.** P4 §1 đoạn 3, P3 §1 đoạn 3.
5. **Kiểm chứng ở đâu và đo bằng gì.** P4 nêu hai miền thử (luật Đất đai VN, luật xe cơ giới Ấn Độ bản Assamese).

### 2.2 Ma trận truy vết (bắt buộc lập trước khi viết)

Mỗi dòng phải đủ 4 cột. Dòng thiếu cột cuối là một tuyên bố chưa được chứng minh.

| Hạn chế (Intro/RW) | Cơ chế (Method) | Phép đo (Experiment) | Kết quả nào sẽ bác bỏ |
| --- | --- | --- | --- |
| P4: LLM ảo giác trích dẫn luật | Trả lời từ đường suy luận Π trên KG (§4.2) | P4 không đo riêng tỷ lệ trích dẫn sai; chỉ có điểm IRAC tổng | Tỷ lệ điều luật bịa hoặc sai không thấp hơn baseline |
| P4: xung đột giữa các quy định | Trọng tài Ω với 3 nguyên tắc Lex (§4.3) | Không có tập câu hỏi xung đột riêng | Trên câu xung đột, bỏ Ω mà điểm không giảm |
| P4: cập nhật luật tốn kém | Toán tử δ\_ins/upd/del (§3.3) | Không đo | Sau cập nhật, KB vẫn trả về điều đã bãi bỏ |

&#91;Suy luận\] Cột 3 cho thấy lỗ hổng thường gặp: P3 và P4 đều viết kết luận kiểu “xoá bỏ ảo giác” (P4 §6) mà không có phép đo nào cho ảo giác. Khi làm bài của mình, điền ma trận này trước; cơ chế nào không có phép đo thì hoặc thêm thí nghiệm (ablation), hoặc hạ tuyên bố xuống mức “hỗ trợ”.

### 2.3 Chọn động từ theo mức bằng chứng

| Đã có gì | Động từ được dùng |
| --- | --- |
| Chưa chứng minh khác công trình gần nhất | apply, adapt, extend |
| Có khác biệt kỹ thuật, chưa đo | propose, introduce |
| Có số đo so với baseline mạnh | improves X by N points on D |
| Có ablation tách được đóng góp từng thành phần | component C accounts for N points |

Tránh “eliminate”, “guarantee”, “absolute”. P4 dùng “absolute legal reliability” (§4.3) cho một hệ đạt 73.13% trên bộ câu tiếng Việt (Table 4); hai điều này mâu thuẫn nhau trong cùng một bài.

### 2.4 Mẫu đoạn đóng góp (cuối Introduction)

> The contributions of this paper are threefold. (i) We formalize \[đối tượng\] as \[cấu trúc\], which makes \[tính chất\] explicit (Section 3). (ii) We \[apply/extend\] \[kỹ thuật\] to \[bài toán\], differing from \[công trình gần nhất\] in \[một điểm cụ thể\] (Section 4). (iii) On \[bộ dữ liệu, N mẫu\], \[hệ\] reaches \[số\] versus \[số\] for \[baseline mạnh\] (Section 5).

Mỗi đóng góp trỏ tới một section. Câu (ii) bắt buộc nêu tên công trình gần nhất. Cả ba bài mẫu không có đoạn này; đây là chỗ nên làm khác ba bài.

## 3. Academic Paragraph Writing

Mỗi đoạn có một việc duy nhất và câu đầu nói việc đó. Ba bài dùng bốn loại đoạn lặp lại; mỗi loại có khuôn riêng.

### 3.1 Bốn loại đoạn và khuôn

**(a) Đoạn nhận xét một công trình** (Related Work). Khuôn: *ai làm gì → bằng cách nào → đạt số bao nhiêu → nhưng thiếu gì so với bài toán của mình*. P2 §2 đoạn về VnLawBERT \[6\] theo đúng khuôn: nêu phương pháp, F1 87% rồi 90.6% sau khi tiền huấn luyện, rồi ba hạn chế (cần nhiều dữ liệu, khó cập nhật, khó xử lý quan hệ phức tạp).

> &#91;Author\] \[verb: proposed/introduced\] \[method\] for \[task\], which \[mechanism in one clause\]. On \[dataset\], it reaches \[metric = value\]. However, it \[limitation tied to our requirement\], which makes it unsuitable when \[our setting\].

**(b) Đoạn nhóm hướng tiếp cận.** Dùng khi có nhiều công trình cùng loại. P4 §2 mở mỗi đoạn bằng tiêu đề in nghiêng (run-in heading) như *Knowledge Graphs.*; câu cuối nêu điểm yếu, và điểm yếu đó là lý do của hướng ở đoạn sau.

> *\[Approach family\].* \[What it does, 1 sentence\] \[refs\]. Its main strength is \[X\] \[ref\]. However, \[weakness\], because \[reason\]. \[Optional: this motivated (next family)\].

**(c) Đoạn mở một bước phương pháp.** Khuôn: *bước này nhận gì → trả gì → vì sao cần*. P4 §4.1 câu đầu: ánh xạ từ không gian ngôn ngữ tự nhiên L\_NL sang không gian ký hiệu S. Một câu đã nêu đủ đầu vào, đầu ra và vai trò.

> This stage maps \[input, with symbol\] to \[output, with symbol\]. It is needed because \[what fails without it\]. It consists of \[k\] steps: \[step 1\], \[step 2\], and \[step 3\].

**(d) Đoạn diễn giải kết quả.** Khuôn: *con số → so với gì → chỗ nào khác biệt lớn nhất → vì sao (gắn với cơ chế) → chỗ nào không hơn*. P4 §5.4 làm được bước “LLM ổn với câu đơn giản, hệ đề xuất hơn ở câu cần suy luận hệ thống”, nhưng không chỉ ra loại câu nào ứng với câu cần suy luận. P3 §5.4 bỏ qua việc Kind 2 và Kind 6 hoà với chatbot Bộ Tư pháp.

> &#91;System\] reaches \[value\] on \[split\], against \[value\] for \[strongest baseline\]. The gap is largest on \[subset\] (\[+N points\]), where \[property of subset\] requires \[mechanism of ours\]. On \[other subset\] the two systems tie (\[value\]), which suggests \[honest reading\].

### 3.2 Chuyển tiếp giữa các đoạn

| Quan hệ với đoạn trước | Cách nối | Ví dụ |
| --- | --- | --- |
| Bước tiếp theo trong pipeline | Nhắc lại đầu ra của bước trước làm chủ ngữ | P3 §4.2 mở bằng: sau khi biểu diễn câu hỏi thành triple (s, p, o), hệ thực hiện truy vấn… |
| Hạn chế dẫn tới hướng mới | “To overcome \[hạn chế vừa nêu\], …” | P3 §2 đoạn RAG mở bằng “To overcome the shortcomings of LLM” |
| Chuyển từ bối cảnh sang đề xuất | “Thus, this section proposes…” sau đoạn liệt kê vấn đề | P4 §4 đoạn 2 |
| Từ định nghĩa sang ví dụ | “Example N.M:” + một câu tự nhiên + biểu diễn hình thức | P3 Example 3.1, 3.2 |

### 3.3 Quy tắc câu

- Một câu, một mệnh đề. Câu có “not only… but also” thường đang ghép hai ý chưa được chứng minh.
- Câu nêu hạn chế phải có trích dẫn hoặc số. P3 §2 viết “studies have shown that LLMs have inherent problems” mà không có trích dẫn ở câu đó.
- Gọi một thứ bằng một tên duy nhất trong toàn bài. P3 dùng xen “knowledge set”, “knowledge base”, “KB” cho các đối tượng khác nhau.

## 4. Methodology Writing

Phần phương pháp đi theo 6 lớp, từ trừ tượng xuống cụ thể. Ba bài mẫu có lớp 1, 4, 5, 6 và thiếu lớp 2, 3; đó là chỗ người phản biện sẽ hỏi.

1. **Tách bài toán thành bài toán con.** P2 §4.1 tách thành Problem 1 (phân loại và xác định ngữ nghĩa câu hỏi) và Problem 2 (tìm tri thức liên quan). Mỗi bài toán con sau đó có một thuật toán riêng (Algorithm 4.1, 4.2).
2. **Phát biểu hình thức.** Đầu vào, đầu ra, tiêu chí đúng, viết bằng ký hiệu. Ba bài không có mục “Problem Definition” riêng; người đọc phải tự ghép từ Eq.12 và Eq.17 của P3.
3. **Giả định.** Điều phương pháp cần để chạy đúng. Ví dụ ngầm trong P4: văn bản mới nêu rõ điều nào bị bãi bỏ; Rank, Specificity, Date đều tính được cho mọi điều luật. Không bài nào viết ra.
4. **Tổng quan: một hình + một công thức ghép.** P3 Fig.1 đi cùng Eq.7 (D → D′ → S → F → G). P4 Eq.3 gói cả bước xây KB thành một ánh xạ LLM: D\_NL → KG có ontology O làm ràng buộc.
5. **Mỗi giai đoạn một subsection**, theo khuôn ở 4.2.
6. **Phần xử lý ngoại lệ và trường hợp biên.** P2 §4.3: khi câu hỏi thiếu chủ ngữ hoặc tân ngữ, điền dấu ‘\*’ và so khớp bằng các thành phần còn lại; có xét quan hệ is-a (“xe máy” → “mô tô”, “xe gắn máy”). Đoạn này ngắn nhưng trả lời trước câu hỏi của phản biện.

### 4.1 Mẫu Problem Definition (đặt đầu Section 3 hoặc 4)

> **Problem.** Given \[input object, symbol, its type\] and \[resource, e.g. KB G = (V, E, D)\], the task is to produce \[output, symbol, type\] such that \[correctness condition\]. We assume (A1) \[assumption\], (A2) \[assumption\]. Assumption (A1) fails when \[case\]; Section 6 discusses this case.

Câu cuối nêu luôn trường hợp giả định không đúng. Phản biện sẽ tìm ra nó; tự nêu trước thì ít bị trừ điểm hơn.

### 4.2 Khuôn một subsection cơ chế

| Phần | Nội dung | Ví dụ trong bài |
| --- | --- | --- |
| Câu mở | Giai đoạn nhận gì, trả gì | P4 §4.1: ánh xạ L\_NL → S |
| Lý do | Cái gì hỏng nếu bỏ bước này | P2 §3.2: bỏ triple vô nghĩa và gộp triple tương đương để giảm kích thước đồ thị |
| Các bước | Đánh số “Step 1, Step 2”, mỗi bước một công thức hoặc một thuật toán | P3 §3.2 Step 1–3 với Eq.1–6 |
| Tiêu chí quyết định | Điều kiện chấp nhận/loại, có ngưỡng và giá trị | P2: α = 0.6, chọn từ cụm từ đồng nghĩa được chuyên gia xác nhận |
| Ví dụ | Một câu thật chạy qua bước này | P3 Example 3.2: điều vượt đèn đỏ, không phải xe ưu tiên |
| Câu chuyển | Đầu ra được bước sau dùng ra sao | P3 §4.2: “K\_init” là đầu ra của bước so khớp |

### 4.3 Phân biệt viết phương pháp và viết tài liệu hệ thống

&#91;Suy luận\] P2 §4.2 “Requirements of Platform” liệt kê yêu cầu phần mềm (lưu trữ, khả năng mở rộng) và thư viện dùng (VnCoreNLP). Đó là nội dung của báo cáo kỹ thuật. Kiểm tra bằng câu hỏi: nếu thay thư viện khác, đoạn này có cần viết lại không? Nếu có, chuyển nó xuống mục Implementation (Mục 6) hoặc phụ lục.

## 5. Equation Writing Cookbook

Mỗi công thức trong bài là một câu của lập luận: nó phải được dẫn vào, được giải nghĩa, và được dùng lại ở chỗ khác. Công thức không được dùng lại ở đâu (trong thuật toán, công thức sau, hay thí nghiệm) thì bỏ.

### 5.0 Khung 6 phần cho mọi công thức

| # | Phần | Câu mẫu | Ví dụ |
| --- | --- | --- | --- |
| 1 | Dẫn nhập: nói công thức sắp làm gì | “To \[mục đích\], we define \[tên\] as follows:” | P3 trước Eq.4: các câu được ánh xạ sang không gian vector, rồi tính độ tương đồng cosine |
| 2 | Công thức hiển thị, có số | một dòng, đánh số (n) | P3 Eq.4 |
| 3 | Mệnh đề “where”: mọi ký hiệu mới | “where x is …, y ∈ Y is …” | P3 sau Eq.8: F\_C, F\_E, F\_L, F\_O, mỗi tập một gạch đầu dòng |
| 4 | Diễn giải: ý nghĩa, không đọc lại ký hiệu | “Intuitively, … / This ensures that …” | P4 sau Eq.8: một kết luận chỉ hợp lệ khi không có ngoại lệ nào chứng minh được |
| 5 | Giá trị tham số và cách chọn | “We set τ = …, chosen by … (Section 5)” | P2 α = 0.6. P3 thiếu: τ không có giá trị |
| 6 | Cầu nối: công thức này được dùng ở đâu | “The output \[ký hiệu\] is the input of Algorithm k / Eq.(m).” | P3: Q ở Eq.15 là đầu vào của Algorithm 1 |

### 5.1 Bảng ký hiệu và ba lỗi ký hiệu trong bài mẫu

Lập bảng ký hiệu trước khi viết công thức đầu tiên (bảng này có thể không in ra bài). Quy ước: chữ hoa nghiêng = tập; chữ thường = phần tử; chữ hoa thư pháp (𝒯, ℒ) = hàm hoặc toán tử; chỉ số dưới = thành viên; chỉ số trên = phiên bản/thời điểm.

| Lỗi | Vị trí | Sửa |
| --- | --- | --- |
| Một ký hiệu hai nghĩa | P3: s\_ij là mệnh đề con (Eq.3), s là chủ ngữ triple (Def 3.2) | đổi mệnh đề con thành c\_ij hoặc κ\_ij |
| Một đối tượng hai kiểu | P3: Def 3.2 nói fact là một tập triple; Def 3.3 viết f\_i = (s\_i, p\_i, o\_i) là một triple | chọn một: fact ⊆ E × R × E |
| Tên trùng giữa hai tập | P4: R là tập quan hệ trong Def 3.1, rồi là tập triple trong đoạn trước Def 3.3 | giữ R cho quan hệ, T cho triple |

### 5.2 Dạng A — Definition (định nghĩa cấu trúc bằng bộ n-phần tử)

**Khi nào.** Lần đầu giới thiệu đối tượng mà cả bài thao tác lên: KB, đồ thị, luật, trạng thái.

**Dẫn dắt.** Một câu nói đối tượng cần biểu diễn được những gì (P4 §3.2: vừa cấu trúc phân cấp vừa ngữ nghĩa thuật ngữ). Sau đó mới đưa bộ phần tử.

**Trình bày.** “Definition k.” + bộ phần tử + danh sách gạch đầu dòng, mỗi thành phần một dòng có kiểu toán học. P3 Def 3.1 làm tốt: G = (V, E, D), với E ⊆ V × V và D: V ∪ E → DocID — có cả kiểu của D, không chỉ lời mô tả.

**Diễn giải và cầu nối.** Theo ngay sau bằng một ví dụ cụ thể (P3 Example 3.1: “người lái xe máy và dùng điện thoại” thành hai triple nối bằng ∧).

```latex
\textbf{Definition 1.} A \emph{[tên]} is a tuple \mathcal{X} = (A, B, \phi), where
(i) A is a finite set of [phần tử];
(ii) B \subseteq A \times L \times A is a set of labelled [quan hệ], L being the label set;
(iii) \phi : A \cup B \to \mathcal{P}(\mathit{Src}) maps each element to its source units.
```

Lỗi cần tránh: P2 Eq.1 viết K = (C, R, Rules) + (Concept, Rela). Dấu “+” giữa hai bộ không có nghĩa toán học. Viết K = (C, R, Rules, Concept, Rela), hoặc nói rõ đây là cặp (M, G).

### 5.3 Dạng B — Mathematical model / ánh xạ có kiểu

**Khi nào.** Một bước xử lý (kể cả bước do LLM làm) biến đối tượng loại này thành loại khác.

**Trình bày.** Chữ ký hàm (signature) trước, quy tắc sau. P3 Eq.3 viết L\_split: δ\_i ↦ {s\_i1, …, s\_ik}; P4 §4.1 viết σ: E\_raw → O. Gán tên hàm cho bước LLM giúp các công thức sau nhắc tới nó như một đối tượng.

**Kiểm tra kiểu (bắt buộc).** Miền giá trị trong chữ ký phải trùng với kiểu của vế phải. P4 Def 3.3 ghi δ\_del: D × Cla → D (trả về văn bản) nhưng vế phải D\_old \\ T\_c là văn bản trừ đi tập triple. Sửa: cho toán tử tác động lên tập triple của KB.

```latex
\delta_{\mathrm{del}} : 2^{T} \times \mathit{Cla} \to 2^{T}, \qquad
\delta_{\mathrm{del}}(T^{t}, c) = T^{t} \setminus T_c,
\quad T_c = \{\tau \in T^{t} \mid \mathrm{src}(\tau) = c\}
```

**Câu mẫu.** “We model \[bước\] as a function f: X → Y. Given x ∈ X, f returns \[mô tả y\]. In our implementation f is realised by \[LLM/thuật toán\], with the prompt given in Appendix A.” Câu cuối tách định nghĩa toán học khỏi cách cài đặt.

### 5.4 Dạng C — Pipeline composition (ghép chuỗi)

**Khi nào.** Sau khi đã định nghĩa từng bước, hoặc ở đầu section để hứa trước các bước. P3 Eq.7 đặt sau ba bước để tổng kết; Eq.12 đặt đầu §4.1 để hứa trước. Cả hai cách đều dùng được; chọn một cách và giữ nguyên trong bài.

```latex
D \xrightarrow{\;\mathcal{P}\;} D' \xrightarrow{\;\mathcal{L}_{\mathrm{split}}\;} S
  \xrightarrow{\;\mathcal{F}_{\mathrm{extract}}\;} F \xrightarrow{\;\mathcal{B}\;} G,
\qquad G = (\mathcal{B} \circ \mathcal{F}_{\mathrm{extract}} \circ \mathcal{L}_{\mathrm{split}} \circ \mathcal{P})(D)
```

**Quy tắc.** Mỗi mũi tên mang tên một hàm đã định nghĩa hoặc sẽ định nghĩa ngay sau. P3 Eq.7 có mũi tên cuối tên “Knowledge Extraction” nhưng không có hàm nào mang tên đó (F\_extract đã là bước trước). Mỗi nút phải trùng một khối trong hình tổng quan.

### 5.5 Dạng D — Scoring function (hàm tính điểm)

**Khi nào.** Cần một số để xếp hạng hoặc lọc: độ tương đồng, độ tin cậy, độ liên quan.

**Dẫn dắt.** Nói cái gì cần được đo và vì sao (P3: kiểm tra câu tách ra không làm sai nghĩa câu gốc). Đưa thành phần dựng sẵn (embedding) thành công thức riêng trước (P3 Eq.5) rồi mới đến điểm số (Eq.4).

**Sau công thức phải có 3 thứ.** (1) Miền giá trị của điểm và chiều tốt (cao hơn = giống hơn). (2) Cách điểm được dùng (ngưỡng, top-k). (3) Mô hình embedding cụ thể và giá trị ngưỡng. P3 có (2), thiếu (1) và (3).

```latex
\mathrm{sim}(x, y) = \frac{\mathbf{v}(x) \cdot \mathbf{v}(y)}{\lVert \mathbf{v}(x) \rVert \, \lVert \mathbf{v}(y) \rVert} \in [-1, 1],
\qquad \mathbf{v}(\cdot) = \mathrm{Embed}_{\theta}(\cdot)
```

> where Embed\_θ is \[mô hình, phiên bản\]. A candidate y is kept iff sim(x, y) ≥ τ. We set τ = \[giá trị\], the value that maximised \[chỉ số\] on a held-out set of \[N\] pairs labelled by \[ai\] (Section 5.x).

### 5.6 Dạng E — Constraint / acceptance condition (ràng buộc)

**Khi nào.** Phát biểu điều kiện để một ứng viên được chấp nhận hoặc để một ánh xạ hợp lệ.

**Trình bày.** Dùng lượng từ ∀/∃ và kéo theo ⇒. P4 Eq.7 là mẫu gọn: với mọi cạnh e = (s, p, o) của đồ thị truy vấn, ảnh f(e) phải là cạnh của KG.

**Diễn giải.** Nói ràng buộc này loại đi điều gì. Nếu ràng buộc chặt (yêu cầu nhãn quan hệ trùng hẳn) hay lỏng (P3 Algorithm 2 cho p′ ≃ p) thì phải định nghĩa ≃. P3 không định nghĩa ≃.

```latex
f : V_q \to V_{KG} \ \text{injective, such that} \quad
\forall (s, p, o) \in E_q : \ \exists p' \in R \ \big(f(s), p', f(o)\big) \in E_{KG} \wedge p' \simeq p,
\quad p' \simeq p \iff \mathrm{sim}(p', p) \ge \tau_r
```

Câu nối: “The set of all such mappings, M(G\_q), is the input of the reasoning stage (Section 4.3).”

### 5.7 Dạng F — Logical rule (luật suy diễn, có ngoại lệ)

**Khi nào.** Biểu diễn điều kiện → hệ quả, đặc biệt khi có ngoại lệ.

**Trình tự 4 bước của P3 §3.3 (nên chép khuôn).** (1) Eq.8: dạng tổng quát của luật. (2) Một gạch đầu dòng cho mỗi tập F\_C, F\_E, F\_L, F\_O. (3) Eq.9 và Eq.10 tách vế trái và vế phải, đặt tên cho từng vế. (4) Example 3.2: một câu luật thật → bốn tập fact → Eq.11 là luật cụ thể.

```latex
R_i : \Big(\bigwedge_{f \in F_C} f\Big) \wedge \neg\Big(\bigvee_{f \in F_E} f\Big)
  \;\Rightarrow\; \Big(\bigwedge_{f \in F_L} f\Big) \wedge \Big(\bigwedge_{f \in F_O} f\Big)
```

**Phải nói rõ ngữ nghĩa của ¬.** Phủ định cổ điển (chứng minh được là sai) khác phủ định do thất bại (không chứng minh được là đúng). P3 Eq.8 không nói dùng loại nào. P4 Eq.8 nói rõ là Negation as Failure:

```latex
\mathrm{Valid}(C) \iff \mathrm{Prove}(C) \wedge \neg\,\mathrm{Prove}(\mathrm{Exception}(C))
```

**Câu mẫu sau luật.** “Here ¬ denotes negation as failure: an exception blocks the conclusion only if it is derivable from the KB. Consequently, adding a fact can withdraw a conclusion, i.e. the inference is non-monotonic.” Câu cuối nối công thức với một tính chất hình thức có tên trong tài liệu.

**Hàm suy diễn phải có định nghĩa vận hành.** P3 Eq.16 viết K\_new = Infer(K\_init, R) rồi giải thích Infer là “tập tri thức mới được suy ra” — định nghĩa vòng. Thay bằng điểm bất động của toán tử hệ quả trực tiếp:

```latex
T_R(K) = K \cup \{\, \mathrm{head}(r) \mid r \in R,\ \mathrm{body}(r) \text{ holds in } K \,\},
\qquad \mathrm{Infer}(K_0, R) = T_R^{\,n}(K_0) \ \text{with } T_R^{\,n+1}(K_0) = T_R^{\,n}(K_0)
```

Kèm một câu về dừng: với R hữu hạn và không sinh hằng mới, dãy tăng và bị chặn nên dừng. Nếu có phủ định do thất bại, cần thêm điều kiện phân tầng (stratified) hoặc nêu ngữ nghĩa dùng (ví dụ answer set); đây là kết quả sách giáo khoa, phải trích nguồn chuẩn, không tự nhận.

### 5.8 Dạng G — Transformation / state update (biến đổi trạng thái)

**Khi nào.** Đối tượng thay đổi theo thời gian hoặc theo sự kiện: KB khi có luật mới, đồ thị sau khi làm gọn.

**Khuôn của P4 §3.3 (nên chép).** (1) Gọi trạng thái là KB\_t. (2) Eq.5: KB\_{t+1} = T\_Δ(KB\_t). (3) Eq.6: T\_Δ là hợp thành của các toán tử cơ bản δ\_n ∘ … ∘ δ\_1. (4) Def 3.3: mỗi toán tử cơ bản (bãi bỏ, sửa đổi, bổ sung) có chữ ký và vế phải. Cách này biến một mô tả bằng lời (“cập nhật khi luật đổi”) thành đối tượng kiểm tra được.

**Phần P4 còn thiếu.** Thứ tự các δ có ảnh hưởng kết quả không (xóa rồi thêm khác thêm rồi xóa). Phải nêu quy tắc sắp thứ tự, hoặc chứng minh các δ giao hoán khi chúng tác động lên các điều khác nhau.

```latex
KB^{t+1} = \mathcal{T}_{\Delta}(KB^{t}), \quad
\mathcal{T}_{\Delta} = \delta_n \circ \cdots \circ \delta_1, \quad
\delta_k \in \{\delta_{\mathrm{ins}}, \delta_{\mathrm{upd}}, \delta_{\mathrm{del}}\}
```

> The operators are applied in the order del → upd → ins. Operators acting on distinct clauses commute, so the result does not depend on the order within each group. After applying T\_Δ, every triple whose source clause was repealed by D\_new is absent from KB^{t+1} (Property 1).

Phát biểu thành “Property” như câu cuối tạo ra một điều thí nghiệm có thể kiểm tra (xem ma trận ở Mục 2.2).

### 5.9 Dạng H — Ordering / priority (quan hệ ưu tiên)

**Khi nào.** Chọn giữa các ứng viên mâu thuẫn theo tiêu chí không phải số đo liên tục.

**P4 §4.3** nêu ba nguyên tắc Lex Superior (cấp văn bản), Lex Specialis (độ cụ thể), Lex Posterior (ngày ban hành), mỗi nguyên tắc một bất đẳng thức. Thiếu: khi hai nguyên tắc cho kết quả ngược nhau thì nguyên tắc nào thắng. Ba bất đẳng thức riêng lẻ chưa tạo thành một thứ tự. Viết thành thứ tự từ điển (lexicographic) và nêu thứ tự ưu tiên:

```latex
\kappa(r) = \big(\mathrm{Rank}(r),\ \mathrm{Spec}(r),\ \mathrm{Date}(r)\big), \qquad
r_i \succ r_j \iff \kappa(r_i) >_{\mathrm{lex}} \kappa(r_j)
```

> We order the criteria as Superior > Specialis > Posterior. \[Nguồn pháp lý cho thứ tự này, ví dụ điều luật về áp dụng văn bản\].

&#91;Suy luận\] Thứ tự giữa ba nguyên tắc là vấn đề pháp lý có tranh luận; công thức chỉ đúng khi trích được quy định của hệ thống luật đang xét. Phần trong ngoặc phải do tác giả kiểm chứng.

### 5.10 Dạng I — Objective function (hàm mục tiêu)

**Khi nào.** Phương pháp chọn “cái tốt nhất” trong một tập. Ba bài mẫu không có hàm mục tiêu tường minh. P4 viết bằng lời rằng câu trả lời tối ưu có ưu tiên lớn nhất trong các đường suy luận (§4.3). Câu đó viết được thành một dòng:

```latex
\pi^{*} = \operatorname*{arg\,max}_{\pi \in \Pi_{\mathrm{valid}}(G_q)} \ \Omega(\pi), \qquad
\Pi_{\mathrm{valid}}(G_q) = \{\pi \in \Pi(G_q) \mid \mathrm{Valid}(\mathrm{concl}(\pi))\}
```

**Sau hàm mục tiêu phải có.** (1) Tập khả thi được định nghĩa bằng công thức nào ở trước (ở đây: Eq. của Valid). (2) Xử lý khi hòa (argmax trả nhiều phần tử). (3) Xử lý khi tập rỗng (hệ trả lời “không có căn cứ”; P2 §5.1 có nói trường hợp này bằng lời). (4) Cách tìm nghiệm và độ phức tạp, hoặc tham chiếu tới thuật toán.

Với mô hình học máy, dạng tương ứng là hàm mất mát: θ\* = argmin\_θ (1/|D|) Σ ℓ(f\_θ(x), y) + λ‖θ‖², kèm nêu ℓ, λ và cách chọn λ.

### 5.11 Dạng J — Evaluation metric (thước đo đánh giá)

**Khi nào.** Luôn luôn, nếu thước đo không phải loại chuẩn mà ai cũng biết. Ba bài mẫu không viết công thức cho thước đo. P2 và P3 báo “Accuracy” mà không nói thế nào là một câu trả lời “đúng”. P4 §5.3 mô tả cách chấm IRAC + Clarity bằng lời (một thành phần chỉ có điểm khi mọi chỉ báo của nó đều đạt). Mô tả đó viết thành công thức được \[Suy luận: dựng lại từ lời P4, không phải công thức của bài\]:

```latex
\mathrm{score}(a, q) = \frac{1}{|\mathcal{C}|} \sum_{c \in \mathcal{C}} \mathbb{1}\big[\forall k \in K_c(q):\ \mathrm{sat}(a, k)\big],
\quad \mathcal{C} = \{I, R, A, C, L\}, \qquad
\mathrm{Acc}(Q) = \frac{1}{|Q|} \sum_{q \in Q} \mathrm{score}(\mathrm{sys}(q), q)
```

> where K\_c(q) is the set of check items for component c of question q, written by \[ai, bao nhiêu người\]; sat(a, k) is judged by \[ai\], and agreement between judges is \[κ = …\] on \[N\] doubly-annotated questions.

**Hai điều phải nói rõ.** (1) Trung bình theo câu hay trung bình theo nhóm. P4 Table 4 dùng trung bình không trọng số của bốn nhóm có 57, 22, 27, 13 câu: 73.13% theo nhóm, còn theo câu là 87/119 = 73.11% \[Suy luận: số câu đúng 41, 17, 20, 9 suy ra từ tỷ lệ từng nhóm\]. Chênh nhỏ ở đây, nhưng có thể lớn khi các nhóm lệch nhau. (2) Tỷ lệ phải khớp với mẫu số. P3 Table 1: với 22 câu, giá trị có thể có là biểu thức k/22 (21/22 = 95.45%), nên 96.36% không thể xảy ra — trừ khi có điểm từng phần, mà bài không nói.

### 5.12 Dạng K — Công thức gắn với thuật toán

Thuật toán phải dùng lại ký hiệu của công thức, không đặt ký hiệu mới. P3 làm đúng: Algorithm 1 nhận Q từ Eq.15 và trả S; Algorithm 2 nhận S; Algorithm 3 nhận M. Mỗi dòng Input/Output trỏ về một công thức hoặc định nghĩa, người đọc có thể lần theo dữ liệu từ đầu đến cuối.

### 5.13 Bảng chọn dạng nhanh

| Muốn nói | Dạng | Ký hiệu chính | Bắt buộc kèm theo |
| --- | --- | --- | --- |
| “X gồm những gì” | A Definition | bộ (…), ⊆, kiểu hàm | ví dụ cụ thể |
| “Bước này biến X thành Y” | B Mapping | f: X → Y | kiểm tra kiểu; cài đặt bằng gì |
| “Các bước nối tiếp nhau” | C Composition | →, ∘ | khớp với hình tổng quan |
| “X giống Y bao nhiêu” | D Scoring | sim, score | miền giá trị, ngưỡng có số |
| “Chỉ nhận khi …” | E Constraint | ∀, ∃, ⇒ | định nghĩa mọi quan hệ xấp xỉ |
| “Nếu … trừ khi … thì …” | F Rule | ∧, ¬, ⇒ | ngữ nghĩa của ¬; Infer vận hành |
| “KB đổi khi có sự kiện” | G Transformation | X^{t+1} = 𝒯(X^t) | thứ tự toán tử; tính chất kiểm tra được |
| “Cái nào được ưu tiên” | H Ordering | ≻, >\_lex | thứ tự giữa các tiêu chí |
| “Chọn cái tốt nhất” | I Objective | argmax/argmin | tập khả thi; hòa; rỗng |
| “Hệ đúng bao nhiêu” | J Metric | Acc, P/R/F1 | ai chấm; cách lấy trung bình |

## 6. Implementation Writing

Phần triển khai đạt khi một người khác có thể dựng lại hệ và ra số gần giống. Ba bài mẫu nêu tốt thống kê dữ liệu nhưng thiếu prompt, tham số và cấu hình baseline.

### 6.1 Bảng tái lập: ba bài đã ghi gì

| Mục cần ghi | P2 | P3 | P4 |
| --- | --- | --- | --- |
| Nguồn văn bản, số hiệu | Có: 36 điều, 306 khoản, 762 điểm (§5.2) | Có: BLHS 100/2015 và 12/2017 (§5.1) | Có: Motor Vehicles Act 1988, 14 chương (§5.1) |
| Kích thước KB | 616 khái niệm, 340 quan hệ, 1239 triple | 705 nút, 1037 cạnh | 128 khái niệm, 64 loại quan hệ, 742 đỉnh, 1586 cạnh |
| Mô hình/thư viện | VnCoreNLP, PhoBERT, từ điển LDOCE | ChatGPT 4.1-mini, PhoNLP, VnCoreNLP | ChatGPT-5.2 (baseline); mô hình dùng trong hệ không nêu |
| Prompt cho bước LLM | — | Không | Không |
| Giá trị ngưỡng | α = 0.6 kèm cách chọn | τ không có giá trị | Không áp dụng |
| Bộ câu hỏi: số lượng, nguồn | 180 câu, từ trang công an, tư vấn luật | 266 câu, 6 loại; nguồn ghi chung là câu hỏi thật | 9500 câu (Assamese); 119 câu (đất đai) |
| Ai làm đáp án chuẩn | Không nêu | Không nêu | Chuyên gia pháp lý (số người không nêu) |
| Cấu hình baseline | Không có baseline | Tên hệ; cách đưa văn bản vào ChatGPT không nêu | Fig.6; “refined with specialized data” không được giải thích |
| Thời gian chạy | 0.2 s (khái niệm), 5.6 s (vi phạm) | Không | Không |
| Phần cứng | Không | Không | Không |

&#91;Suy luận\] Số 266 của P3 là tổng 22+63+59+53+33+36 từ Table 1; bài không ghi tổng.

### 6.2 Viết một bước do LLM thực hiện

Bước LLM là bước khó tái lập nhất. Viết đủ 5 thứ:

1. **Mô hình**: tên và phiên bản chính xác, ngày gọi, nhiệt độ (temperature).
2. **Prompt**: toàn văn trong phụ lục; trong thân bài chỉ mô tả mục tiêu và định dạng đầu ra.
3. **Định dạng đầu ra**: ví dụ danh sách triple dạng JSON, và hệ xử lý thế nào khi LLM trả sai định dạng.
4. **Bước kiểm tra đầu ra**: P3 là mẫu tốt ở ý tưởng — câu LLM tách ra chỉ được nhận khi độ tương đồng cosine với câu gốc vượt τ (Eq.4); câu hỏi chuẩn hoá cũng được kiểm tra tương tự (Eq.14). Thiếu: τ bằng bao nhiêu, bao nhiêu phần trăm bị loại.
5. **Độ chính xác của riêng bước này**: ví dụ kiểm tra tay N triple, tỷ lệ đúng. Không bài nào báo số này, nên không biết lỗi của hệ sinh ra từ bước trích xuất hay bước suy luận.

> Step k is performed by \[model, version\] with temperature \[t\]; the prompt is given in Appendix \[X\]. The model returns \[format\]. Outputs that fail to parse are \[retried once / discarded\] (\[n\]% of calls). Each output is accepted only if \[criterion, Eq.(m)\], which rejected \[n\]% of outputs. On a manually checked sample of \[N\] items, the accepted outputs were correct in \[p\]% of cases.

### 6.3 Viết thuật toán để người khác cài được

- **Input/Output có kiểu**, trỏ về định nghĩa (P3 Algorithm 1–3).
- **Mỗi dòng một thao tác có thể lập trình.** P3 Algorithm 2 dòng 4 viết “for each subgraph g ⊆ G”: duyệt mọi đồ thị con là bài toán số mũ. Phải viết cách thật sự sinh ứng viên (ví dụ tra chỉ mục theo nút trung tâm của ngôi sao) hoặc trích thuật toán đã có.
- **Độ phức tạp** một dòng sau thuật toán, hoặc thời gian đo thực tế như P2 (0.2 s và 5.6 s, kèm quy mô KB).
- **Trường hợp rỗng**: P2 nói rõ hệ trả “không có thông tin liên quan” khi không tìm thấy (§5.1). P3 Algorithm 3 lấy giao các tập M\_i; khi giao rỗng thì làm gì, bài không nói.

### 6.4 Ranh giới giữa Implementation và Method

| Thuộc Method | Thuộc Implementation |
| --- | --- |
| Hàm L\_split: δ ↦ {s\_1, …, s\_k} và điều kiện chấp nhận | Mô hình nào, prompt nào, nhiệt độ bao nhiêu |
| Tiêu chí hai triple tương đương | Dùng PhoBERT phiên bản nào, từ điển nào |
| Cấu trúc KB | Lưu trong hệ quản trị nào, đánh chỉ mục ra sao |
| Loại câu hỏi | Giao diện (P2 Fig.5, P3 Fig.3) |

Giao diện người dùng chỉ đưa vào khi nó minh hoạ một đầu ra mà bảng số không thể hiện (ví dụ câu trả lời kèm đường suy luận). P2 dành cả §5.1 “User Interface” để mô tả luồng nhập câu hỏi; phần này không mang thông tin khoa học.

## 7. Figures, Tables & Algorithms

Mỗi hình, bảng, thuật toán phải được nhắc trong văn bản trước khi xuất hiện, và câu nhắc phải nói người đọc cần nhìn thấy gì trong đó.

### 7.1 Hình

| Loại hình | Khi nào | Quy tắc | Ví dụ |
| --- | --- | --- | --- |
| Tổng quan kiến trúc | Một lần, đầu phần phương pháp | Mỗi khối = một subsection, cùng tên; mũi tên ghi ký hiệu dữ liệu chạy qua | P4 Fig.5: ba giai đoạn khớp §4.1–4.3 |
| Quy trình một bước | Khi bước có nhiều nhánh | Không vẽ lại điều công thức đã nói | P2 Fig.1 (làm gọn đồ thị) |
| Ví dụ chạy thật | Cho cơ chế khó hình dung | Một đầu vào thật qua từng bước, có giá trị trung gian | Ba bài đều thiếu |
| Biểu đồ kết quả | Khi cần thấy xu hướng mà bảng không cho thấy | Không lặp lại đúng số trong bảng | P4 Fig.7 và Fig.8 vẽ lại đúng số của Table 2 và Table 4 |

**Caption tự đứng được.** Người đọc lướt chỉ xem hình và caption. Caption nói hình là gì và cần nhìn vào đâu. Caption kiểu “Simulating the process of…” (P4 Fig.3, Fig.4) chỉ nêu tên quá trình.

> **Fig. k.** \[What it shows\]. \[Key reading: e.g. Solid arrows carry data (symbols as in Eq. m); the dashed box is performed by the LLM, the others are symbolic.\]

**Câu dẫn vào hình.** Không viết “as shown in Figure 2” rồi thôi. Viết điều người đọc phải thấy:

> Figure k shows the three stages; note that only Stage 1 calls the LLM, so every legal conclusion is produced by the symbolic stages.

**Khớp số hình.** P2 §4.2 gọi Figure 3 là kiến trúc nền tảng; caption của Fig.3 lại là mô hình biểu diễn tri thức, còn kiến trúc là Fig.2. Dùng `\ref` trong LaTeX, không gõ số tay.

### 7.2 Bảng

- **Hiện mẫu số.** P2 Table 1 có cột Quantity, Correct, Accuracy; kiểm tra được 24/30 = 80.0%, 113/150 = 75.3%, 137/180 = 76.1%. P3 Table 1 và P4 Table 2, 4 chỉ có phần trăm, nên người đọc không kiểm được (và ô 96.36% của P3 là ví dụ lỗi lọt qua).
- **Tách bảng mô tả dữ liệu và bảng kết quả.** P4 làm đúng: Table 1 và Table 3 mô tả loại câu hỏi, Table 2 và Table 4 cho kết quả.
- **Miêu tả loại câu hỏi có ví dụ.** P4 Table 3 có cột Description cho mỗi nhóm. Thêm một câu hỏi mẫu cho mỗi nhóm sẽ giúp người đọc hiểu độ khó.
- **In đậm số tốt nhất mỗi dòng; ghi rõ khi hoà.** P3 Table 1 Kind 2 (87.30%) và Kind 6 (86.11%) là hoà.
- **Dòng trung bình ghi cách tính** (trung bình theo câu hay theo nhóm; xem Mục 5.11).
- **Tiêu đề bảng đặt phía trên** (LNCS), caption hình phía dưới.

> **Table k.** Accuracy (%) on \[dataset\] by question type (\[N\] questions; counts in parentheses). Best per row in bold. The last row averages over questions, not over types.

### 7.3 Thuật toán

Hai kiểu trình bày xuất hiện trong ba bài:

| Kiểu | Bài | Dùng khi | Hạn chế |
| --- | --- | --- | --- |
| Step-list bằng lời (Input / Output / Step 1, 2, 3 với gạch đầu dòng) | P2 Algorithm 4.1, 4.2 | Quy trình nhiều quyết định do người hoặc heuristic | Không cài lại được từng dòng; dễ bỏ qua trường hợp biên |
| Pseudocode đánh số dòng (for/if/return) | P3 Algorithm 1–3 | Thao tác xác định trên cấu trúc đã định nghĩa | Phải dùng đúng ký hiệu của các công thức |

Quy tắc cho pseudocode: Input/Output có kiểu; mỗi biến đã được định nghĩa hoặc khởi tạo; có `return`; đoạn văn sau thuật toán giải thích dòng khó nhất theo số dòng (“Line 5 checks …”) và nêu độ phức tạp. Thuật toán ngắn hơn 4 dòng thì viết thành một câu hoặc một công thức. P3 Algorithm 3 (lấy giao của k tập) là một công thức R = M\_1 ∩ … ∩ M\_k; bài đã viết công thức này ngay trong dòng Output, nên phần thân thuật toán là thừa.

## 8. Writing Quality

Một câu có chiều sâu kỹ thuật khi nó chứa một số, một ký hiệu, một tên riêng hoặc một điều kiện có thể sai. Câu không có thứ nào trong bốn thứ đó thì xoá hoặc viết lại.

### 8.1 Thay câu chung chung bằng câu cụ thể

| Kiểu câu chung chung | Vị trí | Viết lại theo hướng |
| --- | --- | --- |
| Mở bài bằng vai trò của pháp luật trong xã hội | Câu đầu cả ba bài | Mở bằng vấn đề kỹ thuật có số: ví dụ bao nhiêu phần trăm câu hỏi cần liên kết từ hai điều luật trở lên |
| “shows significant potential” | P3 Abstract | “reaches X% on N questions, versus Y% for \[baseline\]” |
| “plays a crucial role” | P2 §1 (và “a crucial component” ở §4.4) | Bỏ; hoặc nói nếu bỏ thành phần đó thì mất gì |
| “smart, reliable and scalable” | P3 §1 | Mỗi tính từ phải có một phép đo; không có thì bỏ |
| “absolute precision/reliability” | P4 Abstract, §4.3 | Không dùng “absolute” cho hệ đạt dưới 100% |
| Câu tổng kết lặp lại đoạn trước | P2 cuối §4.1, §4.4 | Xoá |

### 8.2 Danh mục lỗi để tự kiểm (lấy từ ba bài)

| # | Lỗi | Ví dụ | Cách phát hiện |
| --- | --- | --- | --- |
| 1 | Lộ trình không khớp số section | P2 tr.2 | So câu lộ trình với mục lục |
| 2 | Nói N thành phần, liệt kê N−1 | P2 §4.4 (5 so với 4) | Đếm |
| 3 | Câu dẫn danh sách nhưng danh sách trống | P2 §4.2 tr.7; câu “with the following architecture:” cuối §4.4 | Tìm dấu “:” cuối đoạn |
| 4 | Tham chiếu sai số hình | P2 §4.2 Figure 3 | Dùng `\ref` |
| 5 | Tham số không có giá trị | P3 τ | Liệt kê mọi ký hiệu Hy Lạp, đánh dấu đã gán số chưa |
| 6 | Định nghĩa vòng | P3 Eq.16 | Từ được định nghĩa có xuất hiện trong lời định nghĩa không |
| 7 | Kiểu hàm không khớp vế phải | P4 Def 3.3 | Viết kiểu của vế phải ra giấy |
| 8 | Ký hiệu dùng hai nghĩa | P3 s; P4 R | Bảng ký hiệu (Mục 5.1) |
| 9 | Tỷ lệ không khớp mẫu số | P3 Table 1, 96.36% / 22 câu | Nhân ngược tỷ lệ với mẫu số, phải ra số nguyên |
| 10 | Tuyên bố vượt trội khi có hòa | P3 §5.4 | Đối chiếu từng dòng bảng với câu kết luận |
| 11 | Tuyên bố không có phép đo | P4 §6 “xoá bỏ ảo giác” | Ma trận truy vết (Mục 2.2) |
| 12 | Baseline mô tả không đủ để làm lại | P4 §5.3 | Người khác có dựng lại baseline được không |
| 13 | Trích bài chưa xuất bản như bài chính thức | P3 \[26\], P4 \[29\]: khảo sát của Yue trên arXiv | Lọc danh mục tham khảo tìm “arXiv” |
| 14 | Lỗi chính tả ở tiêu đề | P2 §4.1 “Senarios”; P3, P4 §6 “Future” viết sai; P2 “In this session” thay cho section; P4 §2 “hallucation” | Chạy kiểm tra chính tả trên mã LaTeX |

&#91;Suy luận\] Lỗi 1–4 và 14 là lỗi soạn thảo, sửa trong một giờ. Lỗi 5–13 là lỗi lập luận; người phản biện dùng chúng để đánh giá mức độ chặt chẽ của cả bài.

### 8.3 Phân biệt bài báo với tài liệu mô tả hệ thống

Hỏi ba câu cho mỗi đoạn:

1. Đoạn này có trả lời “vì sao” không, hay chỉ “có cái gì”?
2. Đoạn này có còn đúng nếu đổi thư viện, ngôn ngữ lập trình, giao diện?
3. Người làm cùng hướng có học được gì từ đoạn này mà không đọc mã nguồn?

Hai “không” trở lên thì đoạn đó thuộc báo cáo kỹ thuật. P2 §4.2 (yêu cầu nền tảng) và §5.1 (giao diện) là ví dụ.

## 9. Thứ tự viết, checklist và prompt cho AI agent

### 9.1 Thứ tự viết (khác thứ tự đọc)

1. Ma trận truy vết (Mục 2.2) và bảng ký hiệu (Mục 5.1).
2. Hình tổng quan + công thức ghép chuỗi (Mục 5.4).
3. Section 3: các Definition, mỗi cái một ví dụ.
4. Section 4: mỗi giai đoạn một subsection theo khuôn Mục 4.2.
5. Section 5: bảng dữ liệu, cách chấm (công thức Mục 5.11), bảng kết quả có mẫu số, đoạn diễn giải.
6. Related Work.
7. Introduction, đoạn đóng góp, câu lộ trình.
8. Abstract và Conclusion, viết từ các con số đã có.

Viết Introduction sau Experiment để các tuyên bố ở đầu bài không vượt quá kết quả thật.

### 9.2 Checklist trước khi nộp

- [ ] Mỗi dòng của ma trận truy vết có đủ cột phép đo.
- [ ] Đoạn đóng góp nêu tên công trình gần nhất và điểm khác; chưa chứng minh khác thì dùng “apply/extend”.
- [ ] Baseline là thứ người làm nghề thật sự dùng, có một baseline là LLM mạnh trả lời trực tiếp, cấu hình đủ để làm lại.
- [ ] Mọi công thức có đủ 6 phần (Mục 5.0); mọi công thức được dùng lại ở ít nhất một chỗ.
- [ ] Mọi tham số có giá trị và cách chọn.
- [ ] Mọi hàm có chữ ký khớp với vế phải; không định nghĩa vòng.
- [ ] Ngữ nghĩa phủ định, quan hệ xấp xỉ (≃), thứ tự ưu tiên đều được định nghĩa.
- [ ] Thước đo có công thức; nói rõ ai chấm và mức đồng thuận.
- [ ] Bảng có mẫu số; mọi tỷ lệ nhân ngược ra số nguyên; ghi cách lấy trung bình.
- [ ] Câu kết luận đối chiếu được với từng dòng bảng, kể cả dòng hòa hoặc thua.
- [ ] Prompt LLM trong phụ lục; có số đo độ chính xác của riêng bước LLM.
- [ ] Câu lộ trình khớp mục lục; mọi hình/bảng dùng `\ref`; câu “gồm:” đều có danh sách theo sau.
- [ ] Không có “absolute”, “eliminate”, “guarantee” nếu không có chứng minh hình thức.
- [ ] Không trích bài arXiv như bài đã xuất bản; mọi nhận định về bài khác lấy từ toàn văn, có mục hoặc bảng.
- [ ] Chạy kiểm tra chính tả trên tiêu đề và caption.

### 9.3 Prompt đưa cho AI agent

Dán khối dưới vào đầu phiên làm việc với agent, kèm cookbook này.

```markdown
Bạn viết bản thảo bài báo khoa học CS theo "Scientific Paper Writing Cookbook" đính kèm.

Trước khi viết bất kỳ đoạn nào:
1. Lập ma trận truy vết: Hạn chế | Cơ chế | Phép đo | Kết quả nào sẽ bác bỏ.
   Dòng thiếu cột "Phép đo" → báo cho tôi, không viết tuyên bố đó.
2. Lập bảng ký hiệu. Mỗi ký hiệu một nghĩa, một kiểu.

Khi viết công thức: dùng khung 6 phần (dẫn nhập, công thức, where, diễn giải,
giá trị tham số, cầu nối). Chọn dạng A–K theo bảng Mục 5.13. Kiểm tra kiểu
của mọi hàm. Tham số chưa có giá trị → ghi [CẦN SỐ: tên tham số], không tự điền.

Khi viết kết quả: chỉ dùng số tôi đưa. Nhân ngược mọi tỷ lệ với mẫu số.
Nêu cả chỗ hòa hoặc thua baseline.

Khi nói về công trình khác: chỉ từ toàn văn tôi cung cấp, kèm mục/bảng.
Không có toàn văn → gắn [Chưa kiểm chứng]. Chưa chứng minh khác biệt → dùng "apply/extend".

Cấm: absolute, eliminate, guarantee, significant potential, plays a crucial role.

Sau mỗi section: chạy checklist Mục 9.2 và báo mục nào chưa đạt.
```

### 9.4 Giới hạn của cookbook này

Ba bài mẫu cùng một nhóm tác giả, cùng miền (truy vấn pháp luật bằng KG), cùng khổ bài hội nghị 12–14 trang. Các dạng I (hàm mục tiêu) và J (thước đo) không có trong ba bài; mẫu ở Mục 5.10–5.11 do tôi dựng \[Suy luận\]. Nên đối chiếu thêm với một bài hội nghị/tạp chí hạng cao cùng hướng trước khi dùng cookbook làm chuẩn cho luận văn.

**Điều gì sẽ chứng minh đề xuất này sai:** đưa cookbook cho một agent viết lại Section 3–4 của P3, rồi đưa bản viết lại và bản gốc cho một người chưa đọc cả hai chấm theo checklist Mục 9.2 (không cho biết bản nào là bản nào). Nếu bản viết lại không ít lỗi hơn rõ rệt, cookbook chưa có tác dụng. Phép thử này mất dưới một giờ.
