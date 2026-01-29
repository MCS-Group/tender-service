import json
from src.services.save_excel import save_to_excel, pdf_result_to_excel

file = "C:\\Users\\ItgelOyunbold\\Documents\\itgl\\tender-service\\tender_data\\tender_overviews_with_pdf_info.json"
with open(file, "r", encoding="utf-8") as f:
    overviews = json.load(f)
    pdf_result_to_excel(overviews, "tender_overviews_with_pdf_info.xlsx")
    