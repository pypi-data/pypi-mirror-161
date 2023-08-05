import pytest
import os
import time

def test_density():
    from cacab.plot.main import density
    import numpy as np
    a = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, np.nan])
    dens_x, *_ = density(a)
    assert abs(dens_x[0] + 12.90994449) < 0.000001
    assert abs(dens_x[-1] - 20.90994449) < 0.0000001

#
# def get_filepath(filepath):
#     """ Fix path to file if tests are being done in build pipeline based on a filepath that is relative to tests dir """
#     if not os.path.isfile(filepath):
#         filepath = os.path.join("tests", filepath)
#     return filepath
#
#
# # @pytest.mark.integration  # Only mark your tests as "integration" if they require connections/credentials
# def test_model():
#     assert 1 == 1
