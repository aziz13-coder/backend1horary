import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from models import Planet, Aspect, PlanetPosition, Sign


def make_pos(planet, lon, speed, sign):
    return PlanetPosition(
        planet=planet,
        longitude=lon,
        latitude=0.0,
        house=1,
        sign=sign,
        dignity_score=0,
        speed=speed,
    )


def test_mars_jupiter_square_time_order_independent():
    mars = make_pos(Planet.MARS, 195.97361454606846, 0.649422093300911, Sign.LIBRA)
    jupiter = make_pos(Planet.JUPITER, 107.8889649540042, 0.17943345590025755, Sign.CANCER)

    engine_cls = EnhancedTraditionalHoraryJudgmentEngine

    t_mj = engine_cls._calculate_future_aspect_time(engine_cls, mars, jupiter, Aspect.SQUARE, jd_start=0.0, max_days=30)
    t_jm = engine_cls._calculate_future_aspect_time(engine_cls, jupiter, mars, Aspect.SQUARE, jd_start=0.0, max_days=30)

    assert t_mj is not None
    assert t_jm is not None
    assert pytest.approx(t_mj, rel=1e-2) == 4.08
    assert pytest.approx(t_jm, rel=1e-2) == 4.08
