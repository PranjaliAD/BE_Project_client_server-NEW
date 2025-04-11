import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle

class CO2Predictor:
    def _init_(self, df, grid_intensity=529.1):
        self.grid_intensity = grid_intensity
        self.cpu_power_data = df.groupby('cpu_usage')['total_power'].mean()
        self.power_model = CubicSpline(
            self.cpu_power_data.index,
            self.cpu_power_data.values,
            extrapolate=False
        )

        # Feature engineering
        features = pd.DataFrame({
            'cpu_power': df['cpu_usage'].apply(
                lambda x: self.power_model(x) if x in self.cpu_power_data.index else 8 + (x**1.35)*0.4),
            'memory_impact': df['memory_usage'] * 0.08,
            'process_impact': df['num_processes'] * 0.05,
            'disk_impact': df['disk_usage'] * 0.01
        })

        X = features.values
        y = df['total_power'].values

        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestRegressor(n_estimators=200, min_samples_leaf=5)
        self.model.fit(X_train, y_train)

    def predict_co2(self, cpu, mem, processes, disk):
        if cpu in self.cpu_power_data.index:
            base_power = self.power_model(cpu)
        else:
            base_power = 8 + (cpu**1.35) * 0.4
        features = np.array([[base_power, mem * 0.08, processes * 0.05, disk * 0.01]])
        power = self.model.predict(features)[0]
        co2 = (power / 1000) * self.grid_intensity
        return power, co2

    def optimize_usage(self, current_cpu, current_mem, current_proc, current_disk, target_co2):
        cpu_range = np.linspace(0, min(current_cpu * 2, 100), 50)
        feasible_cpu = []

        for c in cpu_range:
            _, co2 = self.predict_co2(c, current_mem, current_proc, current_disk)
            if co2 <= target_co2:
                feasible_cpu.append(c)

        if not feasible_cpu:
            min_co2 = self.predict_co2(0, current_mem, current_proc, current_disk)[1]
            return {
                "reachable": False,
                "min_co2": min_co2
            }

        optimal_cpu = max(feasible_cpu)
        current_co2 = self.predict_co2(current_cpu, current_mem, current_proc, current_disk)[1]
        new_co2 = self.predict_co2(optimal_cpu, current_mem, current_proc, current_disk)[1]

        mem_reduction = max(current_mem * 0.7, 5)
        proc_reduction = max(current_proc // 2, 1)
        optimized_co2 = self.predict_co2(optimal_cpu, mem_reduction, proc_reduction, current_disk)[1]

        return {
            "reachable": True,
            "current_co2": current_co2,
            "optimal_cpu": optimal_cpu,
            "new_co2": new_co2,
            "co2_reduction": ((current_co2 - new_co2) / current_co2) * 100,
            "optimized_co2": optimized_co2,
            "total_reduction": ((current_co2 - optimized_co2) / current_co2) * 100,
            "mem_reduction": mem_reduction,
            "proc_reduction": proc_reduction
        }