import os
import re

class ResumeParser:
    def __init__(self):
        pass

    def parse(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在")

        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        error_msg = ""

        if ext == '.pdf':
            text, error_msg = self._parse_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            text, error_msg = self._parse_word(file_path)
        elif ext in ['.jpg', '.jpeg', '.png']:
            text, error_msg = self._parse_image_simple(file_path)
        else:
            raise ValueError(f"不支持: {ext}")

        if not text or not text.strip():
            raise ValueError(error_msg or "无法提取文本")

        info = self._extract_info(text)
        info['raw_text'] = text
        return info

    def _parse_pdf(self, file_path):
        try:
            import fitz
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
            doc.close()
            if text.strip():
                return text, ""
        except:
            pass

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                if b'%PDF' in content[:100]:
                    import io
                    try:
                        from pypdf import PdfReader
                        reader = PdfReader(io.BytesIO(content))
                        text = "\n".join([p.extract_text() or "" for p in reader.pages])
                        if text.strip():
                            return text, ""
                    except:
                        pass
        except:
            pass

        return "", "PDF解析失败"

    def _parse_word(self, file_path):
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text, ""
        except Exception as e:
            return "", f"Word错误: {str(e)[:30]}"

    def _parse_image_simple(self, file_path):
        return "", "图片需要OCR，请转换为PDF或Word格式上传"

    def _extract_info(self, text):
        return {
            'name': self._extract_name(text),
            'contact': self._extract_contact(text),
            'education': [],
            'work_experience': [],
            'skills': self._extract_skills(text),
            'certificates': []
        }

    def _extract_name(self, text):
        for p in [r'姓名[：:]\s*([\u4e00-\u9fa5]{2,4})', r'([\u4e00-\u9fa5]{2,4})(?:先生|女士)']:
            m = re.search(p, text)
            if m:
                return m.group(1).strip()
        for line in text.split('\n')[:5]:
            line = line.strip()
            if 2 <= len(line) <= 4 and re.match(r'^[\u4e00-\u9fa5]+$', line):
                return line
        return "未知"

    def _extract_contact(self, text):
        c = {}
        m = re.search(r'1[3-9]\d{9}', text)
        if m: c['phone'] = m.group(0)
        m = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
        if m: c['email'] = m.group(0)
        return c

    def _extract_skills(self, text):
        kw = ['Java', 'Python', 'C++', 'JavaScript', 'Swift', 'iOS', 'Android', 'Django', 'MySQL', 'Redis', 'MongoDB', 'Docker', 'Kubernetes', 'React', 'Vue', 'Angular', 'Spring Boot', 'Flask', 'FastAPI', 'LangChain', 'AI', 'LLM', '机器学习', '深度学习', 'TensorFlow', 'PyTorch', 'Linux', 'Git']
        skills = []
        tl = text.lower()
        for k in kw:
            if k.lower() in tl:
                skills.append(k)
        return list(set(skills))
