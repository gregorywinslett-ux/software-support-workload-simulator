from __future__ import annotations

import math

import pandas as pd


PREFERENCE_VALUES = {
    "A strongly more important": 5.0,
    "A moderately more important": 3.0,
    "A slightly more important": 2.0,
    "about equal": 1.0,
    "B slightly more important": 0.5,
    "B moderately more important": 1 / 3,
    "B strongly more important": 0.2,
}


def pairwise_weights(criteria: list[dict], comparisons: list[str]) -> dict[str, float]:
    ids = [criterion["criterion_id"] for criterion in criteria]
    matrix = [[1.0 for _ in ids] for _ in ids]
    pairs = [(0, 1), (0, 2), (1, 2)]
    for value, (i, j) in zip(comparisons, pairs):
        score = PREFERENCE_VALUES[value]
        matrix[i][j] = score
        matrix[j][i] = 1 / score

    geometric_means = []
    for row in matrix:
        product = math.prod(row)
        geometric_means.append(product ** (1 / len(row)))
    total = sum(geometric_means) or 1
    return {ids[i]: geometric_means[i] / total for i in range(len(ids))}


def aggregate_weights(pairwise_responses: list[dict], selected_criteria: list[dict]) -> pd.DataFrame:
    ids = [criterion["criterion_id"] for criterion in selected_criteria]
    names = {criterion["criterion_id"]: criterion["criterion_name"] for criterion in selected_criteria}
    if not pairwise_responses:
        even = 1 / len(ids) if ids else 0
        return pd.DataFrame(
            [{"criterion_id": cid, "criterion_name": names[cid], "weight": even, "spread": 0.0} for cid in ids]
        )

    rows = [response["calculated_individual_weights"] for response in pairwise_responses]
    df = pd.DataFrame(rows).reindex(columns=ids).fillna(0)
    means = df.mean()
    total = means.sum() or 1
    normalised = means / total
    spreads = df.std(ddof=0).fillna(0)
    return pd.DataFrame(
        [
            {
                "criterion_id": cid,
                "criterion_name": names[cid],
                "weight": float(normalised[cid]),
                "spread": float(spreads[cid]),
            }
            for cid in ids
        ]
    )


def rank_actions(candidate_actions: list[dict], ratings: dict, weights_df: pd.DataFrame) -> pd.DataFrame:
    weight_lookup = dict(zip(weights_df["criterion_id"], weights_df["weight"]))
    rows = []
    for action in candidate_actions[:7]:
        action_id = action["action_id"]
        weighted_score = 0.0
        for criterion_id, weight in weight_lookup.items():
            rating = ratings.get(action_id, {}).get(criterion_id, {}).get("rating", 3)
            weighted_score += float(rating) * float(weight)
        rows.append(
            {
                "action_id": action_id,
                "action_title": action["action_title"],
                "linked_theme": action.get("linked_theme", ""),
                "decision_status": action.get("decision_status", "undecided"),
                "weighted_score": round(weighted_score, 2),
                "percentage_equivalent": round((weighted_score / 5) * 100, 1),
            }
        )
    return pd.DataFrame(rows).sort_values("weighted_score", ascending=False, ignore_index=True)
