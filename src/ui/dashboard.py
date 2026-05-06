import solara
import time
import json
import os
from config import TELEMETRY_ENDPOINT, MAS_HISTORY_TOPIC
from simulation.communication import ZeroMQTelemetryChannel

HISTORY_FILE = "outputs/dashboard_history.json"
_app_started = False

def load_history_from_file():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
                if data:
                    latest_tick = max(int(k) for k in data.keys() if isinstance(k, str) and k.isdigit())
                    return {latest_tick: data[str(latest_tick)]}
        except Exception:
            pass
    return {}

def clear_history_file():
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump({}, f)
    except Exception:
        pass

def save_history_to_file(history):
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        existing_history = {}
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    existing_history = json.load(f)
            except Exception:
                existing_history = {}
        for k, v in history.items():
            try:
                tick_num = int(k) if isinstance(k, str) else k
                existing_history[str(tick_num)] = v
            except (ValueError, TypeError):
                continue
        with open(HISTORY_FILE, 'w') as f:
            json.dump(existing_history, f, indent=2)
    except Exception:
        pass


# --- Risk helpers -------------------------------------------------------------

def _risk_color(score: int) -> str:
    if score > 7:
        return "#dc3545"
    if score > 3:
        return "#e6a817"
    return "#28a745"

def _risk_label(score: int) -> str:
    if score > 7:
        return "High"
    if score > 3:
        return "Medium"
    return "Low"

def _agent_initials(sender: str) -> str:
    parts = [w for w in sender.replace("Agent", "").split() if w]
    if parts:
        return parts[0][:2].upper()
    return sender[:2].upper()


# --- Visual sub-components ---------------------------------------------------

@solara.component
def AgentRow(proposal):
    sender    = proposal.get("sender", "Unknown Agent")
    content   = proposal.get("content", {})
    risk      = proposal.get("risk_score", 0)
    iteration = proposal.get("iteration", 0)

    color    = _risk_color(risk)
    label    = _risk_label(risk)
    initials = _agent_initials(sender)

    row_style = (
        "display: flex; align-items: flex-start; gap: 14px;"
        "padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.07);"
    )
    avatar_style = (
        f"width: 38px; height: 38px; border-radius: 50%;"
        f"background: {color}22; border: 1px solid {color}55;"
        "display: flex; align-items: center; justify-content: center;"
        f"font-size: 12px; font-weight: 700; color: {color}; flex-shrink: 0;"
    )
    badge_style = (
        f"display: inline-block; font-size: 11px; font-weight: 600;"
        f"padding: 3px 9px; border-radius: 10px; color: {color};"
        f"background: {color}22; border: 1px solid {color}55; white-space: nowrap;"
    )

    with solara.Row(style=row_style):
        solara.HTML(tag="div", style=avatar_style, unsafe_innerHTML=initials)
        with solara.Column(style="flex: 1; gap: 3px; min-width: 0;"):
            with solara.Row(style="align-items: center; gap: 8px; flex-wrap: wrap;"):
                solara.Text(sender, style="font-weight: 600; font-size: 14px;")
                solara.Text(f"· Iteration {iteration + 1}", style="font-size: 12px; opacity: 0.45;")
            hypothesis = content.get("hypothesis", "Analyzing...")
            short = hypothesis 
            solara.Text(short, style="font-size: 13px; opacity: 0.7; line-height: 1.5;")
        with solara.Column(style="align-items: flex-end; flex-shrink: 0;"):
            solara.HTML(tag="span", style=badge_style, unsafe_innerHTML=f"Risk {risk}/10 · {label}")


@solara.component
def OrchestratorCard(verdict: dict, tick: int):
    """Bold verdict card for the right-hand panel."""
    verdict_text = verdict.get("verdict", "Normal")
    action_plan  = verdict.get("action_plan", "Continuing monitoring.")
    top_agent    = verdict.get("highest_risk_score_agent", "")

    formatted = verdict_text.replace("_", " ").title()
    is_risk   = "risk" in verdict_text.lower() and verdict_text.lower() != "no_risk"
    accent    = "#e6a817" if is_risk else "#28a745"

    card_style = (
        "background: #666633; border-radius: 10px; padding: 18px 20px;"
        "margin-bottom: 12px; color: #ffffff;"
        f"border-top: 3px solid {accent};"
    )
    label_style = (
        "font-size: 10px; font-weight: 700; letter-spacing: 0.1em;"
        "text-transform: uppercase; opacity: 0.6; margin-bottom: 4px;"
    )
    verdict_style = (
        "font-size: 20px; font-weight: 800; color: #ffffff; line-height: 1.2; margin-bottom: 10px;"
    )
    tick_style = "font-size: 11px; opacity: 0.55; margin-bottom: 14px;"
    divider_style = (
        "border: none; border-top: 1px solid rgba(255,255,255,0.2); margin: 12px 0;"
    )
    plan_style = (
        "font-size: 13px; color: #ffffff; opacity: 0.9; line-height: 1.75;"
    )
    agent_style = (
        f"display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 8px;"
        f"border-radius: 6px; background: {accent}33; color: {accent};"
        f"border: 1px solid {accent}66; margin-top: 10px;"
    )

    with solara.Column(style=card_style):
        solara.HTML(tag="div", style=label_style, unsafe_innerHTML="Orchestrator Verdict")
        solara.HTML(tag="div", style=verdict_style, unsafe_innerHTML=formatted)
        solara.HTML(tag="div", style=tick_style, unsafe_innerHTML=f"Tick {tick}")
        solara.HTML(tag="hr", style=divider_style, unsafe_innerHTML="")
        solara.Markdown(action_plan, style=plan_style)
        if top_agent and top_agent != "None":
            solara.HTML(
                tag="span",
                style=agent_style,
                unsafe_innerHTML=f"Flagged by {top_agent}"
            )


