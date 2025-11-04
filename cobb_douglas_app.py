# cobb_douglas_app.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# st.title("Cobb–Douglas Utility Function: Indifference Curves")
st.markdown(r"Utility function: $U(x, y) = x^{\alpha} y^{\beta}$")

# --- Initialize stored parameters in session_state ---
if "alpha" not in st.session_state:
    st.session_state.alpha = 0.5
if "beta" not in st.session_state:
    st.session_state.beta = 0.5

# --- Input section ---
st.subheader("Set Parameters")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    alpha_input = st.number_input(
        "α (Exponent on X)",
        value=st.session_state.alpha,
        min_value=0.1,
        max_value=2.0,
        step=0.1,
        format="%.2f",
        key="alpha_input"
    )
    with col2:
        beta_input = st.number_input(
        "β (Exponent on Y)",
        value=st.session_state.beta,
        min_value=0.1,
        max_value=2.0,
        step=0.1,
        format="%.2f",
        key="beta_input"
    )
with col3:
    update = st.button("Update Graph")

    # --- Update stored values only when button is pressed ---
if update:
    st.session_state.alpha = alpha_input
    st.session_state.beta = beta_input

# --- Always display graph using stored parameters ---
alpha = st.session_state.alpha
beta = st.session_state.beta

# Compute utility surface
x = np.linspace(0.1, 10, 300)
y = np.linspace(0.1, 10, 300)
X, Y = np.meshgrid(x, y)
U = (X ** alpha) * (Y ** beta)

# Reference points
x_ref = 5
y_refs = np.array([1, 2, 3, 4, 5, 6, 7])
U_levels = (x_ref ** alpha) * (y_refs ** beta)

# Create figure
fig = go.Figure()

# Add one contour line for each utility level
for U_level in U_levels:
    fig.add_trace(go.Contour(
        x=x,
        y=y,
        z=U,
        contours=dict(
            start=U_level,
            end=U_level,
            size=1e-6,
            coloring='none'
        ),
        line=dict(width=2),
        showscale=False,
    ))

    # Add labelled points (5,1)…(5,7)
for y_val, u_val in zip(y_refs, U_levels):
    fig.add_trace(go.Scatter(
        x=[x_ref],
        y=[y_val],
        mode="markers+text",
        text=[f"(5,{int(y_val)}): U={u_val:.2f}"],
        textposition="middle right",
        marker=dict(color="red", size=8)
    ))

fig.update_layout(
    xaxis_title="Good X",
    yaxis_title="Good Y",
    # title=f"Indifference Curves through (5,1)…(5,7)  —  α={alpha:.2f}, β={beta:.2f}",
    width=750,
    height=600,
    showlegend=False
)

st.plotly_chart(fig)