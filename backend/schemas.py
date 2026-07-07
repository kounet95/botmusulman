from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time


class ActivityCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = "cours"
    date: date
    time: time
    capacity: int
    is_paid: bool = False
    price: Optional[float] = None
    speaker: Optional[str] = None
    location: Optional[str] = "Mosquée"
    livestream_url: Optional[str] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    capacity: Optional[int] = None
    is_paid: Optional[bool] = None
    price: Optional[float] = None
    speaker: Optional[str] = None
    location: Optional[str] = None
    livestream_url: Optional[str] = None


class ContentCreate(BaseModel):
    type: str  # hadith | verset | rappel | dua
    content_ar: Optional[str] = None
    content_fr: Optional[str] = None
    content_en: Optional[str] = None
    source: Optional[str] = None
    scheduled_date: date


class DonationCampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = "general"
    goal_amount: Optional[float] = None
    payment_url: Optional[str] = None
    orange_money_number: Optional[str] = None
    mtn_momo_number: Optional[str] = None


class AnnouncementCreate(BaseModel):
    title: str
    body: str
    send_now: bool = False


class SignupRequest(BaseModel):
    mosque_name: str
    city: str
    country: str = "GN"
    email: str
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class MosqueProfileUpdate(BaseModel):
    installation_type: Optional[str] = None  # mosque | ecole | salle_priere | domicile | magasin
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None  # quartier
    postal_code: Optional[str] = None
    country: Optional[str] = None
    association_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    payment_url: Optional[str] = None
    amenities: Optional[list[str]] = None
    construction_year: Optional[int] = None
    capacity_women: Optional[int] = None
    capacity_men: Optional[int] = None
    history: Optional[str] = Field(default=None, max_length=200)
    other_info: Optional[str] = Field(default=None, max_length=200)
