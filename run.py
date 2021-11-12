import dotenv
import uvicorn

dotenv.load_dotenv()
from app import main

if __name__ == "__main__":
    uvicorn.run(main.app, host='127.0.0.1', port=8888)
