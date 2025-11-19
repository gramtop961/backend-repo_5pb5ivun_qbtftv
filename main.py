import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import AroniaProduct, Order, OrderItem

app = FastAPI(title="Aronia Pure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Aronia Pure Backend is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# ---------- Product Endpoints ----------
@app.get("/api/products", response_model=List[AroniaProduct])
def list_products():
    """Return the available Aronia products (from DB if present, else seed a default)."""
    try:
        items = get_documents("aroniaproduct", {})
    except Exception:
        items = []

    if not items:
        # Seed a default product if DB empty/unavailable
        default = AroniaProduct()
        try:
            create_document("aroniaproduct", default)
            items = [default.model_dump()]
        except Exception:
            items = [default.model_dump()]
    else:
        # Convert ObjectId etc. to plain dict
        items = [
            {
                "title": i.get("title"),
                "description": i.get("description"),
                "price": float(i.get("price", 0)),
                "category": i.get("category"),
                "in_stock": bool(i.get("in_stock", True)),
                "image_url": i.get("image_url"),
                "sku": i.get("sku"),
                "volume_ml": int(i.get("volume_ml", 750)),
            }
            for i in items
        ]
    return items

# ---------- Checkout Endpoint ----------
@app.post("/api/checkout")
def create_order(order: Order):
    """Create an order and return an order id. Payment integration can be added later."""
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    # Basic total calculation (server-side)
    total = sum(item.unit_price * item.quantity for item in order.items)

    # Persist to DB if available
    payload = order.model_dump()
    payload["total_amount"] = float(total)

    try:
        order_id = create_document("order", payload)
        return {"status": "ok", "order_id": order_id, "total_amount": total}
    except Exception:
        # Fallback if DB is not configured
        return {"status": "ok", "order_id": None, "total_amount": total}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db as _db
        
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
