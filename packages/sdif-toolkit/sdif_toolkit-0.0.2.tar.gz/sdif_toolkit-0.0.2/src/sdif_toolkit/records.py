import json


class SDIFRecord:

    code: str

    encodings: dict = {
        "code": (0,2)
    }

    def __init__(self, data: str):
        for key in self.encodings:
            value = data[self.encodings[key][0]:self.encodings[key][1]].strip()

            if(value == ""):
                continue

            setattr(self, key, value)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    

class FileDescriptionRecord(SDIFRecord):
    """This record is mandatory for each transfer of data within this
	  file structure.  Each file begins with this record and each file
	  has only one record of this type."""

    code: str
    org_code: str
    sdif_version: str
    file_code: str
    software_name: str
    software_version: str
    contact_name: str
    contact_phone: str
    file_creation_date: str
    submitted_by_lsc: str

    encodings = {
        "code" : (0,2),
        "org_code" : (2,3),
        "sdif_version": (3,11),
        "file_code": (11,13),
        "software_name": (43,63),
        "software_version": (63,73),
        "contact_name": (73,93),
        "contact_phone": (93,105),
        "file_creation_date": (105,113),
        "submitted_by_lsc": (155,157)
    }

    def __init__(self, data: str):
        super().__init__(data)


class MeetRecord(SDIFRecord):
    """This record is used to identify the meet name and address.  The
	  meet name is required, plus the city, state, meet type, start
	  and end dates.  Additional fields provide for the street address,
	  postal code and country code.  Each file may only have one
	  record of this type."""

    code: str
    org_code: str
    name: str
    address_1: str
    address_2: str
    city: str
    state: str
    zip: str
    country: str
    meet_code: str
    start_date: str
    end_date: str
    altitude: str
    course: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "name": (11,41),
        "address_1": (41,63),
        "address_2": (63,85),
        "city": (85,105),
        "state": (105,107),
        "zip": (107,117),
        "country": (117,120),
        "meet_code": (120,121),
        "start_date": (121,129),
        "end_date": (129,137),
        "altitude": (137,141),
        "course": (149,150)
    }
    
    def __init__(self, data: str):
        super().__init__(data)

class MeetHostRecord(SDIFRecord):
    """This record is used to identify the meet host or hosts and the
	  host address.  The meet host name is required.  Additional
	  fields provide for the street address, city, state, postal code,
	  country code and phone number."""
    
    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "name": (11,41),
        "address_1": (41,63),
        "address_2": (63,85),
        "city": (85,105),
        "state": (105,107),
        "zip": (107,117),
        "country": (117,120),
        "phone": (120,132)
    }

    def __init__(self, data: str):
        super().__init__(data)

class TeamIDRecord(SDIFRecord):
    """This record is used to identify the team name, team code, plus
	  region.  When used, more than one team record can be transmitted
	  for a single meet.  The team name, USS team code and team
	  abbreviation are required.  The USS region code is also required.
	  Additional fields provide for the street address, city, state,
	  postal code, and country code."""
    
    code: str
    org_code: str
    team_code: str
    team_name: str
    team_name_abbr: str
    address_1: str
    address_2: str
    city: str
    state: str
    zip: str
    country: str
    region: str
    team_code_ext: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "team_code": (11,17),
        "team_name": (17,47),
        "team_name_abbr": (47,63),
        "address_1": (63,85),
        "address_2": (85,107),
        "city": (107,127),
        "state": (127,129),
        "zip": (129,139),
        "country": (139,142),
        "region": (142,143),
        "team_code_ext": (149,150),
    }
    
    def __init__(self, data: str):
        super().__init__(data)

