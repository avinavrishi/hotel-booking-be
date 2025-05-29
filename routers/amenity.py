from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database.models import Amenity, Property, property_amenity
from database.session import get_db
from routers.request_models.amenity_models import AmenityBase, AmenityOut
from decorator.jwt_decorator import jwt_authorization

router = APIRouter()


@router.get("/amenities", response_model=List[AmenityOut])
def list_amenities(db: Session = Depends(get_db)):
    return db.query(Amenity).all()


@router.post("/amenities", response_model=AmenityOut)
def add_amenity(
    amenity: AmenityBase,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    if not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can add amenities")

    new_amenity = Amenity(name=amenity.name)
    db.add(new_amenity)
    db.commit()
    db.refresh(new_amenity)
    return new_amenity


@router.put("/amenities/{amenity_id}", response_model=AmenityOut)
def update_amenity(
    amenity_id: int,
    update_data: AmenityBase,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    if not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can update amenities")

    amenity = db.query(Amenity).filter(Amenity.amenity_id == amenity_id).first()
    if not amenity:
        raise HTTPException(status_code=404, detail="Amenity not found")

    amenity.name = update_data.name
    db.commit()
    db.refresh(amenity)
    return amenity


@router.delete("/amenities/{amenity_id}")
def delete_amenity(
    amenity_id: int,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    if not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can delete amenities")

    amenity = db.query(Amenity).filter(Amenity.amenity_id == amenity_id).first()
    if not amenity:
        raise HTTPException(status_code=404, detail="Amenity not found")

    db.delete(amenity)
    db.commit()
    return {"msg": "Amenity deleted"}


@router.post("/properties/{property_id}/amenities")
def assign_amenities_to_property(
    property_id: int,
    amenity_ids: List[int],
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    property_obj = db.query(Property).filter(Property.property_id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    if token_data["user_id"] != property_obj.owner_id and not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized to assign amenities")

    for aid in amenity_ids:
        exists = db.query(Amenity).filter(Amenity.amenity_id == aid).first()
        if not exists:
            raise HTTPException(status_code=404, detail=f"Amenity {aid} not found")

    # Delete old relations first
    db.execute(property_amenity.delete().where(property_amenity.c.property_id == property_id))

    # Insert new relations
    insert_stmt = property_amenity.insert().values([
        {"property_id": property_id, "amenity_id": aid} for aid in amenity_ids
    ])
    db.execute(insert_stmt)
    db.commit()

    return {"msg": "Amenities assigned successfully"}
