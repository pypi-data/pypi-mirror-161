from hapne.backend.DemographicHistory import DemographicHistory
import numpy as np


class DemographicHistory2StatsModelAdapter(DemographicHistory):
    """
    Reformat the output of DemographicHistory so that it becomes a (n, 1) array default was (n,)
    """
    @staticmethod
    def shape_output(output):
        """
        :param output: property of the parent class
        :return: property in the correct format
        """
        return np.reshape(output, (-1, 1))

    @DemographicHistory.n.getter
    def n(self):
        return self.shape_output(super().n)

    @DemographicHistory.coal_rate.getter
    def coal_rate(self):
        return self.shape_output(super().coal_rate)

    @DemographicHistory.time.getter
    def time(self):
        return self.shape_output(super().time)

    @DemographicHistory.acc_coal_rate.getter
    def acc_coal_rate(self):
        return self.shape_output(super().acc_coal_rate)

    @DemographicHistory.dt.getter
    def dt(self):
        return self.shape_output(super().dt)
