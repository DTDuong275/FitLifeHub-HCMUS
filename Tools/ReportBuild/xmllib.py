"""Bộ dựng WordprocessingML bám đúng định dạng của BaoCao_GD1_FitLifeHub_v2.docx."""
import re
from xml.sax.saxutils import escape

FONT = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
SZ = 26


def rpr(b=False, i=False, u=False, sz=SZ, dstrike=False):
    return ("<w:rPr>" + FONT + ("<w:b/><w:bCs/>" if b else "") + ("<w:i/><w:iCs/>" if i else "")
            + f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>' + ('<w:u w:val="single"/>' if u else "") + "</w:rPr>")


TOK = re.compile(r"(\*\*|__|\^\^)")


def runs(text, sz=SZ, bold=False):
    """Mini-markup: **đậm**, __gạch chân__, ^^nghiêng^^ (lồng nhau được)."""
    out = []
    b, u, i = bold, False, False
    for part in TOK.split(text):
        if part == "**":
            b = not b if not bold else b
        elif part == "__":
            u = not u
        elif part == "^^":
            i = not i
        elif part:
            out.append(f'<w:r>{rpr(b, i, u, sz)}<w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return "".join(out)


def p(text="", after=100, sz=SZ, keep=False, jc=None, ind=None, bold=False, page_break_before=False,
      style=None, num=None, line=276, keep_lines=False):
    ppr = ""
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if keep:
        ppr += "<w:keepNext/>"
    if keep_lines:
        ppr += "<w:keepLines/>"
    if page_break_before:
        ppr += "<w:pageBreakBefore/>"
    if num is not None:
        ppr += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>'
    ppr += f'<w:spacing w:after="{after}" w:line="{line}" w:lineRule="auto"/>'
    if ind:
        ppr += ind
    if jc:
        ppr += f'<w:jc w:val="{jc}"/>'
    ppr += rpr(sz=sz)
    return f"<w:p><w:pPr>{ppr}</w:pPr>{runs(text, sz, bold)}</w:p>"


def h1(text, first=False, page_break=False):
    # v2: tiêu đề "Tổng quan" không ép cỡ chữ; các H1 khác ép 13pt
    r = f"<w:rPr>{FONT}</w:rPr>" if first else f'<w:rPr>{FONT}<w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr>'
    sp = "" if first else '<w:spacing w:line="276" w:lineRule="auto"/>'
    pb = "<w:pageBreakBefore/>" if page_break else ""
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading1"/>{pb}{sp}{r}</w:pPr><w:r>{r}'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def h2(text, page_break=False):
    r = f'<w:rPr>{FONT}<w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr>'
    pb = "<w:pageBreakBefore/>" if page_break else ""
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading2"/>{pb}<w:spacing w:line="276" w:lineRule="auto"/>{r}</w:pPr>'
            f'<w:r>{r}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def h3(text):
    r = f'<w:rPr>{FONT}<w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr>'
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading3"/><w:spacing w:line="276" w:lineRule="auto"/>{r}</w:pPr>'
            f'<w:r>{r}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def bullet(text, keep=False):
    return p(text, after=60, style="ListParagraph", num=2, keep=keep)


def numbered(text, numid):
    return p(text, after=60, style="ListParagraph", num=numid)


def label(text):
    """Dòng nhãn đậm kiểu "Tác nhân:" / "Quy tắc nghiệp vụ:" (giữ cùng trang với dòng sau)."""
    return p(text, after=40, keep=True, bold=True)


def labeled(head, rest):
    """"Tác nhân: ..." với phần nhãn đậm."""
    return p(f"**{head}** {rest}", after=60)


def spacer(keep=False):
    return (f'<w:p><w:pPr>{"<w:keepNext/>" if keep else ""}<w:spacing w:after="40" w:line="276" w:lineRule="auto"/>'
            f'{rpr()}</w:pPr></w:p>')


def schema_line(num, name, cols_markup):
    """Dòng quan hệ kiểu v2: "1. TEN ( cột, ... )" thụt lề treo."""
    return (f'<w:p><w:pPr><w:keepLines/><w:spacing w:after="70" w:line="276" w:lineRule="auto"/><w:ind w:left="360" w:hanging="360"/>{rpr()}</w:pPr>'
            f'{runs(f"**{num}. {name}**")}{runs(" ( ")}{runs(cols_markup)}{runs(" )")}</w:p>')


# ---------------------------------------------------------------- bảng
BORDER = '<w:top w:val="single" w:sz="4" w:space="0" w:color="999999"/><w:left w:val="single" w:sz="4" w:space="0" w:color="999999"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/><w:right w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
TCMAR = '<w:tcMar><w:top w:w="50" w:type="dxa"/><w:left w:w="90" w:type="dxa"/><w:bottom w:w="50" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tcMar>'


IDENT = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Za-z0-9]+)+\b")


