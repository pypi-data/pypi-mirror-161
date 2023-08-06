# blissdata

The `blissdata` library provides access to:

* all data produced by Bliss acquisitions (Redis database 1)
* all public device settings (Redis database 0)
* beamline configuration (Beacon server)

## Receive data from Bliss acquisitions

```python
import gevent.monkey
gevent.monkey.patch_all()

from blissdata.client import configure_with_beacon_address
from blissdata.data.node import get_session_node

configure_with_beacon_address("localhost", 10001)

node = get_session_node("demo_session")
for event in node.walk_on_new_events():
    print(event)
```

## Pypi installation

```bash
python3 -m pip install blissdata[test]
```

The installation can be tested when installed with the `test` option

```bash
python3 -m pytest --pyargs blissdata
```

Note for installation on Linux: the `pytango` dependency requires
the following system packages (Ubuntu) to be installed

```bash
sudo apt update
sudo apt install libboost-python-dev libtango-dev
```

## Conda installation

```bash
conda install blissdata -c esrf-bcu
```
