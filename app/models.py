from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for better type safety and data consistency
class PlatformType(str, Enum):
    THUMBTACK = "thumbtack"
    TASKRABBIT = "taskrabbit"
    CRAIGSLIST = "craigslist"
    GOOGLE_ADS = "google_ads"
    FACEBOOK_ADS = "facebook_ads"
    TIKTOK_ADS = "tiktok_ads"


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class BusinessCategory(str, Enum):
    HOME_SERVICES = "home_services"
    PROFESSIONAL_SERVICES = "professional_services"
    HEALTH_FITNESS = "health_fitness"
    EVENTS_ENTERTAINMENT = "events_entertainment"
    AUTOMOTIVE = "automotive"
    FOOD_BEVERAGE = "food_beverage"
    RETAIL = "retail"
    OTHER = "other"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    business: Optional["Business"] = Relationship(back_populates="owner")
    messages: List["Message"] = Relationship(back_populates="user")


class Business(SQLModel, table=True):
    __tablename__ = "businesses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=200)
    category: BusinessCategory = Field(default=BusinessCategory.OTHER)
    description: str = Field(max_length=1000)
    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    state: str = Field(max_length=50)
    zip_code: str = Field(max_length=10)
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: User = Relationship(back_populates="business")
    services: List["Service"] = Relationship(back_populates="business")
    platform_accounts: List["PlatformAccount"] = Relationship(back_populates="business")
    leads: List["Lead"] = Relationship(back_populates="business")
    subscriptions: List["Subscription"] = Relationship(back_populates="business")
    analytics: List["Analytics"] = Relationship(back_populates="business")


class Service(SQLModel, table=True):
    __tablename__ = "services"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    name: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    price_min: Optional[Decimal] = Field(default=None, decimal_places=2)
    price_max: Optional[Decimal] = Field(default=None, decimal_places=2)
    duration_hours: Optional[int] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    business: Business = Relationship(back_populates="services")
    leads: List["Lead"] = Relationship(back_populates="service")


class PlatformAccount(SQLModel, table=True):
    __tablename__ = "platform_accounts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    platform_type: PlatformType
    account_id: str = Field(max_length=255)
    account_name: str = Field(max_length=255)
    credentials: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    last_sync: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    business: Business = Relationship(back_populates="platform_accounts")
    leads: List["Lead"] = Relationship(back_populates="platform_account")
    campaigns: List["Campaign"] = Relationship(back_populates="platform_account")


class Campaign(SQLModel, table=True):
    __tablename__ = "campaigns"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    platform_account_id: int = Field(foreign_key="platform_accounts.id")
    name: str = Field(max_length=255)
    campaign_type: str = Field(max_length=100)  # listing, ad, etc.
    budget: Optional[Decimal] = Field(default=None, decimal_places=2)
    target_keywords: List[str] = Field(default=[], sa_column=Column(JSON))
    target_location: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    platform_account: PlatformAccount = Relationship(back_populates="campaigns")
    leads: List["Lead"] = Relationship(back_populates="campaign")


class Lead(SQLModel, table=True):
    __tablename__ = "leads"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    platform_account_id: int = Field(foreign_key="platform_accounts.id")
    campaign_id: Optional[int] = Field(default=None, foreign_key="campaigns.id")
    service_id: Optional[int] = Field(default=None, foreign_key="services.id")

    # Lead contact information
    customer_name: str = Field(max_length=200)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    customer_phone: Optional[str] = Field(default=None, max_length=20)

    # Lead details
    title: str = Field(max_length=300)
    description: str = Field(max_length=2000)
    budget: Optional[Decimal] = Field(default=None, decimal_places=2)
    location: str = Field(max_length=200)
    status: LeadStatus = Field(default=LeadStatus.NEW)

    # Platform-specific data
    platform_lead_id: str = Field(max_length=255)
    platform_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Tracking
    cost: Optional[Decimal] = Field(default=None, decimal_places=2)
    conversion_value: Optional[Decimal] = Field(default=None, decimal_places=2)
    converted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    business: Business = Relationship(back_populates="leads")
    platform_account: PlatformAccount = Relationship(back_populates="leads")
    campaign: Optional[Campaign] = Relationship(back_populates="leads")
    service: Optional[Service] = Relationship(back_populates="leads")
    messages: List["Message"] = Relationship(back_populates="lead")


class Message(SQLModel, table=True):
    __tablename__ = "messages"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="leads.id")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    sender_name: str = Field(max_length=200)
    sender_email: Optional[str] = Field(default=None, max_length=255)
    content: str = Field(max_length=5000)
    is_from_business: bool = Field(default=False)
    is_read: bool = Field(default=False)
    attachments: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lead: Lead = Relationship(back_populates="messages")
    user: Optional[User] = Relationship(back_populates="messages")


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    plan_name: str = Field(max_length=100)
    price: Decimal = Field(decimal_places=2)
    billing_cycle: str = Field(max_length=20)  # monthly, yearly
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    features: List[str] = Field(default=[], sa_column=Column(JSON))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    business: Business = Relationship(back_populates="subscriptions")
    payments: List["Payment"] = Relationship(back_populates="subscription")


