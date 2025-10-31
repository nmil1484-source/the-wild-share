"""
Database migrations for The Wild Share
Runs automatically on application startup
"""
from sqlalchemy import text
from src.models.user import db
import logging

logger = logging.getLogger(__name__)

def run_migrations(app):
    """Run all pending database migrations"""
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Migration 1: Add subscription fields to user table
                logger.info("Running migration: Add subscription fields to user table")
                
                # Check if columns exist before adding
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user'"))
                existing_columns = [row[0] for row in result]
                
                migrations = []
                
                if 'subscription_tier' not in existing_columns:
                    migrations.append("ALTER TABLE \"user\" ADD COLUMN subscription_tier VARCHAR(20) DEFAULT 'free'")
                
                if 'stripe_customer_id' not in existing_columns:
                    migrations.append("ALTER TABLE \"user\" ADD COLUMN stripe_customer_id VARCHAR(255)")
                
                if 'stripe_subscription_id' not in existing_columns:
                    migrations.append("ALTER TABLE \"user\" ADD COLUMN stripe_subscription_id VARCHAR(255)")
                
                if 'subscription_status' not in existing_columns:
                    migrations.append("ALTER TABLE \"user\" ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'inactive'")
                
                if 'subscription_start_date' not in existing_columns:
                    migrations.append("ALTER TABLE \"user\" ADD COLUMN subscription_start_date TIMESTAMP")
                
                if 'subscription_end_date' not in existing_columns:
                    migrations.append("ALTER TABLE \"user\" ADD COLUMN subscription_end_date TIMESTAMP")
                
                if 'trial_ends_at' not in existing_columns:
                    migrations.append("ALTER TABLE \"user\" ADD COLUMN trial_ends_at TIMESTAMP")
                
                # Execute user table migrations
                for migration in migrations:
                    try:
                        conn.execute(text(migration))
                        conn.commit()
                        logger.info(f"✅ Executed: {migration}")
                    except Exception as e:
                        logger.warning(f"⚠️  Migration already applied or failed: {migration} - {e}")
                
                # Migration 2: Add deposit fields to booking table
                logger.info("Running migration: Add deposit fields to booking table")
                
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='booking'"))
                existing_columns = [row[0] for row in result]
                
                booking_migrations = []
                
                if 'deposit_percentage' not in existing_columns:
                    booking_migrations.append("ALTER TABLE booking ADD COLUMN deposit_percentage INTEGER DEFAULT 50")
                
                if 'remaining_amount' not in existing_columns:
                    booking_migrations.append("ALTER TABLE booking ADD COLUMN remaining_amount FLOAT DEFAULT 0")
                
                # Execute booking table migrations
                for migration in booking_migrations:
                    try:
                        conn.execute(text(migration))
                        conn.commit()
                        logger.info(f"✅ Executed: {migration}")
                    except Exception as e:
                        logger.warning(f"⚠️  Migration already applied or failed: {migration} - {e}")
                
                # Update existing bookings
                try:
                    conn.execute(text("UPDATE booking SET deposit_percentage = 50 WHERE deposit_percentage IS NULL"))
                    conn.execute(text("UPDATE booking SET remaining_amount = (total_cost - deposit_amount) WHERE remaining_amount IS NULL OR remaining_amount = 0"))
                    conn.commit()
                    logger.info("✅ Updated existing bookings with deposit fields")
                except Exception as e:
                    logger.warning(f"⚠️  Could not update existing bookings: {e}")
                
                # Create indexes for better performance
                try:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_subscription_tier ON \"user\"(subscription_tier)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_subscription_status ON \"user\"(subscription_status)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_stripe_customer_id ON \"user\"(stripe_customer_id)"))
                    conn.commit()
                    logger.info("✅ Created indexes")
                except Exception as e:
                    logger.warning(f"⚠️  Could not create indexes: {e}")
                
                # Migration 3: Increase capacity_spec column size
                logger.info("Running migration: Increase capacity_spec column size")
                try:
                    # Use a separate transaction for this migration
                    trans = conn.begin()
                    try:
                        conn.execute(text("ALTER TABLE equipment ALTER COLUMN capacity_spec TYPE VARCHAR(500)"))
                        trans.commit()
                        logger.info("✅ Increased capacity_spec column size to 500")
                    except Exception as inner_e:
                        trans.rollback()
                        raise inner_e
                except Exception as e:
                    logger.warning(f"⚠️  Could not increase capacity_spec size: {e}")
                    # Print full error for debugging
                    import traceback
                    logger.error(traceback.format_exc())
                
                # Migration 4: Add boost fields to equipment table
                logger.info("Running migration: Add boost fields to equipment table")
                
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='equipment'"))
                existing_columns = [row[0] for row in result]
                
                equipment_migrations = []
                
                if 'is_boosted' not in existing_columns:
                    equipment_migrations.append("ALTER TABLE equipment ADD COLUMN is_boosted BOOLEAN DEFAULT FALSE")
                
                if 'boost_expires_at' not in existing_columns:
                    equipment_migrations.append("ALTER TABLE equipment ADD COLUMN boost_expires_at TIMESTAMP")
                
                if 'is_homepage_featured' not in existing_columns:
                    equipment_migrations.append("ALTER TABLE equipment ADD COLUMN is_homepage_featured BOOLEAN DEFAULT FALSE")
                
                if 'homepage_featured_expires_at' not in existing_columns:
                    equipment_migrations.append("ALTER TABLE equipment ADD COLUMN homepage_featured_expires_at TIMESTAMP")
                
                if 'total_boosts_purchased' not in existing_columns:
                    equipment_migrations.append("ALTER TABLE equipment ADD COLUMN total_boosts_purchased INTEGER DEFAULT 0")
                
                if 'security_deposit' not in existing_columns:
                    equipment_migrations.append("ALTER TABLE equipment ADD COLUMN security_deposit FLOAT DEFAULT 0.0")
                
                # Execute equipment table migrations
                for migration in equipment_migrations:
                    try:
                        conn.execute(text(migration))
                        conn.commit()
                        logger.info(f"✅ Executed: {migration}")
                    except Exception as e:
                        logger.warning(f"⚠️  Migration already applied or failed: {migration} - {e}")
                
                logger.info("🎉 All migrations completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            # Don't crash the app if migrations fail
            pass

