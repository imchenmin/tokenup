"""
调用dify工作流
"""
import requests
import json
from tokenup.config import settings

# TODO 做成可配置的


def run_dify_video_understand_workflow(transcription,task_id, oss_path, video_title):
    api_key = settings['dify-secret']['dify_workflow_api']
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {
        "inputs": {
            "Transcription": transcription,
            "access_key_id": "1",
            "access_key_secret": "1", # TODO 去掉
            "AppKey": "1", # TODO 飞书key
            "ossPath": oss_path,
            "title": video_title
        },
        "user": task_id,
        "response_mode": "blocking",
    }
    response = requests.post(settings['dify']['workflow_url'], headers=headers, data=json.dumps(data))
    print(response.json())
    # TODO 返回状态监听
