from django.test import TestCase

from core.utils import haversine_m, ip_in_ranges


class IpInRangesTests(TestCase):
    def test_ipv4_inside_range(self):
        self.assertTrue(ip_in_ranges('192.168.1.10', ['192.168.0.0/16']))

    def test_ipv4_outside_range(self):
        self.assertFalse(ip_in_ranges('8.8.8.8', ['192.168.0.0/16']))

    def test_multiple_ranges(self):
        self.assertTrue(ip_in_ranges('10.1.2.3', ['192.168.0.0/16', '10.0.0.0/8']))

    def test_localhost(self):
        self.assertTrue(ip_in_ranges('127.0.0.1', ['127.0.0.0/8']))

    def test_ipv6_loopback(self):
        self.assertTrue(ip_in_ranges('::1', ['::1/128']))

    def test_empty_ip(self):
        self.assertFalse(ip_in_ranges('', ['127.0.0.0/8']))

    def test_invalid_ip(self):
        self.assertFalse(ip_in_ranges('not-an-ip', ['127.0.0.0/8']))

    def test_invalid_cidr_ignored(self):
        # CIDR inválido é ignorado, válido ainda testado
        self.assertTrue(ip_in_ranges('10.0.0.1', ['bogus', '10.0.0.0/8']))


class HaversineTests(TestCase):
    def test_same_point(self):
        self.assertAlmostEqual(haversine_m(0, 0, 0, 0), 0)

    def test_1_degree_latitude_about_111km(self):
        # 1 grau de latitude ≈ 111 km
        d = haversine_m(0, 0, 1, 0)
        self.assertAlmostEqual(d, 111195, delta=100)

    def test_short_distance_meters(self):
        # Dois pontos a ~50m de distância (lat diff ~0.00045 ≈ 50m)
        d = haversine_m(-18.123, -45.456, -18.123 + 0.00045, -45.456)
        self.assertAlmostEqual(d, 50, delta=3)
