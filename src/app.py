import re
import datetime
import yaml
import base64
import json
import subprocess
import os
import time
import pymysql
from collections import Counter
import flask_helper
import random

class NoMoreArgsError(Exception):
    pass

class SimpleGKE:
    def __init__(self, self_uri, db_name, db_hostname, db_port, db_user, db_password, gcloud_service_account, gcloud_project_name="", cluster_name="simple-gke"):
        os.makedirs("/tmp/jobs", exist_ok=True)
        self._gcloud_service_account = gcloud_service_account
        self._gcloud_project_name = gcloud_project_name
        self._cluster_name = cluster_name
        self._db_name = db_name
        self._db_hostname = db_hostname
        self._db_port = db_port
        self._db_user = db_user
        self._db_password = db_password

        self._self_uri = self_uri
        self.create_database()
        self.flask_handler = flask_helper.FlaskHelper()
        self.register()

    def query(self, sqls: list, use_db=True):
        if not isinstance(sqls, list):
            raise ValueError("sqls type msut be list")
        # len(table)
        db = None
        if use_db:
            db = self._db_name

        connection = pymysql.connect(
            host=self._db_hostname, port=int(self._db_port), user=self._db_user,
            password=self._db_password, db=db)

        cursor = connection.cursor(pymysql.cursors.DictCursor)

        for sql in sqls:
            cursor.execute(sql)
        cursor.close()

        connection.commit()
        connection.close()
        return cursor.fetchall()

    def create_database(self):
        sql = f"CREATE DATABASE IF NOT EXISTS `{self._db_name}`"
        return self.query([sql], False)

    def create_table(self, table_name):
        sql = """CREATE TABLE `""" + table_name + """` (
            `idx` INT(11) NOT NULL AUTO_INCREMENT,
            `container_image` VARCHAR(512) NOT NULL,
            `status` VARCHAR(256) NOT NULL DEFAULT 'ready',
            `args` LONGTEXT NOT NULL,
            `reg_date` TIMESTAMP NULL DEFAULT current_timestamp(),
            `updated_date` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            `note` LONGTEXT,
            PRIMARY KEY (`idx`)
        )
        COLLATE='utf8_unicode_ci'
        ;"""
        return self.query([sql])

    def make_job(self, name: str, completions: int, parallelism: int, active_dead_line_seconds: int,
                 container_image: str, command: list, args: list, back_off_limit: int, environ: dict,
                 cpu_limit: str, memory_limit: str, cpu_request: str, memory_request: str) -> str:
        container_name = container_image.split("/")[-1]
        job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": name
            },
            "spec": {
                "completions": completions,
                "parallelism": parallelism,
                "activeDeadlineSeconds": active_dead_line_seconds,
                "template": {
                    "metadata": {
                        "name": name
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": container_name,
                                "image": container_image,
                                "command": command,
                                "args": args,
                                "env": [{"name": key, "value": str(environ[key])} for key in environ],
                                "resources": {
                                    "limits": {
                                        "cpu": cpu_limit,
                                        "memory": memory_limit
                                    },
                                    "requests": {
                                        "cpu": cpu_request,
                                        "memory": memory_request
                                    }
                                }
                            }
                        ],
                        "restartPolicy": "Never"
                    }
                },
                "backoffLimit": back_off_limit
            }
        }

        return yaml.dump(job, encoding="utf-8").decode("utf-8")

    def delete_job(self, table_name):
        return self.check_output(f"kubectl delete jobs {table_name}")

    def register(self):

        @self.flask_handler.route("/")
        def hello(args):
            return "hello world!"

        @self.flask_handler.route("/create_cluster")
        def create_cluster(args):
            machine_type = args["machine_type"]
            disk_size = args["disk_size"]
            num_nodes = args["num_nodes"]

            command = f"""gcloud beta container --project "{self._gcloud_project_name}" clusters create "{self._cluster_name}" --zone "asia-northeast1-a" --no-enable-basic-auth --machine-type "{machine_type}" --image-type "COS" --disk-type "pd-standard" --disk-size "{disk_size}" --metadata disable-legacy-endpoints=true --preemptible --num-nodes "{num_nodes}" --enable-stackdriver-kubernetes --enable-ip-alias --network "projects/{self._gcloud_project_name}/global/networks/default" --subnetwork "projects/{self._gcloud_project_name}/regions/asia-northeast1/subnetworks/default" --default-max-pods-per-node "110" --enable-autoscaling --min-nodes "0" --max-nodes "1000" --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --enable-autoprovisioning --min-cpu 1 --max-cpu 100 --min-memory 1 --max-memory 100 --autoprovisioning-service-account={self._gcloud_service_account} --autoscaling-profile optimize-utilization --enable-vertical-pod-autoscaling --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --autoprovisioning-scopes="https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --quiet --async  """
            # self.hp.slack(command)
            print(command)
            result = self.check_output(command)
            print(result)

            return "your request has been completed. please check the cloud run log"

        @self.flask_handler.route("/delete_cluster")
        def delete_cluster(args):
            command = f"""gcloud beta container clusters delete {self._cluster_name} --zone "asia-northeast1-a" --quiet --async"""
            print(command)
            result = self.check_output(command)
            print(result)
            return "your request has been completed. please check the cloud run log"

        @self.flask_handler.route("/status")
        def status(args):
            table_name = args["table_name"]
            statuses = [item["status"]
                        for item in self.query([f"SELECT * FROM `{table_name}`"])]
            return dict(Counter(statuses))

        @self.flask_handler.route("/get_log")
        def get_log(args):
            table_name = args["table_name"]
            return self.query([f"SELECT * FROM `{table_name}`"])

        @self.flask_handler.route("/clear_log")
        def clear_log(args):
            self.query([f"DROP DATABASE `{self._db_name}`"])
            return self.create_database()

        @self.flask_handler.route("/kill")
        def kill(args):
            return self.delete_job(args["table_name"])

        @self.flask_handler.route("/action")
        def action(args):
            self.check_output(
                f"""gcloud container clusters get-credentials {self._cluster_name} --zone "asia-northeast1-a" """)
            action_name = args["action_name"]
            each_args = args["each_args"]
            parallel_per_count = int(args["parallel_per_count"])
            active_dead_line_seconds = int(args["active_dead_line_seconds"])
            container_image = args["container_image"]
            public_command = args["public_command"]
            public_args = args["public_args"]
            back_off_limit = args["back_off_limit"]
            cpu_limit = args["cpu_limit"]
            memory_limit = args["memory_limit"]
            cpu_request = args["cpu_request"]
            memory_request = args["memory_request"]

            environ = args["environ"]
            environ["MASTER_URI"] = self._self_uri
            if parallel_per_count < 1:
                raise ValueError("parallel action count must be more then 0")

            values = []
            for item in each_args:
                args = base64.b64encode(json.dumps(
                    item, ensure_ascii=False, default=str).encode()).decode()
                values.append(f"('{container_image}', '{args}')")
            if not action_name:
                action_name = container_image.split("/")[-1]

            table_name = action_name + "-" + datetime.datetime.now().strftime("%y%m%d-%H%M%S") + \
                "-" + self.get_random_string(3).lower()

            matched = re.match('[a-z0-9]([-a-z0-9]*[a-z0-9])?', table_name)
            if not matched or table_name != matched[0]:
                raise ValueError(
                    f"name regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?'), but {action_name} received.")

            environ["TABLE_NAME"] = table_name

            self.create_table(table_name)
            str_values = ", ".join(values)
            sql = f"INSERT INTO `{table_name}` (container_image, args) VALUES {str_values};"
            self.query([sql])
            compleations = len(values)

            parallelism = int(compleations / parallel_per_count) + 1
            job = self.make_job(table_name, compleations, parallelism,
                                active_dead_line_seconds, container_image, public_command, public_args, back_off_limit,
                                environ, cpu_limit, memory_limit, cpu_request, memory_request)

            job_path = f"/tmp/jobs/{table_name}.yaml"

            with open(job_path, "w", encoding="utf-8") as fp:
                fp.write(job)
            # return job
            self.check_output(f"kubectl apply -f {job_path}")

            return table_name

        @self.flask_handler.route("/fetch")
        def fetch(args):
            table_name = args["table_name"]

            # 만약 status 중 ready 또는 running 이 없는데 가져오려고 한다면 모든 작업을 삭제한다.
            if len(self.query([f"SELECT * FROM `{table_name}` WHERE `status` = 'ready' or `status` = 'running' LIMIT 1;"])) == 0:
                self.delete_job(table_name)
                raise NoMoreArgsError(
                    f"{table_name}. there are no more arguments.")
            else:
                idx = self.query([f"SET @result = (SELECT `idx` From `{table_name}` WHERE `status`='ready' LIMIT 1);",
                                  f"UPDATE `{table_name}` SET `status` = 'running' where idx = @result;", "SELECT @result;"])[0]["@result"]
                result = {}
                query_result = self.query(
                    [f"SELECT idx, container_image, args, status, note FROM `{table_name}` WHERE idx='{idx}'"])[0]
                result["args"] = json.loads(
                    base64.b64decode(query_result["args"].encode()))

                result["idx"] = idx

            return result

        @self.flask_handler.route("/report")
        def report(args):
            idx = args["idx"]
            table_name = args["table_name"]
            note = args["note"]
            if isinstance(note, list) or isinstance(note, dict):
                note = json.dumps(note, ensure_ascii=False, default=str)

            note = pymysql.escape_string(str(note))
            status = "complete" if args["success"] else "fail"

            return self.query([f"UPDATE `{table_name}` SET `status` = '{status}', `note`='{note}' where idx = {idx};"])


    def check_output(self, command):
        result = ""
        print(command)
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE)
        for b_line in iter(process.stdout.readline, b''):
            try:
                line = b_line.decode("cp949")
            except:
                try:
                    line = b_line.decode("utf-8")
                except:
                    pass
            print(line, end="")
            result += line

        return result

    def get_random_string(self, length=10):
        random_box = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        random_box_length = len(random_box)
        result = ""
        for _ in range(length):
            result += random_box[int(random.random()*random_box_length)]

        return result

if __name__ == "__main__":
    SimpleGKE(os.environ["SELF_URI"], os.environ.get("DB_NAME", "simple_gke"), 
    os.environ["DB_HOSTNAME"], os.environ.get("DB_PORT", 3306),
    os.environ["DB_USER"], os.environ["DB_PASSWORD"],
    os.environ["GCLOUD_SERVICE_ACCOUNT"], os.environ["GCLOUD_PROJECT_NAME"], 
    os.environ.get("CLUSTER_NAME", "simple-gke")
    ).flask_handler.listen()

# GCLOUD_AUTH_PATH required.
