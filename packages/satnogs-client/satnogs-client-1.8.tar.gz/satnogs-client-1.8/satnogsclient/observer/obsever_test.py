import unittest

from satnogsclient.observer.observer import rx_device_for_frequency


class RXDeviceForFrequency(unittest.TestCase):

    def test_single_device(self):
        device = rx_device_for_frequency('device1', 100 * 10**6)
        self.assertEqual(device, 'device1')

    def test_invalid_value(self):
        self.assertRaises(ValueError, rx_device_for_frequency, 'missing colon', 1)
        self.assertRaises(ValueError, rx_device_for_frequency,
                          'invalid_range:device1 100-200:device2', 1)

    def test_no_device_for_freq(self):
        self.assertRaises(LookupError, rx_device_for_frequency, '100-200:device1 200-300:device2',
                          1000)

    def test_chooses_correct_device(self):
        device = rx_device_for_frequency('100-200:device1 200-300:device2 300-400:d3',
                                         250.0 * 10**6)
        self.assertEqual(device, 'device2')

    def test_chooses_first_device(self):
        device = rx_device_for_frequency('100-200:device1 100-200:device2', 100 * 10**6)
        self.assertEqual(device, 'device1')
