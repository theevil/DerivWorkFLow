from fastapi import APIRouter


router = APIRouter()


@router.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


