from unittest import TestCase

import pydicom
from dicom_parser.utils.siemens.csa.header import CsaAsciiHeader
from dicom_parser.utils.siemens.private_tags import SIEMENS_PRIVATE_TAGS
from tests.fixtures import TEST_RSFMRI_IMAGE_PATH


class CsaAsciiHeaderTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        dcm = pydicom.dcmread(TEST_RSFMRI_IMAGE_PATH)
        tag = SIEMENS_PRIVATE_TAGS["CSASeriesHeaderInfo"]
        cls.series_header_info = dcm.get(tag).value
        cls.ascii_header = CsaAsciiHeader(cls.series_header_info)

    def test_init_prepares_cached_variables(self):
        fresh_header = CsaAsciiHeader(self.series_header_info)
        self.assertEqual(fresh_header._parsed, {})

    def test_parse_returns_dict(self):
        parsed = self.ascii_header.parse()
        self.assertIsInstance(parsed, dict)

    def test_parse_results_for_nested_dict_value(self):
        parsed = self.ascii_header.parse()
        slice_array_size = 64
        value = parsed["sSliceArray"]["lSize"]
        self.assertEqual(slice_array_size, value)
        k_space_slice_resolution = 1
        value = parsed["sKSpace"]["dSliceResolution"]
        self.assertEqual(k_space_slice_resolution, value)

    def test_parse_results_for_nested_list_value(self):
        parsed = self.ascii_header.parse()
        value = parsed["sCoilSelectMeas"]["aRxCoilSelectData"]
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 2)

    def test_parsed_property(self):
        self.assertIsInstance(self.ascii_header.parsed, dict)
        self.assertIs(self.ascii_header.parsed, self.ascii_header.parsed)

    def test_n_slices_property(self):
        result = self.ascii_header.n_slices
        expected = self.ascii_header.parsed["sSliceArray"]["lSize"]
        self.assertEqual(result, expected)
