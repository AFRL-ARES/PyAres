import numpy as np
from skopt import gp_minimize
from skopt.space import Real
from skopt.optimizer import Optimizer
from skopt.learning import GaussianProcessRegressor
from PyAres import AresPlannerService
from PyAres import PlanResponse
from PyAres import PlanRequest

if __name__ == "__main__":
    


# 1. Define the search space and the objective function
dimensions = [Real(-2.0, 2.0, name='x'), Real(-2.0, 2.0, name='y')]

def objective_function(params):
    x, y = params
    return (x**2 + y - 11)**2 + (x + y**2 - 7)**2

# 2. Initialize the optimizer
# We use the Optimizer class directly to get the ask/tell functionality.
# We also specify the surrogate model (GP) and the acquisition function (LCB for exploration).
# The acq_func_kwargs allows you to set the kappa value for LCB.
optimizer = Optimizer(
    dimensions=dimensions,
    base_estimator='GP',
    acq_func='LCB',
    acq_func_kwargs={'kappa': 3.0} # A higher kappa for more exploration
)

# 3. Manually run the optimization loop
n_initial_points = 5
n_total_steps = 100

# Initial random samples (optional, but recommended)
for i in range(n_initial_points):
    next_point = optimizer.ask() # Asks for a random point initially
    result = objective_function(next_point)
    optimizer.tell(next_point, result)
    print(f"Step {i+1}: Evaluated at {next_point}, result = {result}")

# Iterative Bayesian optimization steps
for i in range(n_total_steps - n_initial_points):
    # Ask for the next best point based on the current model
    next_point = optimizer.ask()
    
    # Evaluate the point (this is your expensive black-box call)
    result = objective_function(next_point)
    
    # Tell the optimizer the result
    optimizer.tell(next_point, result)
    
    print(f"Step {n_initial_points + i + 1}: Evaluated at {next_point}, result = {result}")

# 4. Get the best result after all steps
print("\nOptimization complete.")
best_x = optimizer.Xi[np.argmin(optimizer.yi)]
best_y = np.min(optimizer.yi)
print(f"Best solution found: {best_x}")
print(f"Best value found: {best_y}")
