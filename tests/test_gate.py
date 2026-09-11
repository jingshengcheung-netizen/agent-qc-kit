import unittest
from agent_qc_kit.gate import check_text

class GateTests(unittest.TestCase):
    def test_pass_with_url_and_disclaimer(self):
        t = (
            "Frontier releases shift diligence from benchmarks to stoppability.\n"
            "https://openai.com/index/path-to-astra/\n"
            "Not investment advice."
        )
        self.assertEqual(check_text(t), [])

    def test_fail_truncated(self):
        t = "业落地 Frontier 的真卡不是智商\nhttps://example.com"
        rules = {f.rule for f in check_text(t)}
        self.assertIn("truncated_open", rules)

    def test_fail_advice(self):
        t = "This name will 10x, buy now.\nhttps://example.com"
        rules = {f.rule for f in check_text(t)}
        self.assertIn("investment_advice", rules)

    def test_fail_number_no_url(self):
        t = "ARR hit $74.1B last quarter according to vibes."
        rules = {f.rule for f in check_text(t)}
        self.assertIn("number_without_source", rules)

if __name__ == "__main__":
    unittest.main()
