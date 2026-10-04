"""
Quickbyte - Application entry point
Creates the Flask app, wires up the database, security (CSRF + sessions),
context processors and blueprints.

Run:
    python app.py
Then open http://127.0.0.1:5000
"""
import os
from flask import Flask, render_template, request, session, flash, redirect, url_for

import db
import seed
from helpers import (
    current_user, get_csrf_token, validate_csrf, cart_count, ORDER_STATUSES,
)


def create_app():
    app = Flask(__name__)

    # Secret key: from env in production, stable dev fallback otherwise.
    app.config["SECRET_KEY"] = os.environ.get(
        "QUICKBYTE_SECRET", "dev-quickbyte-secret-change-me"
    )
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,   # JS cannot read the session cookie
        SESSION_COOKIE_SAMESITE="Lax",  # basic CSRF hardening at cookie level
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )

    db.init_app(app)

    # ------------------------------------------------------------------
    # CSRF protection: reject unsafe methods without a valid token.
    # ------------------------------------------------------------------
    @app.before_request
    def csrf_protect():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            if not validate_csrf():
                if request.accept_mimetypes.best == "application/json" \
                        or request.headers.get("X-CSRFToken"):
                    return {"error": "Invalid or missing CSRF token."}, 400
                flash("Your session expired. Please try again.", "error")
                return redirect(request.referrer or url_for("main.index"))

    # ------------------------------------------------------------------
    # Template globals available in every page.
    # ------------------------------------------------------------------
    @app.context_processor
    def inject_globals():
        from db import query
        return {
            "current_user": current_user(),
            "csrf_token": get_csrf_token(),
            "cart_count": cart_count(),
            "nav_categories": query(
                "SELECT * FROM categories ORDER BY name"
            ),
            "ORDER_STATUSES": ORDER_STATUSES,
        }

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from routes.auth import bp as auth_bp
    from routes.main import bp as main_bp
    from routes.orders import bp as orders_bp
    from routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    # ------------------------------------------------------------------
    # Error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404,
                               message="Page not found"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403,
                               message="Access denied"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500,
                               message="Something went wrong"), 500

    # ------------------------------------------------------------------
    # First-run: create tables + seed demo data.
    # ------------------------------------------------------------------
    with app.app_context():
        db.init_db()
        if seed.seed():
            app.logger.info("Database seeded with demo data.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
