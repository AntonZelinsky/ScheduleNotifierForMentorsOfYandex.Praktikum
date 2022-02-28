import logging

import dotenv
from fastapi import Depends, FastAPI

import notion
from app.services import CohortService
from core.database import get_db, SessionLocal

dotenv.load_dotenv()
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    service: CohortService = CohortService(SessionLocal())
    cohorts = service.get_cohorts()

    user_data = notion.get_mentors_on_duty(cohorts)
    pass