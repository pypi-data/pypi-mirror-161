# A package to make forecast visualisation easier

**Objective**: To make forecast visualisation easier and more expressive.

To install the package

```
pip install forecast-tool
```

Let me show you how the package works


## (1) Make a simple forecast using ARIMA model
**Input [1]**:

```python
from forecast_tool import forecast_plot as fp

period = 'm' #[y, m, w, d]

fp.overall_vis(df, date='Date', newtarget='Volume', period,show_model_name=True, numElems=8)
```