# ability to import module from relative path
import sys; sys.path.append('./src'); sys.path.append('../src')

from vipro_python.egress import rabbitmq

def test_functions_exist():
  assert rabbitmq.queue != None
  assert rabbitmq.exchange != None
  assert rabbitmq.send_as_json != None

def test_send_to_queue():
  q = rabbitmq.queue('vipro_python_unit_test1', durable=False, auto_delete=True, meta={'purpose': 'unit_testing'})
  rabbitmq.send_as_json(q, {'test': '123', 'foo': 321})

def test_send_to_exchange():
  q = rabbitmq.exchange('vipro_python_unit_test2', durable=False, auto_delete=False, meta={'purpose': 'unit_testing'})
  rabbitmq.send_as_json(q, {'test': '123', 'foo': 321})