class Payment(SQLModel, table=True):
    __tablename__ = "payments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    subscription_id: int = Field(foreign_key="subscriptions.id")
    amount: Decimal = Field(decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: str = Field(max_length=50)  # card, bank_transfer, etc.
    transaction_id: Optional[str] = Field(default=None, max_length=255)
    processor_response: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    processed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    subscription: Subscription = Relationship(back_populates="payments")


class Analytics(SQLModel, table=True):
    __tablename__ = "analytics"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    date: datetime
    platform_type: Optional[PlatformType] = Field(default=None)

    # Metrics
    leads_count: int = Field(default=0)
    qualified_leads_count: int = Field(default=0)
    converted_leads_count: int = Field(default=0)
    total_spend: Decimal = Field(default=Decimal("0"), decimal_places=2)
    total_revenue: Decimal = Field(default=Decimal("0"), decimal_places=2)
    cost_per_lead: Optional[Decimal] = Field(default=None, decimal_places=2)
    conversion_rate: Optional[Decimal] = Field(default=None, decimal_places=4)

    # Additional metrics
    metrics: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    business: Business = Relationship(back_populates="analytics")


class Recommendation(SQLModel, table=True):
    __tablename__ = "recommendations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    type: str = Field(max_length=100)  # platform_suggestion, budget_optimization, etc.
    title: str = Field(max_length=300)
    description: str = Field(max_length=1000)
    priority: int = Field(default=1)  # 1=high, 2=medium, 3=low
    impact_score: Optional[int] = Field(default=None)  # 1-10 scale
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    is_dismissed: bool = Field(default=False)
    dismissed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EmailAlert(SQLModel, table=True):
    __tablename__ = "email_alerts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    alert_type: str = Field(max_length=100)  # new_lead, lead_converted, etc.
    recipient_email: str = Field(max_length=255)
    subject: str = Field(max_length=500)
    content: str = Field(max_length=5000)
    sent_at: Optional[datetime] = Field(default=None)
    delivery_status: str = Field(default="pending", max_length=50)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=255)


class UserUpdate(SQLModel, table=False):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


class BusinessCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    category: BusinessCategory = Field(default=BusinessCategory.OTHER)
    description: str = Field(max_length=1000)
    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    state: str = Field(max_length=50)
    zip_code: str = Field(max_length=10)
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)


class BusinessUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    category: Optional[BusinessCategory] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=1000)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=50)
    zip_code: Optional[str] = Field(default=None, max_length=10)
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)


class ServiceCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    price_min: Optional[Decimal] = Field(default=None, decimal_places=2)
    price_max: Optional[Decimal] = Field(default=None, decimal_places=2)
    duration_hours: Optional[int] = Field(default=None)


class ServiceUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    price_min: Optional[Decimal] = Field(default=None, decimal_places=2)
    price_max: Optional[Decimal] = Field(default=None, decimal_places=2)
    duration_hours: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class PlatformAccountCreate(SQLModel, table=False):
    platform_type: PlatformType
    account_id: str = Field(max_length=255)
    account_name: str = Field(max_length=255)
    credentials: Dict[str, Any] = Field(default={})
    settings: Dict[str, Any] = Field(default={})


class PlatformAccountUpdate(SQLModel, table=False):
    account_name: Optional[str] = Field(default=None, max_length=255)
    credentials: Optional[Dict[str, Any]] = Field(default=None)
    settings: Optional[Dict[str, Any]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class LeadCreate(SQLModel, table=False):
    platform_account_id: int
    campaign_id: Optional[int] = Field(default=None)
    service_id: Optional[int] = Field(default=None)
    customer_name: str = Field(max_length=200)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    title: str = Field(max_length=300)
    description: str = Field(max_length=2000)
    budget: Optional[Decimal] = Field(default=None, decimal_places=2)
    location: str = Field(max_length=200)
    platform_lead_id: str = Field(max_length=255)
    platform_data: Dict[str, Any] = Field(default={})
    cost: Optional[Decimal] = Field(default=None, decimal_places=2)


class LeadUpdate(SQLModel, table=False):
    status: Optional[LeadStatus] = Field(default=None)
    conversion_value: Optional[Decimal] = Field(default=None, decimal_places=2)


class MessageCreate(SQLModel, table=False):
    lead_id: int
    sender_name: str = Field(max_length=200)
    sender_email: Optional[str] = Field(default=None, max_length=255)
    content: str = Field(max_length=5000)
    is_from_business: bool = Field(default=False)
    attachments: List[str] = Field(default=[])


class CampaignCreate(SQLModel, table=False):
    platform_account_id: int
    name: str = Field(max_length=255)
    campaign_type: str = Field(max_length=100)
    budget: Optional[Decimal] = Field(default=None, decimal_places=2)
    target_keywords: List[str] = Field(default=[])
    target_location: Dict[str, Any] = Field(default={})
    settings: Dict[str, Any] = Field(default={})


class CampaignUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=255)
    budget: Optional[Decimal] = Field(default=None, decimal_places=2)
    target_keywords: Optional[List[str]] = Field(default=None)
    target_location: Optional[Dict[str, Any]] = Field(default=None)
    settings: Optional[Dict[str, Any]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class SubscriptionCreate(SQLModel, table=False):
    plan_name: str = Field(max_length=100)
    price: Decimal = Field(decimal_places=2)
    billing_cycle: str = Field(max_length=20)
    features: List[str] = Field(default=[])


class PaymentCreate(SQLModel, table=False):
    subscription_id: int
    amount: Decimal = Field(decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    payment_method: str = Field(max_length=50)
