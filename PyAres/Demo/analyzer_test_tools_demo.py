from PyAres.test_tools import AnalyzerTestClient


if __name__ == "__main__":
  client = AnalyzerTestClient()
  
  # 1. Health Checks
  client.check_status()
  client.get_info()

  # 2. Run a Mock Analysis
  # Replace these keys with actual data your analyzer expects
  sample_inputs = {
      "Temperature": 130.5
  }

  client.run_analysis(inputs=sample_inputs)

    