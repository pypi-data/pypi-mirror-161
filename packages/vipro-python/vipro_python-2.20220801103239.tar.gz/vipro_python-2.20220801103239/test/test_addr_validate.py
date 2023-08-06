# ability to import module from relative path
import sys; sys.path.insert(0,'./src'); sys.path.insert(0,'../src')

# determine 1st line of the address
from vipro_python.ai.validate import contains_company_word

def test_company():
  res = contains_company_word("Anchor Hanover Group ( Helen Court)")
  assert res == True

def test_person():
  res = contains_company_word("Tom Medhurst")
  assert res == False