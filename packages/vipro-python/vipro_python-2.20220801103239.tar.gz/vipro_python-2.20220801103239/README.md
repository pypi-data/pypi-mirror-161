# vipro-python
A set of convenience functions to make writing python, mostly in jupyter notebooks, as efficient as possible.

## egress

A set of functions for sending data out.

### [RabbitMQ](./src/vipro_python/egress/rabbitmq.py) • examples [#1](./test/test_egress_rabbitmq.py)

```python
from vipro_python.egress import rabbitmq
```

Send data to RabbitMQ queues or exchanges.

### [A.I.](./src/vipro_python/ai/__init__.py) • examples [#1](./test/test_addr.py) [#2](./test/test_addr_validate.py)

A set of A.I. functions for cleansing or normalising companies and postal addresses.

```python
from vipro_python.ai import address, address_explode, clean, explode_date_range, name, validate
```