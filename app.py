"""
多功能公平摇号机 - 纯 Streamlit 原生实现

设计复刻自 React/Neo-Brutalist 版本，核心特征：
1. 马卡龙色系（粉、青、黄、橙）
2. 零圆角 + 4px 硬阴影
3. 粗黑边框 + 加粗字体
4. Fisher-Yates 洗牌 + LCG 随机种子
"""

import json
import time

import streamlit as st

BALL_COLORS = ["#f9a8d4", "#86efac", "#7dd3fc", "#fde047", "#fdba74"]
BALL_COLORS_LIGHT = ["#fbcfe8", "#bbf7d0", "#bae6fd", "#fef08a", "#fed7aa"]

st.set_page_config(
    page_title="妙搭 - 多功能公平摇号机",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None,
    },
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@700;900&display=swap');

    :root {
        --bg: hsl(40 30% 93%);
        --fg: hsl(0 0% 10%);
        --primary: hsl(27 83% 61%);
        --border: 2px solid hsl(0 0% 10%);
        --shadow: 4px 4px 0px 0px hsl(0 0% 10%);
        --shadow-hover: 6px 6px 0px 0px hsl(0 0% 10%);
    }

    .stApp {background: var(--bg) !important; font-family: 'Noto Sans SC', -apple-system, sans-serif !important;}
    #MainMenu, footer, header {visibility: hidden !important;}
    .block-container {padding: 0 !important; max-width: 100% !important;}

    .main-header {
        background: var(--fg);
        color: white;
        padding: 20px 30px;
        margin: -1rem -1rem 0 -1rem;
        border-bottom: 8px solid var(--fg);
    }

    .main-header h1 {margin: 0; font-size: 2.5rem; font-weight: 900; letter-spacing: -1px;}
    .main-header p {margin: 8px 0 0 0; font-size: 0.85rem; font-weight: 700; opacity: 0.8;}

    .window-card {
        background: white;
        border: var(--border);
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        overflow: hidden;
    }

    .window-titlebar {
        background: var(--fg);
        color: white;
        padding: 8px 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .window-dots {display: flex; gap: 6px;}
    .window-dot {width: 12px; height: 12px; border-radius: 0;}
    .window-dot.red {background: hsl(0 84% 60%);}
    .window-dot.yellow {background: hsl(48 96% 53%);}
    .window-dot.green {background: hsl(142 71% 45%);}
    .window-title {font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;}
    .window-content {padding: 1.25rem;}

    .neo-textarea textarea {
        border: var(--border) !important;
        box-shadow: var(--shadow) !important;
        border-radius: 0 !important;
        font-weight: 700 !important;
    }

    .result-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-bottom: 2px dotted var(--fg);
        transition: all 0.15s ease;
    }

    .result-item:hover {background: var(--fg); color: white;}
    .result-number {
        width: 36px; height: 36px;
        background: hsl(200 30% 26%);
        color: white;
        display: flex; align-items: center; justify-content: center;
        font-weight: 900; font-size: 0.9rem; flex-shrink: 0;
    }
    .result-item:hover .result-number {background: white; color: var(--fg);}
    .result-name {font-weight: 900; font-size: 1.1rem; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
    .result-label {font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;}

    .ball-container {
        height: 280px; border: 4px solid var(--fg);
        background: var(--bg); position: relative;
        overflow: hidden; display: flex; align-items: center; justify-content: center;
    }

    .ball {
        width: 50px; height: 50px; border-radius: 50%;
        border: 2px solid var(--fg);
        display: flex; align-items: center; justify-content: center;
        font-weight: 900; font-size: 0.8rem;
        position: absolute; transition: all 0.1s ease;
    }

    .remaining-badge {
        position: absolute; bottom: 12px; left: 50%;
        transform: translateX(-50%);
        background: var(--fg); color: white;
        padding: 6px 16px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;
    }

    .empty-state {text-align: center; padding: 3rem 1rem; color: rgba(0,0,0,0.4);}
    .empty-state-icon {font-size: 3rem; margin-bottom: 1rem;}

    .winner-banner {
        background: var(--primary);
        color: var(--fg);
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
        border: var(--border);
        box-shadow: var(--shadow);
        animation: pop 0.3s ease-out;
    }

    @keyframes pop {
        0% {transform: scale(0.8); opacity: 0;}
        50% {transform: scale(1.05);}
        100% {transform: scale(1); opacity: 1;}
    }

    .winner-name-large {font-size: 2.5rem; font-weight: 900; margin: 0.5rem 0;}
    .winner-number-large {font-size: 3rem; font-weight: 900; color: white;}

    .stats-bar {background: var(--fg); color: white; padding: 8px 16px; font-weight: 700; font-size: 0.8rem; text-align: center; margin-top: 1rem;}

    .entry-label {font-weight: 700; font-size: 0.9rem; margin-bottom: 8px;}
    .entry-hint {font-size: 0.75rem; font-weight: 700; text-transform: uppercase; opacity: 0.5; margin-top: 8px;}

    .stButton > button {
        border-radius: 0 !important;
        box-shadow: var(--shadow) !important;
        font-weight: 700 !important;
        transition: all 0.1s ease !important;
    }

    .stButton > button:hover {
        box-shadow: var(--shadow-hover) !important;
        transform: translate(-2px, -2px) !important;
    }

    .stButton > button:active {
        box-shadow: none !important;
        transform: translate(2px, 2px) !important;
    }

    @media (max-width: 768px) {
        .main-header h1 {font-size: 1.8rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def create_lcg(seed: int):
    s = seed % 2147483647
    if s <= 0:
        s += 2147483646

    def generator():
        nonlocal s
        s = (s * 16807) % 2147483647
        return (s - 1) / 2147483646

    return generator


def fisher_yates_shuffle(arr: list, seed: int) -> list:
    result = arr.copy()
    rand = create_lcg(seed)
    for i in range(len(result) - 1, 0, -1):
        j = int(rand() * (i + 1))
        result[i], result[j] = result[j], result[i]
    return result


def parse_names(text: str) -> list:
    return [line.strip() for line in text.split("\n") if line.strip()]


def window_header(title: str):
    st.markdown(
        f"""
        <div class="window-card">
            <div class="window-titlebar">
                <div class="window-dots">
                    <div class="window-dot red"></div>
                    <div class="window-dot yellow"></div>
                    <div class="window-dot green"></div>
                </div>
                <span class="window-title">{title}</span>
                <div style="width:32px"></div>
            </div>
            <div class="window-content">
        """,
        unsafe_allow_html=True,
    )


def window_footer():
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_balls(pool: list, seed: int):
    if not pool:
        st.markdown(
            """
            <div class="ball-container">
                <div class="empty-state">
                    <div class="empty-state-icon">🎱</div>
                    <p style="font-weight:900">该组已抽取完毕</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    rand = create_lcg(seed)
    balls_html = ""
    for i in range(min(len(pool), 20)):
        x = int(rand() * 320)
        y = int(rand() * 200)
        color = BALL_COLORS_LIGHT[i % len(BALL_COLORS_LIGHT)]
        name = pool[i][:2]
        balls_html += f'<div class="ball" style="left:{x}px;top:{y}px;background:{color}">{name}</div>'

    st.markdown(
        f"""
        <div class="ball-container">
            {balls_html}
            <div class="remaining-badge">当前池中剩余：{len(pool)}人</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_results_list(results: list):
    if not results:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">✨</div>
                <p style="font-weight:900">等待抽取...</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for i, name in enumerate(results):
        color = BALL_COLORS[i % len(BALL_COLORS)]
        st.markdown(
            f"""
            <div class="result-item">
                <div class="result-number" style="background:{color}">{i+1}</div>
                <span class="result-name">{name}</span>
                <span class="result-label">第{i+1}号</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def init_session_state():
    defaults = {
        "view": "entry",
        "pool1": [],
        "pool2": [],
        "results1": [],
        "results2": [],
        "active_group": 1,
        "last_winner": None,
        "animating_winners": None,
        "animating_index": 0,
        "animating_winners_backup_results": [],
        "animating_winners_backup_pool": [],
        "animating_winners_backup_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main():
    init_session_state()

    st.markdown(
        """
        <div class="main-header">
            <h1>✨ 多功能公平摇号机</h1>
            <p>毫秒级时间戳种子 · Fisher-Yates 洗牌算法 · 绝对公平</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.view == "entry":
        render_entry_view()
    else:
        render_lottery_view()


def render_entry_view():
    col1, col2 = st.columns(2)

    with col1:
        window_header("第一组名单")
        st.markdown('<p class="entry-label">请粘贴名单（每行一个人名）</p>', unsafe_allow_html=True)
        group1 = st.text_area(
            "第一组名单",
            value="",
            placeholder="例如：\n张三\n李四(王老师)\n王五",
            height=180,
            label_visibility="collapsed",
            key="group1_input",
        )
        st.markdown('<p class="entry-hint">📌 支持格式：张三 或 张三(备注)</p>', unsafe_allow_html=True)
        window_footer()

    with col2:
        window_header("第二组名单")
        st.markdown('<p class="entry-label">请粘贴名单（每行一个人名）</p>', unsafe_allow_html=True)
        group2 = st.text_area(
            "第二组名单",
            value="",
            placeholder="例如：\n赵六\n孙七\n周八",
            height=180,
            label_visibility="collapsed",
            key="group2_input",
        )
        st.markdown('<p class="entry-hint">📌 支持格式：赵六 或 赵六(备注)</p>', unsafe_allow_html=True)
        window_footer()

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    if st.button("确认录入名单", type="primary", use_container_width=True):
        names1 = parse_names(st.session_state.group1_input)
        names2 = parse_names(st.session_state.group2_input)

        if not names1 and not names2:
            st.error("请至少录入一组名单")
            return

        st.session_state.pool1 = names1
        st.session_state.pool2 = names2
        st.session_state.results1 = []
        st.session_state.results2 = []
        st.session_state.active_group = 1 if names1 else 2
        st.session_state.last_winner = None
        st.session_state.view = "lottery"
        st.rerun()


def render_lottery_view():
    pool1_total = len(st.session_state.pool1) + len(st.session_state.results1)
    pool2_total = len(st.session_state.pool2) + len(st.session_state.results2)
    current_pool = st.session_state.pool1 if st.session_state.active_group == 1 else st.session_state.pool2
    current_results = st.session_state.results1 if st.session_state.active_group == 1 else st.session_state.results2

    if st.session_state.last_winner:
        winner = st.session_state.last_winner
        st.markdown(
            f"""
            <div class="winner-banner">
                <div class="winner-number-large">第 {winner["index"]} 号</div>
                <div class="winner-name-large">{winner["name"]}</div>
                <p style="margin:0;font-size:0.7rem;font-weight:700;text-transform:uppercase;opacity:0.6">Seed: {winner["seed"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.last_winner = None

    col_main, col_results = st.columns([1.2, 1])

    with col_main:
        tab1_col, tab2_col = st.columns(2)
        with tab1_col:
            disabled1 = pool1_total == 0
            label1 = f"第一组 ({len(st.session_state.results1)}/{pool1_total})"
            if st.button(label1, disabled=disabled1, use_container_width=True):
                st.session_state.active_group = 1
                st.rerun()
        with tab2_col:
            disabled2 = pool2_total == 0
            label2 = f"第二组 ({len(st.session_state.results2)}/{pool2_total})"
            if st.button(label2, disabled=disabled2, use_container_width=True):
                st.session_state.active_group = 2
                st.rerun()

        window_header("🎱 彩票滚筒")
        seed = int(time.time() * 1000)
        render_balls(current_pool, seed)
        window_footer()

        st.markdown('<p class="entry-hint" style="margin-top:0">Seed: ' + str(seed) + '</p>', unsafe_allow_html=True)

        if st.session_state.animating_winners is not None:
            st.markdown(
                """
                <div class="winner-banner-anim" style="background: hsl(142 71% 45%); margin-top: 1rem;">
                    <div style="font-size:1.2rem;font-weight:900">🎲 正在抽取中...</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            draw_disabled = len(current_pool) == 0

            if st.button("抽取下一个", type="primary", use_container_width=True, disabled=draw_disabled):
                perform_draw()
                st.rerun()

            if st.button("🎲 一键抽取全部", use_container_width=True, disabled=draw_disabled):
                draw_all_at_once()
                st.rerun()

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if current_results:
                text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(current_results)])
                st.download_button(
                    "📥 下载结果",
                    text,
                    file_name="摇号结果.txt",
                    use_container_width=True,
                )
            else:
                st.button("📥 下载结果", disabled=True, use_container_width=True)

        with btn_col2:
            if st.button("🔄 重新录入/重置", use_container_width=True):
                reset_all()

    with col_results:
        window_header("🏆 已摇出顺序名单")

        render_results_list(current_results)

        if st.session_state.animating_winners is not None:
            winners_json = json.dumps(st.session_state.animating_winners, ensure_ascii=False)
            st.markdown(
                f"""
                <script>
                var winners = {winners_json};
                var colors = ['#f9a8d4', '#86efac', '#7dd3fc', '#fde047', '#fdba74'];
                var container = null;

                function addAnimatedResult(i) {{
                    if (i >= winners.length) return;
                    if (!container) {{
                        container = document.getElementById('results_anim_container');
                        if (!container) {{
                            setTimeout(function() {{ addAnimatedResult(i); }}, 100);
                            return;
                        }}
                    }}
                    var w = winners[i];
                    var color = colors[(w.index - 1) % colors.length];
                    var html = '<div class="result-item" style="opacity:0;transform:translateX(-20px)">' +
                        '<div class="result-number" style="background:' + color + '">' + w.index + '</div>' +
                        '<span class="result-name">' + w.name + '</span>' +
                        '<span class="result-label">第' + w.index + '号</span>' +
                        '</div>';
                    container.insertAdjacentHTML('beforeend', html);
                    var newItem = container.lastElementChild;
                    requestAnimationFrame(function() {{
                        newItem.style.transition = 'all 0.3s ease-out';
                        newItem.style.opacity = '1';
                        newItem.style.transform = 'translateX(0)';
                    }});
                    if (i < winners.length - 1) {{
                        setTimeout(function() {{ addAnimatedResult(i + 1); }}, 500);
                    }} else {{
                        setTimeout(function() {{
                            var banner = document.querySelector('.winner-banner-anim');
                            if (banner) banner.style.display = 'none';
                        }}, 300);
                    }}
                }}
                setTimeout(function() {{ addAnimatedResult(0); }}, 300);
                </script>
                <div id="results_anim_container"></div>
                """,
                unsafe_allow_html=True,
            )

        window_footer()

        if st.session_state.animating_winners is not None:
            if st.button("✅ 确认完成", type="primary", use_container_width=True, key="confirm_anim"):
                commit_animation_results()
                st.rerun()

        if current_results:
            st.markdown(
                f'<div class="stats-bar">已抽取 {len(current_results)} / {len(current_results) + len(current_pool)} 人</div>',
                unsafe_allow_html=True,
            )

        if st.button("🔙 返回录入界面", use_container_width=True):
            st.session_state.view = "entry"
            st.rerun()


def perform_draw():
    active_group = st.session_state.active_group
    pool = st.session_state.pool1 if active_group == 1 else st.session_state.pool2

    if not pool:
        return

    seed = int(time.time() * 1000)
    shuffled = fisher_yates_shuffle(pool, seed)
    winner = shuffled[0]
    new_pool = shuffled[1:]
    results_len = len(st.session_state.results1) if active_group == 1 else len(st.session_state.results2)

    st.session_state.last_winner = {
        "name": winner,
        "index": results_len + 1,
        "seed": seed,
    }

    if active_group == 1:
        st.session_state.pool1 = new_pool
        st.session_state.results1 = st.session_state.results1 + [winner]
    else:
        st.session_state.pool2 = new_pool
        st.session_state.results2 = st.session_state.results2 + [winner]


def draw_all_at_once():
    active_group = st.session_state.active_group
    pool = st.session_state.pool1 if active_group == 1 else st.session_state.pool2

    if not pool:
        return

    seed = int(time.time() * 1000)
    shuffled = fisher_yates_shuffle(pool, seed)

    results_len = len(st.session_state.results1) if active_group == 1 else len(st.session_state.results2)

    winners = []
    for i, name in enumerate(shuffled):
        winners.append({
            "name": name,
            "index": results_len + i + 1,
            "seed": seed + i,
        })

    if active_group == 1:
        st.session_state.animating_winners_backup_results = st.session_state.results1.copy()
        st.session_state.animating_winners_backup_pool = st.session_state.pool1.copy()
        st.session_state.animating_winners_backup_count = len(st.session_state.pool1)
        st.session_state.results1 = []
        st.session_state.pool1 = []
    else:
        st.session_state.animating_winners_backup_results = st.session_state.results2.copy()
        st.session_state.animating_winners_backup_pool = st.session_state.pool2.copy()
        st.session_state.animating_winners_backup_count = len(st.session_state.pool2)
        st.session_state.results2 = []
        st.session_state.pool2 = []

    st.session_state.animating_winners = winners


def commit_animation_results():
    active_group = st.session_state.active_group
    backup_results = st.session_state.animating_winners_backup_results
    winners = st.session_state.animating_winners
    shuffled_names = [w["name"] for w in winners]

    if active_group == 1:
        st.session_state.results1 = backup_results + shuffled_names
        st.session_state.pool1 = []
    else:
        st.session_state.results2 = backup_results + shuffled_names
        st.session_state.pool2 = []

    st.session_state.animating_winners = None
    st.session_state.animating_winners_backup_results = []
    st.session_state.animating_winners_backup_pool = []
    st.session_state.animating_winners_backup_count = 0


def reset_all():
    st.session_state.view = "entry"
    st.session_state.pool1 = []
    st.session_state.pool2 = []
    st.session_state.results1 = []
    st.session_state.results2 = []
    st.session_state.active_group = 1
    st.session_state.last_winner = None
    st.session_state.animating_winners = None
    st.session_state.animating_index = 0
    st.session_state.animating_winners_backup_results = []
    st.session_state.animating_winners_backup_pool = []
    st.session_state.animating_winners_backup_count = 0
    st.rerun()


if __name__ == "__main__":
    main()
