from enum import Enum

from pydantic import BaseModel


class Category(Enum):
    TOOLS = 'tools'
    CONSUMABLES = 'consumables'

class Item(BaseModel):
    name: str
    price: float
    count: int
    id: int
    category: Category

items = {
    0: Item(name='Hammer', price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name='Pliers', price=5.99, count=20, id=1, category=Category.TOOLS),
    2: Item(name='Nails', price=1.99, count=100, id=2, category=Category.CONSUMABLES),
}
