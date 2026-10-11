"""
CTFd Hint Penalty Plugin - Minimal Version
Automatically deducts points when hints are viewed
Allows hints to be viewed BEFORE solving (standard CTF workflow)
"""
from flask import Blueprint, jsonify
from CTFd.models import db, Hints, Users, Awards, Challenges
from CTFd.plugins import register_plugin_blueprint
from CTFd.utils import get_current_user
from sqlalchemy import text
import logging
from datetime import datetime

log = logging.getLogger(__name__)

# Create the hint_deductions table model
class HintDeduction(db.Model):
    __tablename__ = "hint_deductions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    hint_id = db.Column(db.Integer, db.ForeignKey("hints.id"), nullable=False)
    challenge_id = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, default=5)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "hint_id", name="uq_user_hint_deduction"),
    )


# Create blueprint for custom hint endpoints
bp = Blueprint("hint_penalty", __name__, url_prefix="/api/v1/hint-penalty")


@bp.route("/hints/<int:hint_id>", methods=["GET"])
def get_hint_unrestricted(hint_id):
    """
    Get a hint WITHOUT requiring the challenge to be solved first.
    Deducts points automatically.
    """
    user = get_current_user()

    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    if not user.team_id:
        return jsonify({"success": False, "message": "User must be on a team"}), 403

    # Get the hint
    hint = Hints.query.filter_by(id=hint_id).first()
    if not hint:
        return jsonify({"success": False, "message": "Hint not found"}), 404

    # Check if challenge exists
    challenge = Challenges.query.filter_by(id=hint.challenge_id).first()
    if not challenge:
        return jsonify({"success": False, "message": "Challenge not found"}), 404

    try:
        # Check if this user already viewed this hint
        existing = db.session.query(HintDeduction).filter_by(
            user_id=user.id,
            hint_id=hint_id
        ).first()

        if not existing:
            # Create deduction record
            cost = hint.cost if hint.cost else 5
            deduction = HintDeduction(
                user_id=user.id,
                hint_id=hint_id,
                challenge_id=hint.challenge_id,
                cost=cost,
            )
            db.session.add(deduction)
            db.session.flush()

            # Create negative award immediately
            award = Awards(
                team_id=user.team_id,
                name="Hint penalty",
                description=f"Penalty for viewing hint on Challenge #{hint.challenge_id}",
                value=-cost,
                category="hints",
                type="standard",
            )
            db.session.add(award)
            db.session.commit()

            log.info(
                f"[HINT VIEW] User {user.id} (Team {user.team_id}) "
                f"viewed hint {hint_id}: -{cost} pts"
            )

            return jsonify({
                "success": True,
                "data": {
                    "id": hint.id,
                    "challenge_id": hint.challenge_id,
                    "content": hint.content,
                    "cost": cost,
                    "penalty_applied": True,
                    "penalty_amount": cost,
                }
            })
        else:
            # Already viewed - return hint without additional penalty
            cost = hint.cost if hint.cost else 5
            return jsonify({
                "success": True,
                "data": {
                    "id": hint.id,
                    "challenge_id": hint.challenge_id,
                    "content": hint.content,
                    "cost": cost,
                    "penalty_applied": False,
                    "penalty_message": "Already viewed - no additional penalty",
                }
            })

    except Exception as e:
        log.error(f"Error processing hint view: {e}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Error processing hint"}), 500


def load(app):
    """Load the plugin"""

    # Register the blueprint
    register_plugin_blueprint(app, bp)

    # Create the hint_deductions table if it doesn't exist
    with app.app_context():
        try:
            db.create_all()
            log.info("✓ Hint Penalty Plugin initialized")
        except Exception as e:
            log.error(f"✗ Error initializing plugin: {e}")

    log.info("✓ Hint Penalty Plugin loaded successfully")