class TeamEntryRecord(SDIFRecord):
    """This record is used to identify the team coach.  When used, one
	  team entry record would be submitted with the C1 team ID record.
	  The USS team code and team coach field are required.  Additional
	  fields provide for the number of individual swimmers, number of
	  splash records, number of relay entries, number of relay name
	  entries and number of split records."""

    code: str
    org_code: str
    team_code: str
    coach_name: str
    coach_phone: str
    num_entries: str
    num_athletes: str
    num_relay_entries: str
    num_relay_swimmers: str
    num_splits: str
    team_name_abbr: str
    team_code_ext: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "team_code": (11,17),
        "coach_name": (17,47),
        "coach_phone": (47,59),
        "num_entries": (59,65),
        "num_athletes": (65,71),
        "num_relay_entries": (71,76),
        "num_relay_swimmers": (76,82),
        "num_splits": (82,88),
        "team_name_abbr": (88,104),
        "team_code_ext": (149,150)
    }

    def __init__(self, data: str):
        super().__init__(data)

class IndividualEventRecord(SDIFRecord):
    """This record is used to identify the athlete and the individual
	  event.  When used, one individual event record would be
	  submitted for each swimmer entered in an individual event.  The
	  athlete name, USS registration number, birth date and gender
	  code are required.  Fields for the stroke, distance, event
	  number, age range, and date of swim are also required.
	  Additional fields provide for the citizenship, age or class, 
	  seed time, prelim time, swim off time, finals time and pool
	  lanes used in competition.

	  NOTE:  Individual event records must be preceded by at least one
	  C1 team ID record and one C2 team entry record.  If these two 
	  records are missing, the individual is assumed to be attached
	  to the previous "team" that has proper coding.  Athlete
	  registration data is not available to meet management programs
	  and proper coding is essential."""
    

    code: str
    org_code: str
    swimmer_name: str
    swimmer_id: str
    attach_code: str
    citizen_code: str
    swimmer_birthdate: str
    swimmer_age: str
    swimmer_sex: str
    event_sex: str
    event_distance: str
    stroke: str
    event_number: str
    event_lower_age: str
    event_upper_age: str
    date: str
    seed_time: str
    seed_course: str
    prelim_time: str
    prelim_course: str
    swimoff_time: str
    swimoff_course: str
    final_time: str
    final_course: str
    prelim_heat: str
    prelim_lane: str
    final_heat: str
    final_lane: str
    prelim_rank: str
    final_rank: str
    points: str
    time_class: str
    flight: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "swimmer_name": (11,39),
        "swimmer_id": (39,51),
        "attach_code": (51,52),
        "citizen_code": (52,55),
        "swimmer_birtdate": (55,63),
        "swimmer_age": (63,65),
        "swimmer_sex": (65,66),
        "event_sex": (66,67),
        "event_distance": (67,71),
        "stroke": (71,72),
        "event_number": (72,76),
        "event_lower_age": (76,78),
        "event_upper_age": (78,80),
        "date": (80,88),
        "seed_time": (88,96),
        "seed_course": (96,97),
        "prelim_time": (97,105),
        "prelim_course": (105,106),
        "swimoff_time": (106,114),
        "swimoff_course": (114,115),
        "final_time": (115,123),
        "final_course": (123,124),
        "prelim_heat": (124,126),
        "prelim_lane": (126,128),
        "final_heat": (128,130),
        "final_lane": (130,132),
        "prelim_rank": (132,135),
        "final_rank": (135,138),
        "points": (138,142),
        "time_class": (142,144),
        "flight": (144,145)
    }
    
    def __init__(self, data: str):
        super().__init__(data)


class IndividualAdministrativeRecord(SDIFRecord):
    """This record is used to identify the athlete and his/her
	  administrative information. When used, one individual
	  administrative record would be submitted for each swimmer in
	  the file.  The athlete name, USS registration number, birth
	  date and gender code are required."""
    
    code: str
    org_code: str
    team_code: str
    team_code_ext: str
    swimmer_name: str
    swimmer_id: str
    attach_code: str
    citizen_code: str
    swimmer_birthdate: str
    swimmer_age: str
    swimmer_sex: str
    admin_info_1: str
    admin_info_4: str
    swimmer_phone_1: str
    swimmer_phone_2: str
    swimmer_reg_date: str
    member_code: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "team_code": (11,17),
        "team_code_ext": (17,18),
        "swimmer_name": (18,46),
        "swimmer_id": (47,59),
        "attach_code": (59,60),
        "citizen_code": (60,63),
        "swimmer_birthdate": (63,71),
        "swimmer_age": (71,73),
        "swimmer_sex": (73,74),
        "admin_info_1": (74,104),
        "admin_info_4": (104,124),
        "swimmer_phone_1": (124,136),
        "swimmer_phone_2": (136,148),
        "swimmer_reg_date": (148,156),
        "member_code": (156,157)
    }

    def __init__(self, data: str):
        super().__init__(data)

