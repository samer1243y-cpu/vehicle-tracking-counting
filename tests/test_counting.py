import unittest
from counting import LineCounter

class CrossingTests(unittest.TestCase):
    def test_crosses_finite_segment_once(self):
        c=LineCounter({'A':((0,0),(10,0))})
        self.assertEqual(c.update(1,(5,-2)),[])
        self.assertEqual(c.update(1,(5,2)),['A'])
        self.assertEqual(c.update(1,(5,-2)),[])
        self.assertEqual(c.counts,{'A':1})

    def test_extension_is_not_counted(self):
        c=LineCounter({'A':((0,0),(10,0))})
        c.update(1,(20,-2)); self.assertEqual(c.update(1,(20,2)),[])

    def test_touch_then_cross_and_independent_ids(self):
        c=LineCounter({'A':((0,0),(10,0))})
        c.update(1,(5,-2)); self.assertEqual(c.update(1,(5,0)),[])
        self.assertEqual(c.update(1,(5,2)),['A'])
        c.update(2,(5,2)); self.assertEqual(c.update(2,(5,-2)),['A'])
        self.assertEqual(c.counts['A'],2)

    def test_reject_degenerate_line(self):
        with self.assertRaises(ValueError): LineCounter({'A':((0,0),(0,0))})

if __name__=='__main__': unittest.main()
