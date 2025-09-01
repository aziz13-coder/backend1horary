import os
import sys
from datetime import datetime

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from horary_engine.perfection import check_future_prohibitions
from models import Planet, Aspect, PlanetPosition, HoraryChart, Sign


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


def calc_aspect_time(p1, p2, aspect, jd, max_days):
    delta = ((p1.longitude - p2.longitude - aspect.degrees + 180) % 360) - 180
    v = p1.speed - p2.speed
    if v == 0:
        return None
    return -delta / v


def test_translation_abscission_translator_cutoff():
    # Moon will translate Mars to Jupiter but is cut off by Sun first
    mars = make_pos(Planet.MARS, 10.0, 0.5, Sign.ARIES)
    jupiter = make_pos(Planet.JUPITER, 25.0, 0.2, Sign.ARIES)
    moon = make_pos(Planet.MOON, 0.0, 13.0, Sign.ARIES)
    sun = make_pos(Planet.SUN, 15.0, 1.0, Sign.ARIES)

    planets = {p.planet: p for p in [mars, jupiter, moon, sun]}

    chart = HoraryChart(
        date_time=datetime(2024, 1, 1),
        date_time_utc=datetime(2024, 1, 1),
        timezone_info="UTC",
        location=(0.0, 0.0),
        location_name="test",
        planets=planets,
        aspects=[],
        houses=[0.0] * 12,
        house_rulers={},
        ascendant=0.0,
        midheaven=0.0,
    )

    result = check_future_prohibitions(chart, Planet.MARS, Planet.JUPITER, 10.0, calc_aspect_time)

    assert result["type"] == "abscission"
    assert result["abscissor"] == Planet.SUN
    assert result["significator"] == Planet.MOON
    assert "cuts off light carried by Moon" in result["reason"]
