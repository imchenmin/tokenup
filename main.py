import streamlit as st
from tokenup.agent import tongyi_asr_handle
from pathlib import Path
import tempfile
from tokenup.storage_providers import aliyun_oss
import pandas as pd
from tokenup.constant import TaskStatus
from tokenup.agent.dify_handler import run_dify_video_understand_workflow
from tokenup.media_handler.audio_extract import extract_audio
import time
import threading
from tokenup.config import settings

st.set_page_config(layout="wide")

access_key_id = settings['aliyun-oss']['access_key_id']
access_key_secret = settings['aliyun-oss']['access_key_secret']
endpoint = settings['aliyun-oss']['endpoint']
bucket_name = settings['aliyun-oss']['bucket_name']
oss_manager = aliyun_oss.OSSManager(access_key_id, access_key_secret, endpoint, bucket_name)
INTRO_STR = "# TokenUp Web UI \n \n 按Token索骥 \n \n 上传文件、网页、音频、视频，然后和智能体聊天吧。"

columns_to_display = ['sourceName', 'audio_file', 'status', 'progress']
column_config = {
    "sourceName": st.column_config.Column("视频名称"),
    "audio_file": st.column_config.LinkColumn("音频文件"),
    "status": st.column_config.Column("当前状态"),
    "progress": st.column_config.ProgressColumn("进度")
}

def stream_data():
    for word in INTRO_STR:
        yield word
        time.sleep(0.02)

def main_page():
    st.write_stream(stream_data())
    # st.write(INTRO_STR)
    media_file_upload()
    
def update_table(status_gui, task_status):
    with status_gui.container():
        st.dataframe(task_status[columns_to_display], column_config=column_config)

def media_file_upload():
    uploaded_files = st.file_uploader("上传视频文件", type=["mp4", "mov"], accept_multiple_files=True)
    task_list = []
    if uploaded_files is None:
        return
    for video_file in uploaded_files:
        if video_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(video_file.read())
            task_init = {"sourceName": video_file.name, "videoName": tfile.name, 'audio_file': None, "status": TaskStatus.INIT, "task_id": 0, 'asr_status': TaskStatus.ONGOING, 'progress': 0}
            task_list.append(task_init)
    task_status = pd.DataFrame(task_list)
    status_gui = st.empty()
    for index, task in task_status.iterrows():
        update_table(status_gui, task_status)
        task_status.loc[index, 'status'] = TaskStatus.AUDIO_PROCESSING
        task_status.loc[index, 'progress'] = 0.2
        Path("audio_tmp").mkdir(exist_ok=True)
        audio_file = Path("audio_tmp") / (Path(task['videoName']).name + ".mp3")
        ret, msg = extract_audio(str(Path(task['videoName'])), audio_file)
        print(ret, msg)
        update_table(status_gui, task_status)
        if ret:
            task_status.loc[index, 'status'] = TaskStatus.AUDIO_UPLOADING
            task_status.loc[index, 'progress'] = 0.3
            oss_manager.upload_file(audio_file, 'audio/')
            mp3_url = f"https://bucket-feishu.oss-cn-shenzhen.aliyuncs.com/audio/{Path(audio_file).name}"
            task_status.loc[index, 'audio_file'] = mp3_url
            update_table(status_gui, task_status)
            task_status.loc[index, 'task_id'] = tongyi_asr_handle.tongyi_tingwu_api(mp3_url)
            task_status.loc[index, 'asr_status'] = TaskStatus.ONGOING
            task_status.loc[index, 'status'] = TaskStatus.ASR_PROCESSING
            task_status.loc[index, 'progress'] = 0.5
            update_table(status_gui, task_status)
                
    all_finish_flag = False
    while not all_finish_flag:
        all_finish_flag = True
        for index, task in task_status.iterrows():
            print(task)
            if task['asr_status'] == TaskStatus.ONGOING:
                print(task)
                task_status.loc[index, 'status'] = TaskStatus.ASR_PROCESSING
                task_status.loc[index, 'progress'] = 0.6
                all_finish_flag = False
                response = tongyi_asr_handle.query_tingwu_task(task['task_id'])
                task_status.loc[index, 'asr_status'] = response['Data']['TaskStatus']
                if task_status.loc[index, 'asr_status'] == TaskStatus.COMPLETED:
                    # 调用dify工作流
                    task_status.loc[index, 'status'] = TaskStatus.DIFY_PROCESSING
                    task_status.loc[index, 'progress'] = 0.8
                    mp3_url = f"https:/{bucket_name}.{endpoint}/audio/{Path(task['audio_file']).name}"
                    # 支持同步上传多个任务到dify
                    # TODO 上传后完成状态未更新
                    thread = threading.Thread(target=run_dify_video_understand_workflow, args=(response['Data']['Result']['Transcription'], task['task_id'], mp3_url, task['sourceName']) )
                    thread.start()
                    task_status.loc[index, 'status'] = TaskStatus.READY
                    task_status.loc[index, 'progress'] = 1
                update_table(status_gui, task_status)
        time.sleep(10)
    if all_finish_flag:
        st.link_button("跳转到飞书", url="lark://")
main_page()