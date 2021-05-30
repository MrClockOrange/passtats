import unittest
import gpx_util as g

class MyTestCase(unittest.TestCase):
    def test_parse_komoot(self):
        dists, alts, delta_dist, delta_alt = g.parse_gpx('../gpx_files/2021-05-30_379583043_Bouchaux.gpx')
        print(dists[-1])
        self.assertAlmostEquals(3359.362165496456, dists[-1])

    def test_parse_other(self):
        dists, alts, delta_dist, delta_alt = g.parse_gpx('../gpx_files/15.gpx')
        print(dists[-1])
        self.assertAlmostEquals(174092.71480061114, dists[-1])




if __name__ == '__main__':
    unittest.main()
