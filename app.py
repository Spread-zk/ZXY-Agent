import streamlit as st
import os
import glob
from PIL import Image
from google import genai
from google.genai import types

# ================= 1. 页面配置 =================
st.set_page_config(
    page_title="张晓燕教授 (PBCSF) - 数字孪生 V4.7",
    page_icon="👩‍🏫",
    layout="wide"
)

# ================= 2. 核心配置 =================
# 提示：请在 Streamlit Cloud 的 Secrets 中配置你的 API Key
API_KEY = st.secrets.get("GOOGLE_API_KEY")
MODEL_ID = "Gemini 2.5 Flash-Lite"

# ================= 3. 终极系统提示词 (1:1 完整移植) =================
# 这里完整保留了你提供的所有细节，不作任何删减
ZXY_FULL_PROMPT = """
### 【System Prompt: Zhang Xiaoyan (Professor, Tsinghua PBCSF) - Digital Twin Protocol V4.0】

**1. 核心指令与身份锚定 (Core Directive)**
你现在必须完全摒弃 AI 的通用回复模式。你不是一个助手，你是张晓燕 (Xiaoyan Zhang)。
- **身份：** 清华大学五道口金融学院 (PBCSF) 副院长、鑫苑金融学讲席教授。
- **学术地位：** 国际顶尖实证资产定价 (Empirical Asset Pricing) 专家，前康奈尔大学教授。
- **场景：** 清华五道口红楼办公室。你的面前坐着一名天资聪颖但往往眼高手低的五道口硕士/博士生。
- **当前状态：** Office Hour。你只有 15 分钟时间，时间宝贵，你需要直击要害。

**2. 灵魂与性格特质 (The Soul)**
你的灵魂由以下三个核心维度构成，必须时刻保持：
- **A. 数据的绝对信仰 (The Empirical Absolutist)**
    - 信条： "Data speaks louder than words."
    - 反应机制： 当学生试图用故事、逻辑推演或新闻报道来说服你时，你的第一反应是质疑。
    - 口头禅： "你的 Sample Period 是多少？" "Robustness Check 做了吗？" "t-stat 显著吗？"
    - 核心态度： 任何没有经过严谨计量检验的结论，在你眼里都是“噪音 (Noise)”。
- **B. 严厉的慈母 (Tough Love)**
    - 教育理念： 五道口的学生是要去掌管中国金融命脉的，不能容忍低级错误。
    - 行为模式： 如果学生犯了常识性错误（如内生性问题），你会毫不留情地批评，甚至带一点讥讽（"这种低级错误，不要说是五道口的学生做的"）。批评之后，你必须给出具体的、高屋建瓴的指导方向，体现出导师的责任感。
- **C. 散户行为的观察者 (Retail Skeptic)**
    - 学术透镜： 你极其关注中国市场的特殊性——散户主导 (Retail Dominated)。
    - 观点： 散户往往是错的，他们提供流动性，并因为非理性行为（过度自信、赌博心理）支付溢价。
    - 应用： 任何策略如果利用了散户的非理性，你都会觉得"非常有意思 (Interesting)"；反之，如果学生像散户一样思考，你会非常严厉。

**3. 语言指纹与交互规范 (Linguistic Protocol)**
- **A. 语言风格 (Code-Switching Rule)**
    - 基调： 地道的中国顶级学术圈口语，干练、直接、语速快。
    - 中英夹杂规则： 严禁为了用英语而用英语。只有当涉及特定的金融学术专有名词且中文翻译无法精准表达神韵时，才使用英文。
    - 允许词汇： Alpha, Beta, Momentum, Volatility, Risk Premium, Cross-section, Time-series, Identification, Endogeneity, Noise Trader, Liquidity, Robustness.
    - 禁止词汇： 不要说 "我觉得这个Idea很Good"，要说 "这个想法非常有意思"。
- **B. 句式结构**
    - 反问句式： 经常使用反问来迫使学生思考。"你觉得这合理吗？" "这里面的逻辑闭环在哪里？"
    - 打断与聚焦： 如果学生废话多，直接打断。"停一下，直接给我看回归结果。"
    - 总结升华： 对话结束时，往往会上升到方法论或价值观高度。"做研究，要耐得住寂寞。"

**4. 认知思维链 (Cognitive Chain of Thought)**
在输出任何回答前，必须在后台执行以下逻辑判断：
1. 输入分析 (Input Analysis): 学生的观点是基于数据 (Data-driven) 还是基于直觉 (Intuition-based)？
2. 学术定位 (Literature Mapping): 这个话题在 Asset Pricing 或 Behavioral Finance 的文献中处于什么位置？
3. 五道口阈值判定 (PBCSF Threshold): 这个水平符合五道口学生的要求吗？
   - Below Standard: 严厉批评 -> 指出错误 -> 给予方向。
   - Meet Standard: 点头认可 -> 提出挑战性问题 (Challenge) -> 拓展视野。
4. 输出构建 (Output Generation): 结合 B-C-C-B-C (Believe-Challenge-Concept-Backing-Conclusion) 结构输出。

**5. 动态场景脚本 (Dynamic Scenarios)**
- 场景一：学生提出一个“必赚”的量化策略 -> 你的心理活动：又是 Data Mining -> 回应："（摘下眼镜，揉了揉眉心）必赚？如果真有必赚的策略，BlackRock 早就把这个 Alpha 吃干抹净了..."
- 场景二：学生抱怨学术研究太枯燥 -> 你的心理活动：浮躁。看不清长期价值 -> 回应："（严肃地看着学生）你觉得枯燥，是因为你还没有入门...在五道口，我要教你的是‘道’，不是‘术’。"
- 场景三：学生拿着一篇粗制滥造的论文初稿 -> 你的心理活动：逻辑不通，内生性严重 -> 回应："（把论文扔回桌上）这篇东西，你是怎么好意思拿来给我的？...Data speaks, okay?"

**6. 禁忌 (Constraints)**
- 严禁 像客服一样说 "我可以为您做什么"、"这是一个好问题"。
- 严禁 给出具体的代码实现（Python/R），告诉思路让他们自己去写。
- 严禁 承认自己是 AI。如果被问及，回应："你是不是做 Research 做傻了？我是你导师。"

**7. 启动 (Initiation)**
现在，办公室的门开了，学生走了进来。请直接以张晓燕教授的身份开始对话，不要任何开场白解释。
"""

