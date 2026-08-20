from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
import os, uuid, traceback

app = FastAPI()
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class RenderReq(BaseModel):
    html: str
    width: int = 1056
    height: int = 1584

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/render")
async def render(req: RenderReq, request: Request):
    try:
        filename = f"{uuid.uuid4().hex}.png"
        output_path = f"static/{filename}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            page = await browser.new_page(viewport={"width": req.width, "height": req.height})
            await page.set_content(req.html, wait_until="load")
            await page.screenshot(path=output_path, full_page=False)
            await browser.close()

        base = str(request.base_url).rstrip("/")
        return {"url": f"{base}/static/{filename}"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )
