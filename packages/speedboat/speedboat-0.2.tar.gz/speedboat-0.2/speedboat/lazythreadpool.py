from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

import logging

logger = logging.getLogger('speedboat.lazythreadpool')

class LazyThreadPool:

    def __init__(self):
        self.max_workers = 50
        self.max_pending = 200

    def submit(self, f, iterator):
        with ThreadPoolExecutor(max_workers=self.max_workers) as tp:
            futures = set()
            for x in iterator:
                future = tp.submit(f, x)
                futures.add(future)

                while len(futures) > self.max_pending:
                    done, futures = wait(futures, None, FIRST_COMPLETED)
                    for r in done:
                        yield r.result()

            while futures:
                done, futures = wait(futures, None, FIRST_COMPLETED)
                for r in done:
                    yield r.result()


