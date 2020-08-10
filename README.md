# Simple GKE

매우 큰 작업을 실행하는 서비스가 필요할 때 Lambda 와 Cloud Run 은 Timeout, Memory, CPU 등의 제한이 있어서 문제가 될 때가 있습니다. 이 문제를 해결하기 위해 만들어졌습니다.

**서비스를 생성하고 작업하기**

    ```python
    from pprint import pprint
    import layers.helper
    import sys


    class Job:
        def __init__(self, hp):
            # 레이어 패키지 핸들러입니다.
            self.hp = hp
            pass
        
        # 개발자는 여기에서 원하는 동작을 실행하면 됩니다.
        # args 변수는 요청자가 Jobber API에 요청을 보낼 때 함께 보낸 매개변수입니다.
        # note 변수는 보고 할 결과값을 작성하면 됩니다.
        # 에러가 발생한다면 에러 메시지가 보고됩니다.
        def work(self, args):
            note = ""

            return note

    class App:
        def __init__(self):
            self.hp = layers.helper.Helper()
            self.fetched = self.fetch()
            self.args = self.fetched["args"]

        # 이 작업에 사용될 매개변수를 가져옵니다.
        # table_name 은 작업의 이름입니다.
        def fetch(self):
            return self.hp.post(self.hp.environ["JOBBER_URI"] + "/fetch", {
                "table_name": self.hp.environ["JOBBER_TABLE_NAME"]
            })

        # 성공여부와 결과메시지를 보고합니다.
        def report(self, success, note=""):
            self.hp.post(self.hp.environ["JOBBER_URI"] + "/report", {
                "table_name": self.hp.environ["JOBBER_TABLE_NAME"],
                "idx": self.fetched["idx"],
                "success": success,
                "note": note
            })

            return note

        def work(self):
            note = ""
            try:
                note = Job(self.hp).work(self.args)
            except Exception as e:
                self.report(False, str(e))
                self.hp.error(e)
            else:
                self.report(True, str(note))

            return note

    if __name__ == "__main__":
        App().work()

    ```

1. 구구단을 처리 할 수 있는 작업을 작성합니다.

    ```python
    ...

    def work(self, args):
        number_a = args["number_a"]
        number_b_list = args["number_b_list"]
        
        note = [number_a * number_b for number_b in number_b_list]

    ...
    ```

**만든 작업을 테스트해보기**

1. 주피터 노트북이 있다면 주피터 노트북을 엽니다.

1. GKE 클러스터가 실행되고 있지 않다면 Jobber API 에 요청하여 클러스터를 실행합니다. GKE Console 에서 클러스터 이름이 jobber 인 것이 있으면 실행되고 있는 것입니다.
    * 아래의 코드를 주피터 노트북에서 실행시켜 클러스터를 실행합니다.
    ```python
    import requests
    url = "[CLOUD RUN 에 실행되고 있는 JOBBER 의 주소]/create_cluster"

    data = {
        # "machine_type": "n1-standard-1",
        # "disk_size": 35,
        # "num_nodes": 3
    }

    requests.post(url, json=data).text
    ```

1. 테스트를 위해 테스트 코드를 작성해보겠습니다. 먼저 app.py 가 있는 폴더에서 test.py 파일을 찾아 편집기로 열어 아래의 코드를 붙여넣습니다.
    * each_args 에 값을 넣는 코드만 추가되었습니다.

    ```python

    from pprint import pprint
    import requests
    import validator_collection
    import base64
    import datetime
    import json
    import base64
    import threading
    import server.settings

    setting_handler = server.settings.Settings()

    environ = setting_handler.get_envrion()
    jobber_uri = environ["JOBBER_URI"]
    project_name = environ["GCLOUD_PROJECT_NAME"]
    service_name = setting_handler.get_name()

    # 개발자는 여기에서 요청 할 매개변수를 작성하면 됩니다.
    each_args = []

    for i in range(10):
        args = {}
        args["number_a"] = i + 1
        args["number_b_list"] = [j for j in range(100)]
        each_args.append(args)

    data = {
        "each_args": each_args,
        "environ": environ, # 환경변수입니다.
        "container_image": f"gcr.io/{project_name}/{service_name}", # 실행 할 작업 도커 이미지입니다.
        "parallel_action_count": 5, # 하나의 인스턴스가 몇개의 작업을 실행 할 지 정합니다.
        # "action_name": "your_action_name", # 이 값을 생략하면 도커 이미지 이름으로 자동 배정됩니다.
        # "active_dead_line_seconds": 3600, # 이 작업의 시간제한을 정합니다.
        # "public_command": [], # 만약 Dockerfile 에서 CMD 명령으로 어떤 작업을 실행한다면 이 명령어는 사용하지 않아도 됩니다. 모든 작업에 배정될 명령어입니다.
        # "public_args": [], # 위 명령어에 붙을 인자들입니다.
    }

    response = requests.post(f"{jobber_uri}/action", json=data)

    print(response.status_code)

    print(response.json()["message"])

    ```

