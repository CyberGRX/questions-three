class Status:

    def __init__(self, level, name):
        self.level = level
        self.name = name

    def __eq__(self, other):
        return hasattr(other, 'level') and self.level == other.level

    def __ge__(self, other):
        return self.level >= other.level

    def __gt__(self, other):
        return self.level > other.level

    def __le__(self, other):
        return self.level <= other.level

    def __lt__(self, other):
        return self.level < other.level

    def __str__(self):
        return self.name

    def __repr__(self):
        return('<Jenkins status %s>' % self.name)


PASS = Status(0, 'SUCCESS')
ERROR = Status(1, 'UNSTABLE')
FAIL = Status(2, 'FAILURE')
