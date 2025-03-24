from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
import openpyxl
from deep_translator import GoogleTranslator
from io import BytesIO
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report
from typing import Union, Dict

excel_translator = APIRouter(tags=["Excel Translator"])

@excel_translator.post("/translate")
async def translate_excel(
    file: UploadFile = File(...),
    source_language: str = 'auto',
    destination_language: str = 'es',
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    # Load the workbook from the uploaded file
    # contents = await file.read()
    wb = openpyxl.load_workbook(file.file)
    
    langs_list = GoogleTranslator().get_supported_languages()
    print(langs_list)
    
    translator = GoogleTranslator(source=source_language, target=destination_language)
 
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            texts_to_translate = []
            cells_to_update = []
            
            for cell in row:
                if isinstance(cell.value, str):  # Only translate text values
                    texts_to_translate.append(cell.value)
                    cells_to_update.append(cell)

            if texts_to_translate:
                try:
                    # Batch translate instead of calling API for each cell
                    translated_texts = translator.translate_batch(texts_to_translate)
                    
                    for cell, translated_text in zip(cells_to_update, translated_texts):
                        cell.value = translated_text

                except Exception as e:
                    print(f"Error translating sheet '{sheet.title}': {e}")
    
    
    # Save to a BytesIO buffer
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    original_filename = file.filename

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "POST /translate",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
    
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=translated_{original_filename}"})