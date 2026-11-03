"""Dựng TONG_HOP_CONG_VIEC.html từ TONG_HOP_CONG_VIEC.md.

Chạy: python -X utf8 -I utils/render_report.py [md] [html]   (mặc định hai file ở gốc dự án)

Chỉ dùng thư viện chuẩn. Chỉ hiểu phần Markdown mà báo cáo dùng: tiêu đề # đến ####, đoạn,
danh sách gạch đầu dòng / đánh số lồng nhau, bảng, khối mã ```, đường kẻ ---, **đậm**, *nghiêng*,
`mã`. Gặp dòng bảng lệch cột hoặc khối mã không đóng thì dừng (ValueError), không đoán.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = """
:root {
  --bg: #f4f6f7; --surface: #ffffff; --ink: #15202b; --muted: #556270; --line: #d9e0e5;
  --accent: #0a6c74; --accent-soft: #dff0f1; --code-bg: #e9eef1;
  --font-body: "Be Vietnam Pro", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f1519; --surface: #162027; --ink: #e6edf1; --muted: #9aa9b5; --line: #2a3944;
    --accent: #4fc1c8; --accent-soft: #12373b; --code-bg: #1c2a33; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0f1519; --surface: #162027; --ink: #e6edf1; --muted: #9aa9b5; --line: #2a3944;
  --accent: #4fc1c8; --accent-soft: #12373b; --code-bg: #1c2a33; color-scheme: dark;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 16px; }
body {
  margin: 0; background: var(--bg); color: var(--ink); font: 400 16px/1.7 var(--font-body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 24px 64px; -webkit-font-smoothing: antialiased;
}
.shell { max-width: 1160px; margin: 0 auto; display: grid; grid-template-columns: 250px minmax(0, 1fr); gap: 40px; align-items: start; }
@media (max-width: 900px) { .shell { grid-template-columns: minmax(0, 1fr); gap: 16px; } }

.toc { position: sticky; top: 16px; max-height: calc(100vh - 32px); overflow-y: auto; font-size: 14px; line-height: 1.45; }
.toc summary { display: none; cursor: pointer; font-weight: 600; padding: 10px 14px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }
.toc ol { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1px; }
.toc ol ol { margin: 0 0 6px 14px; }
.toc a { display: block; padding: 5px 10px; border-radius: 6px; color: var(--muted); text-decoration: none; }
.toc ol ol a { font-size: 13px; padding: 3px 10px; }
.toc a:hover, .toc a:focus-visible { background: var(--accent-soft); color: var(--accent); outline: none; }
.toc .num { font-family: var(--font-mono); font-size: 12px; margin-right: 6px; opacity: .8; }
@media (max-width: 900px) {
  .toc { position: static; max-height: none; }
  .toc summary { display: block; }
  .toc ol.top { margin-top: 8px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 8px; }
}

main { min-width: 0; max-width: 860px; }
header.top { padding-bottom: 24px; margin-bottom: 8px; border-bottom: 1px solid var(--line); }
.kicker { font: 500 12px/1 var(--font-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin: 0 0 14px; }
h1 { font-size: clamp(26px, 4.4vw, 38px); line-height: 1.25; font-weight: 700; letter-spacing: -.01em; margin: 0 0 14px; text-wrap: balance; }
header.top p { color: var(--muted); font-size: 15px; margin: 0 0 8px; }
h2 { font-size: 24px; line-height: 1.3; font-weight: 700; margin: 56px 0 14px; text-wrap: balance; }
h2 .num { font: 500 14px var(--font-mono); color: var(--accent); margin-right: 10px; vertical-align: 2px; }
h3 { font-size: 18px; line-height: 1.4; font-weight: 600; margin: 34px 0 8px; text-wrap: balance; }
h3 .tag { font: 500 13px var(--font-mono); background: var(--accent-soft); color: var(--accent); padding: 2px 8px; border-radius: 6px; margin-right: 8px; vertical-align: 2px; }
h4 { font-size: 16px; line-height: 1.4; font-weight: 600; margin: 24px 0 6px; color: var(--accent); }
section[id] { scroll-margin-top: 16px; }
p { margin: 0 0 14px; }
ul, ol { margin: 0 0 14px; padding-left: 24px; }
li { margin-bottom: 6px; }
li > ul, li > ol, li > .tbl, li > pre { margin: 8px 0 10px; }
li::marker { color: var(--muted); }
strong { font-weight: 600; }
hr { border: 0; border-top: 1px solid var(--line); margin: 36px 0 0; }
code { font-family: var(--font-mono); font-size: .86em; background: var(--code-bg); padding: 1px 6px; border-radius: 4px; word-break: break-word; }
pre { font: 400 13px/1.55 var(--font-mono); background: var(--code-bg); padding: 14px 16px; border-radius: 8px; overflow-x: auto; margin: 0 0 16px; }
pre code { background: none; padding: 0; font-size: inherit; word-break: normal; }
.tbl { overflow-x: auto; margin: 0 0 20px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; line-height: 1.55; }
th, td { text-align: left; vertical-align: top; padding: 9px 14px; border-bottom: 1px solid var(--line); }
th { font: 600 12px/1.3 var(--font-mono); letter-spacing: .05em; text-transform: uppercase; color: var(--muted); background: var(--bg); }
tr:last-child td { border-bottom: 0; }
td code { white-space: normal; }
footer { margin-top: 56px; padding-top: 20px; border-top: 1px solid var(--line); color: var(--muted); font-size: 14px; }
summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700'
    '&family=JetBrains+Mono:wght@400;500&display=swap">'
)

CODE_SPAN = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ITALIC = re.compile(r"(?<![\w*])\*(?![\s*])([^*]+?)(?<![\s*])\*(?![\w*])")
BULLET = re.compile(r"^([-*]) (.*)$")
ORDERED = re.compile(r"^(\d+)\. (.*)$")
TABLE_SEP = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")
HEADING = re.compile(r"^(#{1,4}) (.*)$")


def inline(text):
    """Escape HTML, rồi đổi `mã`, **đậm**, *nghiêng*. Mã được thay bằng ký hiệu giữ chỗ trước để đậm / nghiêng
    bao quanh được cả đoạn có mã, và chữ trong mã không bị đổi định dạng."""
    codes = []

    def keep(m):
        codes.append("<code>" + html.escape(m.group(1), quote=False) + "</code>")
        return "\x00%d\x00" % (len(codes) - 1)

    s = CODE_SPAN.sub(keep, text)
    s = html.escape(s, quote=False)
    s = BOLD.sub(r"<strong>\1</strong>", s)
    s = ITALIC.sub(r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)


def split_row(line):
    """Tách một dòng bảng theo dấu |, không tách dấu | nằm trong `mã` hay đứng sau dấu \\."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, in_code, i = [], [], False, 0
    while i < len(s):
        ch = s[i]
        if ch == "`":
            in_code = not in_code
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def slug(text):
    s = re.sub(r"[^\w]+", "-", text.lower(), flags=re.UNICODE).strip("-")
    return s[:60] or "muc"


def render_list(lines):
    """Danh sách: mỗi mục bắt đầu ở cột 0, các dòng thụt vào dưới nó là nội dung của mục (đoạn, bảng, danh sách con...),
    được bỏ thụt rồi phân tích lại bằng parse_blocks."""
    items = []  # [kind, số thứ tự, dòng đầu, các dòng sau]
    for ln in lines:
        m = BULLET.match(ln)
        kind = "ul"
        if not m:
            m = ORDERED.match(ln)
            kind = "ol"
        if m:
            items.append([kind, m.group(1), m.group(2), [], m.start(2)])
        else:
            items[-1][3].append(ln)
    out, cur = [], None
    for kind, num, first, rest, width in items:
        if kind != cur:
            if cur:
                out.append("</%s>" % cur)
            out.append('<ol start="%s">' % num if kind == "ol" and num != "1" else "<%s>" % kind)
            cur = kind
        body = [first] + [l[width:] if not l[:width].strip() else l.lstrip() for l in rest]
        blocks = parse_blocks(body)
        parts = []
        for k, blk in enumerate(blocks):
            parts.append(inline(blk[1]) if k == 0 and blk[0] == "p" else render_block(blk))
        out.append("<li>" + "".join(parts) + "</li>")
    out.append("</%s>" % cur)
    return "".join(out)


def render_table(lines):
    head = split_row(lines[0])
    rows = [split_row(r) for r in lines[2:]]
    for r in rows:
        if len(r) != len(head):
            raise ValueError("dòng bảng có %d cột, tiêu đề có %d: %s" % (len(r), len(head), r[0][:40]))
    out = ['<div class="tbl"><table><thead><tr>']
    out += ["<th>" + inline(c) + "</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def parse_blocks(md_lines):
    """Trả về danh sách khối: ('h', level, text) | ('p', text) | ('list', lines) | ('table', lines) | ('code', lines) | ('hr',)."""
    blocks, i, n = [], 0, len(md_lines)
    while i < n:
        ln = md_lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith("```"):
            j = i + 1
            while j < n and not md_lines[j].startswith("```"):
                j += 1
            if j >= n:
                raise ValueError("khối mã mở ở dòng %d không có dòng đóng" % (i + 1))
            blocks.append(("code", md_lines[i + 1:j]))
            i = j + 1
        elif HEADING.match(ln):
            m = HEADING.match(ln)
            blocks.append(("h", len(m.group(1)), m.group(2).strip()))
            i += 1
        elif ln.strip() == "---":
            blocks.append(("hr",))
            i += 1
        elif ln.lstrip().startswith("|") and i + 1 < n and TABLE_SEP.match(md_lines[i + 1].strip()):
            j = i
            while j < n and md_lines[j].lstrip().startswith("|"):
                j += 1
            blocks.append(("table", md_lines[i:j]))
            i = j
        elif BULLET.match(ln) or ORDERED.match(ln):
            j = i
            while j < n:
                cur = md_lines[j]
                if cur.strip():
                    if cur.startswith(" ") or BULLET.match(cur) or ORDERED.match(cur):
                        j += 1
                        continue
                    break
                k = j
                while k < n and not md_lines[k].strip():
                    k += 1
                if k < n and (md_lines[k].startswith(" ") or BULLET.match(md_lines[k]) or ORDERED.match(md_lines[k])):
                    j = k
                    continue
                break
            blocks.append(("list", md_lines[i:j]))
            i = j
        elif re.match(r"^\s+([-*]|\d+\.) ", ln):
            raise ValueError("dòng %d: mục danh sách thụt vào mà không nằm dưới mục nào: %s" % (i + 1, ln.strip()[:40]))
        else:
            j = i
            while j < n and md_lines[j].strip() and not HEADING.match(md_lines[j]) and not md_lines[j].startswith("```") \
                    and not BULLET.match(md_lines[j]) and not ORDERED.match(md_lines[j]) and md_lines[j].strip() != "---" \
                    and not md_lines[j].lstrip().startswith("|"):
                j += 1
            blocks.append(("p", " ".join(s.strip() for s in md_lines[i:j])))
            i = j
    return blocks


def render_block(b):
    kind = b[0]
    if kind == "p":
        return "<p>" + inline(b[1]) + "</p>"
    if kind == "list":
        return render_list(b[1])
    if kind == "table":
        return render_table(b[1])
    if kind == "code":
        return "<pre><code>" + html.escape("\n".join(b[1]), quote=False) + "</code></pre>"
    if kind == "hr":
        return ""  # đường kẻ trong md chỉ ngăn mục; mỗi mục đã là một section riêng
    raise ValueError("khối %s không được hỗ trợ ở đây" % kind)


def render(md_text):
    blocks = parse_blocks(md_text.splitlines())
    title = next((b[2] for b in blocks if b[0] == "h" and b[1] == 1), "Tổng hợp công việc")
    toc, body, header = [], [], []
    state = "header"  # header -> trước tiêu đề ## đầu tiên
    in_section = False
    kicker = ""
    for b in blocks:
        kind = b[0]
        if kind == "h" and b[1] == 1:
            continue
        if kind == "h" and b[1] == 2:
            if in_section:
                body.append("</section>")
            state, in_section = "body", True
            m = re.match(r"^(\d+)\.\s+(.*)$", b[2])
            num, text = (m.group(1), m.group(2)) if m else ("", b[2])
            sid = "s" + num if m else slug(b[2])
            toc.append([sid, num, text, []])
            body.append('<section id="%s"><h2>%s%s</h2>' % (sid, '<span class="num">%s</span>' % num if num else "", inline(text)))
            continue
        if state == "header":
            if kind == "p":
                m = re.match(r"^Cập nhật: (\S+?)\.\s*(.*)$", b[1])
                if m and not kicker:
                    kicker = m.group(1)
                    header.append("<p>" + inline(m.group(2)) + "</p>" if m.group(2) else "")
                else:
                    header.append("<p>" + inline(b[1]) + "</p>")
            elif kind == "hr":
                pass
            else:
                raise ValueError("khối %s trước mục ## đầu tiên chưa được hỗ trợ" % kind)
            continue
        if kind == "h":
            level, text = b[1], b[2]
            sid = "%s-%s" % (toc[-1][0], slug(text)) if toc else slug(text)
            tag = re.match(r"^(A\d+):\s*(.*)$", text)
            if level == 3:
                toc[-1][3].append((sid, text))
                inner = '<span class="tag">%s</span>%s' % (tag.group(1), inline(tag.group(2))) if tag else inline(text)
                body.append('<h3 id="%s">%s</h3>' % (sid, inner))
            else:
                body.append('<h%d id="%s">%s</h%d>' % (level, sid, inline(text), level))
        elif kind == "p":
            body.append("<p>" + inline(b[1]) + "</p>")
        elif kind == "list":
            body.append(render_list(b[1]))
        elif kind == "table":
            body.append(render_table(b[1]))
        elif kind == "code":
            body.append("<pre><code>" + html.escape("\n".join(b[1]), quote=False) + "</code></pre>")
        elif kind == "hr":
            pass  # các đường kẻ trong md chỉ ngăn mục; mỗi mục đã là một section riêng
    if in_section:
        body.append("</section>")

    toc_html = ['<ol class="top">']
    for sid, num, text, subs in toc:
        toc_html.append('<li><a href="#%s">%s%s</a>' % (sid, '<span class="num">%s</span>' % num if num else "", inline(text)))
        if subs:
            toc_html.append("<ol>" + "".join('<li><a href="#%s">%s</a></li>' % (s, inline(t)) for s, t in subs) + "</ol>")
        toc_html.append("</li>")
    toc_html.append("</ol>")

    return (
        '<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Đồ thị tri thức BLDS 2015</title>\n" + FONTS + "\n<style>" + CSS + "</style>\n</head>\n<body>\n"
        '<div class="shell">\n<nav class="toc" aria-label="Mục lục"><details id="toc" open><summary>Mục lục</summary>'
        + "".join(toc_html) + "</details></nav>\n<main>\n"
        '<header class="top">' + ('<p class="kicker">Cập nhật %s</p>' % html.escape(kicker) if kicker else "")
        + "<h1>" + inline(title) + "</h1>" + "".join(header) + "</header>\n"
        + "\n".join(body) + "\n</main>\n</div>\n"
        '<script>if (matchMedia("(max-width: 900px)").matches) document.getElementById("toc").removeAttribute("open");</script>\n'
        "</body>\n</html>\n"
    )


def main(argv):
    md_path = Path(argv[1]) if len(argv) > 1 else ROOT / "TONG_HOP_CONG_VIEC.md"
    out_path = Path(argv[2]) if len(argv) > 2 else md_path.with_suffix(".html")
    page = render(md_path.read_text(encoding="utf-8"))
    out_path.write_text(page, encoding="utf-8", newline="\n")
    print("đã ghi %s (%d byte)" % (out_path, len(page.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
