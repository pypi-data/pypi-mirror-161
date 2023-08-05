import streamlit as st

from pollination_streamlit_viewer import viewer


col1, col2 = st.columns(2)

with col1:
    viewer("lala",
        sidebar=False,
        style={
            "height": "320px"
        }
    )

with col2:
    viewer("foo",
    sidebar=False,
    style={
            "height": "320px"
        }
    )


col3, col4 = st.columns(2)

with col3:
    viewer("bar",
        sidebar=False,
        style={
                "height": "320px"
            }
    )

with col4:
    viewer("baz",
        sidebar=False,
        style={
                "height": "320px"
            }
    )