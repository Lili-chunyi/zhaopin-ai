# 🤖 AI 招聘助理

> 基于大模型的智能简历匹配与岗位推荐系统

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 项目简介

AI 招聘助理是一款面向候选人的智能求职辅助工具，通过解析候选人的简历，自动分析与岗位的匹配度，并提供针对性的优化建议。

### 核心功能

- 📄 **简历解析** - 支持 PDF、Word 格式简历自动提取关键信息
- 🎯 **智能匹配** - 基于技能、经验、加分项等多维度进行岗位匹配度计算
- 📊 **结果展示** - 直观展示匹配度评分、优势分析、待提升项
- 💡 **优化建议** - 针对缺失技能提供具体的学习和项目建议
- 🎁 **加分项识别** - 自动识别 GitHub 链接、Demo 链接、AIGC 经验等加分项

## 🛠️ 技术栈

- **前端框架**: [Streamlit](https://streamlit.io/) - 快速构建数据应用
- **后端语言**: Python 3.9+
- **简历解析**: PyMuPDF (PDF), python-docx (Word)
- **文本匹配**: jieba (中文分词) + Jaccard 相似度算法
- **数据存储**: JSON 格式岗位数据

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd zhaopinai
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
streamlit run main.py --server.port 8501
```

### 5. 访问应用

打开浏览器访问: http://localhost:8501

## 📁 项目结构

```
zhaopinai/
├── main.py              # Streamlit 主应用
├── matcher.py           # 简历与岗位匹配算法
├── resume_parser.py     # 简历解析模块
├── jd_loader.py         # 岗位数据加载
├── jds.json             # 岗位描述数据
├── requirements.txt    # Python 依赖
└── .streamlit/
    └── config.toml     # Streamlit 配置
```

## 📊 匹配算法说明

匹配度计算采用多维度加权算法：

1. **文本相似度 (25%)** - 使用 jieba 分词 + Jaccard 相似度
2. **技能匹配 (50%)** - 简历技能与岗位要求技能的匹配程度
3. **经验匹配 (25%)** - 工作年限与岗位要求的匹配程度
4. **加分项 (最高 20%)** - GitHub 链接、AIGC 经验、IM 经验等

## 🔧 配置说明

### 岗位数据 (jds.json)

岗位数据存储在 `jds.json` 文件中，格式如下：

```json
{
  "id": 1,
  "position_name": "AI-Native 工程师（iOS方向）",
  "department": "技术部",
  "responsibilities": ["核心工作职责描述"],
  "requirements": {
    "skills": ["Swift", "iOS", "Core ML"],
    "experience": "3年以上",
    "education": "本科及以上",
    "hard_requirements": ["提交Demo链接"]
  }
}
```

### Streamlit 配置

可在 `.streamlit/config.toml` 中修改：

- 服务端口
- 主题设置
- 页面布局等

## 📝 使用流程

1. **选择岗位** - 在左侧边栏点击查看岗位详情
2. **上传简历** - 上传 PDF 或 Word 格式简历
3. **开始匹配** - 点击"提交，开始匹配"按钮
4. **查看结果** - 查看整体匹配度、优势、待提升项
5. **优化建议** - 根据建议优化简历或调整投递方向

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 自由使用、修改和分发
