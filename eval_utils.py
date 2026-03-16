def calculate_document_score(extraction_accuracy, clause_completeness, summary_accuracy, summary_usefulness):
    """
    Calculate overall document evaluation score.
    Each metric is 1–5.
    """
    scores = [
        extraction_accuracy,
        clause_completeness,
        summary_accuracy,
        summary_usefulness
    ]

    return round(sum(scores) / len(scores), 2)


def aggregate_evaluation_metrics(evaluations):
    """
    Aggregate evaluation statistics for dashboard.
    """
    if not evaluations:
        return {
            "total_evaluations": 0,
            "average_score": 0
        }

    total_score = sum(e.overall_score for e in evaluations)

    return {
        "total_evaluations": len(evaluations),
        "average_score": round(total_score / len(evaluations), 2)
    }


def get_quality_rating(score):
    """
    Convert numeric score into human readable rating.
    """
    if score >= 4.5:
        return "Excellent"
    elif score >= 3.5:
        return "Good"
    elif score >= 2.5:
        return "Fair"
    else:
        return "Poor"
