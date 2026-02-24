from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis_client import redis_client
import json
from database import engine, Base, get_db
from models import Item
from schemas import ItemCreate, ItemResponse

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(data: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = Item(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)

    await redis_client.delete("items:all")
    return item

@app.get("/items", response_model=list[ItemResponse])
async def get_items(search: str | None = None, db: AsyncSession = Depends(get_db)):
    cached = await redis_client.get("items:all")
    if cached:
        print(">>> cache HIT")
        return json.loads(cached)
    
    print(">>> cache MISS")

    query = select(Item)
    if search:
        query = query.where(Item.title.ilike(f"%{search}%"))
    result = await db.execute(query)
    items = result.scalars().all()



    items_data = [ItemResponse.model_validate(i).model_dump() for i in items]
    await redis_client.set("items:all", json.dumps(items_data), ex=30)

    return items


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item_by_id(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
        
    return item

@app.delete("/items/{item_id}", status_code=204)
async def remove_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    await db.delete(item)
    await db.commit()
    return None

