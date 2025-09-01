import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from models import HoraryChart, Planet, PlanetPosition, Sign
from horary_engine.engine import EnhancedTraditionalHoraryJudgmentEngine
from taxonomy import Category


def make_chart_from_json():
    """Create a HoraryChart using positions from enhanced-horary-chart-1756708131856.json."""
    # Planetary positions mirrored from the JSON chart
    planets_data = {
        Planet.SUN: (158.91979242667188, -0.0001808935620013507, 1, Sign.VIRGO, 1, 0.9675002592643899),
        Planet.MOON: (258.0476987021077, -5.276668951869315, 4, Sign.SAGITTARIUS, 4, 12.0952993744552),
        Planet.MERCURY: (147.22454413800813, 1.5174603949094156, 1, Sign.LEO, -1, 1.8774146601089163),
        Planet.VENUS: (127.67036889775018, 0.12976744873214563, 12, Sign.LEO, 4, 1.2008693261296217),
        Planet.MARS: (195.97361454606826, 0.24926711834228568, 2, Sign.LIBRA, -2, 0.649422087786682),
        Planet.JUPITER: (107.8889649540042, -0.03227499672376491, 11, Sign.CANCER, 5, 0.17943345590025755),
        Planet.SATURN: (0.016986152664401517, -2.4791355765508176, 8, Sign.ARIES, -8, -0.06935779541321868),
    }
    planets = {
        planet: PlanetPosition(
            planet=planet,
            longitude=lon,
            latitude=lat,
            house=house,
            sign=sign,
            dignity_score=dignity,
            speed=speed,
        )
        for planet, (lon, lat, house, sign, dignity, speed) in planets_data.items()
    }

    return HoraryChart(
        date_time=datetime(2025, 9, 1, 5, 14),
        date_time_utc=datetime(2025, 9, 1, 2, 14),
        timezone_info="Asia/Jerusalem",
        location=(30.8124247, 34.8594762),
        location_name="test",
        planets=planets,
        aspects=[],
        houses=[0.0] * 12,
        house_rulers={1: Planet.SUN, 5: Planet.JUPITER},
        ascendant=0.0,
        midheaven=0.0,
        solar_analyses={},
    )


def test_prohibition_overrides_translation():
    chart = make_chart_from_json()
    engine = EnhancedTraditionalHoraryJudgmentEngine()

    # Simulate a prohibition occurring before any translation can complete
    def fake_prohibition(chart, q, qs, days):
        return {
            "prohibited": True,
            "type": "abscission",
            "reason": "Mars cuts off light",
            "prohibitor": Planet.MARS,
            "significator": qs,
        }

    engine._check_future_prohibitions = fake_prohibition  # type: ignore

    translation_called = {"called": False}

    def fake_translation(chart, q, qs):
        translation_called["called"] = True
        return {
            "found": True,
            "translator": Planet.MOON,
            "sequence": "Moon carries light",
            "favorable": True,
            "confidence": 60,
            "timing_days": 2,
        }

    engine._check_enhanced_translation_of_light = fake_translation  # type: ignore

    question_analysis = {"question_type": Category.GAMBLING, "significators": {}}

    result = engine._apply_enhanced_judgment(
        chart,
        question_analysis,
        window_days=30,
        question_text="will I win the lottery?",
    )

    assert result["traditional_factors"]["perfection_type"] == "abscission"
    # Ensure translation path was skipped due to prohibition
    assert translation_called["called"] is False
