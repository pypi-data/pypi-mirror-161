class ObservableFunctionNotFoundError(ValueError):
    def __init__(self, not_found_function_name):
        # Call the base class constructor with the parameters it needs
        super().__init__(f"Observable function with name {not_found_function_name} not found.")
        self.errors = f"Observable function with name {not_found_function_name} not found."
