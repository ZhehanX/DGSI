# Week 7: The Automated Supply Chain - Agent Instructions

## Core Mandates
- **Surgical Implementation**: Follow the specs in `docs/prd.md` (derived from `week7.pdf`) precisely.
- **REST-First**: Ensure all new functionality is exposed via REST for the Turn Engine.
- **Agentic Compatibility**: When writing CLI commands, ensure they are descriptive and error-resilient for LLM agents.

## Implementation Details
### Retailer App
- Run multiple instances using different config files (e.g., `--config retailer-1.json --port 8003`).
- Markup: Minimum 15% above manufacturer wholesale.
- Auto-fulfillment: On `day advance`, check if backordered items can now be fulfilled.

### Manufacturer Updates
- Orders Table: Add a `direction` column (inbound/outbound) or use a separate `sales_orders` table.
- Capacity: Track daily capacity and utilization.

### Turn Engine (`turn_engine.py`)
- Sequence: Retailer Turn -> Manufacturer Turn -> Provider Turn.
- Order Generation Logic:
  ```python
  price_factor = max(0.2, 1.0 - (price - base_price) / base_price)
  n = max(0, int(random.gauss(adjusted_mean, variance)))
  ```
- Agent Call: `subprocess.run(["gemini", "-p", prompt], ...)`

## Development Workflow
1.  **Retailer Implementation**: Build the Retailer app from scratch (or base it on the Provider/Manufacturer pattern).
2.  **Manufacturer Update**: Adapt the Manufacturer app to accept inbound orders from Retailers.
3.  **Turn Engine**: Implement `turn_engine.py` to orchestrate the three apps.
4.  **Skill File**: Draft `skills/manufacturer-manager.md` and test it with `gemini -p "some prompt"`.
5.  **Proof of Concept**: Run a 3-day simulation and verify agent logs.

## Technical Details
- **Retailer Port**: 8003 (default)
- **Manufacturer Port**: 8002
- **Provider Port**: 8001
- **Log Location**: `DGSI-week-07/logs/`
- **Agent Timeout**: 180 seconds

## Verification Checklist
- Run `./retailer-cli serve` and verify `GET /api/catalog`.
- Run `python turn_engine.py config/sim.json scenarios/smoke-test.json 1`.
- Check `logs/` for agent output.
