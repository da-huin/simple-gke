from pprint import pprint
import sys
import os
import requests

master_uri = os.environ["MASTER_URI"]
table_name = os.environ["TABLE_NAME"]

def work(args):
    number_a = args["number_a"]
    number_b_list = args["number_b_list"]
    
    note = [number_a * number_b for number_b in number_b_list]
    return note    

class Worker():


    def __init__(self):
        fetched_data = self.fetch()
        self.worker_index = fetched_data["idx"]
        self.args = fetched_data.get("args", {})

    def fetch(self):
        response = requests.post(f"{master_uri}/fetch", json={"table_name": table_name})

        assert response.status_code == 200

        return response.json()

    def report(self, success, note=""):
        response = requests.post(f"{master_uri}/report", json={
            "table_name": table_name,
            "idx": self.worker_index,
            "success": success,
            "note": note
        })

        assert response.status_code == 200
        
        return response.json()

    def start(self):
        note = ""
        try:
            note = work(self.args)
        except Exception as e:
            self.report(False, str(e))
            raise Exception(e)
        else:
            self.report(True, str(note))

        return note


Worker().start()
