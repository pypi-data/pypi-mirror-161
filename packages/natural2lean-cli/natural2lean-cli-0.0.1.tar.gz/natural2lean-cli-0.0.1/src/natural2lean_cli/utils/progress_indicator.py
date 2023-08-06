BACK = "\u001b[1000D" + "\u001b[1A"

COMPLETED = "▰"
LEFT = "▱"


class ProgressIndicator:
    def __init__(self, length: int, total: int):
        self.length = length
        self.total = total
        print()
        self.update(0)

    def update(self, progress: int):
        n = int(progress / self.total * self.length)
        bar = (
            COMPLETED * n
            + LEFT * (self.length - n)
            + f" {int(progress/self.total*100)}%"
        )

        print(BACK + bar)

    def finish(self):
        self.update(self.total)
