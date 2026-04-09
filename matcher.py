import re

def calculate_similarity(resume_text, jd_text):
    import jieba
    try:
        resume_words = set(jieba.cut(resume_text.lower()))
        jd_words = set(jieba.cut(jd_text.lower()))

        stopwords = {'的', '是', '在', '了', '和', '与', '或', '等', '及', '有', '无', '为', '以', '及', '其', '之', '于', '中', '上', '下', '内', '外', '能', '可', '会', '能'}
        resume_words = resume_words - stopwords
        jd_words = jd_words - stopwords

        if not jd_words:
            return 0.5

        intersection = len(resume_words & jd_words)
        union = len(resume_words | jd_words)

        if union == 0:
            return 0.0

        return intersection / union
    except:
        return 0.0

def extract_experience_years(text):
    patterns = [
        r'(\d+)\s*年.*经验',
        r'经验\s*(\d+)\s*年',
        r'(\d+)\s*年以上?',
        r'工作\s*(\d+)\s*年',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return 0

class Matcher:
    def __init__(self):
        pass

    def match_resume_to_jds(self, resume_info, jds):
        matches = []

        resume_text = self._build_resume_text(resume_info)
        raw_text = resume_info.get('raw_text', '')
        resume_skills = resume_info.get('skills', [])

        for jd in jds:
            jd_text = self._build_jd_text(jd)
            jd_skills = jd.get('requirements', {}).get('skills', [])

            similarity = calculate_similarity(resume_text, jd_text)

            skill_result = self._calculate_skill_match(
                resume_skills,
                raw_text,
                jd_skills
            )

            experience_result = self._calculate_experience_match(resume_info, jd)

            hard_result = self._calculate_hard_requirement_bonus(raw_text, jd)

            common_result = self._calculate_common_bonus(raw_text)

            skill_score = skill_result['score']
            experience_score = experience_result['score']

            bonus_total = hard_result['bonus'] + common_result['bonus']

            overall_match = (
                similarity * 0.25 +
                skill_score * 0.50 +
                experience_score * 0.25
            )

            if bonus_total > 0:
                overall_match = overall_match * (1 + bonus_total * 0.2)

            overall_match = min(overall_match, 1.0)

            matches.append({
                'jd': jd,
                'similarity': similarity,
                'skill_match': skill_score,
                'experience_match': experience_score,
                'hard_bonus': hard_result['bonus'],
                'common_bonus': common_result['bonus'],
                'overall_match': overall_match,
                'matched_skills': skill_result['matched'],
                'missing_skills': skill_result['missing'],
                'skill_details': skill_result['details'],
                'experience_details': experience_result['details'],
                'hard_details': hard_result['details'],
                'common_details': common_result['details']
            })

        matches.sort(key=lambda x: x['overall_match'], reverse=True)
        return matches

    def _build_resume_text(self, resume_info):
        parts = []
        parts.append(resume_info.get('name', ''))
        for exp in resume_info.get('work_experience', []):
            parts.append(exp.get('company', ''))
            parts.append(exp.get('position', ''))
        for edu in resume_info.get('education', []):
            parts.append(edu.get('degree', ''))
            parts.append(edu.get('school', ''))
        parts.extend(resume_info.get('skills', []))
        parts.extend(resume_info.get('certificates', []))
        parts.append(resume_info.get('raw_text', ''))
        return ' '.join(parts)

    def _build_jd_text(self, jd):
        parts = []
        parts.append(jd.get('position_name', ''))
        parts.append(jd.get('department', ''))
        parts.extend(jd.get('responsibilities', []))
        req = jd.get('requirements', {})
        parts.extend(req.get('skills', []))
        parts.append(req.get('experience', ''))
        parts.append(req.get('education', ''))
        keywords = req.get('keywords', [])
        for kw in keywords:
            parts.extend([kw] * 3)
        return ' '.join(parts)

    def _calculate_skill_match(self, resume_skills, raw_text, jd_skills):
        if not jd_skills:
            return {'score': 1.0, 'matched': [], 'missing': [], 'details': []}

        matched = []
        missing = []
        details = []

        raw_lower = raw_text.lower()
        resume_skills_lower = [s.lower() for s in resume_skills]

        for skill in jd_skills:
            skill_lower = skill.lower()
            is_matched = False

            if skill_lower in resume_skills_lower:
                is_matched = True
            elif skill_lower in raw_lower:
                is_matched = True
            else:
                for rskill in resume_skills_lower:
                    if skill_lower in rskill or rskill in skill_lower:
                        is_matched = True
                        break

            if is_matched:
                matched.append(skill)
                details.append(f"✓ {skill}")
            else:
                missing.append(skill)

        score = len(matched) / len(jd_skills) if jd_skills else 1.0

        return {
            'score': score,
            'matched': matched,
            'missing': missing,
            'details': details
        }

    def _calculate_experience_match(self, resume_info, jd):
        raw_text = resume_info.get('raw_text', '')
        resume_years = extract_experience_years(raw_text)

        jd_exp_text = jd.get('requirements', {}).get('experience', '')
        jd_years = extract_experience_years(jd_exp_text)

        if jd_years == 0:
            return {'score': 1.0, 'details': ['该岗位无明确工作年限要求']}

        if resume_years == 0:
            return {'score': 0.6, 'details': [f'无法确定工作年限，该岗位要求{jd_years}年以上']}

        if resume_years >= jd_years:
            years_diff = resume_years - jd_years
            if years_diff <= 1:
                score = 1.0
                details = [f'工作年限 {resume_years} 年，符合岗位要求 ({jd_years}年以上)']
            elif years_diff <= 3:
                score = 0.95
                details = [f'工作年限 {resume_years} 年，超过岗位要求 ({jd_years}年以上)']
            else:
                score = 0.85
                details = [f'工作年限 {resume_years} 年，明显超过岗位要求']
        else:
            years_diff = jd_years - resume_years
            if years_diff <= 1:
                score = 0.75
                details = [f'工作年限 {resume_years} 年，略低于岗位要求 ({jd_years}年以上)']
            elif years_diff <= 3:
                score = 0.55
                details = [f'工作年限 {resume_years} 年，低于岗位要求 ({jd_years}年以上)']
            else:
                score = 0.30
                details = [f'工作年限 {resume_years} 年，明显低于岗位要求 ({jd_years}年以上)']

        return {'score': min(score, 1.0), 'details': details}

    def _calculate_hard_requirement_bonus(self, raw_text, jd):
        raw_lower = raw_text.lower()
        bonus = 0
        details = []

        if 'github.com' in raw_lower or 'github' in raw_lower:
            bonus += 0.10
            details.append("GitHub 链接")

        if 'demo' in raw_lower or '项目链接' in raw_lower or '作品集' in raw_lower:
            bonus += 0.10
            details.append("Demo/项目链接")

        if '行测' in raw_text or '国考' in raw_text or '公务员考试' in raw_text:
            bonus += 0.05
            details.append("国考/行测成绩")

        return {'bonus': bonus, 'details': details}

    def _calculate_common_bonus(self, raw_text):
        raw_lower = raw_text.lower()
        bonus = 0
        details = []

        aigc_keywords = ['aigc', 'ai生成', '人工智能应用', 'ai产品', '大模型应用', 'chatgpt', 'gpt', '文心一言', '通义千问', 'ai助手']
        if any(kw in raw_lower for kw in aigc_keywords):
            bonus += 0.10
            details.append("AIGC类产品经验")

        im_keywords = ['即时通讯', 'im', '聊天', '消息', 'websocket', 'xmpp', 'mqtt', '实时通讯', '社交', '社群']
        if any(kw in raw_lower for kw in im_keywords):
            bonus += 0.10
            details.append("IM类产品经验")

        tool_app_keywords = ['工具app', '工具类', '效率工具', '工具软件', '工具应用', 'utility app', 'productivity']
        if any(kw in raw_lower for kw in tool_app_keywords):
            bonus += 0.10
            details.append("工具类APP开发经验")

        ai_keywords = ['热爱ai', '机器学习', '深度学习', 'tensorflow', 'pytorch', '神经网络', 'ai技术', '人工智能', 'ml', 'dl', 'ai行业']
        if any(kw in raw_lower for kw in ai_keywords):
            bonus += 0.10
            details.append("了解AI/机器学习/深度学习")

        leadership_keywords = ['带团队', '组建团队', '团队管理', '技术负责人', '技术lead', 'team lead', 'tech lead', '管理经验', '下属', '负责人']
        if any(kw in raw_lower for kw in leadership_keywords):
            bonus += 0.10
            details.append("带团队/组建团队经验")

        return {'bonus': bonus, 'details': details}

    def get_best_match(self, resume_info, jds, threshold=0.3):
        matches = self.match_resume_to_jds(resume_info, jds)

        if not matches:
            return None, "没有找到可匹配的岗位"

        best_match = matches[0]

        if best_match['overall_match'] < threshold:
            suggestions = self._generate_suggestions(resume_info, matches)
            return None, suggestions

        reason = self._generate_reason(best_match)
        return best_match, reason

    def _generate_reason(self, best_match):
        jd = best_match['jd']
        overall = round(best_match['overall_match'] * 100, 1)

        lines = []
        lines.append(f"**{jd['position_name']}** - 匹配度: **{overall}%**")
        lines.append("")

        skill_details = best_match.get('skill_details', [])
        if skill_details:
            lines.append(f"**技能匹配 ({len(best_match.get('matched_skills', []))}/{len(jd.get('requirements', {}).get('skills', []))}):**")
            lines.append('  ' + ', '.join(skill_details))

        exp_details = best_match.get('experience_details', [])
        if exp_details:
            lines.append(f"**经验匹配:** {exp_details[0]}")

        hard_details = best_match.get('hard_details', [])
        common_details = best_match.get('common_details', [])
        all_bonus = hard_details + common_details
        if all_bonus:
            bonus_total = round((best_match.get('hard_bonus', 0) + best_match.get('common_bonus', 0)) * 100)
            lines.append(f"**加分项 (+{bonus_total}%):** {', '.join(all_bonus)}")

        return '\n'.join(lines)

    def _generate_suggestions(self, resume_info, all_matches):
        skills = resume_info.get('skills', [])
        raw_text = resume_info.get('raw_text', '')

        suggestions = []
        suggestions.append("很抱歉，目前没有完全匹配您背景的岗位（匹配度均低于30%）。")

        if skills:
            suggestions.append("\n根据您的技能，建议关注以下方向：")

            skill_category = []

            if any(s.lower() in ['swift', 'objective-c', 'ios', 'core ml', 'mlx', 'swiftui', 'xcode'] for s in skills):
                skill_category.append(("AI-Native 工程师（iOS方向）", "iOS开发 + AI应用集成"))

            if any(s.lower() in ['python', 'django', 'langchain', 'celery', 'postgresql', 'mysql', 'redis'] for s in skills):
                skill_category.append(("AI-Native 工程师（Django方向）", "Python后端 + AI框架"))

            if any(s.lower() in ['android', '逆向', 'frida', '加固', '反编译'] for s in skills):
                skill_category.append(("AI-Native 工程师（Android 反编译方向）", "Android逆向分析"))

            if any(s.lower() in ['llama.cpp', 'mlx', 'mnn', 'tflite', '模型量化', '端侧推理'] for s in skills):
                skill_category.append(("AI-Native 工程师（端侧大模型方向）", "端侧模型部署优化"))

            if any(s.lower() in ['mqtt', 'xmpp', 'websocket', 'sqlite', 'realm', 'im', '即时通讯'] for s in skills):
                skill_category.append(("AI-Native 工程师（IM类方向）", "IM系统 + AI增强"))

            if any(s.lower() in ['产品', '原型', 'ab实验', '数据分析', '用户增长'] for s in skills):
                skill_category.append(("AI-产品工程师", "产品设计 + 全栈开发"))

            if any(s.lower() in ['pytest', 'jest', 'junit', 'appium', '自动化测试', 'tdd'] for s in skills):
                skill_category.append(("AI-TDD 质量工程师", "测试框架 + AI评估"))

            if any(s.lower() in ['交互设计', '原型设计', '用户研究', '热力图', '交互原型'] for s in skills):
                skill_category.append(("AI-产品工程师（交互方向）", "交互设计 + AIGC产品"))

            if skill_category:
                for pos, desc in skill_category:
                    suggestions.append(f"  • **{pos}** - 适合有{desc}经验的候选人")
            else:
                suggestions.append("  • 根据您的技能组合，建议尝试技术类或产品类岗位")

        suggestions.append("\n投递建议：")
        suggestions.append("  1. 完善简历中的项目经验描述，突出与目标岗位相关的技能")
        suggestions.append("  2. 如有GitHub仓库或Demo项目，建议在简历中添加链接")
        suggestions.append("  3. 部分岗位要求提供项目作品，可提前准备")

        return '\n'.join(suggestions)