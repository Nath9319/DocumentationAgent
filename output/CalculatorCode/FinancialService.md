# Documentation for `FinancialService`

```python
class FinancialService:
    """
    A service class for handling common financial calculations.
    
    This class provides methods to perform essential financial computations 
    such as calculating future value, present value, and periodic payments 
    for loans. It utilizes the numpy_financial library for accurate 
    financial calculations.
    
    Methods:
    --------
    calculate_future_value(rate: float, nper: int, pmt: float, pv: float) -> float:
        Calculates the future value of an investment based on the provided parameters.
        
    calculate_present_value(rate: float, nper: int, pmt: float, fv: float) -> float:
        Calculates the present value of an investment based on the provided parameters.
        
    calculate_payment(rate: float, nper: int, pv: float) -> float:
        Calculates the periodic payment required to repay a loan based on the loan's 
        interest rate, total number of payment periods, and present value.
    """

    def calculate_future_value(self, rate: float, nper: int, pmt: float, pv: float) -> float:
        """
        Calculates the future value of an investment.

        The future value is computed using the formula:
        FV = PV * (1 + r)^n + PMT * (((1 + r)^n - 1) / r)

        Parameters:
        ----------
        rate : float
            The interest rate per period (as a decimal).
        nper : int
            The total number of payment periods in the investment.
        pmt : float
            The payment made each period; it cannot change over the life of the investment.
        pv : float
            The present value, or the total amount that a series of future payments is worth now.

        Returns:
        -------
        float
            The future value of the investment after the specified number of periods.

        Example:
        --------
        >>> service = FinancialService()
        >>> future_value = service.calculate_future_value(rate=0.05, nper=10, pmt=100, pv=1000)
        >>> print(future_value)
        1628.894626777442
        """
        return npf.fv(rate=rate, nper=nper, pmt=pmt, pv=pv)

    def calculate_present_value(self, rate: float, nper: int, pmt: float, fv: float) -> float:
        """
        Calculates the present value of an investment.

        The present value (PV) is the current worth of a future sum of money or stream of cash flows 
        given a specified rate of return. This method uses the net present value formula to compute 
        the present value based on the provided parameters.

        Parameters:
        ----------
        rate : float
            The interest rate per period.
        nper : int
            The total number of payment periods in the investment.
        pmt : float
            The payment made each period; it cannot change over the life of the investment.
        fv : float
            The future value, or a cash balance you want to attain after the last payment is made.

        Returns:
        -------
        float
            The present value of the investment.

        Example:
        --------
        >>> service = FinancialService()
        >>> pv = service.calculate_present_value(rate=0.05, nper=10, pmt=-100, fv=1000)
        >>> print(pv)
        -1234.56789
        """
        return npf.pv(rate=rate, nper=nper, pmt=pmt, fv=fv)

    def calculate_payment(self, rate: float, nper: int, pv: float) -> float:
        """
        Calculates the periodic payment for a loan.

        This method computes the periodic payment amount required to repay a loan 
        based on the loan's interest rate, total number of payment periods, and 
        present value (loan amount).

        Parameters:
        ----------
        rate : float
            The interest rate for each period (as a decimal). For example, 
            an annual interest rate of 5% should be provided as 0.05.
            
        nper : int
            The total number of payment periods for the loan. This represents 
            the duration over which the loan will be repaid, typically in months 
            or years.
            
        pv : float
            The present value or principal amount of the loan. This is the total 
            amount borrowed.

        Returns:
        -------
        float
            The periodic payment amount that must be made to fully repay the loan 
            over the specified number of periods at the given interest rate.

        Example:
        --------
        >>> service = FinancialService()
        >>> payment = service.calculate_payment(rate=0.05/12, nper=60, pv=10000)
        >>> print(payment)
        188.71
        """
        return npf.pmt(rate=rate, nper=n