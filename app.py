import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Healthcare No-Show Analysis",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {font-size: 40px; color: #1f2937; text-align: center; font-weight: 700;}
    .sub-header {font-size: 18px; color: #6b7280; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
st.sidebar.title("🏥 No-Show Analysis")
st.sidebar.caption("Brazilian Public Healthcare System")
page = st.sidebar.radio("Go to:", [
    "🏠 Overview",
    "🗄️ Database & Data Quality",
    "📩 SMS Reminder Impact",
    "⏳ Lead Time Analysis",
    "🗺️ Neighbourhood Patterns",
    "🔁 Repeat No-Shows",
    "👥 Age & Gender",
    "🎯 High-Risk Segments",
    "💡 Recommendations"
])

st.sidebar.markdown("---")
st.sidebar.caption("Author: Ioannis Koutnas · Data Analyst")
st.sidebar.caption("Data: Kaggle — Brazilian Medical Appointments")

# ====================== OVERVIEW ======================
if page == "🏠 Overview":
    st.markdown('<p class="main-header">Healthcare Appointment No-Show Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Real-World Data from the Brazilian Public Healthcare System — '
        'Built with Relational SQL</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Appointments", "110,526")
    with col2:
        st.metric("Unique Patients", "62,298")
    with col3:
        st.metric("Neighbourhoods", "81")
    with col4:
        st.metric("Overall No-Show Rate", "20.19%")

    st.markdown("### Business Problem")
    st.info(
        "When patients skip scheduled medical appointments without canceling, clinics lose "
        "money, staff time is wasted, and other patients face longer wait times. This project "
        "builds a clean relational database from raw appointment logs and uses SQL to uncover "
        "why patients miss appointments — turning insights into practical scheduling fixes."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.success(
            "**Strongest predictor — Lead Time:** Same-day appointments have near-zero "
            "no-show rates; appointments booked 8+ days out show consistently higher "
            "no-show rates (~30–36%)."
        )
    with col2:
        st.warning(
            "**The SMS Paradox:** Patients who *received* an SMS reminder actually had a "
            "**higher** no-show rate (27.57%) than those who didn't (16.7%) — a reminder of "
            "why this is observational data, not a causal experiment (see SMS page for why)."
        )

    st.markdown("### Analysis Roadmap")
    st.markdown(
        "1. **Database & Data Quality** — cleaning, schema, validation\n"
        "2. **SMS Reminder Impact** — the counterintuitive SMS paradox\n"
        "3. **Lead Time Analysis** — the strongest operational predictor\n"
        "4. **Neighbourhood Patterns** — geographic disparities\n"
        "5. **Repeat No-Shows** — chronic patient behavior\n"
        "6. **Age & Gender** — demographic breakdowns\n"
        "7. **High-Risk Segments** — combining SMS + lead time\n"
        "8. **Recommendations** — actionable operational strategies"
    )

# ====================== DATABASE & DATA QUALITY ======================
elif page == "🗄️ Database & Data Quality":
    st.title("🗄️ Database Design & Data Quality")

    st.markdown(
        "The raw dataset arrived as a single, denormalized spreadsheet — every row repeated "
        "patient demographics, clinic locations, and appointment details. This was restructured "
        "into a clean **relational database** (SQLite) with dedicated `patients`, "
        "`neighbourhoods`, and `appointments` tables, linked by foreign keys."
    )

    st.markdown("### Data Quality Audit")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Missing values per core field**")
        missing_df = pd.DataFrame({
            "Field": ["PatientId", "AppointmentID", "Gender", "Age",
                      "ScheduledDay", "AppointmentDay", "Neighbourhood", "No-show"],
            "Missing Values": [0, 0, 0, 0, 0, 0, 0, 0]
        })
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("**Numeric distribution checks**")
        numeric_df = pd.DataFrame({
            "Statistic": ["count", "mean", "std", "min", "25%", "50%", "75%", "max"],
            "Age": [110527, 37.09, 23.11, -1, 18, 37, 55, 115],
            "SMS_received": [110527, 0.32, 0.47, 0, 0, 0, 1, 1]
        })
        st.dataframe(numeric_df, use_container_width=True, hide_index=True)

    st.markdown("### Key Validation Takeaways")
    st.markdown(
        "- **Complete record integrity:** zero missing values across all core demographic, "
        "location, and scheduling fields.\n"
        "- **Appointment vs. patient granularity:** all 110,527 `AppointmentID` values are "
        "unique, while 48,228 records are repeat bookings by returning patients — confirming "
        "the need for a separate patient dimension table.\n"
        "- **Boundary correction:** the audit flagged a minimum `Age` of **-1** (a corrupt "
        "entry). Filtering it out dropped the clean appointment count from **110,527 to "
        "110,526**.\n"
        "- **Relational schema result:** **62,298 distinct patients** across **81 clinic "
        "neighbourhoods**, with zero orphaned keys or redundant entries."
    )

    st.markdown("### Final Database Summary")
    summary_df = pd.DataFrame({
        "patient_count": [62298],
        "neighbourhood_count": [81],
        "appointment_count": [110526]
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ====================== SMS REMINDER IMPACT ======================
elif page == "📩 SMS Reminder Impact":
    st.title("📩 5.1 & 5.2 — Baseline Attendance & the SMS Reminder Paradox")

    st.markdown("### 5.1 Overall Baseline Attendance")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.metric("Total Appointments", "110,526")
        st.metric("No-Shows", "22,319")
        st.metric("No-Show Rate", "20.19%")
    with col2:
        fig, ax = plt.subplots(figsize=(5.5, 5))
        ax.pie(
            [88207, 22319],
            labels=[f"Attended (79.81%)", f"No-Show (20.19%)"],
            autopct='%1.1f%%', startangle=90,
            colors=['#2ca02c', '#d62728'],
            wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2),
            textprops=dict(size=11, weight='bold')
        )
        ax.set_title('Overall Appointment Attendance Breakdown', weight='bold', pad=15)
        st.pyplot(fig)

    st.markdown("---")
    st.markdown("### 5.2 Apparent SMS Reminder Paradox")

    sms_df = pd.DataFrame({
        "SMS Status": ["No SMS (0)", "SMS Received (1)"],
        "Total Appointments": [75044, 35482],
        "No-Show Rate": ["16.70%", "27.57%"]
    })
    st.dataframe(sms_df, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(["No SMS (0)", "SMS Received (1)"], [16.7, 27.57],
                   color=['#1f77b4', '#ff7f0e'], width=0.45)
    ax.set_ylabel('No-Show Rate (%)', weight='bold')
    ax.set_ylim(0, 35)
    ax.set_title('Apparent SMS Reminder Paradox', weight='bold', pad=15)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', weight='bold')
    st.pyplot(fig)

    st.error(
        "**This is not evidence that SMS reminders cause no-shows.** This is observational "
        "data — the SMS system was very likely more heavily triggered for appointments with "
        "**long lead times** (which independently carry much higher no-show risk, see the "
        "next page), confounding the raw comparison. Isolating SMS effect *within* the same "
        "lead-time bracket is exactly what the High-Risk Segments page does."
    )

# ====================== LEAD TIME ANALYSIS ======================
elif page == "⏳ Lead Time Analysis":
    st.title("⏳ 5.3 Appointment Lead Time and No-Show Rate")

    st.markdown(
        "This analysis evaluates whether the gap between booking (`scheduled_day`) and the "
        "actual appointment (`appointment_day`) impacts attendance."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Same-Day (0 days)", "21.35%", "no-show rate")
    col2.metric("1 Day Lead Time", "23.82%")
    col3.metric("Longest tail (150+ days)", "up to 60–75%", "high volatility, low N")

    st.markdown("### Complete Day-by-Day No-Show Trend")
    st.image(str("lead_time_trend.png"), use_container_width=True)

    st.markdown(
        "- **Same-day appointments** show the lowest no-show rates — immediate demand "
        "correlates strongly with attendance.\n"
        "- **No-show rates climb and stay elevated** (roughly 30–45%) as lead time extends "
        "into the 50–100 day range.\n"
        "- **Beyond ~100 days**, the line becomes volatile because each daily bucket contains "
        "very few appointments — individual patient behavior dominates rather than a stable trend.\n"
        "- **Negative lead-time entries** (appointment logged before booking — a data artifact) "
        "were filtered out prior to this analysis."
    )

    st.success(
        "**Lead time is the single strongest operational predictor of no-show behavior** "
        "identified in this analysis — more so than SMS status, age, gender, or neighbourhood."
    )

# ====================== NEIGHBOURHOOD PATTERNS ======================
elif page == "🗺️ Neighbourhood Patterns":
    st.title("🗺️ 5.4 Neighbourhood-Level No-Show Patterns")

    st.markdown(
        "Comparing no-show rates across the **74 neighbourhoods** with at least 100 "
        "qualifying appointments reveals meaningful geographic disparities."
    )

    neigh_df = pd.DataFrame({
        "Neighbourhood": ["SANTOS DUMONT", "SANTA CECÍLIA", "SANTA CLARA", "ITARARÉ", "JESUS DE NAZARETH",
                           "SANTA MARTHA", "DO CABRAL", "DE LOURDES", "SOLON BORGES", "MÁRIO CYPRESTE"],
        "No-Show Rate": ["28.92%", "27.46%", "26.48%", "26.27%", "24.40%",
                          "15.84%", "15.71%", "15.41%", "14.71%", "14.56%"],
        "Risk Tier": ["Highest"]*5 + ["Lowest"]*5
    })
    st.dataframe(neigh_df, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    names = ["MÁRIO CYPRESTE", "SOLON BORGES", "DE LOURDES", "DO CABRAL", "SANTA MARTHA",
             "JESUS DE NAZARETH", "ITARARÉ", "SANTA CLARA", "SANTA CECÍLIA", "SANTOS DUMONT"]
    values = [14.56, 14.71, 15.41, 15.71, 15.84, 24.40, 26.27, 26.48, 27.46, 28.92]
    colors_neigh = ['#2ca02c']*5 + ['#d62728']*5
    bars = ax.barh(names, values, color=colors_neigh, height=0.6)
    ax.set_xlabel('No-Show Rate (%)', weight='bold')
    ax.set_title('Neighbourhood No-Show Rate Disparities (Highest vs. Lowest Risk)', weight='bold', pad=15)
    ax.grid(axis='x', linestyle=':', alpha=0.7, color='gray')
    ax.set_xlim(0, 35)
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.2f}%', xy=(width, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords="offset points", ha='left', va='center', weight='bold')
    st.pyplot(fig)

    st.markdown(
        "**Santos Dumont** has nearly **double** the no-show rate of **Mário Cypreste** "
        "(28.92% vs. 14.56%) — a gap large enough to justify localized operational "
        "interventions (e.g. added reminder touchpoints or overbooking buffers) for the "
        "highest-risk neighbourhoods."
    )

# ====================== REPEAT NO-SHOWS ======================
elif page == "🔁 Repeat No-Shows":
    st.title("🔁 5.5 Repeat No-Show Behavior")

    st.markdown(
        "Are missed appointments spread evenly across patients, or concentrated in a "
        "subset of chronic no-show patients? **3,226 patients** have missed 2 or more "
        "appointments."
    )

    dist_df = pd.DataFrame({
        "Missed Appointments": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18],
        "Number of Patients": [2418, 516, 162, 58, 33, 13, 9, 3, 4, 4, 1, 1, 1, 1, 1, 1]
    })

    fig, ax = plt.subplots(figsize=(12, 5.5))
    bars = ax.bar(dist_df["Missed Appointments"].astype(str), dist_df["Number of Patients"],
                   color='#e377c2', width=0.6)
    ax.set_xlabel('Number of Missed Appointments (No-Shows) per Patient', weight='bold')
    ax.set_ylabel('Number of Patients', weight='bold')
    ax.set_title('Distribution of Chronic Repeat No-Show Patients', weight='bold', pad=15)
    ax.set_ylim(0, dist_df["Number of Patients"].max() * 1.15)
    ax.grid(axis='y', linestyle=':', alpha=0.7, color='gray')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 4), textcoords="offset points", ha='center', va='bottom',
                    weight='bold', fontsize=8.5)
    st.pyplot(fig)

    col1, col2, col3 = st.columns(3)
    col1.metric("Patients with 2+ No-Shows", "3,226")
    col2.metric("Most Common", "2 misses", "2,418 patients (75%)")
    col3.metric("Most Extreme Case", "18 no-shows", "1 patient")

    st.markdown(
        "- The distribution is heavily **right-skewed**: the overwhelming majority of repeat "
        "no-show patients (2,418 of 3,226, ~75%) missed exactly 2 appointments.\n"
        "- A small tail of **chronic offenders** exists — patients with 10+ no-shows — who "
        "may warrant individualized case management rather than blanket policy changes.\n"
        "- This supports **targeted follow-up strategies** (e.g. a phone call after a 2nd "
        "miss) over broad, one-size-fits-all outreach."
    )

# ====================== AGE & GENDER ======================
elif page == "👥 Age & Gender":
    st.title("👥 5.6 & 5.7 — Demographic Breakdowns")

    st.markdown("### 5.6 No-Show Rate by Age Group")
    age_df = pd.DataFrame({
        "Age Group": ["Under 18", "18–35", "36–55", "56–75", "75+"],
        "Total Appointments": [27397, 25624, 30015, 22101, 5389],
        "No-Show Rate": ["21.91%", "23.81%", "19.71%", "15.52%", "16.13%"]
    })
    st.dataframe(age_df, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(age_df["Age Group"], [21.91, 23.81, 19.71, 15.52, 16.13],
                   color='#4c72b0', width=0.5)
    ax.set_ylabel('No-Show Rate (%)', weight='bold')
    ax.set_xlabel('Age Bracket', weight='bold')
    ax.set_ylim(0, 30)
    ax.set_title('No-Show Rate by Age Group', weight='bold', pad=15)
    ax.grid(axis='y', linestyle=':', alpha=0.7, color='gray')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', weight='bold')
    st.pyplot(fig)

    st.markdown(
        "**Young adults (18–35)** have the highest no-show rate (23.81%), while "
        "**older patients (56–75)** are the most reliable attendees (15.52%) — consistent "
        "with busier, less routine-driven lifestyles among younger patients."
    )

    st.markdown("---")
    st.markdown("### 5.7 No-Show Rate by Gender")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        gender_df = pd.DataFrame({
            "Gender": ["Female (F)", "Male (M)"],
            "Total Appointments": [71839, 38687],
            "No-Show Rate": ["20.31%", "19.97%"]
        })
        st.dataframe(gender_df, use_container_width=True, hide_index=True)
        st.caption("Difference is small (0.34 points) — no strong gender-based effect.")
    with col2:
        fig, ax = plt.subplots(figsize=(5, 4.5))
        bars = ax.bar(["Female (F)", "Male (M)"], [20.31, 19.97],
                       color=['#e377c2', '#1f77b4'], width=0.45)
        ax.set_ylabel('No-Show Rate (%)', weight='bold')
        ax.set_ylim(0, 30)
        ax.set_title('No-Show Rate by Gender', weight='bold', pad=15)
        ax.grid(axis='y', linestyle=':', alpha=0.7, color='gray')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', weight='bold')
        st.pyplot(fig)

# ====================== HIGH-RISK SEGMENTS ======================
elif page == "🎯 High-Risk Segments":
    st.title("🎯 5.8 High-Risk Appointment Segments")

    st.markdown(
        "Combining **SMS status** and **lead time** together isolates whether the SMS "
        "paradox seen earlier holds up once lead time is controlled for."
    )

    segment_df = pd.DataFrame({
        "SMS Status": ["No SMS", "SMS Received", "No SMS", "SMS Received"],
        "Lead Time Group": ["1–7 days", "1–7 days", "8+ days", "8+ days"],
        "Total Appointments": [15424, 11548, 15840, 23934],
        "No-Show Rate": ["25.38%", "23.76%", "36.05%", "29.41%"]
    })
    st.dataframe(segment_df, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = ["1–7 days", "8+ days"]
    no_sms = [25.38, 36.05]
    sms = [23.76, 29.41]
    width = 0.25
    positions = range(len(x))
    ax.bar([p - width/2 for p in positions], no_sms, width=width, label="No SMS", color='#d95f02')
    ax.bar([p + width/2 for p in positions], sms, width=width, label="SMS Received", color='#2ca02c')
    ax.set_xticks(list(positions))
    ax.set_xticklabels(x)
    ax.set_ylabel('No-Show Rate (%)', weight='bold')
    ax.set_xlabel('Lead Time Group', weight='bold')
    ax.set_ylim(0, 42)
    ax.set_title('Re-Examining the SMS Effect Within Lead-Time Groups', weight='bold', pad=15)
    ax.legend()
    for i, (nv, sv) in enumerate(zip(no_sms, sms)):
        ax.annotate(f'{nv:.2f}%', xy=(i - width/2, nv), xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', weight='bold', fontsize=9)
        ax.annotate(f'{sv:.2f}%', xy=(i + width/2, sv), xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', weight='bold', fontsize=9)
    st.pyplot(fig)

    st.success(
        "**The paradox resolves once lead time is controlled for.** Within *both* lead-time "
        "brackets, patients who received an SMS actually had a **lower** no-show rate than "
        "those who didn't (23.76% vs. 25.38% for short lead times; 29.41% vs. 36.05% for "
        "long lead times). The earlier raw SMS comparison was confounded — SMS reminders "
        "were disproportionately sent to long-lead-time (higher-risk) appointments, which "
        "masked the reminder's real, positive effect."
    )

    st.markdown(
        "**Highest-risk segment:** long lead time (8+ days) with **no** SMS reminder — "
        "**36.05%** no-show rate, the single riskiest combination identified in this analysis."
    )

# ====================== RECOMMENDATIONS ======================
elif page == "💡 Recommendations":
    st.title("💡 Operational Recommendations")

    st.markdown(
        "Based on the SQL analysis, these are low-cost, targeted operational adjustments "
        "designed for near-term implementation."
    )

    with st.expander("1. Lead Time Minimization & Adaptive Scheduling", expanded=True):
        st.markdown(
            "- **Short-window prioritization:** schedule non-urgent, routine visits within "
            "a **1–7 day window** whenever feasible — the strongest lever identified.\n"
            "- **Overbooking buffers for long-horizon slots:** for appointments requiring "
            "**8+ day lead times**, apply controlled double-booking to offset the expected "
            "**~30–36% baseline drop-out rate**."
        )

    with st.expander("2. Tiered Digital Reminder Protocols", expanded=True):
        st.markdown(
            "- **Risk-based delivery:** trigger SMS/email/push reminders based on "
            "appointment risk profile rather than a uniform schedule.\n"
            "- **Multi-touch sequences for long lead times:** the High-Risk Segments analysis "
            "shows SMS reminders *do* reduce no-shows once lead time is controlled for — "
            "prioritize reminder coverage for 8+ day appointments, where the effect "
            "(36.05% → 29.41%) is largest in absolute terms."
        )

    with st.expander("3. Geographic & Neighbourhood-Level Targeting", expanded=True):
        st.markdown(
            "- Focus outreach resources on the highest-risk neighbourhoods (e.g. **Santos "
            "Dumont, Santa Cecília, Santa Clara** — all above 26% no-show rate) rather than "
            "applying uniform citywide policy."
        )

    with st.expander("4. Chronic Repeat No-Show Case Management", expanded=True):
        st.markdown(
            "- Flag patients after a **2nd missed appointment** for a personal follow-up "
            "call rather than automated messaging alone.\n"
            "- Identify and individually manage the small tail of chronic offenders "
            "(10+ no-shows) separately from the broader repeat-no-show population."
        )

    with st.expander("5. Age-Targeted Engagement", expanded=True):
        st.markdown(
            "- **18–35 year-olds** show the highest no-show rate (23.81%) — consider "
            "mobile-first reminder channels (SMS/app push) better suited to this group's "
            "communication habits."
        )

    st.info(
        "**Warning:** this is observational data. The SMS paradox demonstrates how easily "
        "raw comparisons can mislead without controlling for confounders like lead time — "
        "any operational change should be piloted and measured, not assumed."
    )

# ====================== FOOTER ======================
st.markdown("---")
st.caption("🏥 Healthcare Appointment No-Show Analysis | Data: Brazilian Public Healthcare System (Kaggle) | Built with Streamlit")
