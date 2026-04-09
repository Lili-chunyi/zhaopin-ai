import streamlit as st
import os

st.markdown("""
<style>
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .card-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .advantage-item {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .improve-item {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .bonus-item {
        background-color: #cce5ff;
        border-left: 4px solid #007bff;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .step-header {
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 10px 0;
    }
    .stSidebar {
        width: 33% !important;
    }
    [data-testid="stSidebar"] {
        width: 33% !important;
    }
</style>
""", unsafe_allow_html=True)

def render_jd_detail(jd):
    st.markdown(f"### {jd['position_name']}")
    st.markdown(f"**部门:** {jd['department']}")
    st.markdown("---")
    st.markdown("#### 核心工作")
    for resp in jd.get('responsibilities', []):
        st.write(f"• {resp}")
    st.markdown("---")
    st.markdown("#### 任职要求")
    reqs = jd.get('requirements', {})
    if reqs.get('skills'):
        st.write(f"**技能:** {', '.join(reqs['skills'])}")
    if reqs.get('experience'):
        st.write(f"**经验:** {reqs['experience']}")
    if reqs.get('education'):
        st.write(f"**学历:** {reqs['education']}")

def get_match_rating(percentage):
    if percentage >= 80:
        return "非常匹配！您的背景与岗位高度契合", "🎉"
    elif percentage >= 60:
        return "比较匹配，有不错的竞争力", "👍"
    elif percentage >= 40:
        return "有一定基础，但关键技能还需补充", "💪"
    elif percentage >= 30:
        return "需要加强，建议针对性提升", "📚"
    else:
        return "建议调整投递方向或优化简历", "🔍"

def render_match_step1(overall, rating, emoji, jd_name=None):
    st.markdown(f"""
    <div class="card">
        <div class="card-header">📊 第一步：整体匹配度</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(overall / 100)
    with col2:
        st.markdown(f"### {overall}%")
    st.markdown(f"### {emoji} {rating}")
    
    if overall >= 30 and jd_name:
        st.success(f"🎯 **推荐岗位：{jd_name}**")

def render_match_step2(best_match, resume_info):
    matched_skills = best_match.get('matched_skills', [])
    experience_details = best_match.get('experience_details', [])
    hard_details = best_match.get('hard_details', [])
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">✅ 第二步：您的优势</div>
    </div>
    """, unsafe_allow_html=True)
    
    has_advantage = False
    
    if matched_skills:
        has_advantage = True
        for skill in matched_skills:
            st.markdown(f"<div class='advantage-item'>✓ {skill} - 简历中已具备该技能</div>", unsafe_allow_html=True)
    
    if experience_details:
        has_advantage = True
        for exp in experience_details:
            st.markdown(f"<div class='advantage-item'>📈 {exp}</div>", unsafe_allow_html=True)
    
    if hard_details:
        has_advantage = True
        for detail in hard_details:
            st.markdown(f"<div class='advantage-item'>⭐ {detail}</div>", unsafe_allow_html=True)
    
    if not has_advantage:
        st.info("暂无明显优势，建议查看待提升项")

def render_match_step3(best_match, jd_data):
    missing_skills = best_match.get('missing_skills', [])
    common_details = best_match.get('common_details', [])
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">⚠️ 第三步：待提升</div>
    </div>
    """, unsafe_allow_html=True)
    
    has_missing = False
    
    if missing_skills:
        has_missing = True
        for skill in missing_skills[:5]:
            tip = get_improve_tip(skill, jd_data)
            st.markdown(f"<div class='improve-item'>❌ 缺少 {skill}<br><small>{tip}</small></div>", unsafe_allow_html=True)
        if len(missing_skills) > 5:
            st.write(f"...还有 {len(missing_skills) - 5} 项技能")
    
    if common_details:
        for detail in common_details:
            tip = get_common_tip(detail)
            st.markdown(f"<div class='improve-item'>❌ {detail}<br><small>{tip}</small></div>", unsafe_allow_html=True)
    
    if not has_missing:
        st.success("太棒了！您已满足该岗位的所有要求！")

def render_bonus_section(best_match):
    hard_details = best_match.get('hard_details', [])
    common_details = best_match.get('common_details', [])
    all_bonus = hard_details + common_details
    
    if not all_bonus:
        return
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">★ 加分项</div>
    </div>
    """, unsafe_allow_html=True)
    
    for detail in all_bonus:
        st.markdown(f"<div class='bonus-item'>★ {detail}</div>", unsafe_allow_html=True)

