# Documentation for `calculate_future_value`

```python
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
``` 

### Documentation Breakdown:
- **Function Purpose:** Clearly states that the function calculates the future value of an investment.
- **Formula Explanation:** Provides a brief explanation of the formula used for calculation.
- **Parameters Section:** Details each parameter, including type, description, and any necessary formatting (e.g., decimal for rate).
- **Returns Section:** Specifies the return type and what it represents.
- **Example Usage:** Offers a practical example to illustrate how to use the function and what output to expect.