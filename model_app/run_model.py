import pickle
from co2_predictor_module import CO2Predictor

# Load the model
with open("co2_predictor.pkl", "rb") as f:
    predictor = pickle.load(f)

# Predict example
power, co2 = predictor.predict_co2(cpu=50, mem=30, processes=20, disk=10)
print(f"Power: {power:.2f} W, CO₂: {co2:.2f} g/h")

# Optimize usage
result = predictor.optimize_usage(25, 30, 20, 10, target_co2=15)
print("Optimization Result:",result)