@solara.component
def IterationDivider(iteration: int):
    solara.Text(
        f"Iteration {iteration + 1}",
        style=(
            "font-size: 11px; font-weight: 600; letter-spacing: 0.08em;"
            "opacity: 0.45; text-transform: uppercase; padding: 10px 16px 4px;"
        )
    )


# --- Main history renderer ---------------------------------------------------

@solara.component
def HistoryRenderer(history):
    from collections import defaultdict

    if not history:
        with solara.Column(style="padding: 40px; align-items: center;"):
            solara.Text("Waiting for simulation data...", style="font-size: 14px; opacity: 0.45;")
        return

    latest_tick = max(history.keys()) if history else None
    if latest_tick is None:
        return

    tick_state    = history[latest_tick]
    all_proposals = tick_state.get("proposals", [])
    verdict       = tick_state.get("verdict", {})

    # Header
    proposal_count = len(all_proposals)
    solara.Text("Agent Analysis", style="font-size: 22px; font-weight: 700;")
    solara.Text(
        f"Tick {latest_tick} · {proposal_count} proposal{'s' if proposal_count != 1 else ''}",
        style="font-size: 13px; opacity: 0.5; margin-bottom: 16px;"
    )

    # Two-column layout
    with solara.Row(style="gap: 20px; align-items: flex-start;"):

        # Left — proposals list
        with solara.Column(style="flex: 1; min-width: 0;"):
            panel_style = (
                "border: 1px solid rgba(255,255,255,0.09);"
                "border-radius: 10px; overflow: hidden;"
            )
            iterations = defaultdict(list)
            for p in all_proposals:
                iterations[p.get("iteration", 0)].append(p)

            with solara.Column(style=panel_style):
                for it_num in sorted(iterations.keys()):
                    IterationDivider(it_num)
                    for prop in sorted(iterations[it_num], key=lambda x: x.get("sender", "")):
                        AgentRow(prop)

        # Right — orchestrator verdict panel
        with solara.Column(style="width: 300px; flex-shrink: 0;"):
            solara.Text(
                "Verdict",
                style=(
                    "font-size: 11px; font-weight: 700; letter-spacing: 0.1em;"
                    "text-transform: uppercase; opacity: 0.45; margin-bottom: 10px;"
                )
            )
            if verdict and isinstance(verdict, dict) and verdict.get("verdict"):
                OrchestratorCard(verdict, latest_tick)
            else:
                with solara.Column(style=(
                    "border: 1px solid rgba(255,255,255,0.09); border-radius: 10px;"
                    "padding: 24px; align-items: center;"
                )):
                    solara.Text("Awaiting verdict...", style="font-size: 13px; opacity: 0.35;")


# --- Top-level app component -------------------------------------------------

@solara.component
def MASDashboard(model, history_state=None):
    history_state = solara.use_reactive(load_history_from_file())
    last_history_update = solara.use_reactive(0)

    def clear_on_app_start():
        global _app_started
        if not _app_started:
            clear_history_file()
            history_state.set({})
            _app_started = True

    solara.use_effect(clear_on_app_start, dependencies=[])

    def watch_history(cancel):
        subscriber = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=MAS_HISTORY_TOPIC,
            bind=False
        )
        current_tick_data = {}
        last_tick         = None
        last_update_time  = time.time()

        try:
            while not cancel.is_set():
                try:
                    while True:
                        event = subscriber.subscribe(block=False)
                        if event is None:
                            break
                        if isinstance(event, dict):
                            tick      = event.get("tick")
                            payload   = event.get("payload", {})
                            new_state = payload.get("state", {})
                            if new_state and tick is not None:
                                if tick != last_tick:
                                    if last_tick is not None and current_tick_data:
                                        save_history_to_file({last_tick: current_tick_data})
                                        history_state.set({last_tick: current_tick_data})
                                    last_tick         = tick
                                    current_tick_data = new_state.copy()
                                else:
                                    existing_proposals = current_tick_data.get("proposals", [])
                                    new_proposals      = new_state.get("proposals", [])
                                    current_tick_data["proposals"] = existing_proposals + new_proposals
                                    if "verdict" in new_state and new_state.get("verdict"):
                                        current_tick_data["verdict"] = new_state["verdict"]

                    current_time = time.time()
                    if current_tick_data and last_tick is not None and (current_time - last_update_time) >= 0.5:
                        history_state.set({last_tick: current_tick_data})
                        last_update_time = current_time
                except Exception:
                    pass
                time.sleep(0.2)
        finally:
            try:
                if current_tick_data and last_tick is not None:
                    save_history_to_file({last_tick: current_tick_data})
                subscriber.close()
            except Exception:
                pass

    solara.use_thread(watch_history, dependencies=[])

    history = history_state.value

    with solara.Column(style="padding: 24px 28px; gap: 0; max-width: 1200px; margin: 0 auto;"):
        with solara.AppBarTitle():
            solara.Text("Multi-Agent System Decision Dashboard")
        HistoryRenderer(history)