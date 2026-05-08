# Freight Safe User Guide

## Introduction

Freight Safe is a smart freight monitoring and safety platform designed to help users monitor truck activity, cargo conditions, and route behavior in real time.

The system simulates freight transport operations and provides live monitoring through an interactive dashboard and map interface. Freight Safe also uses an intelligent decision engine that analyzes vehicle activity and identifies unusual behavior, delays, route deviations, or cargo-related concerns.

This guide explains:

* What Freight Safe does
* How the system works
* How to install and start the system
* What users should expect during operation
* Common issues and solutions

This guide is written for non-technical users.

---

# What Freight Safe Does

Freight Safe monitors simulated freight transportation activity and presents live operational data through a visual dashboard.

The system is designed to:

* Track truck movement across routes
* Monitor cargo and vehicle telemetry
* Detect unusual or risky behavior
* Provide automated safety assessments
* Display live operational information through a web interface

Freight Safe can simulate several operational situations, including:

* Normal freight operations
* Route deviations
* Unexpected vehicle stops
* Cargo state changes
* Security-related anomalies

The system continuously analyzes incoming telemetry and produces automated assessments from multiple monitoring agents.

An orchestrator component combines these assessments into a final operational verdict.

---

# How Freight Safe Works

## System Overview

Freight Safe operates as a live monitoring environment.

The system consists of four main parts:

1. Truck Simulation
2. Monitoring and Telemetry Collection
3. Intelligent Decision Engine
4. User Dashboard

---

## 1. Truck Simulation

The simulation represents freight trucks moving through a transport network.

Each truck continuously produces operational information such as:

* Current location
* Route progress
* Cargo status
* Door activity
* Movement behavior

This information is generated automatically during the simulation.

---

## 2. Monitoring and Telemetry Collection

Freight Safe continuously collects operational data from the simulated trucks.

The monitoring system processes information such as:

* Vehicle movement
* Stops and delays
* Route deviations
* Cargo condition changes
* Door opening events

This information is streamed live to the dashboard.

---

## 3. Intelligent Decision Engine

The decision engine acts as a group of automated monitoring agents.

Each agent analyzes the situation from a different perspective.

Examples include:

* Route safety analysis
* Cargo condition analysis
* Operational behavior analysis

The system then combines these analyses into a final recommendation or verdict.

Users can view:

* Agent observations
* Safety recommendations
* Current operational assessments
* Final orchestrator decisions

---

## 4. User Dashboard

The Freight Safe dashboard provides a live operational view.

The dashboard contains two main sections:

### Simulation Map

The map shows:

* Live truck movement
* Route progress
* Vehicle positions
* Operational activity

### MAS Decision Dashboard

The dashboard displays:

* Latest monitoring results
* Agent reasoning
* Operational assessments
* Final orchestrator verdicts

The dashboard always displays the latest available operational update.

---

# System Requirements

Before installing Freight Safe, ensure the following are available.

## Required Software

* Python 3.10 or newer
* Internet connection
* Modern web browser

## Required Access

Freight Safe requires a valid Google API key to enable the intelligent decision engine.

Without the API key:

* The simulation may still start
* Intelligent monitoring and analysis features will not function properly

---

# Installation Guide

## Step 1: Download the Project

Download or clone the Freight Safe project folder onto your computer.

Place the folder somewhere easy to access.

Example:

* Desktop
* Documents
* Development workspace

---

## Step 2: Open a Terminal or Command Window

Depending on your operating system:

### Windows

Open:

* PowerShell
* Command Prompt

### macOS or Linux

Open:

* Terminal

Navigate to the Freight Safe project folder.

---

## Step 3: Create a Virtual Environment

A virtual environment keeps the project dependencies isolated from the rest of the computer.

Run:

```bash
python -m venv .venv
```

---

