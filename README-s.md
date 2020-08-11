# Simple GKE

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

