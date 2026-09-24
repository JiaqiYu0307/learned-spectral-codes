"""Create compact, screen-readable PDF copies for static web hosting."""
from pathlib import Path
import shutil
import subprocess
import sys

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "spectral-research-site"
POPPLER = Path(r"C:\Users\Jiaqi\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
JOBS = [
    (ROOT / "_SIGGRAPH_Asia___Spectral_Rendering_Without_a_Spectral_Renderer.pdf", SITE / "dist/assets/paper.pdf"),
    (ROOT / "supplyments.pdf", SITE / "dist/assets/supplement.pdf"),
]


def compact(source: Path, target: Path) -> None:
    scratch = SITE / "tmp/pdfs" / target.stem
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    prefix = scratch / "page"
    subprocess.run([
        str(POPPLER), "-jpeg", "-r", "150", "-jpegopt",
        "quality=84,optimize=y,progressive=y", str(source), str(prefix)
    ], check=True)
    pages = sorted(scratch.glob("page-*.jpg"))
    if not pages:
        raise RuntimeError(f"No pages rendered from {source}")
    pdf = canvas.Canvas(str(target), pagesize=(612, 792), pageCompression=1)
    for page in pages:
        with Image.open(page) as image:
            width, height = image.size
        scale = min(612 / width, 792 / height)
        draw_w, draw_h = width * scale, height * scale
        pdf.drawImage(ImageReader(str(page)), (612-draw_w)/2, (792-draw_h)/2,
                      width=draw_w, height=draw_h, preserveAspectRatio=True)
        pdf.showPage()
    pdf.setTitle(source.stem)
    pdf.save()
    print(f"{target.name}: {len(pages)} pages, {target.stat().st_size} bytes")


if __name__ == "__main__":
    for source, target in JOBS:
        compact(source, target)
