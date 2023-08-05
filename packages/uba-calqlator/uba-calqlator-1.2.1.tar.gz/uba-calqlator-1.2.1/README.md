# Initiate CalQlator 

```python
client = new TechStack(**args)
calqlator = CalQlator(client)
```

# Set scope

```python
inventory_name = 'TestInventory'
from_timepoint = '2010-01-11 00:00:00'
to_timepoint = '2022-12-31 23:59:59'
scope = calqlator.scope(inventory_name, from_timepoint, to_timepoint)
```

# Load time series

```python
target_inventory_item_id1 = 'Y5NBb7dfIe'
target_inventory_item_id2 = 'Y5NBb7vGQi'
time_series1 = scope.time_series(target_inventory_item_id1)
time_series2 = scope.time_series(target_inventory_item_id2)
```

# Calculations with time series

```python
calculated_time_series1 = time_series1 + time_series2 
calculated_time_series2 = time_series1 * 0.3
```

# Write time series

```python
target_inventory_item_id = 'YFS6yBQF7o'
scope.write(target_inventory_item_id, calculated_time_series)
```
