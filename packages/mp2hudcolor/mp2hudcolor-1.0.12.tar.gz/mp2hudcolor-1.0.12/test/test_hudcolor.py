from mp2hudcolor import mp2hudcolor_c


def test_hudcolor(tmp_path):
    ntwk_file = str(tmp_path.joinpath("tweak.ntwek"))
    mp2hudcolor_c(ntwk_file, ntwk_file, 1.0, 1.0, 1.0)
