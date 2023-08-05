from tokenize import Number
import pika
import json


# ==== CLASSES ==== #

class Queue:
  ''' send directly to a queue '''
  def __init__(self, connection, channel, queue_name):
    self.connection = connection
    self.channel = channel
    self.queue_name = queue_name

  def publish_raw(self, body, content_type='text/plain', headers = {}):
    headers = add_agent(headers)
    headers['Content-Type'] = content_type
    self.channel.basic_publish(
      exchange='',
      routing_key=self.queue_name,
      body=body,
      properties=pika.BasicProperties(
        content_type=content_type,
        headers=headers,
      ),
    )


class Exchange:
  ''' send to an exchange with optional routing key '''
  def __init__(self, connection, channel, exchange_name, routing_key=''):
    self.connection = connection
    self.channel = channel
    self.exchange_name = exchange_name
    self.routing_key = routing_key

  def publish_raw(self, body, content_type='text/plain', headers = {}):
    headers=add_agent(headers)
    headers['Content-Type'] = content_type
    self.channel.basic_publish(
      exchange=self.exchange_name,
      routing_key=self.routing_key,
      body=body,
      properties=pika.BasicProperties(
        content_type=content_type,
        headers=headers,
      ),
    )


# ==== HELPER FUNCTIONS ==== #

def add_via(meta) -> dict:
  meta['via'] = 'vipro-python'
  return meta

def add_agent(headers) -> dict:
  headers['User-Agent'] = 'vipro-python'
  return headers


def send_as_json(con, pojo, headers={}):
  ''' use this method with one of the RabbitMQ* connections below to send an object as JSON '''
  con.publish_raw(
    json.dumps(pojo),
    'application/json',
    headers,
  )

# ==== HIGHER-ORDER FUNCTIONS ==== #

def send_df(con, df, headers={}) -> Number:
  df.apply(lambda s: send_series(con, s, headers), axis=1)
  return len(df)

def send_series(con, s, headers={}):
  pojo = s.to_json()
  send_as_json(con, pojo, headers)

def queue(queue_name, durable=True, auto_delete=True, meta={}, host='localhost') -> Queue:
  ''' push directly to a rabbitmq queue '''
  meta = add_via(meta)
  connection = pika.BlockingConnection(pika.ConnectionParameters(host))
  channel = connection.channel()
  channel.queue_declare(queue=queue_name, durable=durable, auto_delete=auto_delete, arguments=meta)
  return Queue(connection, channel, queue_name)

def exchange(exchange_name, type='fanout', routing_key='', durable=True, auto_delete=True, meta={}, host='localhost') -> Exchange:
  ''' push to a rabbitmq exchange '''
  meta = add_via(meta)
  connection = pika.BlockingConnection(pika.ConnectionParameters(host))
  channel = connection.channel()
  channel.exchange_declare(exchange=exchange_name, exchange_type=type, durable=durable, auto_delete=auto_delete, arguments=meta)
  return Exchange(connection, channel, exchange_name, routing_key)