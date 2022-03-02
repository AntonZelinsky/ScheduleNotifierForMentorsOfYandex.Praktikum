import dotenv
import uvicorn

dotenv.load_dotenv()
from app import main

if __name__ == "__main__":
    uvicorn.run(main.create_app(), host='0.0.0.0', port=8888)
