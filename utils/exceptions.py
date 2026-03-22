from utils.lookup import FaultType

class Fault(Exception):
    def __init__(self, fault_code: FaultType, fault_message: str = None):
        super().__init__(None)
        self.fault_code = fault_code
        self.fault_message = fault_message
