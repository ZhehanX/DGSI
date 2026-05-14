# DGSI Week 7: The Automated Supply Chain

This project completes the supply chain simulation by adding a Retailer app and automating the flow using a Turn Engine and Gemini CLI agents.

## Project Structure
- `provider/`: Part supplier app (Port 8001)
- `manufacturer/`: 3D printer factory app (Port 8002)
- `retailer/`: Printer retail store app (Port 8003)
- `turn_engine.py`: Orchestration script
- `skills/`: Markdown files teaching Gemini CLI how to play roles
- `config/`: System configuration
- `scenarios/`: Simulation scenarios (demand, market signals)
- `logs/`: Agent output logs

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Apps
You need three terminal windows:
```bash
# Window 1
cd provider && ./provider-cli serve --port 8001
# Window 2
cd manufacturer && ./manufacturer-cli serve --port 8002
# Window 3
cd retailer && ./retailer-cli serve --port 8003
```

### 3. Run the Simulation
```bash
python turn_engine.py config/sim.json scenarios/smoke-test.json 3
```

## Deliverables
- [x] Retailer App implementation
- [x] Manufacturer App updates (Sales orders)
- [x] Turn Engine script
- [x] Manufacturer Manager skill file
- [x] PRD and Short Report
