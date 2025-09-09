import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

# --- 1. Define the simulated, non-linear environment ---
# This is our "unknown" function that the algorithm must learn.
# We'll simulate a sensor's performance based on CO2 level, altitude, and humidity.
# The performance is non-linear, so a simple linear model wouldn't work well.
def true_sensor_performance(X):
    """
    The true, underlying function we are trying to optimize.
    X is a 2D numpy array where X[:, 0] is CO2, X[:, 1] is altitude, and X[:, 2] is humidity.
    """
    co2 = X[:, 0]
    altitude = X[:, 1]
    humidity = X[:, 2]
    # A non-linear function with a peak somewhere in the middle of the 3D space
    return 10 * np.exp(-((co2 - 0.5)**2) / 0.1 - ((altitude - 0.7)**2) / 0.2 - ((humidity - 0.3)**2) / 0.15) + \
           5 * np.sin(2 * np.pi * co2) + \
           3 * np.cos(np.pi * altitude) + \
           2 * np.cos(np.pi * humidity)

# --- 2. Implement the core VOI-based algorithm logic ---
def upper_confidence_bound(X, gp, kappa):
    """
    Calculates the Upper Confidence Bound (UCB) for a set of points X.
    This is our acquisition function, which balances exploration and exploitation.
    - Exploitation: It uses the predicted mean (mu).
    - Exploration: It uses the predicted standard deviation (sigma).
    The 'kappa' parameter controls the balance. Higher kappa = more exploration.
    """
    mu, sigma = gp.predict(X, return_std=True)
    return mu + kappa * sigma

def voi_optimizer_step(gp, X_train, y_train, grid_points, kappa):
    """
    Performs one step of the VOI-based optimization.
    1. Predicts the UCB for all candidate points.
    2. Chooses the point with the highest UCB.
    3. Simulates a new measurement at that point.
    4. Returns the new point and its observed value.
    """
    # Calculate the UCB for all points on the grid
    ucb_scores = upper_confidence_bound(grid_points, gp, kappa)
    
    # Find the index of the point with the highest UCB score
    best_point_idx = np.argmax(ucb_scores)
    
    # The new point to measure is the one with the highest UCB
    next_test_point = grid_points[best_point_idx, :].reshape(1, -1)
    
    # Simulate a measurement from our "true" function
    observed_value = true_sensor_performance(next_test_point)
    
    print(f"  > Selected new test point: CO2={next_test_point[0,0]:.2f}, Altitude={next_test_point[0,1]:.2f}, Humidity={next_test_point[0,2]:.2f}")
    print(f"    Observed sensor performance: {observed_value[0]:.2f}")
    
    return next_test_point, observed_value

# --- 3. Main simulation loop ---
if __name__ == "__main__":
    # Define the search space for CO2 level, altitude, and humidity (normalized from 0 to 1)
    co2_range = np.linspace(0, 1, 50)
    altitude_range = np.linspace(0, 1, 50)
    humidity_range = np.linspace(0, 1, 50)
    grid_co2, grid_alt, grid_humidity = np.meshgrid(co2_range, altitude_range, humidity_range)
    
    # Create a grid of all possible candidate points
    grid_points = np.vstack([grid_co2.ravel(), grid_alt.ravel(), grid_humidity.ravel()]).T

    # Initialize the Gaussian Process model with a suitable kernel
    kernel = C(1.0, (1e-3, 1e3)) * RBF([1.0, 1.0, 1.0], (1e-9, 1e9))
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=50)

    # Start with a few initial random data points
    num_initial_points = 5
    initial_indices = np.random.choice(len(grid_points), num_initial_points, replace=False)
    X_train = grid_points[initial_indices, :]
    y_train = true_sensor_performance(X_train)

    print("Starting optimization with initial random measurements...")
    
    # Use a constant kappa to balance exploration and exploitation
    CONSTANT_KAPPA = 3.0
    # Set a target for the average uncertainty to know when to stop
    UNCERTAINTY_THRESHOLD = 0.5
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # Train the Gaussian Process model on all collected data
        gp.fit(X_train, y_train)

        # Get the predicted standard deviation for all points on the grid
        _, sigma = gp.predict(grid_points, return_std=True)
        average_uncertainty = np.mean(sigma)
        
        print(f"  > Current average model uncertainty: {average_uncertainty:.2f}")

        # Check for the stopping condition
        if average_uncertainty < UNCERTAINTY_THRESHOLD:
            print(f"\nAverage uncertainty ({average_uncertainty:.2f}) is below the threshold ({UNCERTAINTY_THRESHOLD:.2f}). Stopping.")
            break
        
        # Get the next best point based on our VOI criterion (UCB)
        new_point, new_value = voi_optimizer_step(gp, X_train, y_train, grid_points, CONSTANT_KAPPA)
        
        # Add the new data to our training set
        X_train = np.vstack([X_train, new_point])
        y_train = np.vstack([y_train.reshape(-1, 1), new_value.reshape(-1, 1)]).flatten()

    # After the simulation, find the best point we've found
    best_point_found_idx = np.argmax(y_train)
    best_point = X_train[best_point_found_idx, :]
    best_value = y_train[best_point_found_idx]

    print("\n--- Simulation Complete ---")
    print(f"The algorithm terminated after {iteration} iterations because it achieved a 'sufficient' understanding of the space.")
    print(f"The best point observed during exploration was: CO2={best_point[0]:.2f}, Altitude={best_point[1]:.2f}, Humidity={best_point[2]:.2f}")
    print(f"Peak sensor performance observed: {best_value:.2f}")
