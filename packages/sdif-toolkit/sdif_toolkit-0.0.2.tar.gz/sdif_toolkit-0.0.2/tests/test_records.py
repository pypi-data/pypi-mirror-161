import unittest
from sdif_toolkit.records import FileDescriptionRecord, MeetRecord, SDIFRecord, TeamIDRecord

class TestSDIFRecord(unittest.TestCase):

    def test_init(self):
        line = "A01V3      02Meet Results                  Hy-Tek, Ltd         WMM 7.0Fb Hy-Tek, Ltd         866-456-511103062022                                    MM40    N42"
        self.assertEqual(SDIFRecord(line).code, "A0")

class TestFileDescriptionRecord(unittest.TestCase):

    def test_init(self):
        line = "A01V3      02Meet Results                  Hy-Tek, Ltd         WMM 7.0Fb Hy-Tek, Ltd         866-456-511103062022                                    MM40    N42"
        record = FileDescriptionRecord(line)

        self.assertEqual(SDIFRecord(line).code, "A0")
        self.assertEqual(record.code, "A0")
        self.assertEqual(record.org_code, "1")
        self.assertEqual(record.sdif_version, "V3")
        self.assertEqual(record.file_code, "02")
        self.assertEqual(record.software_name, "Hy-Tek, Ltd")
        self.assertEqual(record.software_version, "WMM 7.0Fb")
        self.assertEqual(record.contact_name, "Hy-Tek, Ltd")
        self.assertEqual(record.contact_phone, "866-456-5111")
        self.assertEqual(record.file_creation_date, "03062022")
        with self.assertRaises(AttributeError):
            record.submitted_by_lsc

class TestMeetRecord(unittest.TestCase):

    def test_init(self):
        line = "B11        2022 SE Indiana Divisional Cha2717 S Morgantown Rd                        Greenwood           IN46143     USA 0304202203062022   0        Y 500   N28"
        record = MeetRecord(line)

        self.assertEqual(SDIFRecord(line).code, "B1")
        self.assertEqual(record.code, "B1")
        self.assertEqual(record.org_code, "1")
        self.assertEqual(record.name, "2022 SE Indiana Divisional Cha")
        self.assertEqual(record.address_1, "2717 S Morgantown Rd")
        self.assertEqual(record.city, "Greenwood")
        self.assertEqual(record.state, "IN")
        self.assertEqual(record.zip, "46143")
        self.assertEqual(record.start_date, "03042022")
        self.assertEqual(record.end_date, "03062022")
        self.assertEqual(record.altitude, "0")
        self.assertEqual(record.course, "Y")
        with self.assertRaises(AttributeError):
            record.address_2

class TestMeetHostRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestTeamIDRecord(unittest.TestCase):

    def test_init(self):
        line = "C11IN      INFRSTFranklin Regional Swim Team                   654 Walnut St.                              Franklin            IN46131                       N85"
        record = TeamIDRecord(line)

        self.assertEqual(SDIFRecord(line).code, "C1")
        self.assertEqual(record.code, "C1")
        self.assertEqual(record.org_code, "1")
        self.assertEqual(record.team_code, "INFRST")
        self.assertEqual(record.team_name, "Franklin Regional Swim Team")
        self.assertEqual(record.address_1, "654 Walnut St.")
        self.assertEqual(record.city, "Franklin")
        self.assertEqual(record.state, "IN")
        self.assertEqual(record.zip, "46131")
        
        with self.assertRaises(AttributeError):
            record.team_name_abbr
        with self.assertRaises(AttributeError):
            record.address_2
        with self.assertRaises(AttributeError):
            record.region
        with self.assertRaises(AttributeError):
            record.team_code_ext

class TestTeamEntryRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestIndividualEventRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestIndividualAdministrativeRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestIndividualContactRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestIndividualInformationRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestRelayEventRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestRelayNameRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError

class TestSplitsRecord(unittest.TestCase):

    def test_init(self):
        raise NotImplementedError



if __name__ == "__main__":
    unittest.main()