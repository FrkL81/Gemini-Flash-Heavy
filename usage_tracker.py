import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import threading

class UsageTracker:
    """Track API usage for Google AI Studio models to maximize free tier usage"""
    
    def __init__(self, config_path="usage_data.json"):
        self.config_path = config_path
        self.lock = threading.Lock()
        self.usage_data = self._load_usage_data()
        
    def _load_usage_data(self) -> Dict[str, Any]:
        """Load usage data from file or create new structure"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                # Clean old data (older than 24 hours)
                self._clean_old_data(data)
                return data
            except Exception as e:
                print(f"Error loading usage data: {e}")
        
        # Default structure
        return {
            "models": {},
            "last_reset": datetime.now().isoformat()
        }
    
    def _clean_old_data(self, data: Dict[str, Any]):
        """Remove usage data older than 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for model_name in data.get("models", {}):
            model_data = data["models"][model_name]
            if "requests" in model_data:
                # Filter requests from last 24 hours
                recent_requests = [
                    req for req in model_data["requests"]
                    if datetime.fromisoformat(req["timestamp"]) > cutoff_time
                ]
                model_data["requests"] = recent_requests
                model_data["daily_count"] = len(recent_requests)
    
    def _save_usage_data(self):
        """Save usage data to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"Error saving usage data: {e}")
    
    def record_request(self, model_name: str, request_type: str = "generate"):
        """Record a new API request"""
        with self.lock:
            current_time = datetime.now()
            
            if "models" not in self.usage_data:
                self.usage_data["models"] = {}
            
            if model_name not in self.usage_data["models"]:
                self.usage_data["models"][model_name] = {
                    "requests": [],
                    "daily_count": 0,
                    "minute_count": 0,
                    "last_request": None
                }
            
            model_data = self.usage_data["models"][model_name]
            
            # Add new request
            request_record = {
                "timestamp": current_time.isoformat(),
                "type": request_type
            }
            model_data["requests"].append(request_record)
            
            # Update counters
            self._update_counters(model_name)
            model_data["last_request"] = current_time.isoformat()
            
            # Save to file
            self._save_usage_data()
    
    def _update_counters(self, model_name: str):
        """Update minute and daily counters for a model"""
        model_data = self.usage_data["models"][model_name]
        current_time = datetime.now()
        
        # Count requests in last minute
        minute_ago = current_time - timedelta(minutes=1)
        minute_requests = [
            req for req in model_data["requests"]
            if datetime.fromisoformat(req["timestamp"]) > minute_ago
        ]
        model_data["minute_count"] = len(minute_requests)
        
        # Count requests in last 24 hours
        day_ago = current_time - timedelta(hours=24)
        daily_requests = [
            req for req in model_data["requests"]
            if datetime.fromisoformat(req["timestamp"]) > day_ago
        ]
        model_data["daily_count"] = len(daily_requests)
    
    def get_usage_stats(self, model_name: str, limits: Dict[str, int]) -> Dict[str, Any]:
        """Get current usage statistics for a model"""
        with self.lock:
            if model_name not in self.usage_data.get("models", {}):
                return {
                    "minute_used": 0,
                    "minute_remaining": limits.get("rpm", 0),
                    "daily_used": 0,
                    "daily_remaining": limits.get("daily", 0),
                    "can_make_request": True,
                    "next_available": None
                }
            
            self._update_counters(model_name)
            model_data = self.usage_data["models"][model_name]
            
            minute_used = model_data["minute_count"]
            daily_used = model_data["daily_count"]
            
            minute_limit = limits.get("rpm", 0)
            daily_limit = limits.get("daily", 0)
            
            minute_remaining = max(0, minute_limit - minute_used)
            daily_remaining = max(0, daily_limit - daily_used)
            
            can_make_request = (minute_remaining > 0 and daily_remaining > 0)
            
            # Calculate when next request can be made
            next_available = None
            if not can_make_request and model_data["requests"]:
                if minute_remaining <= 0:
                    # Need to wait for minute window
                    oldest_in_minute = min([
                        datetime.fromisoformat(req["timestamp"])
                        for req in model_data["requests"]
                        if datetime.fromisoformat(req["timestamp"]) > datetime.now() - timedelta(minutes=1)
                    ])
                    next_available = (oldest_in_minute + timedelta(minutes=1)).isoformat()
            
            return {
                "minute_used": minute_used,
                "minute_remaining": minute_remaining,
                "daily_used": daily_used,
                "daily_remaining": daily_remaining,
                "can_make_request": can_make_request,
                "next_available": next_available,
                "minute_limit": minute_limit,
                "daily_limit": daily_limit
            }
    
    def get_all_usage_stats(self, rate_limits: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all models"""
        stats = {}
        for model_name, limits in rate_limits.items():
            stats[model_name] = self.get_usage_stats(model_name, limits)
        return stats
    
    def print_usage_summary(self, rate_limits: Dict[str, Dict[str, int]]):
        """Print a formatted usage summary"""
        print("\n" + "="*80)
        print("📊 RESUMEN DE USO DE MODELOS - CAPA GRATUITA")
        print("="*80)
        
        all_stats = self.get_all_usage_stats(rate_limits)
        
        for model_name, stats in all_stats.items():
            print(f"\n🤖 {model_name}")
            print(f"   📈 Por minuto: {stats['minute_used']}/{stats['minute_limit']} "
                  f"(quedan {stats['minute_remaining']})")
            print(f"   📅 Diario: {stats['daily_used']}/{stats['daily_limit']} "
                  f"(quedan {stats['daily_remaining']})")
            
            if stats['can_make_request']:
                print(f"   ✅ Estado: Disponible para nuevas solicitudes")
            else:
                print(f"   ❌ Estado: Límite alcanzado")
                if stats['next_available']:
                    next_time = datetime.fromisoformat(stats['next_available'])
                    print(f"   ⏰ Próxima disponibilidad: {next_time.strftime('%H:%M:%S')}")
            
            # Calculate efficiency percentage
            daily_efficiency = (stats['daily_used'] / stats['daily_limit']) * 100 if stats['daily_limit'] > 0 else 0
            print(f"   📊 Eficiencia diaria: {daily_efficiency:.1f}%")
        
        print("\n" + "="*80)
        
        # Overall summary
        total_requests = sum(stats['daily_used'] for stats in all_stats.values())
        total_capacity = sum(stats['daily_limit'] for stats in all_stats.values())
        overall_efficiency = (total_requests / total_capacity) * 100 if total_capacity > 0 else 0
        
        print(f"📈 RESUMEN GENERAL:")
        print(f"   Total solicitudes hoy: {total_requests}")
        print(f"   Capacidad total diaria: {total_capacity}")
        print(f"   Eficiencia general: {overall_efficiency:.1f}%")
        print("="*80)