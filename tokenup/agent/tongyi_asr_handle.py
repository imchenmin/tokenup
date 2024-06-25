
import datetime
import json
import configparser
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from tokenup.config import settings

def init_parameters(fileurl):
    """
    初始化请求参数

    Parameters:
    - fileurl (str): 文件 URL

    Returns:
    - dict: 包含请求参数的字典
    """
    body = {
        'AppKey': settings['tongyi-tingwu']['AppKey'],
        'Input': {
            'SourceLanguage': 'cn',
            'TaskKey': 'task' + datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
            'FileUrl': fileurl
        },
        'Parameters': {
            'Transcription': {
                'DiarizationEnabled': True,
                'Diarization': {'SpeakerCount': 1}
            },
            'AutoChaptersEnabled': True,
            'MeetingAssistanceEnabled': True,
            'MeetingAssistance': {'Types': ['Actions', 'KeyInformation']},
            'SummarizationEnabled': True,
            'Summarization': {'Types': ['Paragraph', 'Conversational', 'QuestionsAnswering', 'MindMap']}
        }
    }
    return body

def create_common_request(domain, version, protocolType, method, uri):
    """
    创建通用请求对象并设置基本信息

    Parameters:
    - domain (str): 请求的域名
    - version (str): API 版本
    - protocolType (str): 协议类型（如 'https'）
    - method (str): 请求方法（如 'GET' 或 'POST'）
    - uri (str): URI 模式

    Returns:
    - CommonRequest: 配置好的请求对象
    """
    local_request = CommonRequest()
    local_request.set_accept_format('json')
    local_request.set_domain(domain)
    local_request.set_version(version)
    local_request.set_protocol_type(protocolType)
    local_request.set_method(method)
    local_request.set_uri_pattern(uri)
    local_request.add_header('Content-Type', 'application/json')

    # 打印请求头
    headers = local_request.get_headers()
    for header, value in headers.items():
        try:
            print(f"{header}: {value}")
        except UnicodeEncodeError:
            print(f"{header}: <value contains non-latin-1 characters>")

    return local_request

def get_credentials():
    """
    从配置文件中获取阿里云凭证

    Returns:
    - AccessKeyCredential: 包含访问密钥的凭证对象
    """
    access_key_id = settings['tongyi-tingwu']['access_key_id']
    access_key_secret = settings['tongyi-tingwu']['access_key_secret']

    return AccessKeyCredential(access_key_id=access_key_id, access_key_secret=access_key_secret)


def query_tingwu_task(task_id):
    """
    处理查询任务的请求

    Returns:
    - dict: 查询到的任务信息
    """
    uri = f'/openapi/tingwu/v2/tasks/{task_id}'

    credentials = get_credentials()
    client = AcsClient(region_id='cn-beijing', credential=credentials)

    local_request = create_common_request('tingwu.cn-beijing.aliyuncs.com', '2023-09-30', 'https', 'GET', uri)
    response = client.do_action_with_exception(local_request)
    response_data = json.loads(response)

    print(json.dumps(response_data, indent=4, ensure_ascii=False))

    return response_data


def tongyi_tingwu_api(audio_file_url):
    """
    处理创建任务的请求

    Returns:
    - str: 创建的任务ID
    """
    file_url = audio_file_url
    body = init_parameters(file_url)
    print("请求体：")
    print(json.dumps(body, indent=4, ensure_ascii=False))

    credentials = get_credentials()
    client = AcsClient(region_id='cn-beijing', credential=credentials)

    local_request = create_common_request('tingwu.cn-beijing.aliyuncs.com', '2023-09-30', 'https', 'PUT',
                                          '/openapi/tingwu/v2/tasks')
    local_request.add_query_param('type', 'offline')
    local_request.set_content(json.dumps(body).encode('utf-8'))

    response = client.do_action_with_exception(local_request)
    response_data = json.loads(response)
    print(response_data["Code"])
    print("response: \n" + json.dumps(response_data, indent=4, ensure_ascii=False))

    return response_data.get("Data").get("TaskId")