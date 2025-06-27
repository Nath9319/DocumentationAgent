import numpy_financial as npf

class FinancialService:
    """
    A service class for handling common financial calculations.
    Uses the numpy_financial library.
    """

    def calculate_future_value(self, rate: float, nper: int, pmt: float, pv: float) -> float:
        """
        Calculates the future value of an investment.
        """
        return npf.fv(rate=rate, nper=nper, pmt=pmt, pv=pv)

    def calculate_present_value(self, rate: float, nper: int, pmt: float, fv: float) -> float:
        """
        Calculates the present value of an investment.
        """
        return npf.pv(rate=rate, nper=nper, pmt=pmt, fv=fv)

    def calculate_payment(self, rate: float, nper: int, pv: float) -> float:
        """
        Calculates the periodic payment for a loan.
        """
        return npf.pmt(rate=rate, nper=nper, pv=pv)

# Instantiate the service
financial_service = FinancialService()
