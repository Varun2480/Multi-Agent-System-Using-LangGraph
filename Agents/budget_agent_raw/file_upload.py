# file_upload.py
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Response, status
from fastapi.responses import StreamingResponse

app = FastAPI()

# Define the required columns for the Excel template
EXCEL_COLUMNS = [
    "date",
    "category",
    "description",
    "amount",
    "type(credit/debit)",
    "location",
]


@app.get("/template", summary="Get Excel Template")
async def get_excel_template():
    """
    Generates and returns an Excel file template with predefined columns.
    """
    # Create an empty pandas DataFrame with the specified columns
    df = pd.DataFrame(columns=EXCEL_COLUMNS)

    # Use BytesIO to save the DataFrame to an in-memory Excel file
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)  # Rewind the buffer to the beginning

    # Return the Excel file as a StreamingResponse for download
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=transaction_template.xlsx"
        },
    )


@app.post("/upload", summary="Upload Excel File")
async def upload_excel_file(file: UploadFile = File(...)):
    """
    Accepts an Excel file upload, reads its content, and processes it.
    """
    # Validate file type
    if not file.filename.endswith((".xlsx", ".xls")):
        return Response(
            content="Only .xlsx and .xls files are allowed.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Read the uploaded file content into a BytesIO buffer
        file_content = await file.read()
        excel_buffer = io.BytesIO(file_content)

        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(excel_buffer, engine="openpyxl")

        # --- Basic Validation (Optional but Recommended) ---
        # Check if required columns are present
        missing_columns = [col for col in EXCEL_COLUMNS if col not in df.columns]
        if missing_columns:
            return Response(
                content=f"Missing required columns: {', '.join(missing_columns)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # --- Data Processing (Placeholder for your calculation logic) ---
        print(f"Successfully read file: {file.filename}")
        print("DataFrame head:")
        print(df.head())

        # You can now access and process the data in the 'df' DataFrame
        # For example, store 'df' in a global variable or pass it to another function
        # for your "later calculation".

        return {"filename": file.filename, "message": "File uploaded and read successfully."}

    except Exception as e:
        print(f"Error processing file: {e}")
        return Response(
            content=f"Error processing file: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# To run this application:
# 1. Save the code as file_upload.py
# 2. Install necessary libraries: pip install fastapi uvicorn pandas openpyxl
# 3. Run from your terminal: uvicorn file_upload:app --reload
# 4. Access the interactive API docs at http://127.0.0.1:8000/docs
