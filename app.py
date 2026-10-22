from flask import Flask, jsonify, make_response
from threading import Lock
import os
import time

app = Flask(__name__)
app.json.ensure_ascii = False

# FICTIONAL TEST DATA — not official election results.
TOTAL_ELECTORS = 100_000
SIMULATION_DURATION = 300  # 5 minutes
SIMULATION_START = time.time()  # No Unix timestamp to enter
FINAL_ABSTENTIONS = 18_000
FINAL_BLANK = 1_640
FINAL_NULL = 2_460
FINAL_LULA = 40_000
FINAL_FLAVIO = TOTAL_ELECTORS - FINAL_ABSTENTIONS - FINAL_BLANK - FINAL_NULL - FINAL_LULA
FINAL_TOTAL_VOTES = TOTAL_ELECTORS - FINAL_ABSTENTIONS

# One process is required to keep this in-memory state consistent.
lock = Lock()
request_number = 0
last_total_votes = 0


def portion(final_amount, counted):
    return final_amount * counted // FINAL_TOTAL_VOTES


@app.get("/")
def home():
    return jsonify({"simulation": True, "message": "Fictional election test API", "endpoint": "/results"})


@app.get("/results")
def results():
    global request_number, last_total_votes
    with lock:
        now = time.time()
        elapsed = max(0.0, now - SIMULATION_START)
        # Time moves the count forward; each GET adds at least one vote until complete.
        time_based_votes = int(FINAL_TOTAL_VOTES * min(elapsed / SIMULATION_DURATION, 1.0))
        last_total_votes = min(FINAL_TOTAL_VOTES, max(time_based_votes, last_total_votes + 1))
        request_number += 1
        total_votes = last_total_votes
        number = request_number

    lula_votes = portion(FINAL_LULA, total_votes)
    flavio_votes = portion(FINAL_FLAVIO, total_votes)
    blank_votes = portion(FINAL_BLANK, total_votes)
    null_votes = total_votes - lula_votes - flavio_votes - blank_votes
    valid_votes = lula_votes + flavio_votes

    payload = {
        "simulation": True,
        "notice": "DADOS FICTÍCIOS — SIMULAÇÃO, NÃO SÃO RESULTADOS DO TSE",
        "requestNumber": number,
        "lastUpdated": int(now),
        "updateInterval": 0,
        "simulationDuration": SIMULATION_DURATION,
        "totalElectors": TOTAL_ELECTORS,
        "totalVotes": total_votes,
        "validVotes": valid_votes,
        "blankVotes": blank_votes,
        "nullVotes": null_votes,
        "abstentions": FINAL_ABSTENTIONS,
        "turnout": round(total_votes / TOTAL_ELECTORS * 100, 2),
        "countedPercentage": round(total_votes / FINAL_TOTAL_VOTES * 100, 2),
        "candidates": [
            {"name": "Lula", "votes": lula_votes,
             "percentage": round(lula_votes / valid_votes * 100, 2) if valid_votes else 0},
            {"name": "Flávio Bolsonaro", "votes": flavio_votes,
             "percentage": round(flavio_votes / valid_votes * 100, 2) if valid_votes else 0},
        ],
    }
    response = make_response(jsonify(payload))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
    
