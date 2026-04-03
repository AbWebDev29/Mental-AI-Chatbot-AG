"""
MONGODB AGGREGATION QUERIES FOR MONTHLY REPORTS
Generate clinical insights from stored taxonomy classifications
"""

# =============================================================================
# 1. MONTHLY EMOTION FREQUENCY REPORT
# =============================================================================
# Shows which emotions are most common in the current month
# Useful for tracking mood patterns

query_monthly_emotions = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},  # Start of month
                "$lte": {"$date": "2026-04-03T23:59:59Z"}   # End of month
            }
        }
    },
    {
        "$group": {
            "_id": "$clinical_markers.emotion_tag",
            "count": {"$sum": 1},
            "avg_intensity": {"$avg": "$clinical_markers.intensity"},
            "avg_functional_impact": {"$avg": "$clinical_markers.functional_impact"}
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$project": {
            "_id": 0,
            "emotion": "$_id",
            "count": 1,
            "percentage": {
                "$round": [
                    {"$multiply": [{"$divide": ["$count", {"$sum": "$count"}]}, 100]},
                    2
                ]
            },
            "avg_intensity": {"$round": ["$avg_intensity", 1]},
            "avg_functional_impact": {"$round": ["$avg_functional_impact", 1]}
        }
    }
]


# =============================================================================
# 2. MONTHLY CLINICAL CONDITIONS REPORT
# =============================================================================
# Shows which mental health conditions appear most frequently
# Helps identify primary areas of concern

query_monthly_conditions = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},
                "$lte": {"$date": "2026-04-03T23:59:59Z"}
            }
        }
    },
    {
        "$group": {
            "_id": "$clinical_markers.clinical_label",
            "count": {"$sum": 1},
            "avg_intensity": {"$avg": "$clinical_markers.intensity"},
            "avg_functional_impact": {"$avg": "$clinical_markers.functional_impact"},
            "recurring_count": {
                "$sum": {"$cond": ["$clinical_markers.is_recurring", 1, 0]}
            }
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 10
    },
    {
        "$project": {
            "_id": 0,
            "condition": "$_id",
            "count": 1,
            "percentage": {
                "$round": [{"$multiply": [{"$divide": ["$count", {"$sum": "$count"}]}, 100]}, 2]
            },
            "avg_intensity": {"$round": ["$avg_intensity", 1]},
            "avg_functional_impact": {"$round": ["$avg_functional_impact", 1]},
            "recurring_percentage": {
                "$round": [
                    {"$multiply": [{"$divide": ["$recurring_count", "$count"]}, 100]},
                    1
                ]
            }
        }
    }
]


# =============================================================================
# 3. MONTHLY TRIGGER SOURCE ANALYSIS
# =============================================================================
# Shows what triggers the most distress

query_monthly_triggers = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},
                "$lte": {"$date": "2026-04-03T23:59:59Z"}
            }
        }
    },
    {
        "$group": {
            "_id": "$clinical_markers.trigger_source",
            "count": {"$sum": 1},
            "avg_intensity": {"$avg": "$clinical_markers.intensity"},
            "high_impact_count": {
                "$sum": {"$cond": [{"$gte": ["$clinical_markers.functional_impact", 7]}, 1, 0]}
            }
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$project": {
            "_id": 0,
            "trigger_source": "$_id",
            "frequency": "$count",
            "percentage": {
                "$round": [{"$multiply": [{"$divide": ["$count", {"$sum": "$count"}]}, 100]}, 2]
            },
            "avg_intensity": {"$round": ["$avg_intensity", 1]},
            "high_impact_episodes": "$high_impact_count",
            "high_impact_percentage": {
                "$round": [
                    {"$multiply": [{"$divide": ["$high_impact_count", "$count"]}, 100]},
                    1
                ]
            }
        }
    }
]


# =============================================================================
# 4. FUNCTIONAL IMPACT TREND
# =============================================================================
# Tracks how daily functioning changes throughout the month
# 7-day rolling average to smooth out daily fluctuations

query_functional_impact_trend = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},
                "$lte": {"$date": "2026-04-03T23:59:59Z"}
            }
        }
    },
    {
        "$group": {
            "_id": {
                "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
            },
            "avg_functional_impact": {"$avg": "$clinical_markers.functional_impact"},
            "avg_intensity": {"$avg": "$clinical_markers.intensity"},
            "message_count": {"$sum": 1}
        }
    },
    {
        "$sort": {"_id": 1}
    },
    {
        "$project": {
            "_id": 0,
            "date": "$_id",
            "avg_functional_impact": {"$round": ["$avg_functional_impact", 1]},
            "avg_intensity": {"$round": ["$avg_intensity", 1]},
            "daily_messages": "$message_count"
        }
    }
]


# =============================================================================
# 5. EMOTION CLUSTER DISTRIBUTION
# =============================================================================
# Shows which emotion clusters are most active
# JOY, SADNESS, ANGER, FEAR, SHAME, COMPLEX

query_emotion_clusters = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},
                "$lte": {"$date": "2026-04-03T23:59:59Z"}
            }
        }
    },
    {
        "$group": {
            "_id": "$clinical_markers.emotion_cluster",
            "count": {"$sum": 1},
            "avg_intensity": {"$avg": "$clinical_markers.intensity"},
            "emotions": {
                "$push": "$clinical_markers.emotion_tag"
            }
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$project": {
            "_id": 0,
            "cluster": "$_id",
            "frequency": "$count",
            "percentage": {
                "$round": [{"$multiply": [{"$divide": ["$count", {"$sum": "$count"}]}, 100]}, 2]
            },
            "avg_intensity": {"$round": ["$avg_intensity", 1]},
            "unique_emotions": {
                "$size": {"$setFromArray": ["$emotions"]}
            }
        }
    }
]


