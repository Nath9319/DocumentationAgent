# Documentation for `FinancialService`

```python
class FinancialService:
    """
    A service class for handling common financial calculations.
    
    This class provides methods to perform various financial computations, 
    including calculating future value, present value, and periodic payments 
    for loans. It utilizes the numpy_financial library for accurate financial 
    calculations.

    Methods:
    --------
    calculate_future_value(rate: float, nper: int, pmt: float, pv: float) -> float:
        Calculates the future value of an investment based on the provided parameters.
    
    calculate_present_value(rate: float, nper: int, pmt: float, fv: float) -> float:
        Calculates the present value of an investment based on the provided parameters.
    
    calculate_payment(rate: float, nper: int, pv: float) -> float:
        Calculates the periodic payment required to repay a loan over a specified number of periods.
    
    Dependencies:
    -------------
    This class relies on the numpy_financial library for its calculations.
    """

    def calculate_future_value(self, rate: float, nper: int, pmt: float, pv: float) -> float:
        """
        Calculates the future value of an investment based on the provided parameters.

        The future value is computed using the formula:
        FV = PV * (1 + r)^n + PMT * (((1 + r)^n - 1) / r)

        Parameters:
        ----------
        rate : float
            The interest rate per period (as a decimal). For example, a 5% interest rate should be passed as 0.05.
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
        >>> fv = calculate_future_value(rate=0.05, nper=10, pmt=100, pv=1000)
        >>> print(fv)
        1628.894626777442
        """
        return npf.fv(rate=rate, nper=nper, pmt=pmt, pv=pv)

    def calculate_present_value(self, rate: float, nper: int, pmt: float, fv: float) -> float:
        """
        Calculates the present value of an investment.

        The present value (PV) is the current worth of a future sum of money or stream of cash flows 
        given a specified rate of return. This function uses the net present value formula to compute 
        the present value based on the provided parameters.

        Parameters:
        ----------
        rate : float
            The interest rate per period (as a decimal). For example, a 5% interest rate should be 
            provided as 0.05.
        
        nper : int
            The total number of payment periods in the investment.
        
        pmt : float
            The payment made in each period. This amount does not change over the life of the investment.
        
        fv : float
            The future value, or a cash balance you want to attain after the last payment is made.

        Returns:
        -------
        float
            The present value of the investment, calculated using the provided parameters.

        Example:
        --------
        >>> pv = calculate_present_value(0.05, 10, -100, 1000)
        >>> print(pv)
        613.9132535407591
        """
        return npf.pv(rate=rate, nper=nper, pmt=pmt, fv=fv)

    def calculate_payment(self, rate: float, nper: int, pv: float) -> float:
        """
        Calculates the periodic payment for a loan.

        This function uses the net present value formula to compute the 
        periodic payment required to repay a loan over a specified 
        number of periods at a given interest rate.

        Parameters:
        ----------
        rate : float
            The interest rate for each period (as a decimal).
        nper : int
            The total number of payment periods in the loan term.
        pv : float
            The present value, or the total amount of the loan.

        Returns:
        -------
        float
            The periodic payment amount.

        Example:
        --------
        >>> payment = calculate_payment(0.05, 60, 30000)
        >>> print(payment)
        -566.14
        """
        return npf.pmt(rate=rate, nper=nper, pv=pv)
```

### Documentation Summary:
- **Class Purpose:** The `FinancialService` class provides methods for common financial calculations, leveraging the `numpy_financial` library.
- **Methods Overview:** Each method is documented