import unittest

class TestTest1 (unittest.TestCase):
  def test_test1_1 (self):
    self.assertEquals(1+1, 2)

  def test_shouldfail (self):
    self.assertEquals(0, 1)

if __name__ in ('main', '__main__'):
  unittest.main()
