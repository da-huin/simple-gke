from pprint import pprint
import sys
import os
import requests


# === 여기 (work 함수) 에만 작업하면 됩니다 ===

def work(args):
    # 구구단을 처리 할 수 있는 샘플 작업입니다.
    number_a = args["number_a"]
    number_b_list = args["number_b_list"]
    
    note = [number_a * number_b for number_b in number_b_list]
    return note

# === 여기부터는 무시해도 됩니다 ===


class Worker():

    def __init__(self):
        
        self.master_uri = os.environ["MASTER_URI"]
        self.table_name = os.environ["TABLE_NAME"]
        fetched_data = self.fetch()
        self.worker_index = fetched_data["idx"]
        self.args = fetched_data.get("args", {})

    # 매개변수를 Simple GKE 에서 가져옵니다.
    def fetch(self):
        response = requests.post(f"{self.master_uri}/fetch", json={"table_name": self.table_name})

        assert response.status_code == 200

        return response.json()["message"]


    # 결과를 Simple GKE 에 보고합니다.
    def report(self, success, note=""):
        response = requests.post(f"{self.master_uri}/report", json={
            "table_name": self.table_name,
            "idx": self.worker_index,
            "success": success,
            "note": note
        })

        assert response.status_code == 200
        
        return response.json()["message"]

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