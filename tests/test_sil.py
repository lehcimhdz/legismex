from legismex.sil.models import Legislador

def test_imports():
    from legismex.sil import SILClient
    from legismex.sil import SILParser
    from legismex.sil import Legislador, IniciativaResumen

    assert SILClient
    assert SILParser
    assert Legislador
    assert IniciativaResumen
