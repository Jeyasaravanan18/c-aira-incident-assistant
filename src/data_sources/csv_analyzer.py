"""
CSV Analyzer for Incident Statistics
Analyzes incident_stats.csv to provide insights and trends
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class CSVAnalyzer:
    """Analyzes incident statistics from CSV file"""
    
    def __init__(self, csv_path: str = "data/incident_stats.csv"):
        """
        Initialize CSV analyzer
        
        Args:
            csv_path: Path to the incident statistics CSV file
        """
        self.csv_path = Path(csv_path)
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """Load CSV data into pandas DataFrame"""
        try:
            if self.csv_path.exists():
                self.df = pd.read_csv(self.csv_path)
                logger.info(f"Loaded {len(self.df)} incident records from CSV")
            else:
                logger.warning(f"CSV file not found: {self.csv_path}")
                self.df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            self.df = pd.DataFrame()
    
    def get_total_incidents(self) -> int:
        """Get total number of incidents"""
        if self.df is not None and not self.df.empty:
            return int(self.df['count'].sum())
        return 0
    
    def get_incident_by_type(self) -> Dict[str, int]:
        """Get incident counts grouped by type"""
        if self.df is not None and not self.df.empty:
            return self.df.groupby('incident_type')['count'].sum().to_dict()
        return {}
    
    def get_avg_resolution_time(self) -> float:
        """Get average resolution time across all incidents"""
        if self.df is not None and not self.df.empty:
            # Weighted average based on incident count
            total_time = (self.df['avg_resolution_hours'] * self.df['count']).sum()
            total_count = self.df['count'].sum()
            return round(total_time / total_count, 2) if total_count > 0 else 0
        return 0
    
    def get_severity_distribution(self) -> Dict[str, int]:
        """Get incident counts by severity level"""
        if self.df is not None and not self.df.empty:
            return self.df.groupby('severity')['count'].sum().to_dict()
        return {}
    
    def get_monthly_trends(self) -> pd.DataFrame:
        """Get monthly incident trends"""
        if self.df is not None and not self.df.empty:
            monthly = self.df.groupby('month').agg({
                'count': 'sum',
                'avg_resolution_hours': 'mean'
            }).round(2)
            return monthly
        return pd.DataFrame()
    
    def get_top_incidents(self, n: int = 3) -> List[Dict[str, Any]]:
        """
        Get top N most common incident types
        
        Args:
            n: Number of top incidents to return
            
        Returns:
            List of dictionaries with incident type and count
        """
        if self.df is not None and not self.df.empty:
            top = self.df.groupby('incident_type')['count'].sum().nlargest(n)
            return [{'type': idx, 'count': int(val)} for idx, val in top.items()]
        return []
    
    def get_insights(self) -> List[str]:
        """
        Generate insights from the data
        
        Returns:
            List of insight strings
        """
        insights = []
        
        if self.df is None or self.df.empty:
            return ["No incident data available"]
        
        # Most common incident type
        top_incidents = self.get_top_incidents(1)
        if top_incidents:
            insights.append(
                f"🔴 Most common incident: **{top_incidents[0]['type'].replace('_', ' ').title()}** "
                f"({top_incidents[0]['count']} occurrences)"
            )
        
        # Average resolution time
        avg_time = self.get_avg_resolution_time()
        insights.append(f"⏱️ Average resolution time: **{avg_time} hours**")
        
        # Severity analysis
        severity_dist = self.get_severity_distribution()
        if severity_dist:
            critical_count = severity_dist.get('critical', 0)
            high_count = severity_dist.get('high', 0)
            if critical_count > 0:
                insights.append(f"⚠️ Critical incidents: **{critical_count}** (require immediate attention)")
            if high_count > 0:
                insights.append(f"🟠 High severity incidents: **{high_count}**")
        
        # Monthly trend
        monthly = self.get_monthly_trends()
        if not monthly.empty and len(monthly) >= 2:
            last_month = monthly.iloc[-1]['count']
            prev_month = monthly.iloc[-2]['count']
            change = ((last_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
            
            if change > 10:
                insights.append(f"📈 Incidents increased by **{change:.1f}%** last month")
            elif change < -10:
                insights.append(f"📉 Incidents decreased by **{abs(change):.1f}%** last month")
            else:
                insights.append(f"📊 Incident volume stable (±{abs(change):.1f}%)")
        
        return insights
    
    def get_chart_data(self) -> Dict[str, Any]:
        """
        Get data formatted for charts
        
        Returns:
            Dictionary with chart data
        """
        if self.df is None or self.df.empty:
            return {}
        
        return {
            'incident_by_type': self.get_incident_by_type(),
            'severity_distribution': self.get_severity_distribution(),
            'monthly_trends': self.get_monthly_trends().to_dict(),
            'top_incidents': self.get_top_incidents(5)
        }
    
    def search_similar_incidents(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for similar incidents based on query
        
        Args:
            query: Search query (incident description)
            
        Returns:
            List of matching incident types with statistics
        """
        if self.df is None or self.df.empty:
            return []
        
        query_lower = query.lower()
        results = []
        
        # Search in incident types
        for incident_type in self.df['incident_type'].unique():
            if any(word in incident_type for word in query_lower.split()):
                type_data = self.df[self.df['incident_type'] == incident_type]
                total_count = int(type_data['count'].sum())
                avg_time = round(type_data['avg_resolution_hours'].mean(), 2)
                severity = type_data['severity'].mode()[0] if not type_data.empty else 'unknown'
                
                results.append({
                    'incident_type': incident_type,
                    'total_occurrences': total_count,
                    'avg_resolution_hours': avg_time,
                    'severity': severity,
                    'insight': f"This incident has occurred {total_count} times with an average resolution time of {avg_time} hours."
                })
        
        return results
