from PyAres import PlanRequest, PlanningParameter, AresDataType, ParameterHistoryItem
from PyAres.test_tools import PlannerTestClient

if __name__ == "__main__":
  client = PlannerTestClient()

  # 1. Health Checks
  client.check_status()
  client.get_info()

  # 2. Mock Data
  planning_parameters = []
  planning_parameters.append(PlanningParameter("Param One", 0, 100, [ParameterHistoryItem(123, 128)], AresDataType.NUMBER, False, False, "Random Planner"))
  planning_parameters.append(PlanningParameter("Param Two", 0, 500, [ParameterHistoryItem(132, 122)], AresDataType.NUMBER, False, False, "Random Planner"))
  planning_parameters.append(PlanningParameter("Param Three", 0, 500, [ParameterHistoryItem(141, 121)], AresDataType.NUMBER, False, False, "Random Planner"))
  setting_dict = {"Random Setting" : 4000}
  analysis_results = [10, 20, 30]

  # 3. Create and Send the Request
  request = PlanRequest(planning_parameters, setting_dict, analysis_results)
  response = client.run_planning(request)