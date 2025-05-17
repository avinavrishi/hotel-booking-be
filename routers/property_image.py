from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from database.models import Property, PropertyImage
from decorator.jwt_decorator import jwt_authorization
from routers.request_models.property_image_models import PropertyImageCreate, PropertyImageUpdate, PropertyImageOut
from typing import List

router = APIRouter()


@router.post("/properties/{property_id}/images", response_model=PropertyImageOut)
def upload_image(
    property_id: int,
    image_data: PropertyImageCreate,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    property_obj = db.query(Property).filter(Property.property_id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    if token_data["user_id"] != property_obj.owner_id and not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized to add images")

    new_image = PropertyImage(property_id=property_id, **image_data.dict())
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


@router.get("/properties/{property_id}/images", response_model=List[PropertyImageOut])
def list_property_images(property_id: int, db: Session = Depends(get_db)):
    images = db.query(PropertyImage).filter(PropertyImage.property_id == property_id).all()
    return images


@router.put("/properties/images/{image_id}", response_model=PropertyImageOut)
def update_property_image(
    image_id: int,
    update_data: PropertyImageUpdate,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    image = db.query(PropertyImage).filter(PropertyImage.image_id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    prop = db.query(Property).filter(Property.property_id == image.property_id).first()
    if token_data["user_id"] != prop.owner_id and not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update image")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(image, key, value)

    db.commit()
    db.refresh(image)
    return image


@router.delete("/properties/images/{image_id}")
def delete_property_image(
    image_id: int,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    image = db.query(PropertyImage).filter(PropertyImage.image_id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    prop = db.query(Property).filter(Property.property_id == image.property_id).first()
    if token_data["user_id"] != prop.owner_id and not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized to delete image")

    db.delete(image)
    db.commit()
    return {"msg": "Image deleted successfully"}
