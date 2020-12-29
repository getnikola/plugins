from pytest import fixture


@fixture
def tmp_site_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'pages').mkdir()
    return tmp_path
