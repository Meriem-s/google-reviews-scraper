class InvalidReviewNumber(Exception):
    "Raised when there is a discrepancy between the expected number of reviews and the found total after parsing"

    def __init__(self):
        super().__init__("Reviews number discrepancy found")
