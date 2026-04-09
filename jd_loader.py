import json
import os

class JDLoader:
    def __init__(self, jd_file='jds.json'):
        self.jd_file = jd_file
        self.jds = []
        self.load_jds()

    def load_jds(self):
        """从 JSON 文件加载 JD 数据"""
        if os.path.exists(self.jd_file):
            try:
                with open(self.jd_file, 'r', encoding='utf-8') as f:
                    self.jds = json.load(f)
            except Exception as e:
                print(f"加载 JD 数据失败: {str(e)}")
                self.jds = []
        else:
            print(f"JD 文件 {self.jd_file} 不存在")
            self.jds = []

    def get_all_jds(self):
        """获取所有岗位 JD"""
        return self.jds

    def get_jd_by_id(self, jd_id):
        """根据 ID 获取岗位 JD"""
        for jd in self.jds:
            if jd.get('id') == jd_id:
                return jd
        return None

    def get_jd_by_position(self, position_name):
        """根据岗位名称获取 JD"""
        for jd in self.jds:
            if jd.get('position_name') == position_name:
                return jd
        return None

    def add_jd(self, jd):
        """添加新的岗位 JD"""
        # 生成新的 ID
        if self.jds:
            max_id = max([jd.get('id', 0) for jd in self.jds])
            jd['id'] = max_id + 1
        else:
            jd['id'] = 1
        
        self.jds.append(jd)
        self.save_jds()
        return jd

    def update_jd(self, jd_id, updated_jd):
        """更新岗位 JD"""
        for i, jd in enumerate(self.jds):
            if jd.get('id') == jd_id:
                self.jds[i].update(updated_jd)
                self.save_jds()
                return True
        return False

    def delete_jd(self, jd_id):
        """删除岗位 JD"""
        self.jds = [jd for jd in self.jds if jd.get('id') != jd_id]
        self.save_jds()
        return True

    def save_jds(self):
        """保存 JD 数据到 JSON 文件"""
        try:
            with open(self.jd_file, 'w', encoding='utf-8') as f:
                json.dump(self.jds, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存 JD 数据失败: {str(e)}")
            return False

    def search_jds(self, keyword):
        """根据关键词搜索岗位 JD"""
        results = []
        keyword = keyword.lower()
        
        for jd in self.jds:
            # 搜索岗位名称、部门、职责和要求
            if (
                keyword in jd.get('position_name', '').lower() or
                keyword in jd.get('department', '').lower() or
                any(keyword in resp.lower() for resp in jd.get('responsibilities', [])) or
                any(keyword in req.lower() for req in jd.get('requirements', {}).get('skills', [])) or
                keyword in jd.get('requirements', {}).get('experience', '').lower() or
                keyword in jd.get('requirements', {}).get('education', '').lower()
            ):
                results.append(jd)
        
        return results