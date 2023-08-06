# ability to import module from relative path
import sys; sys.path.insert(0,'./src'); sys.path.insert(0,'../src')

from vipro_python.egress import rabbitmq
import pandas as pd

def test_functions_exist():
  assert rabbitmq.queue != None
  assert rabbitmq.exchange != None
  assert rabbitmq.send_as_json != None
  assert rabbitmq.send_df != None
  assert rabbitmq.send_series != None

def test_send_to_queue():
  q = rabbitmq.queue('vipro_python_unit_test1', durable=False, auto_delete=True, meta={'purpose': 'unit_testing'})
  rabbitmq.send_as_json(q, {'test': '123', 'foo': 321})

def test_send_to_exchange():
  q = rabbitmq.exchange('vipro_python_unit_test2', durable=False, auto_delete=False, meta={'purpose': 'unit_testing'})
  rabbitmq.send_as_json(q, {'test': '123', 'foo': 321})

def test_with_dataframe():
  data = [['tom', 10], ['nick', 15], ['julie', 14]]
  df = pd.DataFrame(data, columns=['Name', 'Age'])
  q = rabbitmq.queue('vipro_python_unit_test3', durable=False, auto_delete=False, meta={'purpose': 'unit_testing'})
  sent = rabbitmq.send_df(q, df)
  assert sent == 3 # rows