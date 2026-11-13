import sys, fitz
from PIL import Image
pdf, outprefix = sys.argv[1], sys.argv[2]
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 60
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
doc = fitz.open(pdf)
imgs = []
for i, pg in enumerate(doc):
    pix = pg.get_pixmap(dpi=dpi)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    imgs.append(im)
print("pages", len(imgs), [im.size for im in imgs[:3]])
# montage per 24 pages
per = cols * 4
for n in range(0, len(imgs), per):
    chunk = imgs[n:n+per]
    w = max(i.width for i in chunk); h = max(i.height for i in chunk)
    rows = (len(chunk) + cols - 1) // cols
    m = Image.new("RGB", (cols * w, rows * h), "white")
    for k, im in enumerate(chunk):
        m.paste(im, ((k % cols) * w, (k // cols) * h))
    m.save(f"{outprefix}_m{n//per+1}.png")
