import os
from sys import argv
import requests

api_url = "http://localhost:9123/grade"

def submit(key, submit_file_path):
  values = {"key": key}
  res = requests.post(api_url, files = {'file': open(submit_file_path,'rb', )}, data=values)  
  if res.status_code == 200 or res.status_code == 201: 
    print("success")
    return
  print(res.status_code)  
  print(res.text)