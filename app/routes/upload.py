from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from pydantic import BaseModel

from app.ingest import ingest_documents


router = APIRouter()


DATA_DIR = Path("data")


# ----------------------------
# Response Model
# ----------------------------

class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


# ----------------------------
# Upload Endpoint
# ----------------------------

@router.post(
    "/upload",
    response_model=UploadResponse
)
async def upload_file(
    file: UploadFile = File(...)
) -> UploadResponse:

    try:

        # 1. Validate extension

        if not file.filename.endswith(
            (".txt", ".pdf")
        ):
            raise HTTPException(
                status_code=400,
                detail="Only TXT and PDF files allowed"
            )

        # 2. Create data folder if missing

        DATA_DIR.mkdir(
            exist_ok=True
        )

        # 3. Save uploaded file

        save_path = DATA_DIR / file.filename

        with open(
            save_path,
            "wb"
        ) as f:
            content = await file.read()

            f.write(content)

        # 4. Ingest document
        # split -> embedding -> pgvector insert

        chunks_count = await ingest_documents(
            save_path
        )

        # 5. Response

        return UploadResponse(
            filename=file.filename,
            chunks=chunks_count,
            message="File uploaded and indexed successfully"
        )

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
