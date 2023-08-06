# format_duration
#### Python module to convert duration to human readable format

## Installation
```commandline
pip install format_duration
```

## Usage
```python
from datetime import timedelta
from format_duration import DurationLimit, format_duration

duration = timedelta(days=1, hours=1, minutes=1, seconds=1)  # duration to format
limit = DurationLimit.MINUTE  # only print till minutes
is_abbreviated = False  # Whether to print in abbreviated form
formatted_duration = format_duration(duration, is_abbreviated, limit)  # formatted duration string
print(formatted_duration)  # 1 days, 1 hours, 1 minutes 
```