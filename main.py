from dotenv import load_dotenv
import os

from flask import Flask, request
from flask_cors import CORS
from datetime import timedelta, datetime

from database import db
from models import ApiUsage

# ------------------------------------------------------------------------------
# 1. LOAD ENV + CREATE APP
# ------------------------------------------------------------------------------

load_dotenv()

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": "http://localhost:3000"}},
    allow_headers=["Content-Type"],
    expose_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"]
)

# ------------------------------------------------------------------------------
# 2. COOKIE + SESSION CONFIG
# ------------------------------------------------------------------------------

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

app.config["SESSION_COOKIE_NAME"] = "session"
app.config["SESSION_COOKIE_DOMAIN"] = "localhost"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True

# ------------------------------------------------------------------------------
# 3. DATABASE CONFIG
# ------------------------------------------------------------------------------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ------------------------------------------------------------------------------
# 4. IMPORT BLUEPRINTS (CLEAN + NO DUPLICATES)
# ------------------------------------------------------------------------------

# Auth + Users
from routes.auth import auth
from routes.protected import protected_bp
from routes.users import users_bp

# AI
from routes.ai import ai_bp

# Admin
from routes.admin_dashboard import admin_dashboard
from routes.api_keys import api_keys_bp
from routes.engines import engines_bp
from routes.security import security_bp
from routes.admin_notifications import admin_notifications_bp
from routes.admin_config import admin_config_bp
from routes.admin_billing import admin_billing_bp
from routes.admin_models import admin_models_bp

# Canvas System
from routes.canvas_templates import canvas_templates
from routes.canvas_template_single import canvas_template_single
from routes.canvas_library import canvas_library_bp
from routes.canvas_ai_tools import canvas_ai_tools_bp
from routes.canvas_export import canvas_export_bp
from routes.canvas_assets import canvas_assets_bp
from routes.canvas_project import canvas_project_bp
from routes.canvas_preferences import canvas_preferences_bp
from routes.canvas_history import canvas_history_bp
from routes.canvas_fonts import canvas_fonts_bp
from routes.canvas_colors import canvas_colors_bp
from routes.canvas_shapes import canvas_shapes_bp
from routes.canvas_text_styles import canvas_text_styles_bp
from routes.canvas_layers import canvas_layers_bp
from routes.canvas_grid import canvas_grid_bp
from routes.canvas_admin import canvas_admin_bp
from routes.canvas_logs import canvas_logs_bp
from routes.canvas_project_delete import canvas_project_delete_bp
from routes.canvas_assets_delete import canvas_assets_delete_bp
from routes.canvas_fonts_delete import canvas_fonts_delete_bp
from routes.canvas_shapes_delete import canvas_shapes_delete_bp
from routes.canvas_colors_delete import canvas_colors_delete_bp
from routes.canvas_analytics import canvas_analytics_bp
from routes.credits_engine import credits_engine_bp

# System
from routes.system_health import system_health_bp
from routes.server_control import server_control_bp

# Credits + Stripe Billing
from routes.credits import credits_bp
from routes.stripe_billing import stripe_billing_bp

# ------------------------------------------------------------------------------
# 5. REGISTER BLUEPRINTS (NO DUPLICATES)
# ------------------------------------------------------------------------------

# Auth
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(protected_bp, url_prefix="/protected")
app.register_blueprint(users_bp, url_prefix="/users")

# AI
app.register_blueprint(ai_bp, url_prefix="/ai")

# Admin
app.register_blueprint(admin_dashboard, url_prefix="/admin/dashboard")
app.register_blueprint(api_keys_bp, url_prefix="/admin/api-keys")
app.register_blueprint(engines_bp, url_prefix="/admin/engines")
app.register_blueprint(security_bp, url_prefix="/security")
app.register_blueprint(admin_notifications_bp, url_prefix="/admin")
app.register_blueprint(admin_config_bp, url_prefix="/admin")
app.register_blueprint(admin_billing_bp, url_prefix="/admin")
app.register_blueprint(credits_engine_bp, url_prefix="/credits")
app.register_blueprint(admin_models_bp, url_prefix="/admin")

# Canvas
app.register_blueprint(canvas_templates, url_prefix="/canvas")
app.register_blueprint(canvas_template_single, url_prefix="/canvas")
app.register_blueprint(canvas_library_bp, url_prefix="/canvas")
app.register_blueprint(canvas_ai_tools_bp, url_prefix="/canvas")
app.register_blueprint(canvas_export_bp, url_prefix="/canvas")
app.register_blueprint(canvas_assets_bp, url_prefix="/canvas")
app.register_blueprint(canvas_project_bp, url_prefix="/canvas")
app.register_blueprint(canvas_preferences_bp, url_prefix="/canvas")
app.register_blueprint(canvas_history_bp, url_prefix="/canvas")
app.register_blueprint(canvas_fonts_bp, url_prefix="/canvas")
app.register_blueprint(canvas_colors_bp, url_prefix="/canvas")
app.register_blueprint(canvas_shapes_bp, url_prefix="/canvas")
app.register_blueprint(canvas_text_styles_bp, url_prefix="/canvas")
app.register_blueprint(canvas_layers_bp, url_prefix="/canvas")
app.register_blueprint(canvas_grid_bp, url_prefix="/canvas")
app.register_blueprint(canvas_admin_bp, url_prefix="/canvas")
app.register_blueprint(canvas_logs_bp, url_prefix="/canvas")
app.register_blueprint(canvas_project_delete_bp, url_prefix="/canvas")
app.register_blueprint(canvas_assets_delete_bp, url_prefix="/canvas")
app.register_blueprint(canvas_fonts_delete_bp, url_prefix="/canvas")
app.register_blueprint(canvas_shapes_delete_bp, url_prefix="/canvas")
app.register_blueprint(canvas_colors_delete_bp, url_prefix="/canvas")
app.register_blueprint(canvas_analytics_bp, url_prefix="/canvas")

# System
app.register_blueprint(system_health_bp, url_prefix="/system")
app.register_blueprint(server_control_bp, url_prefix="/system")

# Credits + Billing
app.register_blueprint(credits_bp, url_prefix="/credits")
app.register_blueprint(stripe_billing_bp, url_prefix="/billing")

# ------------------------------------------------------------------------------
# 6. API USAGE LOGGING
# ------------------------------------------------------------------------------

@app.after_request
def log_api_usage(response):
    try:
        if request.path.startswith("/static") or request.path.startswith("/_next"):
            return response

        if request.path.startswith("/api") or request.path.startswith("/admin"):
            usage = ApiUsage(
                endpoint=request.path,
                count=1,
                timestamp=datetime.utcnow(),
                user_id=getattr(request, "user_id", None),
            )
            db.session.add(usage)
            db.session.commit()
    except Exception as e:
        print("API usage logging failed:", e)

    return response

# ------------------------------------------------------------------------------
# 7. DATABASE CREATION + ADMIN SEEDING
# ------------------------------------------------------------------------------

with app.app_context():
    db.create_all()
    from seed_admin import seed_admin
    seed_admin()

# ------------------------------------------------------------------------------
# 8. START SERVER
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="localhost", port=5050, debug=True)
