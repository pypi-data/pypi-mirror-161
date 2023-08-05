import unittest
from src.sdif_toolkit.time import Time

class TestTimeValidInit(unittest.TestCase):

    def setUp(self) -> None:
        self.expected_minutes = [0, 1, 2, 20, 59]
        self.expected_seconds = [29, 0, 12, 59, 59]
        self.expected_hundredths = [37, 21, 00, 59, 99]
        self.int_input = [2937, 6021, 13200, 125959, 359999]
        self.str_input = ["29.37", "1:00.21", "2:12.00", "20:59.59", "59:59.99"]
        return super().setUp()

    def test_init_int_minutes(self):
        self.assertListEqual([Time(time).minutes for time in self.int_input], self.expected_minutes)

    def test_init_int_seconds(self):
        self.assertListEqual([Time(time).seconds for time in self.int_input], self.expected_seconds)

    def test_init_int_hundredths(self):
        self.assertListEqual([Time(time).hundredths for time in self.int_input], self.expected_hundredths)

    def test_init_str_minutes(self):
        self.assertListEqual([Time(time).minutes for time in self.str_input], self.expected_minutes)

    def test_init_str_seconds(self):
        self.assertListEqual([Time(time).seconds for time in self.str_input], self.expected_seconds)

    def test_init_str_hundredths(self):
        self.assertListEqual([Time(time).hundredths for time in self.str_input], self.expected_hundredths)

class TestTimeSemiValidInit(unittest.TestCase):

    def test_no_semicolon(self):
        time = Time("100.67")
        self.assertEqual(time.minutes, 1)
        self.assertEqual(time.seconds, 0)
        self.assertEqual(time.hundredths, 67)

    def test_no_dot(self):
        time = Time("2:4345")
        self.assertEqual(time.minutes, 2)
        self.assertEqual(time.seconds, 43)
        self.assertEqual(time.hundredths, 45)

    def test_shorthand_hundredths(self):
        time = Time("30.6")
        self.assertEqual(time.minutes, 0)
        self.assertEqual(time.seconds, 30)
        self.assertEqual(time.hundredths, 60)

    def test_no_hundredths(self):
        time = Time("22")
        self.assertEqual(time.minutes, 0)
        self.assertEqual(time.seconds, 22)
        self.assertEqual(time.hundredths, 0)

    def test_semicolon_instead_of_dot(self):
        time = Time("1:03:65")
        self.assertEqual(time.minutes, 1)
        self.assertEqual(time.seconds, 3)
        self.assertEqual(time.hundredths, 65)

class TestTimeInvalidInit(unittest.TestCase):

    def test_not_enough_digits(self):
        with self.assertRaises(ValueError):
            Time("3:3")

    def test_too_many_after_dot(self):
        with self.assertRaises(ValueError):
            Time("1:22.123")

    def test_too_many_between_semicolon_and_dot(self):
        with self.assertRaises(ValueError):
            Time("1:222.00")

    def test_extra_dot(self):
        with self.assertRaises(ValueError):
            Time("1.22.00")
        
class TestTimeStr(unittest.TestCase):

    def setUp(self) -> None:
        self.expected = ["30.60", "1:00.00", "2:15.11"]
        self.int_input = [3060, 6000, 13511]
        self.str_input = ["30.6", "100", "2:15.11"]

    def test_int_to_str(self):
        self.assertListEqual([f"{Time(input)}" for input in self.int_input], self.expected)

    def test_str_to_str(self):
        self.assertListEqual([f"{Time(input)}" for input in self.str_input], self.expected)
