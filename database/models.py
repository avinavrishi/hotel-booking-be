from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, JSON, ARRAY, Enum, Table, Float
from sqlalchemy.orm import relationship
from .session import Base
from sqlalchemy.sql import func
import enum
 
class BaseTable(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)

class User(BaseTable):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_admin = Column(Integer, nullable=True)
    is_staff = Column(Integer, nullable=True)

    # Relationships
    tokens = relationship('Token', back_populates='user')  # Added relationship'
    profile = relationship('UserProfile', back_populates='user')


class Token(Base):
    __tablename__ = 'tokens'

    token_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    token_type = Column(String, nullable=False)  # e.g., 'access' or 'refresh'
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    profile = relationship('UserProfile', back_populates='user', uselist=False)


class UserProfile(BaseTable):
    __tablename__ = 'user_profiles'

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True, nullable=False)

    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String, nullable=True)  # URL to image
    nationality = Column(String, nullable=True)
    preferred_language = Column(String, default='en')

    user = relationship('User', back_populates='profile')


class Property(BaseTable):
    __tablename__ = 'properties'

    property_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price_per_night = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    max_guests = Column(Integer, nullable=False)
    property_type = Column(String, nullable=False)  # apartment, villa, etc.
    is_available = Column(Integer, default=1)  # 1 = true, 0 = false

    owner = relationship('User')
    images = relationship('PropertyImage', back_populates='property')
    bookings = relationship('Booking', back_populates='property')


class PropertyImage(BaseTable):
    __tablename__ = 'property_images'

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.property_id'), nullable=False)
    image_url = Column(String, nullable=False)
    is_cover = Column(Integer, default=0)

    property = relationship('Property', back_populates='images')

class Amenity(Base):
    __tablename__ = 'amenities'

    amenity_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)


"""
used to define a many-to-many relationship where:
One property can have many amenities
One amenity can be linked to many properties
"""
property_amenity = Table(
    'property_amenity',
    Base.metadata,
    Column('property_id', Integer, ForeignKey('properties.property_id')),
    Column('amenity_id', Integer, ForeignKey('amenities.amenity_id'))
)

class BookingStatus(str, enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    cancelled = 'cancelled'
    completed = 'completed'


class Booking(BaseTable):
    __tablename__ = 'bookings'

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    traveler_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    property_id = Column(Integer, ForeignKey('properties.property_id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    guests = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    total_price = Column(Float, nullable=False)

    property = relationship('Property', back_populates='bookings')
    traveler = relationship('User')

class Package(BaseTable):
    __tablename__ = 'packages'

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.property_id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    discount_percent = Column(Float)
    min_nights = Column(Integer)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)

    property = relationship('Property')


class Review(BaseTable):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id'), nullable=False)
    traveler_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    property_id = Column(Integer, ForeignKey('properties.property_id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(Text)

    traveler = relationship('User')
    booking = relationship('Booking')
    property = relationship('Property')


class Payment(BaseTable):
    __tablename__ = 'payments'

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id'), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # paid, refunded, failed
    payment_method = Column(String)  # stripe, paypal
    transaction_id = Column(String)

    booking = relationship('Booking')


