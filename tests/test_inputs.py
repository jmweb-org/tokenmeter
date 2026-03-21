from __future__ import annotations

from tokenmeter.inputs import read_inputs


def test_read_single_file(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("hello world")
    assert read_inputs([f]) == [(str(f), "hello world")]


def test_read_stdin_marker():
    assert read_inputs(["-"], stdin_text="piped text") == [("<stdin>", "piped text")]


def test_read_directory_expands_text_files(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.md").write_text("b")
    (tmp_path / "skip.bin").write_text("nope")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.prompt").write_text("c")

    results = read_inputs([tmp_path])
    names = [name for name, _ in results]
    assert any(n.endswith("a.txt") for n in names)
    assert any(n.endswith("b.md") for n in names)
    assert any(n.endswith("c.prompt") for n in names)
    assert not any(n.endswith("skip.bin") for n in names)


def test_directory_results_are_sorted(tmp_path):
    for name in ["z.txt", "a.txt", "m.txt"]:
        (tmp_path / name).write_text(name)
    names = [n for n, _ in read_inputs([tmp_path])]
    assert names == sorted(names)
