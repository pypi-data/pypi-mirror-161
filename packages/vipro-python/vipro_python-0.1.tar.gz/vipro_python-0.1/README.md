# vipro-python
A set of convenience functions to make writing python, mostly in jupyter notebooks, as efficient as possible.

## egress

A set of functions for sending data out.

### [RabbitMQ](./egress/rabbitmq.py) • [examples](./test/test_egress_rabbitmq.py)

```python
from vipro_python.egress import rabbitmq
```

Send data to RabbitMQ queues or exchanges.