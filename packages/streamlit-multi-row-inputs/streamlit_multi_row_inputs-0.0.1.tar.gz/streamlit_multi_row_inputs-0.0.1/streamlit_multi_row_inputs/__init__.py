import os
from enum import IntEnum
from typing import Any, List

import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_multi_row_inputs",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_multi_row_inputs", path=build_dir)

# --------------------------------------------
# Actual Code

class InputType(IntEnum):
    SHORT_TEXT = 0
    LONG_TEXT = 1
    DATE = 2
    TIME = 3
    DATETIME = 4

def multi_row_inputs(label, input_types: IntEnum, line_num=1, default_list: List[List[Any]]=None, key=None):
    """Create a new instance of "multi_row_inputs".

    Parameters
    ----------
    label: str
        The name of the instantiated component.
    
    input_types: IntEnum
        List of types of each column.
        Currently, textarea, date, and time type are supported.

    default_list: List[List[Any]]
        List of default values.
        Values should be sorted as same order as `input_types`.

    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    List[List]
        List of inputs

    """
    component_value = _component_func(label=label, input_types=input_types, line_num=line_num, key=key, default=default_list)

    return component_value

# --------------------------------------------

if not _RELEASE:
    import streamlit as st

    st.subheader("Multi String Component")
    num_clicks = multi_row_inputs("wow", [
            {"type": InputType.LONG_TEXT, "label": "Event", "weight": 2, "line": 0},
            {"type": InputType.SHORT_TEXT, "label": "Location", "weight": 1, "line": 0},
            {"type": InputType.DATETIME, "label": "From", "weight": 1, "line": 1},
            {"type": InputType.DATETIME, "label": "To", "weight": 1, "line": 2}
        ], line_num=3, default_list=[["Free time", "Del pino resort", "2022-07-30", "2022-07-30"]], key="foo")
    
    for i in num_clicks:
        st.write(i)
