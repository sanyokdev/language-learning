import math
import time


"""
    Some Comment
"""
class TimeTracker:
    def __init__(self, total_items: int):
        self.delay = 0.7
        self.delay_offset = 0

        self.total_items = total_items
        self.progress = 0

        self.start_time = time.time()
        self.end_time = self.start_time
        self.prev_times = []
        self.avg_time_per_item = 0

    def start(self):
        self.start_time = time.time()
        self.progress += 1

    def end(self):
        # Delay the function so we don't request more data than the amount allowed (max is 60rpm)
        time.sleep(self.delay)

        self.end_time = time.time()
        self.prev_times.append(self.end_time - self.start_time)
        self.avg_time_per_item = sum(self.prev_times) / len(self.prev_times)

        self.delay_offset = 1.025 - self.prev_times[len(self.prev_times) - 1]
        self.delay += self.delay_offset

        self.delay = abs(self.delay)

    def print_progress(self):
        time_frac, time_whole = math.modf(round((self.avg_time_per_item * (self.total_items - self.progress)) / 60, 1))
        time_min = int(time_whole)
        time_sec = int(round(time_frac * 60, 2))

        if time_min >= 60:
            time_hour = int(time_min/60)
            time_left_txt = f"Time Left For Chunk: ({ time_hour }h:{ time_min - (60 * time_hour) }m:{ time_sec }s)"
        else:
            time_left_txt = f"Time Left For Chunk: ({ time_min }m:{ time_sec }s)"
        prog_txt = f"Progress: ({ self.progress }/{ self.total_items })"

        print(f"{time_left_txt} | {prog_txt}")

    def print_stats(self):
        print(f"- RPM: { int(60 / self.avg_time_per_item) } | TPR: { round(self.avg_time_per_item, 2) }s")
        # - RPM "Requests per minute"
        # - TPR "Time per request"

    def print_delay(self):
        print(f"- New Delay: { round(self.delay, 5) } | New Offset: { round(self.delay_offset, 5) }")
