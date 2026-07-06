import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pytest

from src.features import (
    canonicalize_smiles,
    is_valid_smiles,
    compute_rdkit_descriptors,
    get_morgan_fingerprint,
    compute_all_features,
    get_descriptor_names,
    feature_dimension,
)


class TestSmilesValidation:
    def test_valid_smiles(self):
        assert canonicalize_smiles("CCO") == "CCO"
        assert is_valid_smiles("CCO") is True

    def test_invalid_smiles(self):
        assert canonicalize_smiles("INVALID") is None
        assert canonicalize_smiles("") is None
        assert is_valid_smiles("INVALID") is False

    def test_canonicalization(self):
        result = canonicalize_smiles("c1ccccc1")
        assert result is not None
        assert "c1ccccc1" in result or "C1=CC=CC=C1" in result

    def test_isomeric_smiles(self):
        result = canonicalize_smiles("C[C@H](O)CC")
        assert result is not None


class TestDescriptors:
    def test_compute_descriptors_ethanol(self):
        desc = compute_rdkit_descriptors("CCO")
        assert desc is not None
        assert "MolWt" in desc
        assert "LogP" in desc
        assert "NumHDonors" in desc
        assert "NumHAcceptors" in desc
        assert "TPSA" in desc
        assert desc["MolWt"] > 0
        assert desc["NumHDonors"] >= 1
        assert desc["NumHAcceptors"] >= 1

    def test_descriptors_invalid(self):
        assert compute_rdkit_descriptors("INVALID") is None
        assert compute_rdkit_descriptors("") is None

    def test_get_descriptor_names(self):
        names = get_descriptor_names()
        assert len(names) >= 29
        assert "MolWt" in names
        assert "LogP" in names
        assert "TPSA" in names


class TestMorganFingerprint:
    def test_fingerprint_shape(self):
        fp = get_morgan_fingerprint("CCO")
        assert fp is not None
        assert fp.shape == (2048,)
        assert fp.dtype == np.float32

    def test_fingerprint_invalid(self):
        assert get_morgan_fingerprint("INVALID") is None

    def test_fingerprint_consistency(self):
        fp1 = get_morgan_fingerprint("CCO")
        fp2 = get_morgan_fingerprint("CCO")
        assert fp1 is not None and fp2 is not None
        np.testing.assert_array_equal(fp1, fp2)

    def test_different_molecules(self):
        fp1 = get_morgan_fingerprint("CCO")
        fp2 = get_morgan_fingerprint("CCCO")
        assert fp1 is not None and fp2 is not None
        assert not np.array_equal(fp1, fp2)


class TestCombinedFeatures:
    def test_all_features_shape(self):
        feat = compute_all_features("CCO")
        assert feat is not None
        expected = feature_dimension()
        assert feat.shape == (expected,)
        assert feat.dtype == np.float32

    def test_all_features_invalid(self):
        assert compute_all_features("INVALID") is None

    def test_feature_dimension(self):
        desc_names = get_descriptor_names()
        expected = len(desc_names) + 2048
        assert feature_dimension() == expected


class TestBatchFeatures:
    def test_basic_batch(self):
        from src.features import feature_pipeline

        smiles = ["CCO", "CCCO", "c1ccccc1"]
        X, idx, names = feature_pipeline(smiles, verbose=False)
        assert len(X) == 3
        assert len(idx) == 3
        assert len(names) == feature_dimension()

    def test_batch_with_invalid(self):
        from src.features import feature_pipeline

        smiles = ["CCO", "INVALID", "CCCO"]
        X, idx, names = feature_pipeline(smiles, verbose=False)
        assert len(X) == 2
        assert len(idx) == 2
        assert 1 not in idx  # INVALID should be excluded

    def test_empty_batch(self):
        from src.features import feature_pipeline

        X, idx, names = feature_pipeline([], verbose=False)
        assert len(X) == 0
        assert len(idx) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
