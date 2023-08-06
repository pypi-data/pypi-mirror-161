from bioreader import readout_platform, readout_type


def test_readout():
    assert readout_type.scRNA_seq == "scRNA-seq"
    assert readout_platform.Chromium__10x_ == "Chromium (10x)"
