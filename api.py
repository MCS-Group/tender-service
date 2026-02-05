import os
import sys
import time
import asyncio
from pydantic import BaseModel
from fastapi import FastAPI
import dotenv
from src.logger import logger
from main import main as process_tender_data
from main import specific_pdf_download
from src.services.save_excel import save_to_excel, pdf_result_to_excel
from src.services.send_email import send_email, send_notification_email
dotenv.load_dotenv()

app = FastAPI(
    title="Tender Document Analysis API",
    description="API for processing tender document data and generating comprehensive Excel reports",
    version="1.0.0"
)

#Request and Response Models
class TenderRequest(BaseModel):
    date_from: str
    date_to: str

class TenderResponse(BaseModel):
    status: str
    message: str
    statistics: dict
    timestamp: str


# API Endpoints
@app.get("/", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    logger.info("Health check requested")
    return {
        "service": "Tender Document analysis API",
        "status": "running",
        "version": "1.0.0",
    }
@app.post("/process_tenders_default", response_model=TenderResponse, tags=["Tender Processing"])
async def process_tenders_default(request: TenderRequest):
    start_time = time.time()
    logger.info(f"Processing tenders from {request.date_from} to {request.date_to}")
    try:
        output_name = f"tender_overviews_{request.date_from}_to_{request.date_to}"
        overviews = await process_tender_data(output_name=output_name, start_date=request.date_from, end_date=request.date_to)
        end_time = time.time()
        elapsed_time = end_time - start_time
        statistics = {
            "date_from": request.date_from,
            "date_to": request.date_to,
            "processing_time_seconds": elapsed_time
        }

        if not overviews:
            send_notification_email(
                report_title="Tender Overview Report",
                message="No tenders found in the specified date range.",
                type="default"
            )
            return TenderResponse(
                status="success",
                message="No tenders found in the specified date range.",
                statistics=statistics,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            )

        

        logger.info("Saving tender overviews to Excel")
        excel_filepath = f"tender_data/tender_overviews_{request.date_from}_to_{request.date_to}.xlsx"
        save_to_excel(overviews, excel_filepath)

        logger.info("Sending email with Excel report")

        with open(excel_filepath, 'rb') as f: 
            filedata = f.read()
        
        send_email(
            filename=os.path.basename(excel_filepath),
            filedata=filedata, 
            report_title="Tender Overview Report",
            total_tenders=len(overviews),
        )
    
        logger.info(f"Tender processing completed in {elapsed_time:.2f} seconds")
        return TenderResponse(
            status="success",
            message="Tender data processed successfully.",
            statistics=statistics,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    except Exception as e:
        logger.error(f"Error processing tenders: {e}")
        return TenderResponse(
            status="error",
            message=str(e),
            statistics={},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    
@app.post("/process_tenders", response_model=TenderResponse, tags=["Tender Processing"])
async def process_tenders(request: TenderRequest):
    start_time = time.time()
    logger.info(f"Processing tenders from {request.date_from} to {request.date_to}")
    try:
        output_name = f"tender_overviews_{request.date_from}_to_{request.date_to}"
        overviews = await process_tender_data(output_name=output_name, start_date=request.date_from, end_date=request.date_to)
        end_time = time.time()
        elapsed_time = end_time - start_time
        statistics = {
            "date_from": request.date_from,
            "date_to": request.date_to,
            "processing_time_seconds": elapsed_time
        }
        if not overviews:
            return TenderResponse(
                status="success",
                message="No tenders found in the specified date range.",
                statistics=statistics,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            )

        specific_filename = f"specific_tender_pdfs_{request.date_from}_to_{request.date_to}"
        pdf_results = await specific_pdf_download(overviews, specific_filename)
        
        # Calculate statistics
        total_pdfs = sum(len(result.get('pdf_paths', [])) for result in pdf_results)
        
        #save excel
        excel_filepath = f"tender_data/tender_overviews_pdf_{request.date_from}_to_{request.date_to}.xlsx"
        pdf_result_to_excel(pdf_results, excel_filepath)
        with open(excel_filepath, 'rb') as f: 
            filedata = f.read()
        
        date_range = f"{request.date_from} to {request.date_to}"
        send_email(
            filename=os.path.basename(excel_filepath),
            filedata=filedata, 
            report_title="Tender Analysis with PDF Reports",
            total_tenders=len(overviews),
        )
    
        logger.info(f"Tender processing completed in {elapsed_time:.2f} seconds")
        return TenderResponse(
            status="success",
            message="Tender data processed successfully.",
            statistics=statistics,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    except Exception as e:
        logger.error(f"Error processing tenders: {e}")
        return TenderResponse(
            status="error",
            message=str(e),
            statistics={},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    
#Monday run 6,7,1
@app.post("/monday_tender_process", response_model=TenderResponse, tags=["Tender Processing"])
async def monday_tender_process():
    start_time = time.time()
    date_to = time.strftime("%Y-%m-%d", time.gmtime(start_time))
    date_from = time.strftime("%Y-%m-%d", time.gmtime(start_time - 2 * 24 * 60 * 60))  # 2 days back to cover weekend
    logger.info(f"Processing tenders from {date_from} to {date_to} - Monday run")
    try:
        output_name = f"tender_overviews_{date_from}_to_{date_to}"
        overviews = await process_tender_data(output_name=output_name, start_date=date_from, end_date=date_to)
        end_time = time.time()
        elapsed_time = end_time - start_time
        statistics = {
            "date_from": date_from,
            "date_to": date_to,
            "processing_time_seconds": elapsed_time
        }
        if not overviews:
            send_notification_email(
                report_title="Tender Overview Report",
                message="No tenders found in the specified date range.",
                type="special_monday"
            )
            return TenderResponse(
                status="success",
                message="No tenders found in the specified date range.",
                statistics=statistics,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            )
        
        #before pdf to send mail
        before_pdf_excel = f"tender_data/tender_overviews_{date_from}_to_{date_to}.xlsx"
        save_to_excel(overviews, before_pdf_excel)
        with open(before_pdf_excel, 'rb') as f: 
            filedata = f.read()
        send_email(
            filename=os.path.basename(before_pdf_excel),
            filedata=filedata,
            report_title="Tender Overview Report",
            total_tenders=len(overviews),
            type="special_monday",
            mail_type="special"
        )

        specific_filename = f"specific_tender_pdfs_{date_from}_to_{date_to}"
        pdf_results = await specific_pdf_download(overviews, specific_filename)
        
        # Calculate statistics
        total_pdfs = sum(len(result.get('pdf_paths', [])) for result in pdf_results)
        
        #save excel
        excel_filepath = f"tender_data/tender_overviews_pdf_{date_from}_to_{date_to}.xlsx"
        pdf_result_to_excel(pdf_results, excel_filepath)
        with open(excel_filepath, 'rb') as f: 
            filedata = f.read()
        
        send_email(
            filename=os.path.basename(excel_filepath),
            filedata=filedata, 
            report_title="Tender Analysis with PDF Reports - Monday Batch",
            total_tenders=len(overviews),
            type="special_monday"
        )
    
        logger.info(f"Monday tender processing completed in {elapsed_time:.2f} seconds")
        return TenderResponse(
            status="success",
            message="Tender data processed successfully.",
            statistics=statistics,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    except Exception as e:
        logger.error(f"Error processing tenders: {e}")
        return TenderResponse(
            status="error",
            message=str(e),
            statistics={},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )

#Wednesday run 2,3
@app.post("/wednesday_tender_process", response_model=TenderResponse, tags=["Tender Processing"])
async def wednesday_tender_process():
    """
    Process tender documents for the given date range and generate an Excel report.
    This endpoint is intended to be triggered by a Wednesday scheduler.
    """
    start_time = time.time()
    date_to = time.strftime("%Y-%m-%d", time.gmtime(start_time))
    date_from = time.strftime("%Y-%m-%d", time.gmtime(start_time - 1 * 24 * 60 * 60))  # 1 day back
    logger.info(f"Processing tenders from {date_from} to {date_to} - Wednesday run")

    try:
        output_name = f"tender_overviews_{date_from}_to_{date_to}"
        overviews = await process_tender_data(output_name=output_name, start_date=date_from, end_date=date_to)
        end_time = time.time()
        elapsed_time = end_time - start_time
        statistics = {
            "date_from": date_from,
            "date_to": date_to,
            "processing_time_seconds": elapsed_time
        }
        if not overviews:
            send_notification_email(
                report_title="Tender Overview Report",
                message="No tenders found in the specified date range.",
                type="special_wednesday"
            )
            return TenderResponse(
                status="success",
                message="No tenders found in the specified date range.",
                statistics=statistics,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            )

        specific_filename = f"specific_tender_pdfs_{date_from}_to_{date_to}"
        pdf_results = await specific_pdf_download(overviews, specific_filename)
        #before pdf to send mail
        before_pdf_excel = f"tender_data/tender_overviews_{date_from}_to_{date_to}.xlsx"
        save_to_excel(overviews, before_pdf_excel)
        # Calculate statistics
        total_pdfs = sum(len(result.get('pdf_paths', [])) for result in pdf_results)
        
        #save excel
        excel_filepath = f"tender_data/tender_overviews_pdf_{date_from}_to_{date_to}.xlsx"
        pdf_result_to_excel(pdf_results, excel_filepath)
        with open(excel_filepath, 'rb') as f: 
            filedata = f.read()
        
        send_email(
            filename=os.path.basename(excel_filepath),
            filedata=filedata, 
            report_title="Tender Analysis with PDF Reports - Wednesday Batch",
            total_tenders=len(overviews),
            type="special_wednesday"
        )
    
        logger.info(f"Wednesday tender processing completed in {elapsed_time:.2f} seconds")
        return TenderResponse(
            status="success",
            message="Tender data processed successfully.",
            statistics=statistics,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )

    except Exception as e:
        logger.error(f"Error processing tenders: {e}")
        return TenderResponse(
            status="error",
            message=str(e),
            statistics={},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    
#Friday run 4,5
@app.post("/friday_tender_process", response_model=TenderResponse, tags=["Tender Processing"])
async def friday_tender_process():
    """
    Process tender documents for the given date range and generate an Excel report.
    This endpoint is intended to be triggered by a Friday scheduler.
    """
    start_time = time.time()
    date_to = time.strftime("%Y-%m-%d", time.gmtime(start_time))
    date_from = time.strftime("%Y-%m-%d", time.gmtime(start_time - 1 * 24 * 60 * 60))  # 1 day back
    logger.info(f"Processing tenders from {date_from} to {date_to} - Friday run")

    try:
        output_name = f"tender_overviews_{date_from}_to_{date_to}"
        overviews = await process_tender_data(output_name=output_name, start_date=date_from, end_date=date_to)
        end_time = time.time()
        elapsed_time = end_time - start_time
        statistics = {
            "date_from": date_from,
            "date_to": date_to,
            "processing_time_seconds": elapsed_time
        }
        if not overviews:
            send_notification_email(
                report_title="Tender Overview Report",
                message="No tenders found in the specified date range.",
                type="default"
            )
            return TenderResponse(
                status="success",
                message="No tenders found in the specified date range.",
                statistics=statistics,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            )
        else:
            #before pdf to send mail
            before_pdf_excel = f"tender_data/tender_overviews_{date_from}_to_{date_to}.xlsx"
            save_to_excel(overviews, before_pdf_excel)
            with open(before_pdf_excel, 'rb') as f: 
                filedata = f.read()
            send_email(
                filename=os.path.basename(before_pdf_excel),
                filedata=filedata, 
                report_title="Tender Overview Report",
                total_tenders=len(overviews),
                type="special_friday",
                mail_type="special"
            )

        

        specific_filename = f"specific_tender_pdfs_{date_from}_to_{date_to}"
        pdf_results = await specific_pdf_download(overviews, specific_filename)
        
        if not pdf_results:
            send_notification_email(
                report_title="Tender PDF Download Report",
                message="No PDFs were downloaded for the tenders in the specified date range.",
                type="special_friday"
            )
            return TenderResponse(
                status="success",
                message="No PDFs were downloaded for the tenders in the specified date range.",
                statistics=statistics,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            )

        #save excel
        excel_filepath = f"tender_data/tender_overviews_pdf_{date_from}_to_{date_to}.xlsx"
        pdf_result_to_excel(pdf_results, excel_filepath)
        with open(excel_filepath, 'rb') as f: 
            filedata = f.read()

        send_email(
            filename=os.path.basename(excel_filepath),
            filedata=filedata, 
            report_title="Tender Analysis with PDF Reports - Friday Batch",
            total_tenders=len(overviews),
            type="special_friday"
        )
    
        logger.info(f"Friday tender processing completed in {elapsed_time:.2f} seconds")
        return TenderResponse(
            status="success",
            message="Tender data processed successfully.",
            statistics=statistics,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    except Exception as e:
        logger.error(f"Error processing tenders: {e}")
        return TenderResponse(
            status="error",
            message=str(e),
            statistics={},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    

@app.post("/daily_tender_process", response_model=TenderResponse, tags=["Tender Processing"])
async def daily_tender_process():
    start_time = time.time()
    logger.info("Starting daily tender processing")
    try:
        today_date = time.strftime("%Y-%m-%d", time.gmtime())
        output_name = f"tender_overviews_{today_date}"
        overviews =await process_tender_data(output_name=output_name, start_date=today_date, end_date=today_date)
        end_time = time.time()
        elapsed_time = end_time - start_time
        statistics = {
            "date": today_date,
            "processing_time_seconds": elapsed_time
        }
        logger.info(f"Daily tender processing completed in {elapsed_time:.2f} seconds")

        if not overviews:
            send_notification_email(
                report_title="Daily Tender Overview Report",
                message="No tenders found for today.",
                type="default"
            )
            return TenderResponse(
                status="success",
                message="No tenders found for today.",
                statistics=statistics,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            )

        #send email with summary
        excel_filepath = f"tender_data/tender_overviews_{today_date}.xlsx"
        with open(excel_filepath, 'rb') as f:
            filedata = f.read()
        send_email(
            filename=os.path.basename(excel_filepath),
            filedata=filedata,
            report_title="Daily Tender Overview Report",
            total_tenders=0,
        )

        return TenderResponse(
            status="success",
            message="Daily tender data processed successfully.",
            statistics=statistics,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )


    except Exception as e:
        logger.error(f"Error in daily tender processing: {e}")
        return TenderResponse(
            status="error",
            message=str(e),
            statistics={},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)