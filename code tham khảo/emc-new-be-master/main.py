import uvicorn
from uvicorn.config import LOGGING_CONFIG

from src.application import create_app

# https://stackoverflow.com/questions/62934384/how-to-add-timestamp-to-each-request-in-uvicorn-logs
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
app = create_app()

# if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    #uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", use_colors=True)