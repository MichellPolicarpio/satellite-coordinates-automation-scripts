# Autor: Michell Alexis Policarpio Moran
# Proyecto: Servicio Social en Grupo Mas Agua
# Descripción: Script automatizado para la captura masiva de imágenes satelitales
#             de coordenadas geográficas de piscinas y áreas sin piscinas
#             utilizando la API de Google Maps Static para la generación de datasets

import requests
from PIL import Image
import io
import os
import time
import random
import json
from typing import List, Dict
from datetime import datetime

class MassImageCapture:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/staticmap"
        self.output_dir = "scripts_automatizadores/data"
        self.coordinates_file = "scripts_automatizadores/coordinates.json"
        
        # Crear directorios
        os.makedirs(f"{self.output_dir}/pools", exist_ok=True)
        os.makedirs(f"{self.output_dir}/no_pools", exist_ok=True)
    
    def load_coordinates(self) -> Dict:
        """Carga las coordenadas desde el archivo JSON"""
        try:
            with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ No se encontró el archivo {self.coordinates_file}")
            print("💡 Ejecuta primero el script 01_coordinate_collector.py")
            return {"pools": [], "no_pools": []}
        except Exception as e:
            print(f"❌ Error cargando coordenadas: {e}")
            return {"pools": [], "no_pools": []}
    
    def capture_single_image(self, lat: float, lon: float, zoom: int = 19, 
                            size: str = "100x100", filename: str = None) -> bool:
        """Captura una imagen de 100x100 píxeles con zoom medio"""
        try:
            params = {
                'center': f"{lat},{lon}",
                'zoom': zoom,
                'size': size,
                'maptype': 'satellite',
                'key': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                
                # Convertir a RGB si está en modo P (paleta)
                if img.mode == 'P':
                    img = img.convert('RGB')
                
                # Redimensionar a 50x50 para el dataset
                img = img.resize((50, 50))
                
                if filename is None:
                    timestamp = int(time.time())
                    filename = f"img_{lat}_{lon}_{timestamp}.jpg"
                
                img.save(filename, 'JPEG', quality=95)
                print(f"✅ Capturada: {filename} en ({lat}, {lon})")
                return True
            else:
                print(f"❌ Error capturando ({lat}, {lon}): {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en ({lat}, {lon}): {e}")
            return False
    
    def capture_single_coordinate(self, coord_data: Dict, coord_type: str) -> int:
        """Captura una sola imagen por coordenada"""
        lat = coord_data["lat"]
        lon = coord_data["lon"]
        description = coord_data["description"]
        
        print(f"\n🎯 Procesando: {description} en ({lat}, {lon})")
        
        captured_count = 0
        
        # Captura única
        filename = f"{description}.jpg"
        if self.capture_single_image(lat, lon, filename=filename):
            # Mover a la carpeta correcta
            source_path = filename
            if coord_type == "pool":
                dest_path = f"{self.output_dir}/pools/{filename}"
            else:
                dest_path = f"{self.output_dir}/no_pools/{filename}"
            
            os.rename(source_path, dest_path)
            captured_count += 1
        
        return captured_count
    
    def mass_capture_all(self) -> Dict:
        """Captura masiva de todas las coordenadas (1 imagen por coordenada)"""
        coordinates = self.load_coordinates()
        
        if not coordinates["pools"] and not coordinates["no_pools"]:
            print("❌ No hay coordenadas para capturar")
            return {"pools": 0, "no_pools": 0}
        
        print("🚀 Iniciando captura masiva...")
        print(f"📊 Piscinas a procesar: {len(coordinates['pools'])}")
        print(f"📊 Áreas sin piscinas a procesar: {len(coordinates['no_pools'])}")
        print(f"📊 1 imagen por coordenada")
        
        total_pools_captured = 0
        total_no_pools_captured = 0
        
        # Capturar piscinas
        print("\n🏊 Capturando piscinas...")
        for i, pool_data in enumerate(coordinates["pools"], 1):
            print(f"\n[{i}/{len(coordinates['pools'])}] Procesando piscina...")
            captured = self.capture_single_coordinate(pool_data, "pool")
            total_pools_captured += captured
        
        # Capturar áreas sin piscinas
        print("\n🏠 Capturando áreas sin piscinas...")
        for i, no_pool_data in enumerate(coordinates["no_pools"], 1):
            print(f"\n[{i}/{len(coordinates['no_pools'])}] Procesando área sin piscinas...")
            captured = self.capture_single_coordinate(no_pool_data, "no_pool")
            total_no_pools_captured += captured
        
        # Actualizar estado en el JSON
        self.update_capture_status()
        
        return {
            "pools": total_pools_captured,
            "no_pools": total_no_pools_captured,
            "total": total_pools_captured + total_no_pools_captured
        }
    
    def update_capture_status(self):
        """Actualiza el estado de captura en el archivo JSON"""
        try:
            with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                coordinates = json.load(f)
            
            # Marcar todas como capturadas
            for pool in coordinates["pools"]:
                pool["captured"] = True
            for no_pool in coordinates["no_pools"]:
                no_pool["captured"] = True
            
            # Actualizar metadatos
            coordinates["metadata"]["last_capture"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            coordinates["metadata"]["capture_completed"] = True
            
            with open(self.coordinates_file, 'w', encoding='utf-8') as f:
                json.dump(coordinates, f, indent=2, ensure_ascii=False)
            
            print("💾 Estado de captura actualizado en scripts_automatizadores/coordinates.json")
            
        except Exception as e:
            print(f"⚠️ Error actualizando estado: {e}")
    
    def show_capture_summary(self):
        """Muestra un resumen de la captura"""
        coordinates = self.load_coordinates()
        
        print("\n📋 RESUMEN DE CAPTURA")
        print("=" * 40)
        print(f"🏊 Piscinas configuradas: {len(coordinates['pools'])}")
        print(f"🏠 Áreas sin piscinas configuradas: {len(coordinates['no_pools'])}")
        
        if coordinates["pools"]:
            print("\n📍 Piscinas:")
            for pool in coordinates["pools"]:
                status = "✅ Capturada" if pool.get("captured", False) else "⏳ Pendiente"
                print(f"   • {pool['description']} - {status}")
        
        if coordinates["no_pools"]:
            print("\n📍 Áreas sin piscinas:")
            for no_pool in coordinates["no_pools"]:
                status = "✅ Capturada" if no_pool.get("captured", False) else "⏳ Pendiente"
                print(f"   • {no_pool['description']} - {status}")

def show_usage_instructions():
    """Muestra instrucciones detalladas de uso del sistema"""
    print("\n💡 INSTRUCCIONES DE USO DEL SISTEMA")
    print("=" * 60)
    print("🎯 PROPÓSITO:")
    print("   Este script captura automáticamente imágenes satelitales de")
    print("   coordenadas geográficas para generar datasets de entrenamiento")
    print("   de modelos de detección de piscinas.")
    print()
    print("📋 REQUISITOS PREVIOS:")
    print("   1. ✅ Ejecutar 01_coordinate_collector.py para configurar coordenadas")
    print("   2. ✅ Tener archivo scripts_automatizadores/coordinates.json con coordenadas válidas")
    print("   3. ✅ API key de Google Maps configurada y habilitada")
    print("   4. ✅ Conexión a internet estable")
    print()
    print("🚀 PROCESO DE CAPTURA:")
    print("   1. El sistema lee las coordenadas del archivo scripts_automatizadores/coordinates.json")
    print("   2. Para cada coordenada, solicita una imagen satelital a Google")
    print("   3. Las imágenes se redimensionan a 50x50 píxeles (formato dataset)")
    print("   4. Se guardan en las carpetas correspondientes (pools/ o no_pools/)")
    print("   5. Se actualiza el estado de captura en el JSON")
    print()
    print("📁 ESTRUCTURA DE SALIDA:")
    print("   scripts_automatizadores/data/")
    print("   ├── pools/          (imágenes de piscinas)")
    print("   └── no_pools/       (imágenes sin piscinas)")
    print()
    print("⚠️  CONSIDERACIONES:")
    print("   • Cada imagen consume 1 solicitud de la API de Google")
    print("   • El proceso puede tomar tiempo con muchas coordenadas")
    print("   • Las imágenes se guardan en formato JPEG con calidad 95%")
    print("   • Zoom fijo en 19 para resolución óptima")
    print()
    print("🔧 SOLUCIÓN DE PROBLEMAS:")
    print("   • Si hay errores de API: verificar límites y cuotas")
    print("   • Si no hay coordenadas: ejecutar el colector primero")
    print("   • Si falla la captura: verificar conexión a internet")
    print("=" * 60)

def main():
    # Tu API key de Google Maps
    API_KEY = "AIzaSyAjhQAX8-uo4bYZ7NeAU_yJDN_zPKZq2qw"  # API key configurada
    
    if API_KEY == "TU_API_KEY_AQUI":
        print("❌ ERROR: Debes configurar tu API key de Google Maps")
        print("💡 Instrucciones para obtener la API key:")
        print("   1. Ve a https://console.cloud.google.com/")
        print("   2. Selecciona tu proyecto 'CapturaImagenes'")
        print("   3. Ve a 'APIs y servicios' → 'Biblioteca'")
        print("   4. Busca y habilita 'Maps Static API'")
        print("   5. Ve a 'APIs y servicios' → 'Credenciales'")
        print("   6. Crea una nueva 'Clave de API'")
        print("   7. Copia la clave y reemplaza 'TU_API_KEY_AQUI' en este script")
        return
    
    # Crear instancia del capturador
    capturer = MassImageCapture(API_KEY)
    
    while True:
        print("\n📸 CAPTURA MASIVA DE IMÁGENES")
        print("=" * 50)
        print("🌐 SISTEMA DE CAPTURA AUTOMATIZADA")
        print("   Este script captura imágenes satelitales de las coordenadas")
        print("   configuradas en scripts_automatizadores/coordinates.json para generar datasets")
        print()
        print("📋 OPCIONES DISPONIBLES:")
        print("1. 📊 Mostrar resumen de coordenadas")
        print("   - Ver estado de piscinas y áreas sin piscinas")
        print("   - Verificar coordenadas configuradas")
        print()
        print("2. 🚀 Iniciar captura masiva")
        print("   - Capturar 1 imagen por coordenada")
        print("   - Imágenes de 50x50 píxeles (formato dataset)")
        print("   - Guardar en carpetas pools/ y no_pools/")
        print()
        print("3. 💡 Ver instrucciones de uso")
        print("4. 🚪 Salir del programa")
        print("=" * 50)
        
        choice = input("Elige una opción (1/2/3/4): ").strip()
        
        if choice == "1":
            capturer.show_capture_summary()
            input("\nPresiona Enter para continuar...")
        elif choice == "2":
            print("\n🚀 Iniciando captura masiva...")
            print("⚠️  NOTA: Este proceso puede tomar tiempo dependiendo")
            print("   de la cantidad de coordenadas configuradas.")
            confirm = input("\n¿Continuar? (s/n): ").strip().lower()
            if confirm in ['s', 'si', 'sí', 'y', 'yes']:
                results = capturer.mass_capture_all()
                print(f"\n🎉 ¡Captura completada!")
                print(f"📊 Total imágenes capturadas: {results['total']}")
                print(f"🏊 Piscinas: {results['pools']}")
                print(f"🏠 Sin piscinas: {results['no_pools']}")
                input("\nPresiona Enter para continuar...")
            else:
                print("❌ Captura cancelada")
        elif choice == "3":
            show_usage_instructions()
            input("\nPresiona Enter para continuar...")
        elif choice == "4":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
