from flask import Flask, jsonify
import os
import time
import math

app = Flask(__name__)
app.json.ensure_ascii = False

UPDATE_INTERVAL = 30
TOTAL_ELECTORS = 100_000
SIMULATION_DURATION = 300  # 5 minutes
# Starts automatically when Render launches the Python server.
# Note: a restart or sleeping/waking service may reset this test simulation.
SIMULATION_START = int(time.time())

# Fixed cumulative vote distribution. No randomness means no vote totals can fall.
# These are invented test values, not real results.
FINAL_ABSTENTIONS = 18_000
FINAL_BLANK = 1_640
FINAL_NULL = 2_460
FINAL_VALID = TOTAL_ELECTORS - FINAL_ABSTENTIONS - FINAL_BLANK - FINAL_NULL
FINAL_LULA = 40_000
FINAL_FLAVIO = FINAL_VALID - FINAL_LULA


def cumulative(final_value, step, total_steps):
    return (final_value * step) // total_steps


@app.get("/")
def home():
    return jsonify({"simulation": True, "message": "Fictional election test API", "endpoint": "/results"})


@app.get("/results")
def results():
    now = int(time.time())
    total_steps = math.ceil(SIMULATION_DURATION / UPDATE_INTERVAL)
    elapsed = max(0, now - SIMULATION_START)
    step = min(total_steps, elapsed // UPDATE_INTERVAL)

    lula_votes = cumulative(FINAL_LULA, step, total_steps)
    flavio_votes = cumulative(FINAL_FLAVIO, step, total_steps)
    blank_votes = cumulative(FINAL_BLANK, step, total_steps)
    null_votes = cumulative(FINAL_NULL, step, total_steps)
    valid_votes = lula_votes + flavio_votes
    total_votes = valid_votes + blank_votes + null_votes
    # Abstentions cannot be determined during partial counting; this is a
    # simulated final estimate and stays constant throughout the test.
    abstentions = FINAL_ABSTENTIONS

    return jsonify({
        "simulation": True,
        "lastUpdated": SIMULATION_START + step * UPDATE_INTERVAL if step else SIMULATION_START,
        "updateInterval": UPDATE_INTERVAL,
        "totalElectors": TOTAL_ELECTORS,
        "totalVotes": total_votes,
        "validVotes": valid_votes,
        "blankVotes": blank_votes,
        "nullVotes": null_votes,
        "abstentions": abstentions,
        "turnout": round(total_votes / TOTAL_ELECTORS * 100, 2),
        "countedPercentage": round(step / total_steps * 100, 2),
        "candidates": [
            {"name": "Lula", "votes": lula_votes, "percentage": round(lula_votes / valid_votes * 100, 2) if valid_votes else 0},
            {"name": "Flávio Bolsonaro", "votes": flavio_votes, "percentage": round(flavio_votes / valid_votes * 100, 2) if valid_votes else 0}
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
    