# =============================================================================
# 6. CLINICAL CATEGORY BREAKDOWN
# =============================================================================
# Shows distribution across clinical categories
# ANXIETY, MOOD, TRAUMA, IDENTITY_PERSONALITY, etc.

query_clinical_categories = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},
                "$lte": {"$date": "2026-04-03T23:59:59Z"}
            }
        }
    },
    {
        "$group": {
            "_id": "$clinical_markers.clinical_category",
            "count": {"$sum": 1},
            "avg_intensity": {"$avg": "$clinical_markers.intensity"},
            "avg_functional_impact": {"$avg": "$clinical_markers.functional_impact"},
            "conditions": {
                "$push": "$clinical_markers.clinical_label"
            }
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$project": {
            "_id": 0,
            "category": "$_id",
            "frequency": "$count",
            "percentage": {
                "$round": [{"$multiply": [{"$divide": ["$count", {"$sum": "$count"}]}, 100]}, 2]
            },
            "avg_intensity": {"$round": ["$avg_intensity", 1]},
            "avg_functional_impact": {"$round": ["$avg_functional_impact", 1]},
            "unique_conditions": {
                "$size": {"$setFromArray": ["$conditions"]}
            }
        }
    }
]


# =============================================================================
# 7. HIGH-INTENSITY EPISODES (Crisis Detection)
# =============================================================================
# Find days with high distress (intensity >= 8)

query_high_intensity_episodes = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},
                "$lte": {"$date": "2026-04-03T23:59:59Z"}
            },
            "clinical_markers.intensity": {"$gte": 8}
        }
    },
    {
        "$project": {
            "_id": 0,
            "timestamp": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$timestamp"}},
            "message": 1,
            "emotion": "$clinical_markers.emotion_tag",
            "condition": "$clinical_markers.clinical_label",
            "intensity": "$clinical_markers.intensity",
            "functional_impact": "$clinical_markers.functional_impact",
            "trigger": "$clinical_markers.trigger_source"
        }
    },
    {
        "$sort": {"timestamp": -1}
    }
]


# =============================================================================
# 8. RECURRING PATTERNS ANALYSIS
# =============================================================================
# Shows what patterns keep coming back

query_recurring_patterns = [
    {
        "$match": {
            "timestamp": {
                "$gte": {"$date": "2026-03-04T00:00:00Z"},
                "$lte": {"$date": "2026-04-03T23:59:59Z"}
            },
            "clinical_markers.is_recurring": True
        }
    },
    {
        "$group": {
            "_id": {
                "emotion": "$clinical_markers.emotion_tag",
                "condition": "$clinical_markers.clinical_label",
                "trigger": "$clinical_markers.trigger_source"
            },
            "count": {"$sum": 1},
            "avg_intensity": {"$avg": "$clinical_markers.intensity"},
            "dates": {
                "$push": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
            }
        }
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$project": {
            "_id": 0,
            "emotion": "$_id.emotion",
            "condition": "$_id.condition",
            "trigger": "$_id.trigger",
            "recurring_count": "$count",
            "avg_intensity": {"$round": ["$avg_intensity", 1]},
            "dates": 1
        }
    }
]


# =============================================================================
# PYTHON HELPER FUNCTION FOR RUNNING REPORTS
# =============================================================================

async def generate_monthly_report(db, user_id: str):
    """
    Generate a comprehensive monthly report for a user
    
    Usage:
        from database import db
        report = await generate_monthly_report(db, "user_id_here")
    """
    
    from datetime import datetime, timedelta
    
    # Get first day of current month
    today = datetime.utcnow()
    first_day = today.replace(day=1)
    
    report = {
        "user_id": user_id,
        "report_date": datetime.utcnow().isoformat(),
        "period": f"{first_day.strftime('%B %Y')}",
        "sections": {}
    }
    
    # 1. Monthly emotions
    emotions_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day}
            }
        },
        *query_monthly_emotions
    ])
    report["sections"]["emotions"] = await emotions_cursor.to_list(None)
    
    # 2. Monthly conditions
    conditions_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day}
            }
        },
        *query_monthly_conditions
    ])
    report["sections"]["conditions"] = await conditions_cursor.to_list(None)
    
    # 3. Triggers
    triggers_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day}
            }
        },
        *query_monthly_triggers
    ])
    report["sections"]["triggers"] = await triggers_cursor.to_list(None)
    
    # 4. Functional impact trend
    trend_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day}
            }
        },
        *query_functional_impact_trend
    ])
    report["sections"]["functional_impact_trend"] = await trend_cursor.to_list(None)
    
    # 5. Emotion clusters
    clusters_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day}
            }
        },
        *query_emotion_clusters
    ])
    report["sections"]["emotion_clusters"] = await clusters_cursor.to_list(None)
    
    # 6. Clinical categories
    categories_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day}
            }
        },
        *query_clinical_categories
    ])
    report["sections"]["clinical_categories"] = await categories_cursor.to_list(None)
    
    # 7. High intensity episodes
    high_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day},
                "clinical_markers.intensity": {"$gte": 8}
            }
        },
        *query_high_intensity_episodes
    ])
    report["sections"]["high_intensity_episodes"] = await high_cursor.to_list(None)
    
    # 8. Recurring patterns
    recurring_cursor = db.sessions.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "timestamp": {"$gte": first_day},
                "clinical_markers.is_recurring": True
            }
        },
        *query_recurring_patterns
    ])
    report["sections"]["recurring_patterns"] = await recurring_cursor.to_list(None)
    
    return report
