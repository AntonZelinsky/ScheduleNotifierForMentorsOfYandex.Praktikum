import logging

import dotenv
from fastapi import Depends, FastAPI

from app.services import CohortService
from core.database import SessionLocal, get_db
from core.services.notion_services import NotionServices

dotenv.load_dotenv()
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    service: CohortService = CohortService(SessionLocal())
    cohorts = service.get_cohorts()
    notion_services = NotionServices()

    user_data = notion_services.get_mentors_on_duty(cohorts)
    pass
