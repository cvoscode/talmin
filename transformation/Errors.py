class DependencyError(Exception):
    def __init__(self, message, dependency_name):
        self.message = message
        self.dependency_name = dependency_name
        super().__init__(message)