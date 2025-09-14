import matplotlib.pyplot as plt

# Actual test angles from -90° to +90° in steps of 10
actual_angles = list(range(90, -91, -10))  # [90, 80, 70, ..., -80, -90]

# Replace this with your predicted values
predicted_angles = [90, 82, 71, 60, 48, 37, 28, 23, 8, 0, -7, -19, -29, -40, -54, -63, -67, -79, -87]
# Compute absolute errors
errors = [abs(a - p) for a, p in zip(actual_angles, predicted_angles)]

# Print results as a table
print("Angle | Predicted | Error")
print("---------------------------")
for a, p, e in zip(actual_angles, predicted_angles, errors):
    print(f"{a:>5} | {p:>9} | {e:>5}")

# Plot error vs angle
plt.figure(figsize=(10, 4))
plt.plot(actual_angles, errors, marker='o', linestyle='-')
plt.title("Sound Source Localization Error")
plt.xlabel("Actual Angle (°)")
plt.ylabel("Localization Error (°)")
plt.grid(True)
plt.show()

# Print average error
avg_error = sum(errors) / len(errors)
print(f"\nAverage Error: {avg_error:.2f}°")
