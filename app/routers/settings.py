from fastapi import APIRouter
from fastapi.params import Depends

from ...core import config


router = APIRouter()


@router.get('/settings')
def get_settings(settings=Depends(config.get_settings())):
    return settings
