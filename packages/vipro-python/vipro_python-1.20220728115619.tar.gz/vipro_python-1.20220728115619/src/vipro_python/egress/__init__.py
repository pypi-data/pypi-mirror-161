
def foreach_row(df, predicate):
  return df.apply(predicate, axis=1)