## Step 4: Activate the Virtual Environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```bat
.venv\Scripts\activate.bat
```

### macOS or Linux

```bash
source .venv/bin/activate
```

---

## Step 5: Install Required Components

Run:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs all required system components.

Installation may take several minutes.

---

# Configuring Freight Safe

## Step 1: Create the Environment File

Inside the project folder, create a file named:

```text
.env
```

---

## Step 2: Add the API Configuration

Add the following content:

```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.0-flash
```

Replace:

```text
your_google_api_key_here
```

with your actual Google API key.

---

## Important Notes

* The API key is required for intelligent analysis.
* If the API key is missing, the decision engine will not start.
* Restart the application after changing the `.env` file.

---

# Starting Freight Safe

## Starting the Web Application

Run:

```bash
solara run src/app.py
```

After startup, the system displays a local web address.

Example:

```text
http://localhost:8765
```

Open this address in your browser.

---

# What You Will See

## Main Application Tabs

Freight Safe contains two main tabs.

---

## Simulation Map Tab

This tab displays:

* Truck movement
* Route activity
* Vehicle positioning
* Live operational behavior

Users can visually observe the freight operation in real time.

---

## MAS Decision Dashboard Tab

This tab displays:

* Agent analysis
* Safety observations
* Cargo assessments
* Operational warnings
* Final orchestrator decisions

The dashboard updates automatically as the simulation runs.

---

# Available Operational Scenarios

Freight Safe supports multiple simulation scenarios.

The active scenario is selected in the system configuration.

## Available Scenarios

### Normal

Both trucks follow expected operational behavior.

Expected behavior:

* Normal route progress
* No major alerts
* Stable monitoring assessments

---

### Deviation

One truck takes a longer or unexpected route.

Expected behavior:

* Route deviation alerts
* Increased monitoring attention
* Updated operational assessments

---

### Anomaly Stop Open at D

One truck stops unexpectedly and briefly opens its cargo door.

Expected behavior:

* Security-related observations
* Door activity alerts
* Elevated risk assessments

---

### Cargo State

Cargo telemetry changes over time.

Expected behavior:

* Cargo condition monitoring
* Cargo-related alerts
* Dynamic safety evaluations

---

# How the Dashboard Information Should Be Interpreted

The dashboard is designed to provide operational awareness.

## Agent Proposals

Each monitoring agent provides:

* Observations
* Reasoning
* Recommendations

These proposals may differ because each agent evaluates the situation differently.

---

## Orchestrator Verdict

The orchestrator combines all agent assessments into a final operational decision.

This is the primary recommendation presented to the user.

Examples may include:

* Continue monitoring
* Investigate route deviation
* Check cargo integrity
* Review vehicle stop activity

---

# Expected System Behavior

Users should expect:

* Continuous live updates
* Real-time truck movement
* Automated operational analysis
* Frequent dashboard refreshes
* Scenario-specific alerts

The dashboard always prioritizes the latest operational update.

Older events may no longer appear once new information is received.

---

# Saved Output Files

Freight Safe automatically creates operational output files.

Important files include:

## Dashboard History

```text
outputs/dashboard_history.json
```

Stores recent dashboard information for the current session.

---

## Monitoring Logs

```text
outputs/monitoring_logs/output.json
```

Stores monitoring activity and telemetry information.

---

## Evaluation Reports

```text
outputs/llm_scenario_metrics_report.md
```

Contains evaluation metrics.

---

## Timing Reports

```text
outputs/llm_scenario_timing_report.md
```

Contains timing and performance information.

---

# Common Issues and Solutions

## Problem: "GOOGLE_API_KEY is not set"

Cause:

* The API key is missing from the `.env` file.

Solution:

* Verify the `.env` file exists
* Ensure the API key is correctly entered
* Restart the application

---

## Problem: The Dashboard Shows No Data

Cause:

* The simulation is not running correctly
* Data is not being published

Solution:

* Restart the simulation
* Restart the web application
* Wait several seconds for updates to appear

---

## Problem: The Dashboard or Map Freezes

Cause:

* Browser rendering issue
* Application synchronization issue

Solution:

* Refresh the browser
* Restart the application
* Start a fresh browser session

---

## Problem: Changes to `.env` Do Not Apply

Cause:

* The application loads settings only during startup

Solution:

* Fully restart Freight Safe after editing `.env`

---

# Operational Expectations

Freight Safe is designed as a simulation and monitoring environment.

Users should understand:

* The system simulates freight operations rather than controlling real vehicles
* Intelligent analysis is generated automatically
* Alerts and verdicts are based on simulated telemetry behavior
* Different scenarios produce different operational outcomes

The purpose of Freight Safe is to demonstrate:

* Freight monitoring workflows
* Telemetry analysis
* Multi-agent operational reasoning
* Automated safety assessment concepts

---

# Summary

Freight Safe is a freight monitoring and operational analysis platform that combines:

* Live truck simulation
* Real-time telemetry monitoring
* Intelligent multi-agent analysis
* Automated operational assessments
* Interactive dashboard visualization

The platform is intended to help users understand how modern freight monitoring systems can identify unusual operational behavior and provide automated safety analysis in real time.
