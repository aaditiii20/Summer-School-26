"""
ML Clustering Intelligence Module for Outbreak Detection
Pattern recognition for regional disease outbreaks
"""
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# ========== CLUSTERING ENGINE ==========

class OutbreakClusterer:
    """K-Means clustering for disease pattern detection"""
    
    def __init__(self, n_clusters: int = 5, max_iterations: int = 100):
        self.n_clusters = n_clusters
        self.max_iterations = max_iterations
        self.centroids = []
        self.clusters = {}
    
    def euclidean_distance(self, p1: List[float], p2: List[float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))
    
    def initialize_centroids(self, data: List[List[float]]) -> None:
        """Initialize centroids randomly from data points"""
        import random
        self.centroids = random.sample(data, min(self.n_clusters, len(data)))
    
    def assign_clusters(self, data: List[List[float]]) -> Dict:
        """Assign each data point to nearest centroid"""
        clusters = defaultdict(list)
        
        for idx, point in enumerate(data):
            distances = [self.euclidean_distance(point, centroid) for centroid in self.centroids]
            nearest_cluster = distances.index(min(distances))
            clusters[nearest_cluster].append(idx)
        
        return clusters
    
    def calculate_centroids(self, data: List[List[float]], clusters: Dict) -> List[List[float]]:
        """Calculate new centroids based on cluster means"""
        new_centroids = []
        
        for i in range(self.n_clusters):
            if i in clusters and clusters[i]:
                cluster_points = [data[idx] for idx in clusters[i]]
                new_centroid = [sum(col) / len(cluster_points) 
                               for col in zip(*cluster_points)]
                new_centroids.append(new_centroid)
            else:
                new_centroids.append(self.centroids[i] if i < len(self.centroids) else [0] * len(data[0]))
        
        return new_centroids
    
    def fit(self, data: List[List[float]]) -> Dict:
        """Fit clustering model"""
        if not data:
            return {"error": "No data provided"}
        
        self.initialize_centroids(data)
        
        for iteration in range(self.max_iterations):
            old_centroids = [c[:] for c in self.centroids]
            
            self.clusters = self.assign_clusters(data)
            self.centroids = self.calculate_centroids(data, self.clusters)
            
            # Check convergence
            if all(self.euclidean_distance(old, new) < 0.001 
                   for old, new in zip(old_centroids, self.centroids)):
                return {"converged": True, "iterations": iteration + 1}
        
        return {"converged": False, "iterations": self.max_iterations}


