## TokenUp
你的多模态AI助手，让生活更轻松。

WIP...正在开发中
[项目看板](https://trello.com/b/Icuef1ga/)
> from 2024 funder park ai hackathon.
to maybe future.

https://github.com/imchenmin/tokenup/assets/20356658/f2fabb62-c0a4-4103-bb90-bab95c51843f

## 使用
### 运行方法：终端运行（Windows，MacOS）
1. 下载项目
   ```
   git clone https://github.com/imchenmin/tokenup.git
   cd tokenup
   ```
2. 安装依赖文件
   ```
   pip install -r requirements.txt
   ```
4. 设置配置文件：.secret_template.toml，将其重命名为.secret.toml
   具体步骤详见[配置文件介绍](docs/配置文件介绍.md)
5. 设置dify工作流
6. 设置moonshot api
7. 设置阿里云 api
8. 设置飞书机器人
9. 运行
   ```bash
   streamlit run main.py
   ```

## 特性列表
1. [x] AI视频总结（基于通义听悟+moonshot 128k llm）
2. [ ] 播客总结（支持网页链接，通过提取audio标签实现下载）
3. [ ] 内建多模态知识库

## 开发
项目技术栈：Streamlit + DIFY + MoonShot API + 飞书 + 通义听悟
