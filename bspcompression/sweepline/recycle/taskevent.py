class TaskEvent(Event):

    def __init__(self, time, task):
        self.time = time
        self.task = task

    def __lt__(self, other):
        self.time < other.time

    def trigger(self):
        self.task.execute()
