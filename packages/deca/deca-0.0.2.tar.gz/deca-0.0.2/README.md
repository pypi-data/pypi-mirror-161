# Decaying numbers

This library offers a datatype that can be used for working with
decaying numbers.

A use case is keeping track of the popularity of pages on your
website: by using a hit counter that gradually decreases the weight
for older hits, a more representative view of the current popularity
can be shown.

An example implementation of such a hit counter could be as follows:

``` python
from collections import defaultdict
from deca import Deca, DecaFactory

DF = DecaFactory(half_life = 24*3600)
counter = defaultdict(lambda: DF(0))

def register_hit(url: str) -> None:
    counter[url].inc(1)

def get_top_10() -> list[tuple[str, Deca]]:
    return sorted(
	    counter.items(),
		key=lambda item: item[1],
		reverse=True
	)[:10]
```

Besides this there is more functionality on the Deca classes that
allow you to apply some basic mathematical operations on them.
Also, as shown by the above example, there is support for comparing
them, so they can be sorted easily.
