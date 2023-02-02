class NoCidFound(Exception):
    "The search item is not a business to review and has no CID assigned to, please enter the correct venue!"

    def __init__(self):
        super().__init__("Reviews number discrepancy found")