def render_match_reason(best_match, jd_data, resume_info):
    matched = best_match.get('matched_skills', [])
    missing = best_match.get('missing_skills', [])
    overall = round(best_match['overall_match'] * 100, 1)
    
    lines = []
    
    if matched:
        skill_text = "、".join(matched[:3])
        lines.append(f"您有 {skill_text} 经验，与{jd_data['position_name']}岗位匹配")
    
    if missing:
        skill_text = "、".join(missing[:3])
        lines.append(f"但还缺少 {skill_text} 技能")
    
    exp_details = best_match.get('experience_details', [])
    if exp_details:
        lines.append(exp_details[0])
    
    if overall < 30:
        lines.append("")
        lines.append("**投递建议**:")
        lines.append("• 建议先投递与您当前技能更匹配的岗位")
        lines.append("• 可以突出团队管理或项目统筹能力")
        lines.append("• 建议在简历中添加 GitHub 或项目演示链接")
    
    return "，".join(lines) if lines else ""

def render_no_match_result(result, resume_info, jds, matcher):
    st.markdown("---")
    st.subheader("😅 暂未找到完全匹配的岗位")
    st.write("以下是为您分析的结果：")
    
    st.markdown("### 📊 整体评估")
    st.info("您的简历与现有岗位的匹配度均低于30%，但仍有亮点可以发挥")
    
    from matcher import Matcher
    m = Matcher()
    all_matches = m.match_resume_to_jds(resume_info, jds)
    
    if all_matches:
        best = all_matches[0]
        matched = best.get('matched_skills', [])
        if matched:
            st.markdown("### ✅ 您的优势")
            for skill in matched:
                st.markdown(f"<div class='advantage-item'>✓ {skill}</div>", unsafe_allow_html=True)
        
        missing = best.get('missing_skills', [])
        if missing:
            st.markdown("### ⚠️ 待提升")
            for skill in missing[:5]:
                st.markdown(f"<div class='improve-item'>❌ 缺少 {skill}</div>", unsafe_allow_html=True)
    
    st.markdown("### 💡 其他岗位方向建议")
    st.write("根据您的技能，以下岗位可能适合您：")
    
    skills = resume_info.get('skills', [])
    raw_text = resume_info.get('raw_text', '').lower()
    
    suggestions = []
    for jd in jds:
        jd_skills = jd.get('requirements', {}).get('skills', [])
        matched = [s for s in jd_skills if s.lower() in [x.lower() for x in skills] or s.lower() in raw_text]
        if matched:
            suggestions.append((jd, len(matched)))
    
    suggestions.sort(key=lambda x: x[1], reverse=True)
    
    for jd, score in suggestions[:3]:
        st.write(f"• **{jd['position_name']}** (匹配 {score} 个技能)")
        with st.expander(f"查看{jd['position_name']}详情"):
            render_jd_detail(jd)
    
    st.markdown("### 💡 简历优化建议")
    st.write("• 完善项目经验描述，突出与目标岗位相关的技能")
    st.write("• 添加 GitHub 仓库或 Demo 项目链接")
    st.write("• 完善教育背景和工作经历")

def get_improve_tip(skill, jd_data):
    tips = {
        'Swift': '可以尝试做一个 SwiftUI 小项目并上传到 GitHub',
        'Core ML': '学习苹果官方 Core ML 文档，尝试集成一个图像识别模型',
        'iOS': '深入理解 iOS 系统架构，积累项目经验',
        'Python': '完成 Django 或 Flask 项目实战',
        'Java': '深入理解 Spring Boot 框架',
        'Docker': '学习容器化部署，完成 Docker Compose 项目',
        'Kubernetes': '了解 K8s 基础概念和部署流程',
        'React': '完成 React 全栈项目，包含Hooks和状态管理',
        'Vue': '学习 Vue3 组合式API，完成项目实战',
        'MySQL': '深入理解索引、事务和优化技巧',
        'Redis': '学习缓存策略和分布式锁应用',
        'AI': '学习 LangChain 或 LangFlow 框架',
        'LLM': '了解提示工程和模型微调基础',
        '机器学习': '完成 Kaggle 入门竞赛项目',
        '深度学习': '学习 PyTorch 并完成图像或NLP项目',
    }
    return tips.get(skill, f'建议学习 {skill} 相关项目经验')

def get_common_tip(detail):
    tips = {
        'GitHub 链接': '可以在简历中添加您的 GitHub 个人主页链接',
        'Demo/项目链接': '建议制作一个项目演示Demo并提供链接',
        '国考/行测成绩': '如果考试成绩不错，可以在简历中注明',
    }
    return tips.get(detail, '建议补充该材料')

