from threading import Timer


class RepeatTimer(Timer):
    """
    Repeat the timer until cancelled
    """

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
