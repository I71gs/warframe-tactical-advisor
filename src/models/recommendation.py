class Recommendation:

    def __init__(
        self,
        action,
        reason,
        power_gain,
        account_progress,
        time_efficiency
    ):

        self.action = action
        self.reason = reason

        self.power_gain = power_gain
        self.account_progress = account_progress
        self.time_efficiency = time_efficiency

    def calculate_score(self):

        return (
            self.power_gain * 0.4
            + self.account_progress * 0.4
            + self.time_efficiency * 0.2
        )