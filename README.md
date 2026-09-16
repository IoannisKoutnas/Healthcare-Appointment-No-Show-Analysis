# Medical Appointment No-Show Analysis

An end-to-end data analytics project using Python, SQLite, and Streamlit to investigate attendance patterns and key predictors of missed medical appointments in the Brazilian Public Healthcare System (110,526 records).

## Overview
This repository contains a data analytics pipeline that normalizes raw appointment logs into a relational database model, performs exploratory data analysis to unearth key attendance drivers, and serves an interactive 9-page analytical dashboard using Streamlit.

## Key Findings
* **Lead Time Driver:** Lead time is the single strongest operational predictor of attendance. Same-day bookings have minimal no-shows, whereas bookings scheduled 8+ days in advance show a 30–36% drop-out rate.
* **SMS Paradox:** Initial raw data suggests SMS recipients miss appointments more often. Controlling for lead time resolves this paradox, showing that long lead times confound the relationship and that SMS reminders consistently improve attendance.
* **Clinic Neighborhoods:** Identified high-risk locations (e.g., Santos Dumont at ~28.9% no-show rate) to help target operational improvements.
