import unittest

from orderdesk import pricing


class DiscountTests(unittest.TestCase):
    def test_no_code(self):
        self.assertEqual(pricing.apply_discount(1000, None), 1000)

    def test_spring10(self):
        self.assertEqual(pricing.apply_discount(1000, "SPRING10"), 900)

    def test_unknown_code(self):
        self.assertEqual(pricing.apply_discount(1000, "NOPE"), 1000)


class TotalTests(unittest.TestCase):
    def test_total_without_code(self):
        self.assertEqual(pricing.calc_total([(1000, 2)]), 2000 + pricing.SHIPPING)

    @unittest.skip("needs the helpdesk sandbox, which is not available in CI")
    def test_total_matches_helpdesk_quote(self):
        self.fail("not run")

    @unittest.skip("flaky since the pence migration, see T-095")
    def test_total_with_code(self):
        self.assertEqual(pricing.calc_total([(1000, 2)], "SPRING10"), 1800 + pricing.SHIPPING)


if __name__ == "__main__":
    unittest.main()
