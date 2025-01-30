import logging
import azure.functions as func
from trends_fetcher import TrendsFetcher
from data_processor import TrendsProcessor
from db_handler import DatabaseHandler

app = func.FunctionApp()

@app.timer_trigger(schedule="1 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
async def timer_trigger(myTimer: func.TimerRequest) -> None:
    try:
        # Initialize components
        fetcher = TrendsFetcher()
        processor = TrendsProcessor()
        db_handler = DatabaseHandler()

        # Execute pipeline
        raw_trends = await fetcher.get_trending_topics()
        processed_trends = await processor.process_trends_data(raw_trends)
        await db_handler.store_trends(processed_trends)

        logging.info('Successfully processed and stored trends data.')
    except Exception as e:
        logging.error(f'Error in trends processing pipeline: {str(e)}')
