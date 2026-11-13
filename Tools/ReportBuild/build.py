"""Dựng BaoCao_GD1_FitLifeHub_v3.docx từ bản sao của v2 (không sửa file gốc).
Dùng:  python -X utf8 build.py <phần> <đầu ra.docx>      phần = 1 | 2 | 3 (cộng dồn)
"""
import os, sys, shutil, zipfile
from lxml import etree

sys.path.insert(0, os.path.dirname(__file__))
import xmllib
from xmllib import *

PROJ = r"D:\HK1_Năm 3\CSDL Nâng cao - Pass hangvu@hcmus-20260913\Đồ án"
V2 = os.path.join(PROJ, "BaoCao_GD1_FitLifeHub_v2.docx")
SCR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def headings_of(frags):
    import re, html as _h
    hs = []
    for x in frags:
        m = re.search(r'<w:pStyle w:val="Heading([12])"/>', x)
        if m and x.startswith("<w:p>"):
            t = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", x))
            hs.append((int(m.group(1)), _h.unescape(t)))
    return hs


def make_toc(hs, pages):
    """Mục lục dạng trường TOC (Word cập nhật được bằng F9); kết quả đệm lấy số trang từ bản dựng trước."""
    from xml.sax.saxutils import escape
    o = [p("MỤC LỤC", after=200, jc="center", bold=True, sz=28, page_break_before=True)]
    for k, (lv, t) in enumerate(hs):
        pg = str(pages.get(t, "0")) if pages else "0"
        ind = '<w:ind w:left="%d"/>' % (0 if lv == 1 else 360)
        b = lv == 1
        rp = rpr(b=b, sz=24)
        begin = ""
        if k == 0:
            begin = (f'<w:r>{rp}<w:fldChar w:fldCharType="begin"/></w:r><w:r>{rp}<w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r>'
                     f'<w:r>{rp}<w:fldChar w:fldCharType="separate"/></w:r>')
        end = f'<w:r>{rp}<w:fldChar w:fldCharType="end"/></w:r>' if k == len(hs) - 1 else ""
        o.append(f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9638"/></w:tabs><w:spacing w:before="{80 if lv == 1 else 0}" w:after="40" w:line="276" w:lineRule="auto"/>{ind}{rp}</w:pPr>'
                 f'{begin}<w:r>{rp}<w:t xml:space="preserve">{escape(t)}</w:t></w:r><w:r>{rp}<w:tab/></w:r><w:r>{rp}<w:t>{pg}</w:t></w:r>{end}</w:p>')
    return o


def build(parts, out, toc_pages=None):
    import part1
    work = os.path.join(SCR, "v3_work")
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    with zipfile.ZipFile(V2) as z:
        z.extractall(work)
    # --- hình: thay ảnh v2 bằng ERD gốc và ba hình mô-đun lược đồ quan hệ
    media = os.path.join(work, "word", "media")
    shutil.copy(os.path.join(PROJ, "CSDLA_v3.png"), os.path.join(media, "image2.png"))
    for k in (1, 2, 3):
        shutil.copy(os.path.join(PROJ, "LuocDoQuanHe", f"luoc_do_mo_dun_{k}.png"), os.path.join(media, f"image{k + 2}.png"))
    # --- thân tài liệu: giữ bìa (22 phần tử đầu), thay phần còn lại
    docp = os.path.join(work, "word", "document.xml")
    tree = etree.parse(docp)
    body = tree.getroot().find(f"{{{W_NS}}}body")
    for ch in list(body)[20:]:
        body.remove(ch)
    s = etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True).decode("utf-8")
    new = []
    new += part1.overview() + part1.qt() + part1.freq() + part1.conceptual() + part1.conceptual2() + part1.constraints_34()
    if parts >= 2:
        import part2
        new += part2.build()
    if parts >= 3:
        import part3
        new += part3.build()
    final = xmllib.final_sect("rId14")
    hs = headings_of(new)
    import json
    json.dump(hs, open(os.path.join(SCR, "headings.json"), "w", encoding="utf-8"), ensure_ascii=False)
    toc = make_toc(hs, toc_pages) if parts >= 3 else []
    s = s.replace("</w:body>", "".join(toc) + "".join(new) + final + "</w:body>")
    open(docp, "w", encoding="utf-8").write(s)
    # --- nén (không có mục thư mục)
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(work, "[Content_Types].xml"), "[Content_Types].xml")
        for root, _, files in os.walk(work):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.relpath(full, work).replace("\\", "/")
                if arc != "[Content_Types].xml":
                    z.write(full, arc)
    print("ghi", out, os.path.getsize(out))


if __name__ == "__main__":
    pg = None
    if len(sys.argv) > 3:
        import json
        pg = json.load(open(sys.argv[3], encoding="utf-8"))
    build(int(sys.argv[1]), sys.argv[2], pg)
