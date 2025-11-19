"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image_url: Optional[str] = Field(None, description="Main product image")
    sku: Optional[str] = Field(None, description="Stock keeping unit")
    volume_ml: Optional[int] = Field(None, description="Volume in milliliters")

# Aronia-specific product
class AroniaProduct(BaseModel):
    title: str = Field("Aronia Pure - 100% Chokeberry Juice")
    description: str = Field(
        "Cold-pressed from fresh aronia berries, unfiltered to retain natural goodness. Tart, rich, and invigorating."
    )
    price: float = Field(12.90, ge=0)
    category: str = Field("Beverages")
    in_stock: bool = True
    image_url: Optional[str] = Field(
        "https://images.unsplash.com/photo-1626595424320-b872d5efaa11?auto=format&fit=crop&w=1600&q=80"
    )
    sku: str = Field("ARONIA-750ML")
    volume_ml: int = Field(750, ge=50)

# Order schema for checkout
class OrderItem(BaseModel):
    product_sku: str
    title: str
    unit_price: float
    quantity: int = Field(1, ge=1, le=24)

class Order(BaseModel):
    customer_name: str
    customer_email: EmailStr
    shipping_address: str
    items: List[OrderItem]
    notes: Optional[str] = None

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
