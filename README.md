<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="./static/icon.png" alt="Project logo" ></a>
 <br>

 
</p>

<h3 align="center">Simple GKE</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/da-huin/simple_gke.svg)](https://github.com/da-huin/simple_gke/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/da-huin/simple_gke.svg)](https://github.com/da-huin/simple_gke/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> 매우 큰 작업을 실행하는 서비스가 필요할 때 Lambda 와 Cloud Run 은 Timeout, Memory, CPU 등의 제한이 있어서 문제가 될 때가 있습니다. 이 문제를 해결하기 위해 만들어졌습니다.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

Simple GKE 가 작동하는 방식은 아래와 같습니다.

1. Simple GKE 라는 서비스를 클라우드런에 실행시킵니다.

1. `작업을 관리하는 사용자의 코드`에서 Simple GKE 서비스에 클러스터를 켜달라고 요청합니다. (상시로 켜두어도 됩니다.)

1. 작업시킬 작업자 도커를 Google Container Registry 에 배포합니다.

1. `작업을 관리하는 사용자의 코드`에서 Simple GKE 서비스에 작업자 도커에 각자의 매개변수를 넣어 작업을 진행해달라고 요청합니다.

1. Simple GKE 는 RDB 에 작업별 매개변수를 저장하고 GKE 에 작업을 실행해달라고 말합니다.

1. 작업자 도커에서 Simple GKE 와 통신하며 작업 상황을 보고합니다.

1. 작업의 결과를 API 로 받아보거나 RDB Viewer 에서 직접 확인 할 수 있습니다.

1. 작업이 완료되면 GKE 는 자동으로 클러스터의 인스턴스들을 공격적으로 줄입니다.

## 🏁 Getting Started <a name = "getting_started"></a>

<a name="prerequisites"></a>

### 🚀 Tutorial

#### 1. Cloud Run 에 배포하기

Cloud Run 에 어떤 방식으로든 배포 할 수 있으면 됩니다. 여기에서는 [easy_cloudrun](https://github.com/da-huin/easy_cloudrun) 을 사용한 방식으로 배포해보겠습니다.

아래의 코드로 Cloud Run 에 배포합니다.

1. Sample 작업자 도커 확인하기

    Sample 작업자 도커 경로: `SIMPLE_GKE_DIRECTORY/sample`

```python
import easy_cloudrun

handler = easy_cloudrun.EasyCloudRun()

dockerfile_dir = "YOUR_SIMPLE_GKE_DIRECTORY" # 이 깃의 폴더 경로입니다.
environ = {}

environ = {
    "SELF_URI": "URL of Simple GKE to be deployed in CloudRun", # Example: https://simple-gke-xxxxxxxx-an.a.run.app
    "DB_HOSTNAME": "YOUR_DB_HOSTNAME",
    "DB_USER": "YOUR_DB_USER",
    "DB_PASSWORD": "YOUR_DB_PASSWORD",
    "GCLOUD_SERVICE_ACCOUNT": "YOUR_GCLOUD_SERVICE_ACCOUNT", # Example: PROJECT_NAME@appspot.gserviceaccount.com
    "GCLOUD_PROJECT_NAME": "YOUR_GCLOUD_PROJECT_NAME",
}

commands = {
    "--allow-unauthenticated": ""
}

handler.run("simple-gke", dockerfile_dir, environ=environ)


handler.build_push_deploy("simple-gke", dockerfile_dir,
                          environ=environ, commands=commands)

dockerfile_dir = "SIMPLE_GKE_DIRECTORY/sample" 

handler.build_push("sample", dockerfile_dir)

```

1. Cloud Run 에서 



## 🎈 Usage <a name="usage"></a>

Please check [Prerequisites](#prerequisites) before starting `Usage`.

### 🌱 create <a name="create"></a>

람다 함수를 생성 할 때 사용하세요.

**Parameters**

* `(required) service_name`: str

    람다 함수의 이름입니다.

* `base_dir`: str (default = "")

    람다 함수의 기본 경로입니다. 아래와 같이 적용됩니다.

    ```
    services_dir/base_dir/service_name
    ```

**Returns**

* `None`


### 🌱 test <a name="test"></a>

* `(required) service_name`: str

    테스트 할 람다 함수의 이름입니다.

* `pytest`: bool (default=False)

    pytest 로 테스트 할 것인지 여부입니다.

**Returns**

* `None`

### 🌱 deploy_layer <a name="deploy_layer"></a>

* `(required) layer_name`: str

    배포 할 람다 레이어의 이름입니다.

* `(required) requirements`: list

    레이어에 사용 할 패키지 이름들입니다.

**Returns**

* `None`

### 🌱 deploy <a name="deploy"></a>

* `(required) service_name`: str

    배포 할 람다 함수의 이름입니다.

* `(required) layer_name`: str

    람다 함수에 적용 할 람다 레이어의 이름입니다. deploy_layer 에서 정한 레이어의 이름을 사용하세요.

**Returns**

* `None`

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Title icon made by [Freepik](https://www.flaticon.com/kr/authors/freepik).

- If you have a problem. please make [issue](https://github.com/da-huin/simple_gke/issues).

- Please help develop this project 😀

- Thanks for reading 😄
