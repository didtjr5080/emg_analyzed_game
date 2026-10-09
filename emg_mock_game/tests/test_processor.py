import pytest

from emg.processor import EMGProcessor


def test_activation_balance_and_clamping():
    result = EMGProcessor().process(1.5, -0.2)
    assert result.biceps == 1.0
    assert result.triceps == 0.0
    assert result.overall_activation == 0.5
    assert result.balance == 1.0


def test_fatigue_increases_and_recovers():
    processor = EMGProcessor(0.5)
    assert processor.process(0.9, 0.9).fatigue == pytest.approx(0.505)
    assert processor.process(0.1, 0.1).fatigue == pytest.approx(0.502)


def test_fatigue_is_clamped():
    high = EMGProcessor(1).process(1, 1)
    low = EMGProcessor(0).process(0, 0)
    assert high.fatigue == 1.0
    assert low.fatigue == 0.0

