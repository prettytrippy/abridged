from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from typing import Optional
import io
from file_io import read_file
from summarize import summarize
from ab import params, get_ab_params, store_preference
import numpy as np
import os

app = FastAPI(title="Tripp's No-AI Abridger")

# CORS middleware - adjust origins as needed for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    slider_value: float = Form(...),
    start_page: int = Form(...),
    end_page: int = Form(...)
):
    """
    Upload a file and return its filename and bytes.
    
    Args:
        file: The uploaded file
        slider_value: Value from the slider (0-100)
        start_page: Starting page number to process
        end_page: Ending page number to process
        
    Returns:
        JSON response with text summary
    """
    try:
        # Read the file bytes
        file_bytes = await file.read()
        filename = file.filename
        text = read_file(filename, file_bytes, start_page, end_page)

        if np.random.rand() < 0.05:
            theta1, theta2 = get_ab_params()
            summary_a = summarize(text, slider_value, *theta1)
            summary_b = summarize(text, slider_value, *theta2)

            # Return filename and file info
            return JSONResponse(
                content={
                    "mode": "ab_test",
                    "option_a": summary_a,
                    "option_b": summary_b,
                    "theta_a": theta1.tolist(),
                    "theta_b": theta2.tolist(),
                    "test_id": np.random.randint(0, 1000)
                },
                status_code=200
            )

        else:
            summary = summarize(text, slider_value, *params)
        
            # Return filename and file info
            return JSONResponse(
                content={
                    "mode": "normal",
                    "summary": summary
                },
                status_code=200
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@app.post("/record-preference")
async def record_preference(request: Request):
    uh = await request.json()
    choice = uh['choice']
    theta_a = uh['theta_a']
    theta_b = uh['theta_b']

    if choice == 'a':
        store_preference(theta_a, theta_b)
    else:
        store_preference(theta_b, theta_a)

    return JSONResponse(
                content={},
                status_code=200)

if __name__ == "__main__":
    # Run the server
    # uvicorn.run(
    #     "app:app",
    #     host="0.0.0.0",
    #     port=9876,
    #     reload=True  # Enable auto-reload during development
    # )
    port = int(os.environ.get("PORT", 9876))  # <-- ADD THIS LINE
    uvicorn.run("app:app", host="0.0.0.0", port=port)