class IndividualContactRecord(SDIFRecord):
    """This record is used to identify the athlete and his/her contact
	  information. When used, one individual contact record would be
	  submitted for each swimmer in the file.  The athlete name is
	  required. """
    
    code: str
    org_code: str
    team_code: str
    team_code_ext: str
    swimmer_name: str
    swimmer_name_alt: str
    address: str
    city: str
    state: str
    country: str
    zip: str
    country_code: str
    region_code: str
    answer_code: str
    season_code: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "team_code": (11,17),
        "team_code_ext": (17,18),
        "swimmer_name": (18,46),
        "swimmer_name_alt": (46,76),
        "address": (76,106),
        "city": (106,126),
        "state": (126,128),
        "country": (128,140),
        "zip": (140,150),
        "country_code": (150,153),
        "region_code": (153,154),
        "answer_code": (154,155),
        "season_code": (155,156)
    }

    def __init__(self, data: str):
        super().__init__(data)

class IndividualInformationRecord(SDIFRecord):
    """This record provides space for the new USS# as well as the 
	  swimmers preferred first name. For meet files this record will 
	  follow the D0 record and the F0 record if relays are included.
	  A swimmer with multiple D0 records will have one D3 record 
	  following his/her first D0 record."""
    
    code: str
    swimmer_id: str
    pref_name: str
    ethnicity_code: str
    junior_high_flag: str
    senior_high_flag: str
    ymca_flag: str
    college_flag: str
    summer_league_flag: str
    masters_flag: str
    para_flag: str
    water_polo_flag: str
    none_flag: str

    encodings = {
        "code": (0,2),
        "swimmer_id": (2,16),
        "pref_name": (16,31),
        "ethnicity_code": (31,33),
        "junior_high_flag": (33,34),
        "senior_high_flag": (34,35),
        "ymca_flag": (35,36),
        "college_flag": (36,37),
        "summer_league_flag": (37,38),
        "masters_flag": (38,39),
        "para_flag": (39,40),
        "water_polo_flag": (40,41),
        "none_flag": (41,42),
    }

    def __init__(self, data: str):
        super().__init__(data)

class RelayEventRecord(SDIFRecord):
    """This record is used to identify the team and the relay event.
	  When used, one relay event record would be submitted for each
	  relay squad entered in a relay event.  The relay team name, USS
	  team code, and gender code are required.  Fields for the stroke,
	  distance, event number, age range, and date of swim, are also
	  required.  Additional fields provide for the age or class, seed
	  time, prelim time, swim off time, finals time, and pool lanes
	  used in competition."""
    
    code: str
    org_code: str
    relay_id: str
    team_code: str
    num_swimmers: str
    event_sex: str
    distance: str
    stroke: str
    event_number: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "relay_id": (11,12),
        "team_code": (12,18),
        "num_swimmers": (18,20),
        "event_sex": (20,21),
        "distace": (21,25),
        "stroke": (25,26),
        "event_number": (26,30),
        "event_age": (30,34),
        "total_age": (34,37),
        "date": (37,45),
        "seed_time": (45,53),
        "seed_course": (53,54),
        "prelim_time": (54,62),
        "prelim_course": (62,63),
        "swimoff_time": (63,71),
        "swimoff_course": (71,72),
        "final_time": (72,80),
        "final_course": (80,81),
        "prelim_heat": (81,83),
        "prelim_lane": (83,85),
        "final_heat": (85,87),
        "final_lane": (87,89),
        "prelim_rank": (89,92),
        "final_rank": (92,95),
        "points": (95,99),
        "time_class": (99,101)
    }

    def __init__(self, data: str):
        super().__init__(data)

