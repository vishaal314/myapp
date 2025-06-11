"""
Energy Constants Configuration

Centralized configuration for sustainability scanner energy calculations
based on industry benchmarks and research data.
"""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class EnergyConstants:
    """Energy consumption constants for sustainability calculations."""
    
    # Base energy consumption factors
    IMPORT_OVERHEAD_WATTS = 0.5  # Watts per unused import
    DEAD_CODE_FACTOR = 0.0001    # kWh per line of dead code annually
    PACKAGE_DUPLICATION_BASE = 2.5  # kWh per duplicate package annually
    
    # ML Model energy factors (kWh per MB annually)
    ML_MODEL_ENERGY_FACTORS = {
        'very_large': 2.5,  # >500MB models
        'large': 1.8,       # 100-500MB models
        'medium': 0.5       # <100MB models
    }
    
    # Carbon conversion factors
    CARBON_KG_PER_KWH = 0.4      # kg CO₂ per kWh (global average)
    DRIVING_KM_PER_KG_CO2 = 2.4  # km driving equivalent per kg CO₂
    COAL_KG_PER_KG_CO2 = 0.49    # kg coal equivalent per kg CO₂
    TREES_PER_KG_CO2 = 0.046     # trees needed to offset 1 kg CO₂
    
    # Cost factors
    ENERGY_COST_USD_PER_KWH = 0.12  # USD per kWh
    
    # Time constants
    DAYS_PER_YEAR = 365
    HOURS_PER_YEAR = 8760
    
    # Scaling factors
    IMPORT_SCALING_FACTOR = 10
    PACKAGE_SCALING_FACTOR = 100
    ML_MODEL_SCALING_FACTOR = 10
    
    # File size limits (bytes)
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
    MAX_PROCESSING_TIME_SECONDS = 300       # 5 minutes
    
    # Optimization potential ranges
    OPTIMIZATION_POTENTIAL_MAX = 75  # Maximum optimization potential percentage
    
    @classmethod
    def get_ml_energy_factor(cls, size_mb: float) -> float:
        """Get energy factor based on ML model size."""
        if size_mb > 500:
            return cls.ML_MODEL_ENERGY_FACTORS['very_large']
        elif size_mb > 100:
            return cls.ML_MODEL_ENERGY_FACTORS['large']
        else:
            return cls.ML_MODEL_ENERGY_FACTORS['medium']
    
    @classmethod
    def calculate_carbon_footprint(cls, energy_kwh: float) -> Dict[str, float]:
        """Calculate comprehensive carbon footprint metrics."""
        carbon_kg = energy_kwh * cls.CARBON_KG_PER_KWH
        
        return {
            'carbon_emissions_kg_annually': carbon_kg,
            'driving_km_equivalent': carbon_kg * cls.DRIVING_KM_PER_KG_CO2,
            'coal_kg_equivalent': carbon_kg / cls.COAL_KG_PER_KG_CO2,
            'trees_equivalent': carbon_kg / cls.TREES_PER_KG_CO2,
            'cost_usd_annually': energy_kwh * cls.ENERGY_COST_USD_PER_KWH
        }
    
    @classmethod
    def calculate_potential_savings(cls, energy_kwh: float, efficiency_factor: float = 0.85) -> Dict[str, float]:
        """Calculate potential savings with given efficiency factor."""
        savings_kwh = energy_kwh * efficiency_factor
        carbon_savings = savings_kwh * cls.CARBON_KG_PER_KWH
        
        return {
            'energy_kwh_annually': savings_kwh,
            'carbon_kg_annually': carbon_savings,
            'cost_usd_annually': savings_kwh * cls.ENERGY_COST_USD_PER_KWH,
            'trees_equivalent': carbon_savings / cls.TREES_PER_KG_CO2
        }


class ValidationConstants:
    """Constants for validation and testing."""
    
    # Industry benchmarks for validation
    GOOGLE_ANNUAL_MWH = 2.6e6     # Google's annual energy consumption
    AWS_ANNUAL_MWH = 7.2e6        # AWS annual energy consumption
    
    # Code efficiency benchmarks
    UNUSED_IMPORT_OVERHEAD_PCT = 0.15    # 15% performance overhead
    DEAD_CODE_COMPILATION_PCT = 0.08     # 8% compilation time increase
    PACKAGE_DUPLICATION_BLOAT_PCT = 0.25 # 25% storage bloat
    
    # Confidence intervals
    ENERGY_CALCULATION_CONFIDENCE = 0.80  # 80% confidence in calculations
    CARBON_FACTOR_UNCERTAINTY = 0.15     # ±15% uncertainty in carbon factors


class ModelTypeConstants:
    """Constants for ML model type optimization potential."""
    
    OPTIMIZATION_POTENTIAL_BY_TYPE = {
        'Keras/TensorFlow': 45,
        'PyTorch': 40,
        'Scikit-learn/Pickle': 30,
        'TensorFlow SavedModel': 50,
        'ONNX': 25,
        'TensorFlow Lite': 15,
        'Unknown': 40
    }
    
    MODEL_EXTENSIONS = {
        '.pkl': 'Scikit-learn/Pickle',
        '.joblib': 'Scikit-learn/Pickle',
        '.h5': 'Keras/TensorFlow',
        '.pb': 'TensorFlow SavedModel',
        '.pth': 'PyTorch',
        '.pt': 'PyTorch',
        '.onnx': 'ONNX',
        '.tflite': 'TensorFlow Lite'
    }