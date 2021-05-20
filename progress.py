import time

class Progress:
    def __init__(self, total, updateEvery):
        self.total = total
        self.start = time.time()
        self.updateEvery = updateEvery
        self.current = 0
        if self.updateEvery is not None:
            print('START (%d total, updates every %d)' % (self.total, self.updateEvery))
    def update(self):
        if self.updateEvery is None:
            return
        self.current += 1
        if self.current % self.updateEvery == 0 or self.current == self.total:
            print('%d / %d = %.3f (%.2f s)' % (
                self.current,
                self.total,
                self.current/self.total,
                time.time()-self.start
            ))
