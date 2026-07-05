#!/usr/bin/env python3
"""
Unit tests for biorecovery-audit scripts.
"""

import pytest
import json
import tempfile
from pathlib import Path
from scripts.collect_recovery_metrics import validate_sleep, validate_hydration, validate_nutrition, validate_fatigue
from scripts.calculate_recovery_score import calculate_recovery_score


class TestCollectMetrics:
    """Tests for metric collection and validation."""
    
    def test_validate_sleep_restful(self):
        """Test sleep quality inference: restful."""
        result = validate_sleep(7.5)
        assert result["hours"] == 7.5
        assert result["quality"] == "restful"
    
    def test_validate_sleep_interrupted(self):
        """Test sleep quality inference: interrupted."""
        result = validate_sleep(6.0)
        assert result["hours"] == 6.0
        assert result["quality"] == "interrupted"
    
    def test_validate_sleep_poor(self):
        """Test sleep quality inference: poor."""
        result = validate_sleep(4.5)
        assert result["hours"] == 4.5
        assert result["quality"] == "poor"
    
    def test_validate_sleep_invalid(self):
        """Test invalid sleep hours."""
        with pytest.raises(ValueError):
            validate_sleep(25)
        
        with pytest.raises(ValueError):
            validate_sleep(-1)
    
    def test_validate_hydration_valid(self):
        """Test valid hydration levels."""
        assert validate_hydration(2.0) == 2.0
        assert validate_hydration(1.5) == 1.5
    
    def test_validate_hydration_invalid(self):
        """Test invalid hydration levels."""
        with pytest.raises(ValueError):
            validate_hydration(25)
        
        with pytest.raises(ValueError):
            validate_hydration(-1)
    
    def test_validate_nutrition_descriptive(self):
        """Test descriptive nutrition validation."""
        from scripts.collect_recovery_metrics import validate_nutrition
        
        result = validate_nutrition(nutrition_status="seguita-bene")
        assert result["status"] == "seguita-bene"
        assert "normalized" in result
    
    def test_validate_nutrition_numeric(self):
        """Test numeric nutrition validation."""
        from scripts.collect_recovery_metrics import validate_nutrition
        
        result = validate_nutrition(nutrition_target=2500, nutrition_consumed=2400)
        assert result["numeric"]["target"] == 2500
        assert result["numeric"]["consumed"] == 2400
        assert result["numeric"]["delta"] == -100
    
    def test_validate_nutrition_mixed(self):
        """Test mixed nutrition validation."""
        from scripts.collect_recovery_metrics import validate_nutrition
        
        result = validate_nutrition(
            nutrition_status="seguita-bene",
            nutrition_target=2500,
            nutrition_consumed=2500
        )
        assert "status" in result
        assert "numeric" in result
    
    def test_validate_fatigue_valid(self):
        """Test valid fatigue levels."""
        assert validate_fatigue(5) == 5
        assert validate_fatigue(1) == 1
        assert validate_fatigue(10) == 10
    
    def test_validate_fatigue_invalid(self):
        """Test invalid fatigue levels."""
        with pytest.raises(ValueError):
            validate_fatigue(0)
        
        with pytest.raises(ValueError):
            validate_fatigue(11)


class TestRecoveryScore:
    """Tests for recovery score calculation."""
    
    def test_recovery_score_excellent(self):
        """Test excellent recovery (restful sleep, high hydration, low fatigue)."""
        metrics = {
            "sleep": {"hours": 8, "quality": "restful"},
            "hydration": 2.5,
            "nutrition_status": "surplus",
            "perceived_fatigue_level": 2,
        }
        result = calculate_recovery_score(metrics)
        assert result["recovery_score"] >= 1.1
        assert result["rpe_ceiling"] == 10
    
    def test_recovery_score_poor(self):
        """Test poor recovery (poor sleep, low hydration, high fatigue)."""
        metrics = {
            "sleep": {"hours": 4, "quality": "poor"},
            "hydration": 1.0,
            "nutrition_status": "deficit",
            "perceived_fatigue_level": 9,
        }
        result = calculate_recovery_score(metrics)
        assert result["recovery_score"] <= 0.75
        assert result["volume_reduction_percent"] > 20
    
    def test_recovery_score_clamped(self):
        """Test that recovery score is clamped to 0.7–1.2 range."""
        metrics = {
            "sleep": {"hours": 8, "quality": "restful"},
            "hydration": 3.0,
            "nutrition_status": "surplus",
            "perceived_fatigue_level": 1,
        }
        result = calculate_recovery_score(metrics)
        assert 0.7 <= result["recovery_score"] <= 1.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
