# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

app = FastAPI(title="QR Generator API")

# Allow Streamlit/frontend origin(s) — change when you deploy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development; restrict in production to your streamlit origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QRRequest(BaseModel):
    text: str
    initials: str | None = None   # optional custom initials (1-3 chars recommended)
    box_size: int | None = 10
    border: int | None = 4

def derive_initials(s: str) -> str:
    if not s:
        return ""
    # simple heuristic: if user provided a name-like string, take first letters
    parts = [p for p in s.strip().split() if p]
    if len(parts) == 1:
        return parts[0][0].upper()
    # take first letter of first and last (up to 2 letters)
    return (parts[0][0] + parts[-1][0]).upper()

def draw_initials_on_qr(img: Image.Image, initials: str) -> Image.Image:
    """
    Draw a circular badge in the center and put initials text inside.
    """
    if not initials:
        return img

    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # badge sizing: make it ~18% of QR width (tweak factor here)
    badge_frac = 0.18
    badge_diam = int(min(w, h) * badge_frac)
    if badge_diam < 24:
        badge_diam = 24

    # position: center
    cx, cy = w // 2, h // 2
    left = cx - badge_diam // 2
    top = cy - badge_diam // 2
    right = left + badge_diam
    bottom = top + badge_diam

    # draw white circular background with slight black outline
    draw.ellipse((left, top, right, bottom), fill=(255, 255, 255, 255))
    # optional outline
    draw.ellipse((left, top, right, bottom), outline=(0, 0, 0, 150), width=2)

    # draw initials — choose font size to fit
    try:
        # try to use a truetype font if available
        font_size = int(badge_diam * 0.45)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=font_size)
    except Exception:
        font_size = int(badge_diam * 0.45)
        font = ImageFont.load_default()

    text = initials.strip().upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    text_xy = (cx - tw // 2, cy - th // 2 - 1)  # vertically center tweak

    draw.text(text_xy, text, fill=(0, 0, 0, 255), font=font)
    return img

@app.post("/generate", response_class=StreamingResponse)
async def generate_qr(body: QRRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="`text` is required")

    # limit input to reasonable length to avoid abuse
    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Text too long")

    box = max(2, min(40, body.box_size or 10))
    border = max(0, min(10, body.border or 4))

    # create QR
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,  # high correction so we can overlay initials
        box_size=box,
        border=border
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # compute initials
    initials = (body.initials.strip() if body.initials else None)
    if not initials:
        initials = derive_initials(text)

    if initials:
        # keep only letters/digits, up to 3 chars
        import re
        cleaned = re.sub(r"[^A-Za-z0-9]", "", initials)[:3].upper()
        img = draw_initials_on_qr(img, cleaned)

    # output image bytes
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
