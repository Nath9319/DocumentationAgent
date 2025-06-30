# Documentation for `FinancialService.calculate_payment`

```python
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
    return npf.pmt(rate=rate, nper=nper, pv=pv)
``` 

### Documentation Overview:
- **Purpose:** The docstring provides a clear description of what the method does, including its purpose and how it fits into the broader context of loan calculations.
- **Parameters:** Each parameter is described with its type, purpose, and any necessary details (e.g., how to format the interest rate).
- **Returns:** The return value is clearly defined, indicating what the user can expect from the method.
- **Example:** An example usage is included to illustrate how to call the method and what kind of output to expect.