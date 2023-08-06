class MaxIterationsReached(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Max number of iterations reached.")
