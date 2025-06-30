# Documentation for `calculate_payment`

```python
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

### Documentation Breakdown:

- **Function Purpose:** The docstring begins with a clear statement of the function's purpose, explaining that it calculates the periodic payment for a loan.
  
- **Detailed Description:** It elaborates on how the function works, specifically mentioning the use of the net present value formula.

- **Parameters Section:** Each parameter is described with its type and purpose, providing clarity on what values should be passed to the function.

- **Returns Section:** It specifies the return type and what the returned value represents.

- **Example Section:** An example usage of the function is provided to illustrate how to call it and what kind of output to expect, enhancing usability for future developers.