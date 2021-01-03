import multiprocessing
import uvicorn

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
reload = True
worker_class="uvicorn.workers.UvicornWorker"