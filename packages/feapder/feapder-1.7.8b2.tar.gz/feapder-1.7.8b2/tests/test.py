from requests.structures import CaseInsensitiveDict
import requests

data = CaseInsensitiveDict({"A": {"B": 1}})

print(data)
print(data.get("a").get("B"))
