# lctest

A small library for simulate running leetcode

```python
from lctest import *

@testcase(
    (Expected, Parameters)
)
class Solution:
    @solution
    fun doSomething(self, params):
        pass

    def sol(self, params):
        pass
```
