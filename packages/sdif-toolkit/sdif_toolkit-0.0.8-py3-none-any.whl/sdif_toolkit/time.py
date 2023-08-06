import re


class Time:
    minutes: int
    seconds: int
    hundredths: int

    @property
    def value(self) -> int:
        return self.minutes * 6000 + self.seconds * 100 + self.hundredths

    def __init__(self, time) -> None:
        if type(time) is int:
            self.minutes  = time // 6000
            self.seconds = (time % 6000) // 100
            self.hundredths = time % 100
        elif type(time) is str:
            m = re.match(r"(?P<minutes>\d*)?:?(?P<seconds>\d{2})[\.:]?(?P<hundredths>\d{1,2})?$", time)

            if m is None:
                raise ValueError(f"Invalid time string: {time}")

            minutes = m.group("minutes")
            if minutes is None or minutes is "":
                self.minutes = 0
            else:
                self.minutes = int(minutes)

            seconds = m.group("seconds")
            self.seconds = int(seconds)

            hundredths = m.group("hundredths")
            if hundredths is None or hundredths is "":
                self.hundredths = 0
            elif len(hundredths) is 1:
                self.hundredths = int(hundredths) * 10
            else:
                self.hundredths = int(hundredths)

    def __repr__(self) -> str:
        minutes = f"{self.minutes}:" if self.minutes > 0 else ""
        return f"{minutes}{self.seconds:02d}.{self.hundredths:02d}"
            