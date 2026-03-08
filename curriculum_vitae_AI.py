#!/usr/bin/env python3
"""
智能简历分析Agent系统
"""
import streamlit as st
from openai import OpenAI
import io
from PyPDF2 import PdfReader
from docx import Document


# 配置信息
API_BASE_URL = "https://api.siliconflow.cn/v1"
TARGET_POSITIONS = ["机械工程师", "机械工艺工程师", "结构工程师", "前端开发工程师", "Python开发工程师", "产品经理", "数据分析师", "UI/UX设计师"]

def extract_file_content(uploaded_file):
    """提取上传文件的内容"""
    if not uploaded_file:
        return None
    
    file_name = uploaded_file.name.lower()
    
    if file_name.endswith('.txt'):
        file_content = uploaded_file.read()
        return file_content.decode('utf-8')
    
    elif file_name.endswith('.pdf'):
        try:
            pdf_reader = PdfReader(uploaded_file)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            return text_content.strip()
        except Exception as e:
            return f"[PDF文件读取错误: {str(e)}]"
    
    elif file_name.endswith('.docx'):
        try:
            doc = Document(uploaded_file)
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            return text_content.strip()
        except Exception as e:
            return f"[Word文件读取错误: {str(e)}]"
    
    else:
        return "[文件内容] - 演示模式下显示文件已上传"

def get_resume_content(uploaded_file, resume_text):
    """获取简历内容（文件或文本输入）"""
    if uploaded_file:
        return extract_file_content(uploaded_file)
    elif resume_text:
        return resume_text
    else:
        return None




def analyze_resume_with_ai(resume_text, target_position, api_key):
    """使用AI分析简历"""
    if not api_key or api_key.strip() == "":
        return "💡 **请先配置API密钥**\n\n请在左侧侧边栏输入您的硅基流动API密钥以获得真实的AI分析结果。\n\n配置后，AI将智能分析简历内容，给出个性化的评分和改进建议。"
    
    client = OpenAI(api_key=api_key, base_url=API_BASE_URL)
    prompt = f"""
    作为专业HR顾问，请分析以下简历，针对"{target_position}"岗位进行评估。
    
    简历内容：{resume_text}
    
    请提供：1.总体评分（0-100分） 2.详细分析和改进建议 3.核心优势和发展建议
    要求：评分和建议完全基于简历内容，个性化分析，避免模板化回复。
    """
    
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {"role": "system", "content": "你是专业的HR顾问，根据简历内容给出客观、个性化的分析和建议。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

def handle_analysis_click(uploaded_file, resume_text, target_position, api_key):
    """处理分析按钮点击事件"""
    content = get_resume_content(uploaded_file, resume_text)
    if not content:
        st.warning("⚠️ 请先上传简历文件或输入简历内容")
        return
    
    with st.spinner("🤖 AI正在分析您的简历，请稍候..."):
        analysis_result = analyze_resume_with_ai(content, target_position, api_key)
        st.session_state.analysis_result = analysis_result
        st.session_state.target_position = target_position
    
    st.success("✅ 分析完成！请查看右侧分析结果。")
    return True

def main():
    st.set_page_config(page_title="智能简历分析Agent", page_icon="📄", layout="wide")
    
    # 初始化session_state
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## 📄 智能简历分析Agent")
        
        # API密钥输入
        st.markdown("### 🔑 API配置")
        api_key = st.text_input(
            "硅基流动API密钥",
            type="password",
            placeholder="请输入您的API密钥",
            help="在硅基流动官网获取API密钥"
        )
        
        if api_key:
            st.success("✅ API密钥已配置")
        else:
            st.warning("⚠️ 请输入API密钥以使用AI分析功能")
        
        st.markdown("### 🎯 系统功能")
        st.markdown("- 📤 简历上传分析\n- 🤖 AI智能评分\n- 💡 个性化建议\n- 🚀 职业规划指导")
    
    st.title("🤖 智能简历分析Agent系统")
    st.markdown("**基于AI的专业简历分析与职业指导平台**")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 简历上传")
        
        # 目标岗位选择
        target_position = st.selectbox(
            "🎯 选择目标岗位",
            TARGET_POSITIONS,
            help="选择您要应聘的岗位类型"
        )
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "📄 上传简历文件",
            type=['txt', 'pdf', 'docx'],
            help="支持TXT、PDF、DOCX格式文件"
        )
        
        # 文本输入作为备选
        st.markdown("**或者直接输入简历内容：**")
        resume_text = st.text_area(
            "简历内容",
            height=200,
            placeholder="请粘贴您的简历内容..."
        )
        
        # 分析按钮
        if st.button("🚀 开始AI分析", type="primary", use_container_width=True):
            handle_analysis_click(uploaded_file, resume_text, target_position, api_key)
    
    with col2:
        st.markdown("### 📊 分析结果")
        
        if st.session_state.analysis_result:
            # 显示分析结果
            st.markdown(f"**目标岗位：** {st.session_state.get('target_position', '未选择')}")
            
            # 分析结果展示
            with st.container():
                st.markdown(st.session_state.analysis_result)
            
            # 操作按钮
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📋 复制结果", use_container_width=True):
                    st.info("💡 请手动复制上方分析结果")
            
            with col_b:
                if st.button("🔄 重新分析", use_container_width=True):
                    st.session_state.analysis_result = None
                    st.rerun()
        
        else:
            # 显示功能介绍
            st.info("""
            ### 🤖 AI智能分析
            
            **系统特色：**
            - 🎯 个性化分析：AI根据简历内容智能评估
            - 📊 智能评分：0-100分客观评分系统
            - 💡 针对性建议：基于岗位要求的改进指导
            - 🚀 职业规划：专业的发展路径建议
            
            **使用说明：** 选择岗位 → 上传简历 → 开始分析 → 查看结果
            """)
    


if __name__ == "__main__":
    main()