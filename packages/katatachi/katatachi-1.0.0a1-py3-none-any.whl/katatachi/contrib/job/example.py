import time

from katatachi.interface.job import Job
from katatachi.interface.job import JobContext


class ExampleJob(Job):
    def __init__(self, wait_seconds: int, print_str: str):
        self.wait_seconds = wait_seconds
        self.print_str = print_str

    def work(self, context: JobContext):
        time.sleep(self.wait_seconds)
        context.logger().info(
            f"{context.content_store().count({})} items in content store"
        )
        context.logger().info(f"print_str={self.print_str}")
