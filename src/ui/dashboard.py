import matplotlib.pyplot as plt
import solara
import time
from ui.graph import Graph

@solara.component
def RiskHistoryChart(all_proposals):
    if not all_proposals:
        return solara.Markdown("No data available yet.")
        
    # Group by agent and iteration
    agent_data = {}
    for p in all_proposals:
        sender = p.get("sender", "Unknown")
        it = p.get("iteration", 0)
        risk = p.get("risk_score", 0)
        
        if sender not in agent_data:
            agent_data[sender] = {"x": [], "y": []}
            
        agent_data[sender]["x"].append(it)
        agent_data[sender]["y"].append(risk)
        
    fig, ax = plt.subplots(figsize=(8, 4))
    for sender, data in agent_data.items():
        # Sort by iteration just in case
        sorted_points = sorted(zip(data["x"], data["y"]))
        xs = [pt[0] for pt in sorted_points]
        ys = [pt[1] for pt in sorted_points]
        ax.plot(xs, ys, marker="o", label=sender, linestyle="-")
        
    ax.set_title("Agent Risk Scores over Iterations")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Risk Score (0-10)")
    ax.set_ylim(0, 10.5)
    
    # Ensure x-axis ticks are integers
    if all_proposals:
        max_iter = max(p.get("iteration", 0) for p in all_proposals)
        ax.set_xticks(range(max_iter + 1))
        
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend()
    
    solara.FigureMatplotlib(fig)

@solara.component
def AgentReasoningCard(proposal):
    # This component displays the reasoning for a single agent
    sender = proposal.get("sender", "Unknown Agent")
    content = proposal.get("content", {})
    risk = proposal.get("risk_score", 0)
    
    # Pick a color based on the risk score
    if risk > 7:
        color = "#dc3545"
    elif risk > 3:
        color = "#ffc107"
    else:
        color = "#28a745"
    
    with solara.Card(title=f"{sender}", subtitle="Current Round Analysis"):
        with solara.Column(style="min-height: 200px;"):
            solara.Markdown(f"**Risk Level:** {risk}/10", style=f"color: {color}; font-weight: bold")
            solara.Markdown(f"**Observation:** {content.get('hypothesis', 'Analyzing...')}")
            solara.Markdown(f"**Action:** {content.get('action', 'Waiting...')}")

@solara.component 
def MASDashboard(model):
    # We store the data we want to display in a reactive variable
    display_state = solara.use_reactive({})
    
    def watch_history():
        last_processed_idx = -1
        while True:
            try:
                # Get the history list directly from your model
                history_list = getattr(model, "mas_history", [])
                current_idx = len(history_list) - 1
                
                # Update the display state if there is a new entry
                if current_idx > last_processed_idx:
                    new_state = history_list[current_idx].get("state", {})
                    if display_state.value != new_state:
                        display_state.set(new_state)
                    last_processed_idx = current_idx
            except Exception:
                pass
            
            # Wait a second before checking again
            time.sleep(1.0)

    # Run the watcher in the background
    solara.use_thread(watch_history, dependencies=[])

    # Extract the data from our stable display state
    current_state = display_state.value
    all_proposals = current_state.get("proposals", [])
    verdict = current_state.get("verdict", {})

    # Step 1: Find the highest iteration number
    current_iter = 0
    if all_proposals:
        current_iter = max(p.get("iteration", 0) for p in all_proposals)

    # Step 2: Filter to keep ONLY the proposals from the current round
    active_proposals = [p for p in all_proposals if p.get("iteration") == current_iter]

    with solara.Column(style="padding: 20px; gap: 20px;"):
        with solara.lab.Tabs():
            with solara.lab.Tab("Live Dashboard"):
                with solara.Card("System Execution Flow"):
                    Graph(state=current_state)
                
                if verdict:
                    with solara.Card("Orchestrator Verdict", style="background-color: #f0f7ff; color: #1a1a1a; padding: 12px;"):
                        solara.Markdown(f"### Result: {verdict.get('verdict', 'Normal')}",
                                        style="color: #1a1a1a;")
                        solara.Markdown(f"**Action Plan:** {verdict.get('action_plan', 'Continuing monitoring.')}",
                                        style="color: #1a1a1a;")

                # Step 3: Show the agents on top of each other using Column for the current round
                with solara.Card(f"Current Round Reasoning (Iteration {current_iter})", style="background-color: #f9f9f9; color: #1a1a1a; padding: 12px;"):
                    with solara.Column(style={
                        "transform": "scale(0.9)",  
                        "transform-origin": "top left",
                }):
                        # Sort alphabetically so the agents stay in the same position
                        for prop in sorted(active_proposals, key=lambda x: x['sender']):
                            AgentReasoningCard(prop)
                            
            with solara.lab.Tab("History & Analytics"):
                with solara.Columns([1, 1]):
                    # Left column: The interactions text log
                    with solara.Card("Prior Agent Interactions"):
                        with solara.Column(style="max-height: 600px; overflow-y: auto;"):
                            if len(all_proposals) > len(active_proposals):
                                prior_proposals = [p for p in all_proposals if p.get("iteration") != current_iter]
                                iterations = sorted(list(set(p.get("iteration", 0) for p in prior_proposals)), reverse=True)
                                
                                for it in iterations:
                                    solara.Markdown(f"### Iteration {it}")
                                    props_for_it = [p for p in prior_proposals if p.get("iteration") == it]
                                    
                                    for prop in sorted(props_for_it, key=lambda x: x.get('sender', '')):
                                        sender = prop.get("sender", "Unknown")
                                        content = prop.get("content", {})
                                        risk = prop.get("risk_score", 0)
                                        
                                        with solara.Row(style="margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 10px;"):
                                            solara.Markdown(f"**{sender} (Risk: {risk}/10):** {content.get('hypothesis', '')}")
                            else:
                                solara.Markdown("No prior interactions to display yet.")
                                
                    # Right column: The graph
                    with solara.Card("Risk Score Analysis"):
                        RiskHistoryChart(all_proposals)
