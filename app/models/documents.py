from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class ProductDocument(BaseModel):
    product_id: str
    product_name: str
    category: str
    brand: str
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    compatibility: Optional[str] = None
    price_inr: Optional[int] = None
    mrp_inr: Optional[int] = None
    discount_percent: Optional[int] = None
    availability: Optional[str] = None
    stock_quantity: Optional[int] = None
    sku: Optional[str] = None
    description: str
    features: Optional[str] = None
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None


class OrganizationDocument(BaseModel):
    filename: str
    content: str
    metadata: Dict[str, Any] = {}


class ChunkedDocument(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]