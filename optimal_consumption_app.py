import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimal Consumption Tool", layout="centered")

# -------------------------------------------------------------
# INTRO: plain text + separate LaTeX blocks (robust)
# -------------------------------------------------------------
st.header("Optimal Consumption Tool")

st.write(
    "This teaching tool illustrates optimal consumer choice under a budget "
    "constraint for three utility types. Use the sidebar to set the budget M, "
    "prices pₓ and pᵧ, select a utility form and parameters α and β, then "
    "click **Compute optimum** to update the diagram."
)

st.subheader("Utility forms (definitions)")
# Use st.latex for the math — safe and avoids escaping issues
st.latex(r"U(x,y) = \alpha x + \beta y")          # Linear (perfect substitutes)
st.latex(r"U(x,y) = \min(\alpha x,\; \beta y)")  # Leontief (perfect complements)
st.latex(r"U(x,y) = x^{\alpha} y^{\beta}")       # Cobb–Douglas

# -------------------------------------------------------------
# SIDEBAR — USER INPUT (use Unicode in labels, avoid backslashes)
# -------------------------------------------------------------
st.sidebar.header("User Input")

M = st.sidebar.number_input("Budget M", min_value=0.01, value=10.0, step=0.5, format="%.2f")
p_x = st.sidebar.number_input("Price pₓ", min_value=0.01, value=1.0, step=0.1, format="%.2f")
p_y = st.sidebar.number_input("Price pᵧ", min_value=0.01, value=1.0, step=0.1, format="%.2f")

utility_type = st.sidebar.selectbox("Utility function",
                                    ("Linear (perfect substitutes)",
                                     "Leontief (perfect complements)",
                                     "Cobb–Douglas"))

alpha = st.sidebar.number_input("α", min_value=0.01, value=0.5, step=0.05, format="%.3f")
beta = st.sidebar.number_input("β", min_value=0.01, value=0.5, step=0.05, format="%.3f")

compute = st.sidebar.button("Compute optimum")

# -------------------------------------------------------------
# Helper solvers
# -------------------------------------------------------------
def cobb_douglas_opt(px, py, M, α, β):
    x = α / (α + β) * M / px
    y = β / (α + β) * M / py
    U = (x ** α) * (y ** β)
    return x, y, U

def leontief_opt(px, py, M, α, β):
    k = α / β
    x = M / (px + py * k)
    y = k * x
    U = min(α * x, β * y)
    return x, y, U

def linear_opt(px, py, M, α, β):
    slope_IC = α / β
    slope_BL = px / py
    # tolerance for numeric equality
    tol = 1e-9
    if abs(slope_IC - slope_BL) < tol:
        # all budget-line points optimal
        U_any = α * (M / px)  # equals β * (M / py)
        # return a midpoint for plotting convenience
        x_plot = (M / px) / 2
        y_plot = (M / py) / 2
        return x_plot, y_plot, U_any, "many"
    elif slope_IC > slope_BL:
        x = M / px
        y = 0.0
        U = α * x
        return x, y, U, "corner_x"
    else:
        x = 0.0
        y = M / py
        U = β * y
        return x, y, U, "corner_y"

# -------------------------------------------------------------
# Plotting function (keeps plotting logic in one place)
# -------------------------------------------------------------
def plot_budget_and_ic(M, px, py, utility_type, alpha, beta, x_star, y_star, U_star, status_flag):
    x_max = M / px
    y_max = M / py

    fig, ax = plt.subplots(figsize=(6, 6))

    # Budget line
    x_vals = np.linspace(0, x_max, 400)
    budget_y = (M - px * x_vals) / py
    ax.plot(x_vals, budget_y, color="black", label="Budget line")

    # Indifference curve depending on utility_type
    if utility_type.startswith("Linear"):
        # For "many" we still draw the representative indifference curve across budget line
        y_ic = (U_star - alpha * x_vals) / beta
        mask = (y_ic >= 0) & (y_ic <= y_max)
        ax.plot(x_vals[mask], y_ic[mask], color="green", linewidth=2, label=f"IC (U={U_star:.2f})")

    elif utility_type.startswith("Leontief"):
        x_corner = U_star / alpha
        y_corner = U_star / beta
        # horizontal to the right
        ax.plot([x_corner, x_max], [y_corner, y_corner], color="green", linewidth=2, label=f"IC (U={U_star:.2f})")
        # vertical upward
        ax.plot([x_corner, x_corner], [y_corner, y_max], color="green", linewidth=2)

    else:  # Cobb–Douglas
        xs = np.linspace(max(1e-6, x_max * 0.01), x_max, 400)
        ys = (U_star / (xs ** alpha)) ** (1 / beta)
        mask = (ys >= 0) & (ys <= y_max)
        ax.plot(xs[mask], ys[mask], color="green", linewidth=2, label=f"IC (U={U_star:.2f})")

    # Optimal point: only if it is a single point (not the "many" case)
    if status_flag != "many":
        ax.scatter([x_star], [y_star], color="red", zorder=5, label="Optimal bundle")
        ax.text(x_star, y_star, f"  ({x_star:.2f}, {y_star:.2f})", verticalalignment="bottom", fontsize=9)

    ax.set_xlim(0, x_max * 1.05)
    ax.set_ylim(0, y_max * 1.05)
    ax.set_xlabel("Quantity of x")
    ax.set_ylabel("Quantity of y")
    ax.grid(alpha=0.3)
    ax.legend()

    st.pyplot(fig)


# -------------------------------------------------------------
# Main compute/display logic
# -------------------------------------------------------------
if compute:
    if utility_type.startswith("Cobb"):
        x_star, y_star, U_star = cobb_douglas_opt(p_x, p_y, M, alpha, beta)
        status = "single"
        plot_budget_and_ic(M, p_x, p_y, utility_type, alpha, beta, x_star, y_star, U_star, status)

        st.subheader("Optimal choice (Cobb–Douglas)")
        st.latex(rf"x^* = {x_star:.3f}")
        st.latex(rf"y^* = {y_star:.3f}")
        st.latex(rf"U^* = {U_star:.3f}")

    elif utility_type.startswith("Leontief"):
        x_star, y_star, U_star = leontief_opt(p_x, p_y, M, alpha, beta)
        status = "single"
        plot_budget_and_ic(M, p_x, p_y, utility_type, alpha, beta, x_star, y_star, U_star, status)

        st.subheader("Optimal choice (Leontief)")
        st.latex(rf"x^* = {x_star:.3f}")
        st.latex(rf"y^* = {y_star:.3f}")
        st.latex(rf"U^* = {U_star:.3f}")

    else:  # Linear
        x_star, y_star, U_star, status_flag = linear_opt(p_x, p_y, M, alpha, beta)
        # status_flag is one of "corner_x", "corner_y", or "many"
        plot_budget_and_ic(M, p_x, p_y, utility_type, alpha, beta, x_star, y_star, U_star, status_flag)

        st.subheader("Optimal choice (Linear)")

        if status_flag == "many":
            # use st.markdown + st.latex combo for robust math rendering
            st.markdown(
                "Because the marginal rate of substitution equals the price ratio, the consumer is "
                "indifferent among all bundles on the budget line."
            )
            st.latex(r"\frac{\alpha}{\beta} = \frac{p_x}{p_y}")
            st.markdown("**Every point on the budget constraint is optimal.**")
            # Show numeric maximum utility
            st.latex(rf"U^* = {U_star:.3f}")
        else:
            st.latex(rf"x^* = {x_star:.3f}")
            st.latex(rf"y^* = {y_star:.3f}")
            st.latex(rf"U^* = {U_star:.3f}")
