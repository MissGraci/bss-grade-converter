import math
import streamlit as st

st.set_page_config(page_title="BSS | IB–PASB Grade Converter", page_icon="📚", layout="centered")

# Based exclusively on the user-provided Brazilian Social Studies
# May 2026, Timezone 2, Standard Level boundary screenshot.
# Higher Level boundaries and final component weightings were not supplied.
BOUNDARIES = {
    "Paper 1": [(0, 5, 1), (6, 11, 2), (12, 17, 3),
                (18, 22, 4), (23, 26, 5), (27, 31, 6), (32, 40, 7)],
    "Paper 2": [(0, 5, 1), (6, 10, 2), (11, 14, 3),
                (15, 18, 4), (19, 21, 5), (22, 25, 6), (26, 30, 7)],
    "Internal Assessment": [(0, 4, 1), (5, 8, 2), (9, 11, 3),
                            (12, 14, 4), (15, 18, 5), (19, 22, 6), (23, 28, 7)],
    "Final Grade": [(0, 15, 1), (16, 30, 2), (31, 43, 3),
                    (44, 56, 4), (57, 67, 5), (68, 80, 6), (81, 100, 7)],
}
MAX_MARKS = {"Paper 1": 40, "Paper 2": 30, "Internal Assessment": 28, "Final Grade": 100}
# The supplied PASB slide places Grade 1 at 0–50 and Grade 2 at 50–59.
# Show those published bands as-is, even though they overlap at 50.
PASB_BANDS = {1: (0, 50), 2: (50, 59), 3: (60, 69),
              4: (70, 79), 5: (80, 89), 6: (90, 95), 7: (96, 100)}


def round_half_up(value):
    return math.floor(value + 0.5)


def lookup_grade(component, mark):
    for low, high, grade in BOUNDARIES[component]:
        if low <= mark <= high:
            return grade, low, high
    raise ValueError("No corresponding boundary was found.")


def convert_pasb(mark, grade, low, high):
    """A school-use interpolation policy, not a method specified in the PASB slide."""
    pasb_low, pasb_high = PASB_BANDS[grade]
    fraction = (mark - low) / (high - low) if high > low else 0
    result = pasb_low + max(0, min(1, fraction)) * (pasb_high - pasb_low)
    return result


def report(component, percentage, equivalent_mark, boundary_mark):
    grade, low, high = lookup_grade(component, boundary_mark)
    pasb = convert_pasb(boundary_mark, grade, low, high)
    lo_pasb, hi_pasb = PASB_BANDS[grade]
    st.divider()
    st.subheader("Conversion result")
    a, b, c = st.columns(3)
    a.metric("Raw percentage", f"{percentage:.2f}%")
    b.metric("IB grade", str(grade))
    c.metric("PASB mark", str(round_half_up(pasb)))
    st.markdown(
        f"**Equivalent component mark:** {equivalent_mark:.2f}/{MAX_MARKS[component]}  \n"
        f"**Whole mark used for boundary:** {boundary_mark}/{MAX_MARKS[component]}  \n"
        f"**BSS boundary:** {low}–{high}  \n"
        f"**PASB grade band:** {lo_pasb}–{hi_pasb}  \n"
        f"**Interpolated PASB mark:** {pasb:.2f}"
    )
    st.caption(
        "The precise mark within a PASB band is calculated using linear interpolation. "
        "The supplied PASB chart specifies bands, not a required interpolation rule."
    )


st.markdown("""
<style>
.block-container { max-width: 850px; padding-top: 2rem; }
.bss-hero {
    background: linear-gradient(120deg, #152b44, #254f72);
    padding: 30px 34px; border-radius: 20px; margin-bottom: 22px;
    color: #fff !important;
}
.bss-hero .eyebrow { font-size: .76rem; font-weight: 750; letter-spacing: .13em; color: #c4e3ef !important; }
.bss-hero .heading { font-size: clamp(1.75rem, 4vw, 2.5rem); font-weight: 750; line-height: 1.16; margin: 12px 0; color: #fff !important; }
.bss-hero .desc { color: #e1edf4 !important; line-height: 1.55; }
.bss-tag { display: inline-block; margin: 13px 8px 0 0; padding: 5px 11px; border: 1px solid #7695af; background: #ffffff1a; border-radius: 20px; font-size: .76rem; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# HTML deliberately starts at the beginning of lines, avoiding Markdown code blocks.
st.markdown("""
<div class="bss-hero">
<div class="eyebrow">PASB · SOCIAL STUDIES · ASSESSMENT TOOL</div>
<div class="heading">Brazilian Social Studies<br>Grade Converter</div>
<div class="desc">Convert BSS assessment marks to an IB grade and a PASB percentage equivalent.</div>
<span class="bss-tag">Standard Level</span>
<span class="bss-tag">May 2026 · TZ2</span>
<span class="bss-tag">IB → PASB</span>
</div>
""", unsafe_allow_html=True)

st.info(
    "**Boundary source:** BSS SL, May 2026 TZ2 table provided by the teacher. "
    "HL boundaries are not available in the supplied reference. "
    "Final-grade weighting is not supplied, so the final-grade mode accepts an already-weighted overall percentage."
)

mode = st.radio("Calculation mode", ["Single assessment", "Overall final grade"], horizontal=True)

if mode == "Single assessment":
    component = st.selectbox("BSS component", ["Paper 1", "Paper 2", "Internal Assessment"])
    st.caption(f"Reference maximum: {MAX_MARKS[component]} marks")
    c1, c2 = st.columns(2)
    with c1:
        scored = st.number_input("Student's marks", min_value=0.0, step=0.5, value=0.0)
    with c2:
        possible = st.number_input("Total possible marks", min_value=0.5, step=0.5, value=float(MAX_MARKS[component]))
    if st.button("Calculate conversion", type="primary", use_container_width=True):
        if scored > possible:
            st.error("Student marks cannot exceed total possible marks.")
        else:
            percentage = 100 * scored / possible
            equivalent = MAX_MARKS[component] * scored / possible
            boundary_mark = min(MAX_MARKS[component], round_half_up(equivalent))
            report(component, percentage, equivalent, boundary_mark)
else:
    st.caption("Enter the final weighted course percentage (0–100). The source screenshot does not specify component weightings.")
    percentage = st.number_input("Overall weighted percentage", min_value=0.0, max_value=100.0, step=0.5, value=0.0)
    if st.button("Calculate final conversion", type="primary", use_container_width=True):
        boundary_mark = min(100, round_half_up(percentage))
        report("Final Grade", percentage, percentage, boundary_mark)

with st.expander("View BSS reference boundaries"):
    rows = []
    for grade in range(7, 0, -1):
        def grade_band(component):
            low, high, _ = next(item for item in BOUNDARIES[component] if item[2] == grade)
            return f"{low}–{high}"
        rows.append({"IB grade": grade,
                     "Paper 1 (/40)": grade_band("Paper 1"),
                     "Paper 2 (/30)": grade_band("Paper 2"),
                     "IA (/28)": grade_band("Internal Assessment"),
                     "Final (%)": grade_band("Final Grade"),
                     "PASB (%)": f"{PASB_BANDS[grade][0]}–{PASB_BANDS[grade][1]}"})
    st.dataframe(rows, hide_index=True, use_container_width=True)

st.caption("PASB band for IB 1 is shown as 0–50, matching the supplied school chart; it overlaps IB 2 at 50. The IB grade is determined first, so this ambiguity does not affect grade classification.")
