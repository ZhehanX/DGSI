import typer
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.services.provider_service import ProviderService
from app.services.seed import seed_provider_data
import uvicorn

app = typer.Typer()
orders_app = typer.Typer()
app.add_typer(orders_app, name="orders")

@app.command()
def seed():
    """Seed the provider database with initial data."""
    init_db()
    db = SessionLocal()
    try:
        seed_provider_data(db)
    finally:
        db.close()

@app.command()
def catalog():
    """List products in the catalog."""
    db = SessionLocal()
    service = ProviderService(db)
    products = service.get_catalog()
    for p in products:
        typer.echo(f"ID: {p.id} | Name: {p.name} | Lead Time: {p.lead_time_days} days")
        for tier in p.pricing_tiers:
            typer.echo(f"  - Min Qty: {tier.min_quantity} | Unit Price: {tier.unit_price}€")
    db.close()

@app.command()
def stock():
    """Show current provider inventory."""
    db = SessionLocal()
    service = ProviderService(db)
    stocks = service.get_stock()
    for s in stocks:
        typer.echo(f"Product ID: {s.product_id} | Quantity: {s.quantity}")
    db.close()

@orders_app.command("list")
def list_orders(status: str = None):
    """List all orders."""
    db = SessionLocal()
    service = ProviderService(db)
    orders = service.get_orders(status=status)
    for o in orders:
        typer.echo(f"ID: {o.id} | Buyer: {o.buyer} | Product ID: {o.product_id} | Qty: {o.quantity} | Status: {o.status}")
    db.close()

@orders_app.command("show")
def show_order(order_id: int):
    """Show order details."""
    db = SessionLocal()
    service = ProviderService(db)
    o = service.get_order(order_id)
    if o:
        typer.echo(f"ID: {o.id}")
        typer.echo(f"Buyer: {o.buyer}")
        typer.echo(f"Product ID: {o.product_id}")
        typer.echo(f"Quantity: {o.quantity}")
        typer.echo(f"Unit Price: {o.unit_price}€")
        typer.echo(f"Total Price: {o.total_price}€")
        typer.echo(f"Status: {o.status}")
        typer.echo(f"Placed Day: {o.placed_day}")
        typer.echo(f"Expected Delivery Day: {o.expected_delivery_day}")
    else:
        typer.echo("Order not found")
    db.close()

@app.command()
def restock(product_id: int, quantity: int):
    """Add stock to a product."""
    db = SessionLocal()
    service = ProviderService(db)
    service.restock(product_id, quantity)
    typer.echo(f"Added {quantity} to product {product_id}")
    db.close()

@app.command("day-advance")
def day_advance():
    """Advance simulated time."""
    db = SessionLocal()
    service = ProviderService(db)
    new_day = service.advance_day()
    typer.echo(f"Advanced to day {new_day}")
    db.close()

@app.command("day-current")
def day_current():
    """Show current day."""
    db = SessionLocal()
    service = ProviderService(db)
    day = service.get_current_day()
    typer.echo(f"Current Day: {day}")
    db.close()

@app.command()
def serve(port: int = 8001):
    """Start the Provider API."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    app()
