# Timer

Small timer that can do parallel computing

### Installation

```
pip install small-timer
```

### Documentation

1. timer_point(time: Any, repeat:bool = False)
   - _time in seconds_
   - _This function start timer_
2. check_timer() -> bool
   - _This function check_
   - _Was timer fished_
3. check_time() -> list
   - _This function check_
   - _How much time is left_
   - _check_time()[0] - minutes_
   - _check_time()[1] - seconds_
4. restart()
   - _This function restart timer_

### Usage

1. Import class _Timer_:
   ```
   from small_timer import Timer
   ```
2. Create object _timer_:
   ```
   timer = Timer()
   ```
3. Create timer and start it:
   ```
   timer.timer_point(10)
   ```
4. Check timer if timer finished:
   ```
   if timer.check_timer():
       print("Timer finished!!!")
   else:
       print("Timer didn't finish")
   ```

### Example code

```
from small_timer import Timer

timer = Timer()
timer.timer_point(10)

while 1:
    if timer.check_timer():
       print("Timer finished!!!")
       break
    else:
       print("Timer didn't finish")
       print(f"{timer.check_time()[0]}:{timer.check_time()[1]}")
       print()
```
