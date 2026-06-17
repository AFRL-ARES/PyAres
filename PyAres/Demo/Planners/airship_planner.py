from PyAres import AresPlannerService, PlanRequest, PlanResponse, AresDataType
import random
import time
from enum import Enum

class Planners(Enum):
  RANDOM_PLANNER = 1
  TRADITIONAL_PLANNER = 2
  SEARCH_AND_DESTROY_PLANNER = 3

def coord_to_tuple(coord: str):
  """Converts 'B3' to (1, 2)."""
  return (ord(coord[0].upper()) - ord('A'), int(coord[1:]) - 1)

def tuple_to_coord(tup: tuple):
  """Converts (1, 2) to 'B3'."""
  return f"{chr(ord('A') + tup[0])}{tup[1] + 1}"

def generate_all_coords(board_size=10):
  """Generates all coordinates from 'A1' to 'J10'."""
  return [tuple_to_coord((r, c)) for r in range(board_size) for c in range(board_size)]

def convert_param_history(param_history: list):
  converted_history = []
  for value in param_history:
    letter = value.planned_value[0]
    converted_value = ord(letter) + 1 - ord('A')
    converted_history.append((converted_value, int(value.planned_value[1:])))
  return converted_history

def get_random_shot(param_history: list):
  """ Chooses a random, un-shot-at coordinate. """
  converted_param_history = convert_param_history(param_history)
  all_possible_shots = [(c, r) for r in range(1,11) for c in range(1, 11)]
  available_shots = list(set(all_possible_shots) - set(converted_param_history))
  print(f"{len(available_shots)}/{len(all_possible_shots)}")

  if not available_shots:
    return None
  
  return random.choice(available_shots)

def get_traditional_search_shot(param_history: list):
  """ Uses an extremely basic traditional search algorithm, moving across the board """
  shot_number = len(param_history)
  all_possible_shots = [(c, r) for r in range(1,11) for c in range(1, 11)]
  return all_possible_shots[shot_number]

def get_search_and_destroy_shot(request: PlanRequest):
    """A 'Hunt/Target' planner for Airship."""
    param = request.parameters[0]
    shot_history = [p.planned_value for p in param.param_history]
    shot_results = request.analysis_results # 0.0=Miss, 1.0=Hit, 2.0=Sunk
    active_hits = []

    # --- Identify All Active Hits ---
    for i in range(len(shot_history)):
      coord = shot_history[i]
      result = shot_results[i]

      is_sunk = False
      for j in range(i, len(shot_history)):
        if shot_results[j] == 2.0 and shot_history[j] == coord:
            is_sunk = True
            active_hits = []
            break
          
        if result == 1.0 and not is_sunk:
          active_hits.append(coord)

    # Get Unique active hits and sort them for consistency
    active_hits = sorted(list(set(active_hits)))
    next_shot = None

    # --- TARGET MODE ---
    if active_hits:
      print(f"Target Mode -> Active Hits: {active_hits}")
      
      is_horizontal = False
      is_vertical = False

      if len(active_hits) >= 2:
        #Convert the first two active hits to (row, col) tuples
        r1, c1 = coord_to_tuple(active_hits[0])
        r2, c2 = coord_to_tuple(active_hits[1])

        if r1 == r2:
          is_horizontal = True

        elif c1 == c2:
          is_vertical = True

      potential_targets = []

      if is_horizontal or is_vertical:
        print(f"Orientation Known! {'Horizontal' if is_horizontal else 'Vertical'}")
        hit_tuples = [coord_to_tuple(c) for c in active_hits]

        if is_horizontal:
          min_col = min(c for r, c in hit_tuples)
          max_col = max(c for r, c in hit_tuples)
          row = hit_tuples[0][0]

          potential_targets.append((row, min_col - 1))
          potential_targets.append((row, max_col + 1))

        elif is_vertical:
          min_row = min(r for r, c in hit_tuples)
          max_row = max(r for r, c in hit_tuples)
          col = hit_tuples[0][1]

          potential_targets.append((min_row - 1, col))
          potential_targets.append((max_row + 1, col))

      else:
        active_hit_coord = active_hits[0]
        row, col = coord_to_tuple(active_hit_coord)
        potential_targets.extend([(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)])

      valid_targets = []
      for r, c in potential_targets:
        if 0 <= r < 10 and 0 <= c < 10:
          coord = tuple_to_coord((r,c))
          if coord not in shot_history:
            valid_targets.append(coord)

      if valid_targets:
        next_shot = random.choice(valid_targets)
        print(f"Targeting next logical square: {next_shot}")

    # --- HUNT MODE ---
    if next_shot is None:
      if active_hits:
        print("Target mode exhausted (likely cornered the ship). Returning to Hunt Mode... ")
      else:
        print("Hunt Mode -> Searching for a new target.... ")

      available_shots = list(set(generate_all_coords()) - set(shot_history))
      hunt_candidates = [c for c in available_shots if (coord_to_tuple(c)[0] + coord_to_tuple(c)[1] % 2 == 0)]

      if hunt_candidates:
        next_shot = random.choice(hunt_candidates)

      elif available_shots:
        next_shot = random.choice(available_shots)

      else:
        #Game Over
        next_shot = "A1"

    print(f"Planner requesting fire at: {next_shot}")
    time.sleep(0.25)
    return PlanResponse(parameter_names=[param.name], parameter_values=[next_shot])

def plan(request: PlanRequest) -> PlanResponse:
  #For an "Airship" game we should only ever have one parameter, which is our coordinate
  param = request.parameters[0]
  #Get next shot
  if(param.planner_name == Planners.RANDOM_PLANNER.name):
    shot = get_random_shot(param.param_history)
  elif(param.planner_name == Planners.TRADITIONAL_PLANNER.name):
    shot = get_traditional_search_shot(param.param_history)
  else:
    response = get_search_and_destroy_shot(request)
    return response

  time.sleep(0.25)
  letter = chr(ord('A') - 1 + shot[0])
  shot_string = f"{letter}{shot[1]}"
  print(f"Requesting Fire at {shot_string}")

  response = PlanResponse(parameter_names=[param.name], parameter_values=[shot_string])
  return response

if __name__ == "__main__":
  name = "Airship Planner Service"
  description = "A planner service that provides some basic algorithms for playing Airship."
  planner = AresPlannerService(plan, name, description, "1.0.0", port=8003)

  #Add Supported Types
  planner.add_supported_type(AresDataType.STRING)

  planner.add_planner_option(Planners.RANDOM_PLANNER.name, "Randomly shoots at an un-shot-at coordinate", "1.0.0")
  planner.add_planner_option(Planners.TRADITIONAL_PLANNER.name, "Follows a very basic traditional search pattern", "1.0.0")
  planner.add_planner_option(Planners.SEARCH_AND_DESTROY_PLANNER.name, "Searches for ships with random shots, destroys ships upon locating them.", "1.0.0")

  planner.start()