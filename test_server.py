from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    return {"message": "Hello World from Test Server"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
