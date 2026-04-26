import os
import sys
import solara
import pandas as pd
import time

# --- ENVIRONMENT SETUP ---
# Ensure the project root is in sys.path to allow absolute imports from 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Internal project imports
from src.simulation.model import FreightSimulationModel
from src.simulation.agents.truck_agent import TruckAgent
from config import SIM_SEED

class SimulationDashboard:
    """
    UI Components for the Freight Transport Monitoring System.
    Encapsulates the rendering logic for controls and data tables.
    """
    def __init__(self, model_state):
        # model_state is a solara.reactive object holding the Mesa model
        self.model_state = model_state

    def render_controls(self, model, is_running):
        """
        Renders the control panel with start/stop toggle and manual step.
        """
        with solara.Card("Simulation Control", style={"min-width": "300px"}):
            solara.Markdown(f"### Current Tick: {model.tick}")
            
            # Toggle between Start and Stop based on is_running state
            if not is_running.value:
                solara.Button("START LIVE FEED", color="success", 
                              on_click=lambda: is_running.set(True))
            else:
                solara.Button("STOP LIVE FEED", color="error", 
                              on_click=lambda: is_running.set(False))
            
            # Manual step button for debugging or incremental observation
            solara.Button("Manual Step", on_click=lambda: model.step(), 
                          style={"margin-top": "10px"}, text=True)

            # Anomaly UI: Displays a warning if the model detects a bad truck
            if hasattr(model, 'bad_truck_id') and model.bad_truck_id:
                solara.Error(f"⚠️ Anomaly Detected: Truck {model.bad_truck_id}", 
                             style={"margin-top": "20px"})

    def render_table(self, model):
        """
        Extracts agent data from the Mesa model and displays it in a DataFrame.
        """
        truck_data = []
        for agent in model.agents:
            if isinstance(agent, TruckAgent):
                # Access fields from the TruckAgent instance
                truck_data.append({
                    "Truck ID": agent.fields.truck_id,
                    "Pos X": round(agent.fields.position[0], 2),
                    "Pos Y": round(agent.fields.position[1], 2),
                    "Cargo": agent.fields.cargo_type,
                    "Status": "Moving" if not model._all_trucks_reached_goal() else "Arrived"                })
        
        with solara.Card("Fleet Real-time Status"):
            if truck_data:
                solara.DataFrame(pd.DataFrame(truck_data), items_per_page=5)
            else:
                solara.Info("Waiting for agents to initialize...")

    def build_layout(self, is_running):
        """
        Main layout builder that organizes the dashboard structure.
        """
        model = self.model_state.value
        with solara.Column(style={"gap": "20px"}):
            solara.Title("Freight Transport Monitoring System")
            with solara.Row(gap="20px"):
                self.render_controls(model, is_running)
                with solara.Column(style={"flex-grow": "1"}):
                    self.render_table(model)

# --- SOLARA APPLICATION ENTRY POINT ---

@solara.component
def Page():
    """
    Main component that manages the simulation lifecycle and reactive state.
    """
    # Reactive states for the model instance and the execution loop
    model_instance = solara.use_memo(lambda: FreightSimulationModel(rng=SIM_SEED), [])
    model_state = solara.use_reactive(model_instance)
    is_running = solara.use_reactive(False)

    # Instantiate the dashboard helper class
    ui_instance = solara.use_memo(lambda: SimulationDashboard(model_state), [])

    def simulation_loop():
        """
        Background thread that advances the model while is_running is True.
        """
        while is_running.value:
            # Advance simulation by one step
            model_state.value.step()
            
            # Update the reactive state to trigger a UI re-render
            model_state.set(model_state.value)
            
            # Check for auto-stop condition as defined in README
            if hasattr(model_state.value, 'running') and not model_state.value.running:
                is_running.set(False)
                break
                
            time.sleep(0.1)

    # Manage the lifecycle of the simulation loop thread
    solara.use_thread(simulation_loop, dependencies=[is_running.value])

    # Render the final layout
    with solara.Column(style={"padding": "20px", "background-color": "#f0f2f5", "min-height": "100vh"}):
        ui_instance.build_layout(is_running)