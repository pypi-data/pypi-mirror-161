import argparse, os, re
from tkinter import filedialog
from typing import Dict, List
from sdif_toolkit.records import RECORD_TYPES, MeetRecord, TeamIDRecord, IndividualEventRecord, SplitsRecord, IndividualInformationRecord, RelayEventRecord
from sdif_toolkit.time import Time

STROKES = {
    "1": "Free",
    "2": "Back",
    "3": "Breast",
    "4": "Fly",
    "5": "IM",
    "6": "Free Relay",
    "7": "Medley Relay"
}

RESULT_TYPES = {
    "p": "Prelims",
    "s": "Swim-Off",
    "f": "Finals"
}

GENDERS_BG = {
    "m": "Boys",
    "f": "Girls"
}

class Result:
    time: Time
    type: str
    splits: List[Time] = []
    split_distance: int
    rank: int
    points: float

    def __repr__(self) -> str:
        return f"{self.time} ({RESULT_TYPES[self.type]})"

class Seed:
    time: Time
    heat: int
    lane: int
    rank: int

    def __repr__(self) -> str:
        return f"{self.time}"

class AgeGroup:
    lower_age: int
    upper_age: int

    def __init__(self, lower_age, upper_age) -> None:
        self.lower_age = lower_age
        self.upper_age = upper_age

    def __repr__(self) -> str:
        if self.lower_age > 0 and self.upper_age < 100:
            return f"{self.lower_age}-{self.upper_age}"
        elif self.lower_age <= 0 and self.upper_age < 100:
            return f"{self.upper_age} & Under"
        elif self.lower_age > 0 and self.upper_age >= 100:
            return f"{self.lower_age} & Over"
        else:
            return "Open"

class Event:
    number: str
    age_group: AgeGroup
    gender: str
    event: str
    seed: Time
    results: Dict[str, Result] = {}

    def __repr__(self) -> str:
        return f"{GENDERS_BG[self.gender]} {self.age_group} {self.event}"

class Swimmer:
    id: str
    first_name: str
    pref_name: str
    middle_name: str
    last_name: str
    birthdate: str
    age: int
    events: List[Event] = []

    def __init__(self, full_name) -> None:
        name = parse_name(full_name)
        self.first_name = name["first_name"]
        if "middle_name" in name.keys():
            self.middle_name = name["middle_name"]
        self.last_name = name["last_name"]
        

    def __repr__(self) -> str:
        return self.full_pref_name

    @property
    def full_name(self):
        if hasattr(self, "middle_name"):
            return f"{self.last_name}, {self.first_name} {self.middle_name}"
        else:
            return f"{self.last_name}, {self.first_name}"

    @property
    def full_pref_name(self):
        first = self.pref_name if hasattr(self, "pref_name") else self.first_name
        return f"{self.last_name}, {first}"

class Team:
    name: str
    code: str
    swimmers: List[Swimmer] = []

    def __repr__(self) -> str:
        return f"{self.code} - {self.name}"

class Meet:
    name: str
    teams: List[Team] = []

    def __repr__(self) -> str:
        return self.name


def parse_name(name: str):
    m = re.match(r"^(?P<last_name>.*), (?P<first_name>.*) (?P<middle_name>[A-Z])$", name)
    if m is not None:
        return m.groupdict()

    m = re.match(r"^(?P<last_name>.*), (?P<first_name>.*)$", name)
    if m is not None:
        return m.groupdict()

    raise ValueError("Name not properly formatted")   
    

