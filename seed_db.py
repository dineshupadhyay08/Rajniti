import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from dotenv import load_dotenv
load_dotenv()

from app import create_app
import app.core.database as db

from app.database.models.election import Election
from app.database.models.constituency import Constituency
from app.database.models.party import Party
from app.database.models.candidate import Candidate


# --------------------------------------------------
# Utility
# --------------------------------------------------
def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------
# App & DB init
# --------------------------------------------------
app = create_app()

if not db.init_db(app):
    raise RuntimeError("❌ DATABASE_URL missing or DB connection failed")


# --------------------------------------------------
# Seeding
# --------------------------------------------------
with app.app_context():
    session = db.SessionLocal()

    try:
        # ================== ELECTIONS ==================
        elections = load_json("app/data/elections/LS-2024.json")

        for e in elections:
            exists = session.query(Election).filter_by(
                id=e["election_id"]
            ).first()

            if not exists:
                session.add(
                    Election(
                        id=e["election_id"],
                        name=e["name"],
                        type=e["type"],
                        year=e["year"],
                        total_constituencies=e["total_constituencies"],
                        total_candidates=e["total_candidates"],
                        total_parties=e["total_parties"],
                        result_status=e["result_status"],
                    )
                )

        session.commit()
        print("✅ elections inserted")

        # ================== CONSTITUENCIES ==================
        constituencies = load_json(
            "app/data/lok_sabha/lok-sabha-2024/constituencies.json"
        )

        for c in constituencies:
            exists = session.query(Constituency).filter_by(
                id=c["unique_id"]
            ).first()

            if not exists:
                session.add(
                    Constituency(
                        id=c["unique_id"],          # "2-S02"
                original_id=c["id"],        # "2"
                name=c["name"],
                state_id=c["state_id"],     # "S02"
                type="LS",      
                    )
                )

        session.commit()
        print("✅ constituencies inserted")

        # ================== PARTIES ==================
        parties = load_json(
            "app/data/lok_sabha/lok-sabha-2024/parties.json"
        )

        for p in parties:
            exists = session.query(Party).filter_by(
                id=p["id"]
            ).first()

            if not exists:
                session.add(
                    Party(
                        id=p["id"],
                        name=p["name"],
                        short_name=p["short_name"],
                        symbol=p.get("symbol", ""),
                    )
                )

        session.commit()
        print("✅ parties inserted")

        # ================== CANDIDATES ==================
        candidates = load_json(
            "app/data/lok_sabha/lok-sabha-2024/candidates.json"
        )

        for c in candidates:
            exists = session.query(Candidate).filter_by(
                id=c["id"]
            ).first()

            if not exists:
                session.add(
                    Candidate(
                        id=c["id"],
                        name=c["name"],
                        party_id=c["party_id"],
                        constituency_id=c["constituency_unique_id"],  # 🔥 IMPORTANT
                        original_constituency_id=c.get("constituency_id"),
                        state_id=c["state_id"],
                        status=c["status"],        # WON / LOST
                        type=c.get("type", "MP"),  # MP / MLA
                        image_url=c.get("image_url"),
                    )
                )

        session.commit()
        print("✅ candidates inserted")

        print("🎉 DATABASE SEEDING COMPLETED SUCCESSFULLY")

    except Exception as e:
        session.rollback()
        print("❌ ERROR during seeding:")
        raise e

    finally:
        session.close()
