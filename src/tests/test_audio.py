import os
import wave
import subprocess
from pathlib import Path

import pytest

from package.audio import (
    list_audio_files,
    get_audio_duration,
    taglia_audio,
    valida_timestamp,
    timestamp_in_secondi,
)


# --------------------------------------------------------------------------- #
# Helper per simulare ffprobe                                                 #
# --------------------------------------------------------------------------- #
class DummyProc:
    def __init__(self, stdout):
        self.stdout = stdout


# --------------------------------------------------------------------------- #
# list_audio_files                                                            #
# --------------------------------------------------------------------------- #
def test_list_audio_files(tmp_path):
    (tmp_path / "a.mp3").write_bytes(b"")
    (tmp_path / "b.WAV").write_bytes(b"")
    (tmp_path / "c.txt").write_text("hello")
    (tmp_path / "d.mkv").write_bytes(b"")

    files = list_audio_files(str(tmp_path))
    assert set(files) == {"a.mp3", "b.WAV"}


# --------------------------------------------------------------------------- #
# get_audio_duration                                                          #
# --------------------------------------------------------------------------- #
def test_get_audio_duration_wav(tmp_path):
    tone = tmp_path / "tone.wav"
    with wave.open(str(tone), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes(b"\x00\x00" * 8000)  # 1 secondo

    assert get_audio_duration(str(tone)).startswith("0:00:01")


def test_get_audio_duration_ffprobe_success(tmp_path, monkeypatch):
    mp3 = tmp_path / "t.mp3"
    mp3.write_bytes(b"")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: DummyProc(stdout="2.7\n"))
    assert get_audio_duration(str(mp3)) == "0:00:03"


def test_get_audio_duration_ffprobe_error(tmp_path, monkeypatch):
    mp4 = tmp_path / "u.mp4"
    mp4.write_bytes(b"")

    def boom(*a, **k):
        raise RuntimeError("ffprobe failed")

    monkeypatch.setattr(subprocess, "run", boom)
    assert get_audio_duration(str(mp4)) == "N/A"


# --------------------------------------------------------------------------- #
# valida_timestamp / timestamp_in_secondi                                     #
# --------------------------------------------------------------------------- #
def test_valida_timestamp_mm_ss():
    assert valida_timestamp("3:5") == "00:03:05"
    assert valida_timestamp(" 10:2 ") == "00:10:02"


def test_valida_timestamp_hh_mm_ss():
    assert valida_timestamp("1:2:3") == "01:02:03"
    assert valida_timestamp("12:34:56") == "12:34:56"


@pytest.mark.parametrize("bad", ["abc", "1:2:3:4", "12:ab", "", ":::"])
def test_valida_timestamp_invalid(bad):
    assert valida_timestamp(bad) is None


def test_timestamp_in_secondi_basic():
    assert timestamp_in_secondi("00:00:05") == 5
    assert timestamp_in_secondi("01:00:00") == 3600
    assert timestamp_in_secondi("02:03:04") == 2 * 3600 + 3 * 60 + 4


# --------------------------------------------------------------------------- #
# taglia_audio                                                                #
# --------------------------------------------------------------------------- #
def test_taglia_audio_invokes_ffmpeg_and_returns_path(tmp_path, monkeypatch):
    """Passiamo esplicitamente output_file e verifichiamo la chiamata."""
    inp = tmp_path / "in.wav"
    out = tmp_path / "out.wav"
    inp.write_bytes(b"")

    def fake_run(cmd, check, stdout, stderr):
        assert cmd[0] == "ffmpeg"
        assert cmd[-1] == str(out)
        open(cmd[-1], "wb").close()

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert taglia_audio(str(inp), "00:00:00", "00:00:01", str(out)) == str(out)
    assert out.exists()


def test_taglia_audio_default_output_name(tmp_path, monkeypatch):
    """
    Se non passo output_file deve creare <stem>_clip.wav
    nella stessa cartella dell'input.
    """
    inp = tmp_path / "video.mp4"
    inp.write_bytes(b"")

    # intercettiamo la chiamata ffmpeg e creiamo il file dummy
    def fake_run(cmd, check, stdout, stderr):
        # ultimo argomento è il path auto-generato
        open(cmd[-1], "wb").close()

    monkeypatch.setattr(subprocess, "run", fake_run)

    out_path = taglia_audio(str(inp), "00:00:05", "00:00:10", output_file=None)
    assert out_path == str(tmp_path / "video_clip.wav")
    assert Path(out_path).exists()
