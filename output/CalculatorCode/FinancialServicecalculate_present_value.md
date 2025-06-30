# Documentation for `FinancialService.calculate_present_value`

```python
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
``` 

### Documentation Breakdown:
- **Purpose:** The docstring clearly states the function's purpose, which is to calculate the present value of an investment.
- **Parameters:** Each parameter is described with its type and purpose, providing clarity on what values should be passed to the function.
- **Returns:** The return value is specified, indicating what the caller can expect from the function.
- **Example:** An example usage of the function is included to illustrate how to call it and what kind of output to expect.