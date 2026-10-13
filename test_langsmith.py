
from langsmith import traceable


@traceable(name="KILLSWITCH Test")
def test_function(query: str):
    return f"Processed query: {query}"


result = test_function("How does a kill switch work?")
print(result)
