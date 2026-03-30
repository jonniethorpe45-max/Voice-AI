from rq import Worker

from app.jobs.queue import redis_conn


if __name__ == "__main__":
    worker = Worker(["default"], connection=redis_conn)
    worker.work()
