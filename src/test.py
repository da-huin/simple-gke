from pprint import pprint
import requests
import validator_collection
import base64
import layers.tester.api_tester
import datetime
import json
import base64
import threading
tester_handler = layers.tester.api_tester.Tester()


def test_api_hello():
    data = {}

    sc, msg = tester_handler.post("/", data)
    print(msg)
    assert sc == 200


def test_api_create_cluster():
    data = {}

    sc, msg = tester_handler.post("/create_cluster", data)
    print(msg)
    assert sc == 200