def zw(t):
    return IDENT.sub(lambda m: m.group(0).replace("_", "_​"), t)


def cell(content, w, header=False, bold=False, keep=False, sz=SZ, jc=None):
    paras = content if isinstance(content, list) else [content]
    paras = [zw(t) for t in paras]
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>' if header else ""
    body = ""
    for t in paras:
        ppr = ("<w:keepNext/>" if keep else "") + '<w:spacing w:after="20" w:line="276" w:lineRule="auto"/>' + (f'<w:jc w:val="{jc}"/>' if jc else "") + rpr(sz=sz)
        body += f"<w:p><w:pPr>{ppr}</w:pPr>{runs(t, sz, bold or header)}</w:p>"
    return f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders>{BORDER}</w:tcBorders>{shd}{TCMAR}</w:tcPr>{body}</w:tc>'


def table(widths, header, rows, keep=False, first_bold=False, sz=SZ, center_cols=()):
    total = sum(widths)
    x = ('<w:tbl><w:tblPr>' f'<w:tblW w:w="{total}" w:type="dxa"/>'
         '<w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tblBorders>'
         '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="10" w:type="dxa"/><w:right w:w="10" w:type="dxa"/></w:tblCellMar>'
         '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
         "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>")
    if header:
        x += '<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' + "".join(
            cell(h, w, header=True, keep=True, sz=sz) for h, w in zip(header, widths)) + "</w:tr>"
    for r in rows:
        assert len(r) == len(widths), (r, widths)
        x += "<w:tr><w:trPr><w:cantSplit/></w:trPr>" + "".join(
            cell(c, w, bold=(first_bold and k == 0), keep=keep, sz=sz, jc=("center" if k in center_cols else None))
            for k, (c, w) in enumerate(zip(r, widths))) + "</w:tr>"
    return x + "</w:tbl>"


# ---------------------------------------------------------------- hình & phân đoạn
_img_id = [100]


def image(rid, cx, cy, name, descr, page_break_before=False, after=100):
    _img_id[0] += 1
    i = _img_id[0]
    pb = "<w:pageBreakBefore/>" if page_break_before else ""
    return (f'<w:p><w:pPr>{pb}<w:spacing w:after="{after}" w:line="276" w:lineRule="auto"/><w:jc w:val="center"/>{rpr()}</w:pPr>'
            f'<w:r>{rpr()}<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{i}" name="{escape(name)}" descr="{escape(descr)}"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
            f'<pic:nvPicPr><pic:cNvPr id="{i}" name="{escape(name)}"/><pic:cNvPicPr><a:picLocks noChangeAspect="1" noChangeArrowheads="1"/></pic:cNvPicPr></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:srcRect/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr bwMode="auto"><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


def sect_break(kind, footer_rid):
    """Đoạn rỗng mang sectPr kết thúc một phân đoạn. kind: 'portrait' | 'landscape'."""
    if kind == "portrait":
        sp = '<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/>'
    else:
        sp = '<w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="1000" w:right="1134" w:bottom="900" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/>'
    return (f'<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:sectPr><w:footerReference w:type="default" r:id="{footer_rid}"/>{sp}<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr></w:pPr></w:p>')


def final_sect(footer_rid, kind="portrait"):
    s = sect_break(kind, footer_rid)
    m = re.search(r"<w:sectPr>.*</w:sectPr>", s)
    return m.group(0)
