#!/usr/bin/env python3
"""
MONTHLY REPORT GENERATOR
Converts MongoDB aggregation results into a readable HTML/text report
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List


def format_emotion_report(emotions_data: List[Dict[str, Any]]) -> str:
    """Format emotion frequency report"""
    report = "📊 MONTHLY EMOTION REPORT\n"
    report += "=" * 60 + "\n\n"
    
    if not emotions_data:
        return report + "No data available\n"
    
    total = sum(e['count'] for e in emotions_data)
    report += f"Total entries analyzed: {total}\n\n"
    
    report += f"{'Emotion':<25} {'Count':<8} {'%':<8} {'Avg Intensity':<15}\n"
    report += "-" * 60 + "\n"
    
    for emotion in emotions_data:
        report += f"{emotion['emotion']:<25} {emotion['count']:<8} "
        report += f"{emotion['percentage']:<8}% {emotion['avg_intensity']:<15}\n"
    
    return report + "\n"


def format_conditions_report(conditions_data: List[Dict[str, Any]]) -> str:
    """Format clinical conditions report"""
    report = "🏥 MONTHLY CLINICAL CONDITIONS REPORT\n"
    report += "=" * 70 + "\n\n"
    
    if not conditions_data:
        return report + "No data available\n"
    
    total = sum(c['count'] for c in conditions_data)
    report += f"Total entries analyzed: {total}\n\n"
    
    report += f"{'Condition':<30} {'Count':<8} {'%':<8} {'Recurring':<12}\n"
    report += "-" * 70 + "\n"
    
    for condition in conditions_data:
        report += f"{condition['condition']:<30} {condition['count']:<8} "
        report += f"{condition['percentage']:<8}% {condition['recurring_percentage']:<12}%\n"
    
    return report + "\n"


def format_triggers_report(triggers_data: List[Dict[str, Any]]) -> str:
    """Format trigger source analysis"""
    report = "⚠️ TRIGGER SOURCE ANALYSIS\n"
    report += "=" * 70 + "\n\n"
    
    if not triggers_data:
        return report + "No data available\n"
    
    total = sum(t['frequency'] for t in triggers_data)
    report += f"Total trigger instances: {total}\n\n"
    
    report += f"{'Trigger Source':<30} {'Frequency':<12} {'%':<8} {'High Impact %':<15}\n"
    report += "-" * 70 + "\n"
    
    for trigger in triggers_data:
        report += f"{trigger['trigger_source']:<30} {trigger['frequency']:<12} "
        report += f"{trigger['percentage']:<8}% {trigger['high_impact_percentage']:<15}%\n"
    
    return report + "\n"


def format_functional_impact_trend(trend_data: List[Dict[str, Any]]) -> str:
    """Format functional impact trend"""
    report = "📈 FUNCTIONAL IMPACT TREND (Daily Average)\n"
    report += "=" * 60 + "\n\n"
    
    if not trend_data:
        return report + "No data available\n"
    
    report += f"{'Date':<15} {'Functional Impact':<20} {'Messages':<10}\n"
    report += "-" * 60 + "\n"
    
    for day in trend_data:
        report += f"{day['date']:<15} {day['avg_functional_impact']:<20} {day['daily_messages']:<10}\n"
    
    # Calculate trend
    if len(trend_data) >= 2:
        first_impact = trend_data[0]['avg_functional_impact']
        last_impact = trend_data[-1]['avg_functional_impact']
        change = last_impact - first_impact
        trend = "📈 IMPROVING" if change < 0 else "📉 DECLINING" if change > 0 else "➡️ STABLE"
        report += f"\nOverall Trend: {trend} (Change: {change:+.1f})\n"
    
    return report + "\n"


def format_emotion_clusters_report(clusters_data: List[Dict[str, Any]]) -> str:
    """Format emotion cluster distribution"""
    report = "🎯 EMOTION CLUSTER DISTRIBUTION\n"
    report += "=" * 60 + "\n\n"
    
    if not clusters_data:
        return report + "No data available\n"
    
    cluster_names = {
        "JOY": "😊 JOY (Positive)",
        "SADNESS": "😢 SADNESS (Melancholic)",
        "ANGER": "😠 ANGER (Agitated)",
        "FEAR": "😨 FEAR (Anxious)",
        "SHAME": "😔 SHAME (Self-Critical)",
        "COMPLEX": "🌀 COMPLEX (Mixed)"
    }
    
    report += f"{'Cluster':<25} {'Frequency':<12} {'%':<8} {'Avg Intensity':<15}\n"
    report += "-" * 60 + "\n"
    
    for cluster in clusters_data:
        name = cluster_names.get(cluster['cluster'], cluster['cluster'])
        report += f"{name:<25} {cluster['frequency']:<12} "
        report += f"{cluster['percentage']:<8}% {cluster['avg_intensity']:<15}\n"
    
    return report + "\n"


def format_high_intensity_report(episodes_data: List[Dict[str, Any]]) -> str:
    """Format high intensity episodes (crisis detection)"""
    report = "🚨 HIGH-INTENSITY EPISODES (Intensity >= 8)\n"
    report += "=" * 70 + "\n\n"
    
    if not episodes_data:
        return report + "No high-intensity episodes detected ✅\n"
    
    report += f"Total episodes: {len(episodes_data)}\n\n"
    
    for i, episode in enumerate(episodes_data[:10], 1):  # Show last 10
        report += f"{i}. [{episode['timestamp']}]\n"
        report += f"   Emotion: {episode['emotion']}\n"
        report += f"   Condition: {episode['condition']}\n"
        report += f"   Intensity: {episode['intensity']}/10\n"
        report += f"   Functional Impact: {episode['functional_impact']}/10\n"
        report += f"   Trigger: {episode['trigger']}\n"
        report += f"   Message: {episode['message'][:80]}...\n\n"
    
    return report


def format_recurring_patterns_report(patterns_data: List[Dict[str, Any]]) -> str:
    """Format recurring patterns"""
    report = "🔄 RECURRING PATTERNS\n"
    report += "=" * 70 + "\n\n"
    
    if not patterns_data:
        return report + "No recurring patterns detected\n"
    
    for pattern in patterns_data:
        report += f"Pattern: {pattern['emotion']} / {pattern['condition']}\n"
        report += f"  Trigger: {pattern['trigger']}\n"
        report += f"  Occurrences: {pattern['recurring_count']}\n"
        report += f"  Avg Intensity: {pattern['avg_intensity']}/10\n"
        report += f"  Dates seen: {', '.join(pattern['dates'][-5:])}...\n\n"
    
    return report


def generate_html_report(report_data: Dict[str, Any]) -> str:
    """Generate an HTML report"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Monthly Mental Health Report - {report_data.get('period', 'N/A')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background-color: #007bff; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .metric {{ display: inline-block; background-color: #f0f0f0; padding: 15px; margin: 10px; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #666; font-size: 12px; }}
        .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
        .success {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Monthly Mental Health Report</h1>
        <p><strong>Period:</strong> {report_data.get('period', 'N/A')}</p>
        <p><strong>Generated:</strong> {report_data.get('report_date', 'N/A')}</p>
        
        <h2>📊 Summary Metrics</h2>
"""
    
    # Add metrics
    if 'emotions' in report_data.get('sections', {}):
        emotions = report_data['sections']['emotions']
        if emotions:
            top_emotion = emotions[0]
            html += f"""
        <div class="metric">
            <div class="metric-label">Top Emotion</div>
            <div class="metric-value">{top_emotion.get('emotion', 'N/A')}</div>
            <div class="metric-label">{top_emotion.get('count', 0)} occurrences</div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    return html


async def main():
    """Example usage"""
    print("\n" + "=" * 70)
    print("📊 MONTHLY REPORT GENERATOR")
    print("=" * 70 + "\n")
    
    print("Usage Example:")
    print("""
    # In your FastAPI endpoint:
    from monthly_report_queries import generate_monthly_report
    
    @app.get("/reports/monthly/{user_id}")
    async def get_monthly_report(user_id: str):
        report = await generate_monthly_report(db, user_id)
        return report
    
    # Or generate a text report:
    from monthly_report_queries import generate_monthly_report
    from backend.monthly_report_generator import *
    
    report = await generate_monthly_report(db, user_id)
    text_report = format_emotion_report(report['sections']['emotions'])
    print(text_report)
    """)


if __name__ == "__main__":
    asyncio.run(main())
