import hashlib
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def init_db(app):
    """Create tables and seed sample data if the DB is empty."""
    # Import models here to avoid circular imports
    from models import Category, Product, User

    db.create_all()

    # ── Seed Categories ──────────────────────────────────────────────────────
    if Category.query.count() == 0:
        cats = [
            Category(name='Coffee',    icon='\u2615', description='Freshly brewed espresso-based drinks'),
            Category(name='Milk Tea',  icon='\U0001f9cb', description='Classic & flavoured milk teas'),
            Category(name='Fruit Tea', icon='\U0001f353', description='Refreshing fruit-infused teas'),
            Category(name='Smoothies', icon='\U0001f964', description='Thick blended fruit smoothies'),
            Category(name='Matcha',    icon='\U0001f375', description='Premium Japanese matcha drinks'),
            Category(name='Seasonal',  icon='\U0001f338', description='Limited seasonal specials'),
        ]
        db.session.bulk_save_objects(cats)
        db.session.commit()

    # ── Seed Products ─────────────────────────────────────────────────────────
    if Product.query.count() == 0:
        cat = {c.name: c.id for c in Category.query.all()}

        products = [
            # Coffee
            Product(name='Classic Americano',    price=3.50, category_id=cat['Coffee'],
                    description='Bold espresso with hot water. Clean, rich, and energising.',
                    image_url='https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Creamy Latte',          price=4.50, category_id=cat['Coffee'],
                    description='Smooth espresso with velvety steamed milk and light foam.',
                    image_url='https://images.unsplash.com/photo-1561047029-3000c68339ca?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Caramel Macchiato',     price=5.20, category_id=cat['Coffee'],
                    description='Layered espresso, vanilla syrup, milk and caramel drizzle.',
                    image_url='https://images.unsplash.com/photo-1485808191679-5f86510bd9d7?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Cold Brew',             price=4.80, category_id=cat['Coffee'],
                    description='Slow-steeped 18-hour cold brew, served over ice.',
                    image_url='https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&q=80',
                    is_available=True, is_featured=False),
            Product(name='Dalgona Whip Coffee',   price=5.50, category_id=cat['Coffee'],
                    description='Whipped coffee cloud on silky milk — a viral classic.',
                    image_url='https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400&q=80',
                    is_available=True, is_featured=False),

            # Milk Tea
            Product(name='Classic Pearl Milk Tea', price=4.20, category_id=cat['Milk Tea'],
                    description='Taiwanese black tea with chewy tapioca pearls and fresh milk.',
                    image_url='https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Taro Milk Tea',           price=4.50, category_id=cat['Milk Tea'],
                    description='Creamy taro with fresh milk and pearls. Subtly sweet, gorgeous purple.',
                    image_url='https://images.unsplash.com/photo-1546173159-315724a31696?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Brown Sugar Boba',        price=5.00, category_id=cat['Milk Tea'],
                    description='Tiger-stripe caramelised brown sugar with fresh milk and pearls.',
                    image_url='https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400&q=80',
                    is_available=True, is_featured=False),
            Product(name='Hokkaido Milk Tea',       price=4.80, category_id=cat['Milk Tea'],
                    description='Rich Japanese Hokkaido milk with premium black tea.',
                    image_url='https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400&q=80',
                    is_available=True, is_featured=False),

            # Fruit Tea
            Product(name='Passion Fruit Green Tea', price=4.00, category_id=cat['Fruit Tea'],
                    description='Zesty passion fruit with light green tea and real fruit chunks.',
                    image_url='https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Lychee Rose Tea',          price=4.30, category_id=cat['Fruit Tea'],
                    description='Floral rose tea with sweet lychee jelly and fresh lychee.',
                    image_url='https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80',
                    is_available=True, is_featured=False),
            Product(name='Strawberry Lemonade Tea',  price=4.50, category_id=cat['Fruit Tea'],
                    description='Tangy lemonade blended with strawberry puree over green tea.',
                    image_url='https://images.unsplash.com/photo-1497534446932-c925b458314e?w=400&q=80',
                    is_available=True, is_featured=False),

            # Smoothies
            Product(name='Mango Tango Smoothie',   price=5.50, category_id=cat['Smoothies'],
                    description='Thick blended Alphonso mango with yoghurt and a hint of lime.',
                    image_url='https://images.unsplash.com/photo-1546173159-315724a31696?w=400&q=80',
                    is_available=True, is_featured=False),
            Product(name='Berry Blast Smoothie',   price=5.80, category_id=cat['Smoothies'],
                    description='Mixed strawberry, blueberry, raspberry blended with oat milk.',
                    image_url='https://images.unsplash.com/photo-1502741338009-cac2772e18bc?w=400&q=80',
                    is_available=True, is_featured=False),
            Product(name='Avocado Coconut Blend',  price=6.00, category_id=cat['Smoothies'],
                    description='Creamy avocado with coconut milk and a pinch of sea salt.',
                    image_url='https://images.unsplash.com/photo-1610970881699-44a5587cabec?w=400&q=80',
                    is_available=True, is_featured=False),

            # Matcha
            Product(name='Matcha Latte',        price=5.00, category_id=cat['Matcha'],
                    description='Ceremonial grade matcha whisked with steamed oat milk.',
                    image_url='https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Iced Matcha Coconut', price=5.50, category_id=cat['Matcha'],
                    description='Vibrant iced matcha layered over chilled coconut milk.',
                    image_url='https://images.unsplash.com/photo-1594631252845-29fc4cc8cde9?w=400&q=80',
                    is_available=True, is_featured=False),

            # Seasonal
            Product(name='Sakura Cherry Blossom', price=6.00, category_id=cat['Seasonal'],
                    description='Limited spring special — cherry blossom milk tea with sakura jelly.',
                    image_url='https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&q=80',
                    is_available=True, is_featured=True),
            Product(name='Pumpkin Spice Latte',   price=5.80, category_id=cat['Seasonal'],
                    description='Autumn special — pumpkin puree with spiced espresso and cream.',
                    image_url='https://images.unsplash.com/photo-1455099929960-93d9b07f5d54?w=400&q=80',
                    is_available=True, is_featured=False),
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()

    # ── Seed Admin User ───────────────────────────────────────────────────────
    if User.query.count() == 0:
        admin = User(username='admin', password_hash=hash_password('admin123'), is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print('Admin created: username=admin / password=admin123')

    print('Database initialised with sample data.')
