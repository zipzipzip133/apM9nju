from PIL import Image
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from io import BytesIO

app = FastAPI()

@app.post("/api/bypass")
async def detect(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(BytesIO(contents))

        width, height = img.size
        part_width = width // 5
        parts = [img.crop((i * part_width, 0, (i + 1) * part_width, height)) for i in range(5)]

        histograms = []
        for part in parts:
            gray = part.convert("L").resize((32, 32))
            hist = np.histogram(np.array(gray), bins=64, range=(0, 256))[0]
            histograms.append(hist)

        dists = np.zeros((5,))
        for i in range(5):
            for j in range(5):
                if i != j:
                    dists[i] += np.sum(np.abs(histograms[i] - histograms[j]))

        odd_one = int(np.argmax(dists)) + 1
        return JSONResponse({"status": "success", "different_position": odd_one})

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# Vercel needs this
asgi_handler = app
      
