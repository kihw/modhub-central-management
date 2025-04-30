class DeviceController:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, device_id=None, config=None):
        if not self._initialized:
            self._initialized = True
            self.device_id = device_id or ""
            self.config = config or {}
            self.connected = False
            self.status = {"connection": "inactive", "error": None}
            
    async def connect(self):
        if self.connected:
            return True
        try:
            self.connected = True
            self.status = {"connection": "active", "error": None}
            return True
        except Exception as e:
            self.connected = False
            self.status = {"connection": "error", "error": str(e)}
            return False
        
    async def disconnect(self):
        if not self.connected:
            return True
        try:
            self.connected = False
            self.status = {"connection": "inactive", "error": None}
            return True
        except Exception as e:
            self.status = {"connection": "error", "error": str(e)}
            return False
        
    async def get_status(self):
        return {
            "device_id": self.device_id,
            "status": "connected" if self.connected else "disconnected",
            **self.status
        }
        
    async def execute_command(self, command: str, parameters: dict = None):
        if not self.connected:
            return False
            
        if not isinstance(command, str) or not command.strip():
            return False
            
        if parameters and not isinstance(parameters, dict):
            return False
            
        try:
            # Command execution logic would go here
            return True
        except Exception as e:
            self.status["error"] = str(e)
            return False
        
    def reset(self):
        try:
            self.connected = False
            self.status = {"connection": "inactive", "error": None}
            self.config = {}
            return True
        except Exception as e:
            self.status["error"] = str(e)
            return False