class RelayNameRecord(SDIFRecord):
    """This record is used to identify the athletes on a relay team and
	  the relay order.  When used, one relay name record is submitted
	  for each relay athlete entered in a relay event.  Alternates may
	  be listed on additional records as an optional method of using
	  this record.  The relay team name, USS team code, and gender
	  code are required.  The Event ID # field (12/4) is required to
	  properly identify the relay team to an event and to further link
	  the splits for a relay athlete.  Fields for the stroke, distance,
	  event number, age or class, and date of swim, are also required.
	  Additional fields provide for the seed time, prelim time, swim
	  off time, finals time, and pool lanes used in competition.

	  NOTE:  Relay name records must be preceded by at least one E0
	  relay event record.  If this record is missing, the athlete on a 
	  relay team cannot be attached to the proper relay squad."""

    code: str
    org_code: str
    team_code: str
    realy_id: str
    swimmer_name: str
    swimmer_id: str
    citizen_code: str
    swimmer_birthdate: str
    swimmer_age: str
    event_sex: str
    prelim_order: str
    swimoff_order: str
    final_order: str
    split_time: str
    split_course: str
    takeoff_time: str
    swimmer_id_full: str
    pref_name: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "team_code": (15,21),
        "relay_id": (21,22),
        "swimmer_name": (22,50),
        "swimmer_id": (50,62),
        "citizen_code": (62,65),
        "swimmer_birthdate": (65,73),
        "swimmer_age": (73,75),
        "event_sex": (75,76),
        "prelim_order": (76,77),
        "swimoff_order": (77,78),
        "final_order": (78,79),
        "split_time": (79,87),
        "split_course": (87,88),
        "takeoff_time": (88,92),
        "swimmer_id_full": (92,106),
        "pref_name": (106,121) 
    }

    def __init__(self, data: str):
        super().__init__(data)

class SplitsRecord(SDIFRecord):
    """This record is used to identify the athletes in an event and the
	  split times.  When used, one splits record would be submitted for
	  each event that an athlete entered in a meet.  The athlete name,
	  USS registration code, and split distance are required.    
	  A split type code is required to identify the split
	  as an interval or cumulative time.  Ten time fields are provided
	  to record the splits, and multiple records may be used to
	  complete all splits for a long-distance event.

	  NOTE:  Splits records must be preceded by at least one D0 
	  individual event record or one F0 relay name record.  If this 
	  record is missing, there is no way to connect the splits with
	  the swim."""

    code: str
    org_code: str
    swimmer_name: str
    swimmer_id: str
    sequence: str
    num_splits: str
    split_distance: str
    split_code: str
    time_1: str
    time_2: str
    time_3: str
    time_4: str
    time_5: str
    time_6: str
    time_7: str
    time_8: str
    time_9: str
    time_10: str
    swim_code: str

    encodings = {
        "code": (0,2),
        "org_code": (2,3),
        "swimmer_name": (15,43),
        "swimmer_id": (43,55),
        "sequence": (55,56),
        "num_splits": (56,58),
        "split_distance": (58,62),
        "split_code": (62,63),
        "time_1": (63,71),
        "time_2": (71,79),
        "time_3": (79,87),
        "time_4": (87,95),
        "time_5": (95,103),
        "time_6": (103,111),
        "time_7": (111,119),
        "time_8": (119,127),
        "time_9": (127,135),
        "time_10": (135,143),
        "swim_code": (143,144)
    }

    def __init__(self, data: str):
        super().__init__(data)


RECORD_TYPES = {
    "A0": FileDescriptionRecord,
    "B1": MeetRecord,
    "B2": MeetHostRecord,
    "C1": TeamIDRecord,
    "C2": TeamEntryRecord,
    "D0": IndividualEventRecord,
    "D1": IndividualAdministrativeRecord,
    "D2": IndividualContactRecord,
    "D3": IndividualInformationRecord,
    "E0": RelayEventRecord,
    "F0": RelayNameRecord,
    "G0": SplitsRecord
}