1. 아래의 명령어로 작업을 테스트합니다.
    * 실행 후 마지막에 나오는 이름이 작업의 고유이름입니다.

    ```bash
    python3 deploy.py 802 test-jobber
    ```

    만약 이전에 도커가 빌드되서 푸쉬되었고 test.py 파일만 변경하는 경우에는 아래의 명령어로 테스트합니다.

    ```bash
    python3 deploy.py 802 test-jobber --no-build
    ```

    실행결과

    ```bash
    ...

    200
    test-jobber-200709-104647-xtl
    ```
    
1. 작업 테스트를 실행 후 마지막에 print 되는 이름이 작업이 고유이름인데 이 고유이름으로 작업의 결과와 상태를 확인 할 수 있습니다.

1. GKE Console 에서 왼쪽 네비게이션에서 Workloads(두 번째 버튼) 를 클릭합니다.

1. 작업이 제대로 배포되었는지 확인합니다.

1. 작업 결과를 보려면 주피터 노트북에서 아래의 코드를 실행합니다.

    ```python
    import requests

    url = "[CLOUD RUN 에 실행되고 있는 JOBBER 의 주소]/status"
    data = {
        "table_name": "작업이 실행 된 후 결과값으로 받은 고유이름"
    }

    requests.post(url, json=data).json()["message"]
    ```
    실행결과
    * 아직 작업중이라면 다르게 표시 될 수 있습니다.
    ```bash
    {'complete': 10}
    ```

1. 전체 결과를 보려면 주피터에서 아래의 코드를 실행합니다.

    ```python
    import requests

    url = "https://jobber-y4i4rvrklq-an.a.run.app/get_log"
    data = {
        "table_name": "작업이 실행 된 후 결과값으로 받은 고유이름"
    }

    requests.post(url, json=data).json()["message"]
    ```
    실행결과
    ```bash
    ...

    {'args': 'eyJudW1iZXJfYSI6IDEwLCAibnVtYmVyX2JfbGlzdCI6IFswLCAxLCAyLCAzLCA0LCA1LCA2LCA3LCA4LCA5LCAxMCwgMTEsIDEyLCAxMywgMTQsIDE1LCAxNiwgMTcsIDE4LCAxOSwgMjAsIDIxLCAyMiwgMjMsIDI0LCAyNSwgMjYsIDI3LCAyOCwgMjksIDMwLCAzMSwgMzIsIDMzLCAzNCwgMzUsIDM2LCAzNywgMzgsIDM5LCA0MCwgNDEsIDQyLCA0MywgNDQsIDQ1LCA0NiwgNDcsIDQ4LCA0OSwgNTAsIDUxLCA1MiwgNTMsIDU0LCA1NSwgNTYsIDU3LCA1OCwgNTksIDYwLCA2MSwgNjIsIDYzLCA2NCwgNjUsIDY2LCA2NywgNjgsIDY5LCA3MCwgNzEsIDcyLCA3MywgNzQsIDc1LCA3NiwgNzcsIDc4LCA3OSwgODAsIDgxLCA4MiwgODMsIDg0LCA4NSwgODYsIDg3LCA4OCwgODksIDkwLCA5MSwgOTIsIDkzLCA5NCwgOTUsIDk2LCA5NywgOTgsIDk5XX0=',
    'container_image': 'gcr.io/your-project-name/test-jobber',
    'idx': 10,
    'note': '[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 810, 820, 830, 840, 850, 860, 870, 880, 890, 900, 910, 920, 930, 940, 950, 960, 970, 980, 990]',
    'reg_date': 'Thu, 09 Jul 2020 10:46:48 GMT',
    'status': 'complete',
    'updated_date': 'Thu, 09 Jul 2020 10:48:32 GMT'}]

    ```

1. (선택) 모든 작업 로그를 지우려면 아래의 주피터에서 아래의 코드를 실행하세요.
    * 작업로그는 DB 에 저장되기 때문에 deployer/settings.json 에 클라우드런 환경변수를 설정하는 곳에서 지정된 DB 정보로 접속하면 직접 확인 할 수 있습니다.

    ```python
    import requests

    url = "https://jobber-y4i4rvrklq-an.a.run.app/clear_log"
    data = {}

    requests.post(url, json=data).json()["message"]
    ```

1. (선택) 클러스터를 종료하려면 주피터에서 아래의 코드를 입력하세요.
    ```python
    import requests

    url = "https://jobber-y4i4rvrklq-an.a.run.app/delete_cluster"
    data = {}

    requests.post(url, json=data).json()["message"]
    ```

1. 🎉 완료했습니다.


**만든 작업을 배포하기**

