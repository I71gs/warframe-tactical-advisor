from __future__ import annotations
import pytest
from src.core.resource_engine import ResourceEngine
from src.core.resource_forecast_engine import ResourceForecastEngine

def test_resource_forecast_zero_deficit(tmp_path) -> None:
    re = ResourceEngine(state_path=tmp_path / "res.json")
    re.save_owned_resources({"Endo": 10000})
    forecaster = ResourceForecastEngine(resource_engine=re)
    forecast = forecaster.calculate_forecast({"Endo": 5000})
    assert forecast["total_hours"] == 0.0

def test_resource_forecast_endo(tmp_path) -> None:
    re = ResourceEngine(state_path=tmp_path / "res.json")
    re.save_owned_resources({"Endo": 0})
    forecaster = ResourceForecastEngine(resource_engine=re)
    forecast = forecaster.calculate_forecast({"Endo": 15000})
    assert forecast["total_hours"] == 1.0

def test_resource_forecast_credits(tmp_path) -> None:
    re = ResourceEngine(state_path=tmp_path / "res.json")
    re.save_owned_resources({"Credits": 0})
    forecaster = ResourceForecastEngine(resource_engine=re)
    forecast = forecaster.calculate_forecast({"Credits": 2500000})
    assert forecast["total_hours"] == 1.0

def test_resource_forecast_kuva(tmp_path) -> None:
    re = ResourceEngine(state_path=tmp_path / "res.json")
    re.save_owned_resources({"Kuva": 0})
    forecaster = ResourceForecastEngine(resource_engine=re)
    forecast = forecaster.calculate_forecast({"Kuva": 30000})
    assert forecast["total_hours"] == 1.0
