
def foreach_row(df, predicate):
  return df.apply(predicate, axis=1)

def set_output(key, val):
  print('set::{}::{}'.format(key, val))
