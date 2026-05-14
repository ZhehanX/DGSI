"""
Turn Engine Logic Specification (derived from week7.pdf)

1. Orchestration:
   - Read today's signals from scenario.json.
   - Inject customer demand (POST /api/orders to Retailer).
   - Run each role's decisions (Subprocess: gemini -p).
   - Advance all apps to the next day (POST /api/day/advance).
   - Log everything.

2. Demand Generation Logic:
   def generate_customer_demand(day, signal, retailer_prices, base_price):
       base = signal.get("base_demand", {"mean": 5, "variance": 2})
       modifier = signal.get("demand_modifier", 1.0)
       orders = []
       for model, price in retailer_prices.items():
           mean_orders = base["mean"] * modifier
           price_factor = max(0.2, 1.0 - (price - base_price) / base_price)
           adjusted_mean = mean_orders * price_factor
           n = max(0, int(random.gauss(adjusted_mean, base["variance"])))
           orders.extend([(model, 1)] * n)
       return orders

3. Agent Invocation:
   def run_agent_or_stub(role, skill_path, context, cwd):
       if skill_path is None:
           print(f"[stub] {role} would make decisions here")
           return
       prompt = f"Read the skill file at {skill_path}. Today's context: {context}. Execute your daily decisions following the skill's decision framework. Do NOT advance the day - the turn engine does that."
       result = subprocess.run(
           ["gemini", "-p", prompt],           capture_output=True, text=True, cwd=cwd, timeout=180
       )
       Path(f"logs/day-{day:03d}-{role}.log").write_text(result.stdout)

4. Sequence Diagram Order:
   Market Signals -> Customer Demand -> Retailer Turn -> Manufacturer Turn -> Provider Turn -> Advance All.
"""
