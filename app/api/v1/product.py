from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.model.product import Produit
from app.model.user import User
from app.schemas import ProduitCreate, ProduitResponse

router = APIRouter(prefix="/produits", tags=["Produits"])

@router.post("/", response_model=ProduitResponse, status_code=status.HTTP_201_CREATED)
def create_produit(produit: ProduitCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == produit.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    existing_produit = db.query(Produit).filter(Produit.name == produit.name).first()
    if existing_produit:
        raise HTTPException(status_code=400, detail="Produit déjà existant")

    new_produit = Produit(**produit.dict())
    db.add(new_produit)
    db.commit()
    db.refresh(new_produit)
    return new_produit

@router.get("/{produit_id}", response_model=ProduitResponse)
def get_produit(produit_id: int, db: Session = Depends(get_db)):
    produit = db.query(Produit).filter(Produit.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit

@router.get("/", response_model=list[ProduitResponse])
def list_produits(db: Session = Depends(get_db)):
    produits = db.query(Produit).all()
    return produits
