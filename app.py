    import os
    import streamlit as st
    from PIL import Image

    st.set_page_config(page_title='Data Summarizer — Floyd', layout='centered')
    st.title('Data Summarizer — Floyd Steev Santhmayer')
    st.markdown('''
    This demo shows the project scaffold for fetching small samples from PostgreSQL,
    generating concise LLM summaries, and producing follow-up questions.
    ''')

    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    img_path = os.path.join(docs_dir, 'flowchart_colored.png')
    if os.path.exists(img_path):
        st.image(img_path, caption='Processing flowchart (color-coded)', use_column_width=True)
    else:
        st.warning('Flowchart image not found in docs/ — please ensure flowchart_colored.png exists.')

    st.header('Quick links')
    st.markdown('- `flowchart_colored.mmd` — Mermaid source for the flowchart
- `FLOWCHART_DETAILED.md` — Detailed step-by-step explanation')

    st.header('Run locally')
    st.code('''# 1. Copy .env.example to .env and populate
# 2. Install dependencies
pip install -r requirements.txt
# 3. Run Streamlit
streamlit run app.py''', language='bash')
