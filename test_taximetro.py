import pytest

from taximetro import importe_tramo

RATES = {
    "tarifa_parado": 0.02,
    "tarifa_movimiento": 0.05,
}


def test_stopped_rate():
    assert importe_tramo(10, "parado", RATES) == pytest.approx(0.20)


def test_moving_rate():
    assert importe_tramo(10, "movimiento", RATES) == pytest.approx(0.50)


def test_negative_seconds_raise_error():
    with pytest.raises(ValueError):
        importe_tramo(-1, "parado", RATES)


def test_mixed_ride_total():
    fare = importe_tramo(10, "parado", RATES)
    fare += importe_tramo(10, "movimiento", RATES)
    assert fare == pytest.approx(0.70)