def load_jds():
    import json
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    jd_path = os.path.join(base_dir, 'jds.json')
    if os.path.exists(jd_path):
        with open(jd_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def run():
    st.set_page_config(layout="wide", page_title="AI招聘助理")

    if 'selected_job_id' not in st.session_state:
        st.session_state.selected_job_id = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'uploaded_name' not in st.session_state:
        st.session_state.uploaded_name = None
    if 'resume_info' not in st.session_state:
        st.session_state.resume_info = None
    if 'match_result' not in st.session_state:
        st.session_state.match_result = None
    if 'jds' not in st.session_state:
        st.session_state.jds = load_jds()
        if st.session_state.jds:
            st.session_state.selected_job_id = st.session_state.jds[0]['id']

    jds = st.session_state.jds

    with st.sidebar:
        st.markdown("### 📋 岗位列表")
        st.caption("点击岗位名称查看 JD 详情")
        for idx, jd in enumerate(jds):
            is_selected = st.session_state.selected_job_id == jd['id']
            btn_label = f"✅ {jd['position_name']}" if is_selected else jd['position_name']
            if st.button(btn_label, key=f"btn_{jd['id']}"):
                st.session_state.selected_job_id = jd['id']
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### 📝 岗位详情")
        selected_jd = next((jd for jd in jds if jd['id'] == st.session_state.selected_job_id), None)
        if selected_jd:
            with st.container():
                render_jd_detail(selected_jd)

    col1, col2 = st.columns([33, 67])

    with col1:
        st.markdown("### 👋 欢迎使用 AI 招聘助理")
        st.caption("上传简历，自动为您匹配合适岗位")
        
        st.markdown("#### 📝 简历上传")
        uploaded_file = st.file_uploader("选择简历文件", type=["pdf", "docx", "doc"], key="file_uploader")
        
        col_upload, col_clear = st.columns([3, 1])
        with col_upload:
            if uploaded_file is not None:
                st.session_state.uploaded_data = uploaded_file.getvalue()
                st.session_state.uploaded_name = uploaded_file.name
        
        with col_clear:
            if st.session_state.uploaded_data:
                if st.button("🗑️ 清空", key="clear_btn"):
                    st.session_state.uploaded_data = None
                    st.session_state.uploaded_name = None
                    st.session_state.resume_info = None
                    st.session_state.match_result = None
                    st.rerun()

        if st.session_state.uploaded_data:
            size_mb = len(st.session_state.uploaded_data) / (1024 * 1024)
            st.success(f"✅ 已选择：{st.session_state.uploaded_name} ({size_mb:.2f} MB)")
        
        st.markdown("---")
        
        if st.button("✅ 提交，开始匹配", type="primary", key="match_button"):
            if not st.session_state.uploaded_data:
                st.warning("请先上传简历")
            else:
                with st.spinner("正在解析简历并匹配岗位..."):
                    try:
                        suffix = os.path.splitext(st.session_state.uploaded_name)[1].lower()
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(st.session_state.uploaded_data)
                            temp_path = tmp.name

                        from resume_parser import ResumeParser
                        parser = ResumeParser()
                        resume_info = parser.parse(temp_path)

                        try:
                            os.remove(temp_path)
                        except:
                            pass

                        st.session_state.resume_info = resume_info
                        
                        from matcher import Matcher
                        matcher = Matcher()
                        best_match, result = matcher.get_best_match(resume_info, jds)
                        
                        st.session_state.match_result = (best_match, result)
                        
                    except Exception as e:
                        st.error(f"解析简历时出错：{str(e)}")

    with col2:
        if not st.session_state.uploaded_data:
            st.info("👈 请先在左侧上传简历文件")
            st.markdown("""
            ### 📌 使用说明
            1. 在左侧上传您的简历（支持 PDF、Word 格式）
            2. 点击"提交，开始匹配"按钮
            3. 查看匹配结果，了解优势和待提升项
            4. 根据建议优化简历或调整投递方向
            """)
        else:
            if st.session_state.resume_info:
                resume_info = st.session_state.resume_info
                best_match, result = st.session_state.match_result
                
                st.markdown("### 📄 简历信息")
                resume_col1, resume_col2 = st.columns(2)
                with resume_col1:
                    st.write(f"**姓名:** {resume_info.get('name', '未知')}")
                with resume_col2:
                    contact = resume_info.get('contact', {})
                    if contact.get('phone'):
                        st.write(f"**电话:** {contact.get('phone')}")
                
                skills = resume_info.get('skills', [])
                if skills:
                    st.write(f"**技能:** {', '.join(skills)}")
                
                if best_match:
                    jd_data = best_match['jd']
                    overall = round(best_match['overall_match'] * 100, 1)
                    rating_text, emoji = get_match_rating(overall)
                    
                    st.markdown("---")
                    
                    render_match_step1(overall, rating_text, emoji, jd_data['position_name'])
                    
                    st.markdown("---")
                    
                    render_match_step2(best_match, resume_info)
                    
                    st.markdown("---")
                    
                    render_match_step3(best_match, jd_data)
                    
                    render_bonus_section(best_match)
                    
                    st.markdown("---")
                    
                    with st.expander("📄 查看完整 JD 详情"):
                        render_jd_detail(jd_data)
                    
                    reason = render_match_reason(best_match, jd_data, resume_info)
                    if reason:
                        st.markdown(f"### 💡 匹配解读")
                        st.info(reason)
                else:
                    render_no_match_result(result, resume_info, jds, None)

if __name__ == "__main__":
    run()
