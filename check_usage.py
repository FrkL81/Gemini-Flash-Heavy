#!/usr/bin/env python3
"""
Script para verificar el estado actual de uso de los modelos
"""

import yaml
from usage_tracker import UsageTracker

def main():
    """Check current usage status for all models"""
    print("🔍 Verificando estado de uso de modelos...")
    
    try:
        # Load configuration
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Get rate limits
        rate_limits = config['google_ai_studio']['models']['rate_limits']
        
        # Initialize usage tracker
        tracker = UsageTracker()
        
        # Print usage summary
        tracker.print_usage_summary(rate_limits)
        
        # Additional recommendations
        print("\n💡 RECOMENDACIONES PARA MAXIMIZAR USO:")
        
        all_stats = tracker.get_all_usage_stats(rate_limits)
        
        # Find best model to use next
        available_models = []
        for model_name, stats in all_stats.items():
            if stats['can_make_request']:
                efficiency = (stats['daily_used'] / stats['daily_limit']) * 100
                available_models.append((model_name, efficiency, stats['daily_remaining']))
        
        if available_models:
            # Sort by lowest usage (most remaining capacity)
            available_models.sort(key=lambda x: x[1])  # Sort by efficiency (lowest first)
            
            print(f"\n🎯 MODELOS RECOMENDADOS (ordenados por capacidad restante):")
            for i, (model, efficiency, remaining) in enumerate(available_models[:3], 1):
                print(f"   {i}. {model}")
                print(f"      - Eficiencia: {efficiency:.1f}%")
                print(f"      - Solicitudes restantes hoy: {remaining}")
        else:
            print("\n⚠️  TODOS LOS MODELOS HAN ALCANZADO SUS LÍMITES")
            print("   Espera a que se renueven los límites por minuto o diarios")
        
        # Calculate total remaining capacity
        total_remaining = sum(stats['daily_remaining'] for stats in all_stats.values())
        print(f"\n📊 CAPACIDAD TOTAL RESTANTE HOY: {total_remaining} solicitudes")
        
        if total_remaining > 50:
            print("✅ Excelente capacidad restante para investigación profunda")
        elif total_remaining > 20:
            print("⚠️  Capacidad moderada - usa con moderación")
        else:
            print("🚨 Capacidad limitada - conserva para tareas críticas")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()