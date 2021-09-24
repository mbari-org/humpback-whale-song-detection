import time
import unittest

from misc import elapsed_end, parse_days


class Test(unittest.TestCase):
    def test_elapsed_end(self):
        self.assertEqual("5.0s", elapsed_end(time.time() - 5))
        self.assertEqual("59.0s", elapsed_end(time.time() - 59))
        self.assertEqual("01m:02s", elapsed_end(time.time() - 62))
        self.assertEqual("59m:00s", elapsed_end(time.time() - 59 * 60))
        self.assertEqual("01h:00m:00s", elapsed_end(time.time() - 60 * 60))
        self.assertEqual("59m:30s", elapsed_end(time.time() - 60 * 60 + 30))
        self.assertEqual("30m:00s", elapsed_end(time.time() - 30 * 60))
        self.assertEqual("02h:00m:00s", elapsed_end(time.time() - 2 * 60 * 60))

    def test_parse_days(self):
        self.assertEqual(
            parse_days("2018/1/1", "2018/1/7-9"),
            [
                (2018, 1, 1),
                (2018, 1, 7),
                (2018, 1, 8),
                (2018, 1, 9),
            ],
        )

        self.assertEqual(
            parse_days("2019/9-10/2-4"),
            [
                (2019, 9, 2),
                (2019, 9, 3),
                (2019, 9, 4),
                (2019, 10, 2),
                (2019, 10, 3),
                (2019, 10, 4),
            ],
        )
        self.assertEqual(
            parse_days("2019,2020/1/1-3"),
            [
                (2019, 1, 1),
                (2019, 1, 2),
                (2019, 1, 3),
                (2020, 1, 1),
                (2020, 1, 2),
                (2020, 1, 3),
            ],
        )

        self.assertEqual(
            parse_days("2019/11-15/30-35"),
            [
                (2019, 11, 30),
                (2019, 12, 30),
                (2019, 12, 31),
            ],
        )

        # non leap year
        self.assertEqual(
            parse_days("2019/2/28-31"),
            [
                (2019, 2, 28),
            ],
        )

        # leap year
        self.assertEqual(
            parse_days("2020/2/28-31"),
            [
                (2020, 2, 28),
                (2020, 2, 29),
            ],
        )