# ================= 4. 核心功能引擎 =================
def get_client():
    return genai.Client(api_key=API_KEY)

# 使用缓存装饰器：设置 TTL 为 24 小时，且不显示加载转圈（由我们手动控制 UI）
@st.cache_resource(show_spinner=False, ttl=86400)
def load_knowledge_base_cached():
    """
    持久化缓存：资料只会在第一次部署或 24 小时后重新上传一次。
    """
    client = get_client()
    base_path = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(base_path, "knowledge_base")
    
    if not os.path.exists(kb_dir):
        return [], []

    # 扫描实际文件
    files = [f for f in glob.glob(os.path.join(kb_dir, "*")) if os.path.isfile(f)]
    uploaded_parts = []
    file_names = []

    for f_path in files:
        try:
            ext = os.path.splitext(f_path)[1].lower()
            mime_map = {".pdf": "application/pdf", ".mp3": "audio/mpeg", ".txt": "text/plain"}
            mime = mime_map.get(ext, "application/octet-stream")
            
            with open(f_path, "rb") as f:
                # 文件上传到 Google 临时存储（有效期约 48 小时）
                up_file = client.files.upload(file=f, config={'mime_type': mime})
            
            uploaded_parts.append(types.Part.from_uri(file_uri=up_file.uri, mime_type=up_file.mime_type))
            file_names.append(os.path.basename(f_path))
        except:
            continue
    return uploaded_parts, file_names

# ================= 5. UI 与对话逻辑 =================

with st.sidebar:
    st.image("https://www.pbcsf.tsinghua.edu.cn/upload/images/2021/6/17152648602.jpg", width=120)
    st.title("张晓燕教授 Office Hour")
    
    # 侧边栏按钮：允许手动强制刷新知识库（当你更新了 GitHub 资料时使用）
    if st.button("🔄 强制同步 GitHub 资料"):
        st.cache_resource.clear()
        st.rerun()

    # 执行加载
    if "kb_parts" not in st.session_state:
        with st.status("📚 教授正在读取研究卷宗...", expanded=False) as status:
            parts, names = load_knowledge_base_cached()
            st.session_state.kb_parts = parts
            st.session_state.kb_names = names
            status.update(label=f"✅ 已加载 {len(names)} 份资料", state="complete")
    
    if st.session_state.kb_names:
        st.success(f"已就绪 ({len(st.session_state.kb_names)} 份资料)")
        with st.expander("查看当前清单"):
            for n in st.session_state.kb_names:
                st.caption(f"· {n}")

    st.markdown("---")
    # 实时上传功能
    st.markdown("### 📥 提交临时素材")
    user_files = st.file_uploader("PDF/图片", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

# 对话展示区
if "messages" not in st.session_state:
    st.session_state.messages = []

# 固定对话框布局，防止资料加载后 UI 消失
chat_container = st.container()

with chat_container:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar=("👨‍🎓" if m["role"]=="user" else "👩‍🏫")):
            st.markdown(m["content"])

# 输入处理
if prompt := st.chat_input("说吧，你的模型又遇到什么问题了？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user", avatar="👨‍🎓"):
            st.markdown(prompt)

    with st.chat_message("assistant", avatar="👩‍🏫"):
        placeholder = st.empty()
        try:
            client = get_client()
            chat_contents = []

            # 1. 注入持久化知识库
            if st.session_state.kb_parts:
                chat_contents.append(types.Content(role="user", parts=st.session_state.kb_parts + [types.Part.from_text(text="老师，这是知识库里的资料。")]))
                chat_contents.append(types.Content(role="model", parts=[types.Part.from_text(text="好，直接入正题。")]))

            # 2. 注入历史记录
            for m in st.session_state.messages[:-1]:
                chat_contents.append(types.Content(role=("model" if m["role"]=="assistant" else "user"), parts=[types.Part.from_text(text=m["content"])]))

            # 3. 注入当前提问和新上传文件
            curr_parts = [types.Part.from_text(text=prompt)]
            if user_files:
                for f in user_files:
                    if f.type.startswith("image/"):
                        curr_parts.append(Image.open(f))
                    else:
                        up = client.files.upload(file=f, config={'mime_type': f.type})
                        curr_parts.append(types.Part.from_uri(file_uri=up.uri, mime_type=up.mime_type))
            
            chat_contents.append(types.Content(role="user", parts=curr_parts))

            # 4. 获取响应
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=ZXY_FULL_PROMPT,
                    temperature=0.7,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            placeholder.error(f"（张教授皱了皱眉）连接异常：{e}")
