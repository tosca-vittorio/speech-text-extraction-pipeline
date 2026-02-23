import pytest
from package.naming import genera_nome_file_output
from package.errors import ConfigError

# ------------------------------------------------------------------ #
# Parametrized: casi nominali                                        #
# ------------------------------------------------------------------ #
@pytest.mark.parametrize(
    "base, mod, mode, tipo, iniz, fine, exp",
    [
        # ── completa ────────────────────────────────────────────────
        ("f",   "medium", "standard",  "completa", None, None,
         "f (med_std)"),
        ("a",   "tiny",   "accurata",  "completa", None, None,
         "a (tny_acc)"),

        # ── parziale ────────────────────────────────────────────────
        # formato:  base (start_end)(mod_mode)
        ("clip", "base",  "standard", "parziale", "00:01:02", "00:03:04",
        "clip (0102_0304) (bse_std)"),
        ("c",    "small", "accurata", "parziale", "00:00:05", "00:00:10",
        "c (0005_0010) (sml_acc)"),
    ],
)
def test_genera_nome(base, mod, mode, tipo, iniz, fine, exp):
    name = genera_nome_file_output(
        base_name=base,
        modello=mod,
        modalita=mode,
        tipo=tipo,
        inizio=iniz,
        fine=fine,
    )
    assert name == exp


# ------------------------------------------------------------------ #
# Errore se mancano timestamp in modalità parziale                   #
# ------------------------------------------------------------------ #
def test_parziale_missing_timestamps_raises():
    with pytest.raises(ConfigError):
        genera_nome_file_output("x", "base", "standard",
                                "parziale", None, None)


# ------------------------------------------------------------------ #
# Fallback quando modello / modalità non mappati                     #
# ------------------------------------------------------------------ #
@pytest.mark.parametrize(
    "mod, mode, exp_suffix",
    [
        ("unknown", "standard", "unknown_std"),
        ("medium",  "xyz",      "med_xyz"),
        ("X",       "Y",        "X_Y"),
    ],
)
def test_fallback_modello_modalita(mod, mode, exp_suffix):
    res = genera_nome_file_output("base", mod, mode, "completa")
    assert res == f"base ({exp_suffix})"
