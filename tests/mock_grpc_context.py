class MockGrpcContext:
  def __init__(self):
      self._code = None
      self._details = ""

  def set_code(self, code):
      self._code = code

  def set_details(self, details):
      self._details = details

  def abort(self, code, details):
      self._code = code
      self._details = details
      raise Exception(f"gRPC Abort: {code} - {details}")