def read(input):
    """Read .cl2 file into Meet object"""
    if type(input) is str:
        lines = input.split("\n")
    elif type(input) is list:
        lines = input
    elif type(input) is bytes:
        lines = input.decode("utf-8").split("\n")

    output = []

    for line in lines:
        code = line[0:2]
        
        if code in RECORD_TYPES.keys():
            output.append(RECORD_TYPES[code](line))
    
    output = tuple(output)

    meetRecord = next(record for record in output if type(record) is MeetRecord)

    meet = Meet()
    meet.name = meetRecord.name

    team = None
    swimmers = []
    swimmer = None
    event = None
    splits = None
    prevRecord = None

    for record in output:
        
        if type(record) is TeamIDRecord:
            if team is not None and swimmer is not None:
                swimmer.events = events
                swimmers.append(swimmer)
                swimmer = None
                team.swimmers = swimmers
                meet.teams.append(team)

            team = Team()
            team.name = record.team_name
            team.code = record.team_code[2:]
            swimmers = []

        elif type(record) is IndividualEventRecord:
            prevRecord = record
            if event is not None and event.event != f"{record.event_distance} {STROKES[record.stroke]}":
                event.results = results
                events.append(event)

            if swimmer is None:
                swimmer = Swimmer(full_name=record.swimmer_name)
                swimmer.age = int(record.swimmer_age)
                events = []
            elif record.swimmer_name != swimmer.full_name:
                swimmer.events = events
                swimmers.append(swimmer)
                swimmer = Swimmer(full_name=record.swimmer_name)
                swimmer.age = int(record.swimmer_age)
                events = []
            
            event = Event()
            event.event = f"{record.event_distance} {STROKES[record.stroke]}"
            event.number = record.event_number
            lower = 0 if record.event_lower_age == "UN" else int(record.event_lower_age)
            upper = 100 if record.event_upper_age == "OV" else int(record.event_upper_age)
            event.age_group = AgeGroup(lower, upper)
            event.gender = record.event_sex.lower()
            results: Dict[str, Result]= {}

            if hasattr(record, "seed_time"):
                time = record.seed_time
                if time != "NS" and time != "DQ":
                    seed = Seed()
                    seed.time = Time(time)
                    event.seed = seed

            if hasattr(record, "prelim_time"):
                time = record.prelim_time
                if time != "NS" and time != "DQ":
                    prelim_result = Result()
                    prelim_result.type = "p"
                    prelim_result.rank = int(record.prelim_rank)
                    prelim_result.time = Time(time)

                    results["p"] = prelim_result
      
            if hasattr(record, "final_time"):
                time = record.final_time
                if time != "NS" and time != "DQ":
                    final_result = Result()
                    final_result.type = "f"
                    final_result.rank = int(record.final_rank)
                    if hasattr(record, "points"):
                        final_result.points = float(record.points)
                    final_result.time = Time(time)

                    results["f"] = final_result

        elif type(record) is IndividualInformationRecord:
            if hasattr(record, "pref_name"):
                swimmer.pref_name = record.pref_name
            swimmer.id = record.swimmer_id

        elif type(record) is RelayEventRecord:
            prevRecord = record
        
        elif type(record) is SplitsRecord and type(prevRecord) is not RelayEventRecord:
            if splits is None:
                splits = []

            for i in range(min(int(record.num_splits) - len(splits), 10)):
                if hasattr(record, f"time_{i + 1}"):
                    time = getattr(record, f"time_{i + 1}")
                    splits.append(Time(time))
            
            if len(splits) == int(record.num_splits):
                if record.swim_code.lower() in results:
                    results[record.swim_code.lower()].splits = splits
                splits = []


    swimmer.events = events
    swimmers.append(swimmer)
    swimmer = None
    team.swimmers = swimmers
    meet.teams.append(team)

    return meet

def is_valid_path(path):
    """Validates path to ensure it is valid in the current file system"""

    if not path:
        raise ValueError("No path given")
    if os.path.isfile(path) or os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid path: {path}")

def parse_args():
    """Get command line arguments"""

    parser = argparse.ArgumentParser(description="Options")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path, help="The path of the file or folder to process")

    args = vars(parser.parse_args())

    # Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    print("######################################################################")

    return args

def main():

    args = parse_args()

    input_file = args["input_path"]

    if input_file is None:
        input_file = filedialog.askopenfilename()

    if input_file == '':
        exit()

    f = open(input_file)
    meet = read(f.readlines())
    print(meet)


if __name__ == "__main__":
    main()