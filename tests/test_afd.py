import unittest
from afd_core.afd import AFD

class TestAFD(unittest.TestCase):
    def test_simple_accept(self):
        afd = AFD(
            states=["q0","q1"],
            alphabet=["0","1"],
            initial="q0",
            finals=["q1"],
            transitions={
                "q0": {"1":"q1"},
                "q1": {"0":"q1","1":"q1"}
            }
        )
        result = afd.simulate("1")
        self.assertTrue(result.accepted)

if __name__ == "__main__":
    unittest.main()