class OutbreakDetector:
    """Outbreak prediction from morbidity data"""
    
    def __init__(self):
        self.clusterer = OutbreakClusterer(n_clusters=5)
        self.disease_history = []
        self.regional_baselines = {}
    
    def extract_features(self, morbidity_data: List[Dict]) -> List[List[float]]:
        """Extract numerical features from morbidity data"""
        features = []
        
        for record in morbidity_data:
            # Feature vector: [cases, deaths, age_mean, duration_days, spread_rate]
            feature_vector = [
                record.get('cases', 0),
                record.get('deaths', 0),
                record.get('avg_age', 40),
                record.get('duration_days', 7),
                record.get('spread_rate', 1.0)
            ]
            features.append(feature_vector)
        
        return features
    
    def calculate_outbreak_risk(self, cluster_data: List[Dict], region: str) -> Dict:
        """Calculate outbreak risk for a cluster"""
        if not cluster_data:
            return {"risk_level": "low", "score": 0}
        
        # Risk scoring factors
        total_cases = sum(d.get('cases', 0) for d in cluster_data)
        total_deaths = sum(d.get('deaths', 0) for d in cluster_data)
        avg_spread = sum(d.get('spread_rate', 1.0) for d in cluster_data) / len(cluster_data)
        
        # Mortality rate
        mortality_rate = total_deaths / total_cases if total_cases > 0 else 0
        
        # Risk score (0-100)
        risk_score = min(100, 
            (total_cases / 100) * 20 +  # Cases weight
            (mortality_rate * 100) * 30 +  # Mortality weight
            (avg_spread * 20) * 15 +  # Spread rate weight
            (len(cluster_data) / 5) * 20  # Cluster size weight
        )
        
        # Risk level classification
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "cases": total_cases,
            "deaths": total_deaths,
            "mortality_rate": round(mortality_rate, 4),
            "avg_spread_rate": round(avg_spread, 2),
            "cluster_size": len(cluster_data)
        }
    
    def detect_outbreaks(self, morbidity_data: List[Dict], region: str = "india") -> Dict:
        """Detect outbreak patterns in morbidity data"""
        
        if not morbidity_data:
            return {
                "status": "no_data",
                "outbreaks": [],
                "summary": "No morbidity data provided"
            }
        
        # Extract features
        features = self.extract_features(morbidity_data)
        
        # Cluster data
        self.clusterer.fit(features)
        
        # Analyze each cluster
        outbreaks = []
        for cluster_id, point_indices in self.clusterer.clusters.items():
            if not point_indices:
                continue
            
            cluster_data = [morbidity_data[idx] for idx in point_indices]
            risk_assessment = self.calculate_outbreak_risk(cluster_data, region)
            
            # Only report significant outbreaks
            if risk_assessment['risk_level'] in ['high', 'critical']:
                outbreak = {
                    "cluster_id": cluster_id,
                    "region": region,
                    "diseases": list(set(d.get('disease', 'Unknown') for d in cluster_data)),
                    "risk_assessment": risk_assessment,
                    "affected_districts": list(set(d.get('district', 'Unknown') for d in cluster_data)),
                    "prediction_timestamp": datetime.utcnow().isoformat()
                }
                outbreaks.append(outbreak)
        
        # Sort by risk score
        outbreaks.sort(key=lambda x: x['risk_assessment']['risk_score'], reverse=True)
        
        return {
            "status": "success",
            "region": region,
            "total_clusters": len(self.clusterer.clusters),
            "outbreaks_detected": len(outbreaks),
            "outbreaks": outbreaks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def predict_trajectory(self, current_outbreak: Dict, days_ahead: int = 7) -> Dict:
        """Predict future outbreak trajectory"""
        
        risk_score = current_outbreak.get('risk_assessment', {}).get('risk_score', 0)
        spread_rate = current_outbreak.get('risk_assessment', {}).get('avg_spread_rate', 1.0)
        
        projections = []
        for day in range(1, days_ahead + 1):
            # Simple exponential growth model
            projected_cases = current_outbreak.get('risk_assessment', {}).get('cases', 0) * (spread_rate ** day)
            
            projections.append({
                "day": day,
                "projected_cases": round(projected_cases),
                "trend": "increasing" if spread_rate > 1.0 else "stable"
            })
        
        return {
            "current_outbreak": current_outbreak.get('diseases', []),
            "region": current_outbreak.get('region'),
            "projections": projections,
            "forecast_horizon": days_ahead,
            "model": "exponential_growth"
        }


# ========== SAMPLE DATA FOR TESTING ==========

SAMPLE_MORBIDITY_DATA = [
    {"disease": "COVID-19", "cases": 250, "deaths": 5, "avg_age": 45, "duration_days": 14, "spread_rate": 1.8, "district": "Mumbai"},
    {"disease": "COVID-19", "cases": 180, "deaths": 3, "avg_age": 42, "duration_days": 12, "spread_rate": 1.6, "district": "Pune"},
    {"disease": "Dengue", "cases": 120, "deaths": 2, "avg_age": 35, "duration_days": 10, "spread_rate": 1.3, "district": "Bangalore"},
    {"disease": "Dengue", "cases": 95, "deaths": 1, "avg_age": 38, "duration_days": 9, "spread_rate": 1.2, "district": "Hyderabad"},
    {"disease": "Influenza", "cases": 80, "deaths": 1, "avg_age": 40, "duration_days": 7, "spread_rate": 1.1, "district": "Chennai"},
    {"disease": "Malaria", "cases": 45, "deaths": 0, "avg_age": 50, "duration_days": 5, "spread_rate": 0.9, "district": "Jharkhand"},
]


# ========== API ENDPOINT ==========

def detect_outbreaks_handler(request) -> Dict:
    """Outbreak detection endpoint"""
    
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    
    if path == '/ml/outbreaks/detect' and method == 'POST':
        # Detect outbreaks
        try:
            body = json.loads(request.get('body', '{}'))
            morbidity_data = body.get('morbidity_data', SAMPLE_MORBIDITY_DATA)
            region = body.get('region', 'india')
            
            detector = OutbreakDetector()
            result = detector.detect_outbreaks(morbidity_data, region)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({"error": str(e)})
            }
    
    elif path == '/ml/outbreaks/predict' and method == 'POST':
        # Predict trajectory
        try:
            body = json.loads(request.get('body', '{}'))
            outbreak = body.get('outbreak')
            days_ahead = body.get('days_ahead', 7)
            
            if not outbreak:
                return {
                    'statusCode': 400,
                    'body': json.dumps({"error": "outbreak data required"})
                }
            
            detector = OutbreakDetector()
            result = detector.predict_trajectory(outbreak, days_ahead)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({"error": str(e)})
            }
    
    elif path == '/ml/outbreaks/sample' and method == 'GET':
        # Get sample data
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "sample_data": SAMPLE_MORBIDITY_DATA,
                "total_records": len(SAMPLE_MORBIDITY_DATA)
            })
        }
     
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({"error": "Not found"})
        }


# For testing
if __name__ == "__main__":
    detector = OutbreakDetector()
    result = detector.detect_outbreaks(SAMPLE_MORBIDITY_DATA, "india")
    print(json.dumps(result, indent=2))
    
    if result.get('outbreaks'):
        trajectory = detector.predict_trajectory(result['outbreaks'][0], 7)
        print("\nTrajectory Prediction:")
        print(json.dumps(trajectory, indent=2))
