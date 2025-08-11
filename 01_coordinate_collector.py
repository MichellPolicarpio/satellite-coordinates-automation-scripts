# Autor: Michell Alexis Policarpio Moran
# Servicio Social en Grupo Mas Agua
# Descripción: Scripts automatizados para la recolección masiva de coordenadas geográficas
#             de piscinas y áreas sin piscinas para la generación de datasets de entrenamiento

import json
import os
import re
import math
from typing import List, Dict

class CoordinateCollector:
    def __init__(self):
        self.coordinates_file = "scripts_automatizadores/coordinates.json"
        self.coordinates = {
            "pools": [],
            "no_pools": [],
            "metadata": {
                "total_pools": 0,
                "total_no_pools": 0,
                "last_updated": ""
            }
        }
        self.load_existing()
    
    def load_existing(self):
        """Carga coordenadas existentes si el archivo existe"""
        if os.path.exists(self.coordinates_file):
            try:
                with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                    self.coordinates = json.load(f)
                print(f"✅ Cargadas {len(self.coordinates['pools'])} piscinas y {len(self.coordinates['no_pools'])} áreas sin piscinas")
            except Exception as e:
                print(f"⚠️ Error cargando archivo: {e}")
    
    def convert_dms_to_decimal(self, coord_string: str) -> tuple:
        """
        Convierte coordenadas de Google Earth (19°11'19"N 96°07'32"W) 
        a formato decimal (19.1886, -96.1256)
        """
        try:
            # Separar latitud y longitud
            parts = coord_string.split()
            
            # Procesar latitud
            lat_part = parts[0]  # 19°11'19"N
            lat_match = re.match(r"(\d+)°(\d+)'(\d+)\"([NS])", lat_part)
            
            if lat_match:
                lat_deg = int(lat_match.group(1))
                lat_min = int(lat_match.group(2))
                lat_sec = int(lat_match.group(3))
                lat_dir = lat_match.group(4)
                
                lat_decimal = lat_deg + (lat_min / 60) + (lat_sec / 3600)
                if lat_dir == 'S':
                    lat_decimal = -lat_decimal
            else:
                raise ValueError("Formato de latitud incorrecto")
            
            # Procesar longitud
            lon_part = parts[1]  # 96°07'32"W
            lon_match = re.match(r"(\d+)°(\d+)'(\d+)\"([EW])", lon_part)
            
            if lon_match:
                lon_deg = int(lon_match.group(1))
                lon_min = int(lon_match.group(2))
                lon_sec = int(lon_match.group(3))
                lon_dir = lon_match.group(4)
                
                lon_decimal = lon_deg + (lon_min / 60) + (lon_sec / 3600)
                if lon_dir == 'W':
                    lon_decimal = -lon_decimal
            else:
                raise ValueError("Formato de longitud incorrecto")
            
            return (lat_decimal, lon_decimal)
            
        except Exception as e:
            print(f"❌ Error convirtiendo coordenadas: {e}")
            return None
    
    def parse_coordinate_input(self, user_input: str) -> tuple:
        """
        Parsea la entrada del usuario y detecta si es formato DMS o decimal
        Retorna: (lat, lon, coord_type, description) o None si hay error
        """
        try:
            # Detectar si es formato DMS (contiene °, ', ")
            if '°' in user_input and "'" in user_input and '"' in user_input:
                # Es formato DMS, convertir primero
                print("🔄 Detectado formato DMS, convirtiendo...")
                coords = self.convert_dms_to_decimal(user_input)
                if coords:
                    lat, lon = coords
                    print(f"✅ Convertido: ({lat:.6f}, {lon:.6f})")
                    
                    # Pedir tipo y descripción
                    coord_type = input("Tipo (pool/no_pool): ").strip()
                    description = input("Descripción (opcional): ").strip()
                    if not description:
                        description = f"Coord_{lat:.4f}_{lon:.4f}"
                    
                    return (lat, lon, coord_type, description)
                else:
                    return None
            else:
                # Es formato decimal, verificar si tiene tipo y descripción
                parts = user_input.split(',')
                if len(parts) >= 3:
                    # Formato completo: lat, lon, tipo, descripción
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    coord_type = parts[2].strip()
                    description = parts[3].strip() if len(parts) > 3 else f"Coord_{lat}_{lon}"
                    return (lat, lon, coord_type, description)
                elif len(parts) == 2:
                    # Solo coordenadas: pedir tipo y descripción
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    print(f"✅ Coordenadas detectadas: ({lat}, {lon})")
                    
                    # Pedir tipo y descripción
                    coord_type = input("Tipo (pool/no_pool): ").strip()
                    description = input("Descripción (opcional): ").strip()
                    if not description:
                        description = f"Coord_{lat:.4f}_{lon:.4f}"
                    
                    return (lat, lon, coord_type, description)
                else:
                    print("❌ Formato incorrecto. Usa: lat,lon o lat,lon,tipo,descripción")
                    return None
                    
        except ValueError:
            print("❌ Error en las coordenadas. Asegúrate de usar números decimales")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def add_coordinate(self, lat: float, lon: float, coord_type: str, description: str = ""):
        """Agrega una coordenada al tipo especificado"""
        coord_data = {
            "lat": lat,
            "lon": lon,
            "description": description,
            "captured": False
        }
        
        if coord_type.lower() in ['pool', 'piscina', 'p']:
            self.coordinates["pools"].append(coord_data)
            print(f"✅ Piscina agregada: {description} en ({lat}, {lon})")
        elif coord_type.lower() in ['no_pool', 'no_piscina', 'n']:
            self.coordinates["no_pools"].append(coord_data)
            print(f"✅ Área sin piscina agregada: {description} en ({lat}, {lon})")
        else:
            print("❌ Tipo no válido. Usa 'pool' o 'no_pool'")
            return False
        
        self.update_metadata()
        return True
    
    def update_metadata(self):
        """Actualiza los metadatos del archivo"""
        from datetime import datetime
        self.coordinates["metadata"]["total_pools"] = len(self.coordinates["pools"])
        self.coordinates["metadata"]["total_no_pools"] = len(self.coordinates["no_pools"])
        self.coordinates["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_coordinates(self):
        """Guarda las coordenadas en el archivo JSON"""
        try:
            with open(self.coordinates_file, 'w', encoding='utf-8') as f:
                json.dump(self.coordinates, f, indent=2, ensure_ascii=False)
            print(f"💾 Coordenadas guardadas en {self.coordinates_file}")
            print(f"📊 Total piscinas: {len(self.coordinates['pools'])}")
            print(f"📊 Total sin piscinas: {len(self.coordinates['no_pools'])}")
        except Exception as e:
            print(f"❌ Error guardando: {e}")
    
    def show_summary(self):
        """Muestra un resumen de las coordenadas"""
        print("\n📋 RESUMEN DE COORDENADAS")
        print("=" * 50)
        print("🌐 ESTADO ACTUAL DEL DATASET")
        print(f"   Total de coordenadas configuradas: {len(self.coordinates['pools']) + len(self.coordinates['no_pools'])}")
        print()
        print(f"🏊 PISCINAS ({len(self.coordinates['pools'])}):")
        if self.coordinates['pools']:
            for i, pool in enumerate(self.coordinates['pools'], 1):
                print(f"   {i:2d}. {pool['description']}")
                print(f"       📍 ({pool['lat']:.6f}, {pool['lon']:.6f})")
        else:
            print("   ⚠️  No hay piscinas configuradas")
        
        print(f"\n🏠 ÁREAS SIN PISCINAS ({len(self.coordinates['no_pools'])}):")
        if self.coordinates['no_pools']:
            for i, no_pool in enumerate(self.coordinates['no_pools'], 1):
                print(f"   {i:2d}. {no_pool['description']}")
                print(f"       📍 ({no_pool['lat']:.6f}, {no_pool['lon']:.6f})")
        else:
            print("   ⚠️  No hay áreas sin piscinas configuradas")
        
        print("=" * 50)

def interactive_collector():
    """Interfaz interactiva para recolectar coordenadas"""
    collector = CoordinateCollector()
    
    print("📍 ENTRADA INTERACTIVA DE COORDENADAS")
    print("=" * 60)
    print("🎯 MODO DE ENTRADA INTERACTIVA")
    print("   Ingresa coordenadas una por una con su tipo y descripción")
    print("   El sistema detecta automáticamente el formato de entrada")
    print()
    print("📋 FORMATOS ACEPTADOS:")
    print("   • Decimal: 19.1738, -96.1342")
    print("   • Con tipo: 19.1738, -96.1342, pool")
    print("   • Completo: 19.1738, -96.1342, pool, Piscina_Veracruz")
    print("   • DMS: 19°11'19\"N 96°07'32\"W")
    print()
    print("🔍 COMANDOS DISPONIBLES:")
    print("   • 'fin' - Terminar y guardar")
    print("   • 'mostrar' - Ver resumen actual")
    print("   • 'guardar' - Guardar coordenadas")
    print("   • 'ayuda' - Mostrar esta ayuda")
    print("=" * 60)
    
    while True:
        print("\n📍 Ingresa coordenadas o comando:")
        user_input = input("> ").strip()
        
        if user_input.lower() == 'fin':
            break
        elif user_input.lower() == 'mostrar':
            collector.show_summary()
            continue
        elif user_input.lower() == 'guardar':
            collector.save_coordinates()
            continue
        elif user_input.lower() == 'ayuda':
            print("\n📍 ENTRADA INTERACTIVA DE COORDENADAS")
            print("=" * 60)
            print("🎯 MODO DE ENTRADA INTERACTIVA")
            print("   Ingresa coordenadas una por una con su tipo y descripción")
            print("   El sistema detecta automáticamente el formato de entrada")
            print()
            print("📋 FORMATOS ACEPTADOS:")
            print("   • Decimal: 19.1738, -96.1342")
            print("   • Con tipo: 19.1738, -96.1342, pool")
            print("   • Completo: 19.1738, -96.1342, pool, Piscina_Veracruz")
            print("   • DMS: 19°11'19\"N 96°07'32\"W")
            print()
            print("🔍 COMANDOS DISPONIBLES:")
            print("   • 'fin' - Terminar y guardar")
            print("   • 'mostrar' - Ver resumen actual")
            print("   • 'guardar' - Guardar coordenadas")
            print("   • 'ayuda' - Mostrar esta ayuda")
            print("=" * 60)
            continue
        
        # Parsear entrada
        result = collector.parse_coordinate_input(user_input)
        if result:
            lat, lon, coord_type, description = result
            collector.add_coordinate(lat, lon, coord_type, description)
    
    # Guardar al final
    collector.save_coordinates()
    print("\n✅ ¡Recolección completada!")

def show_instructions():
    """Muestra instrucciones sobre cómo obtener coordenadas de Google Maps"""
    print("\n📍 INSTRUCCIONES PARA OBTENER COORDENADAS")
    print("=" * 60)
    print("🌐 PASOS PARA OBTENER COORDENADAS EN GOOGLE MAPS:")
    print()
    print("1. Ve a maps.google.com en tu navegador")
    print("2. Busca la ubicación que quieres marcar")
    print("3. Haz clic derecho en el punto exacto del mapa")
    print("4. Selecciona '¿Qué hay aquí?' en el menú contextual")
    print("5. En la tarjeta de información que aparece, busca las coordenadas")
    print("6. Las coordenadas aparecen en formato decimal (ej: 19.1738, -96.1342)")
    print("7. Copia y pega estas coordenadas en este programa")
    print()
    print("💡 FORMATOS ACEPTADOS:")
    print("   • Decimal: 19.1738, -96.1342")
    print("   • Con tipo: 19.1738, -96.1342, pool")
    print("   • Completo: 19.1738, -96.1342, pool, Piscina_Veracruz")
    print()
    print("🔍 TIPOS DE COORDENADAS:")
    print("   • 'pool' o 'piscina': Para ubicaciones con piscinas")
    print("   • 'no_pool' o 'no_piscina': Para áreas sin piscinas")
    print()
    print("📱 ALTERNATIVA MÓVIL:")
    print("   • Abre Google Maps en tu teléfono")
    print("   • Mantén presionado el punto en el mapa")
    print("   • Las coordenadas aparecen en la parte inferior")
    print()
    print("=" * 60)
    input("\nPresiona Enter para regresar al menú principal...")



if __name__ == "__main__":
    while True:
        print("\n📍 COLECTOR DE COORDENADAS")
        print("=" * 50)
        print("🌐 SISTEMA DE RECOLECCIÓN AUTOMATIZADA")
        print("   Este script permite recolectar y gestionar coordenadas")
        print("   geográficas de piscinas y áreas sin piscinas para")
        print("   la generación de datasets de entrenamiento")
        print()
        print("📋 OPCIONES DISPONIBLES:")
        print("1. 📝 Entrada interactiva de coordenadas")
        print("   - Ingresar coordenadas manualmente")
        print("   - Soporte para formatos decimal y DMS")
        print("   - Configuración de tipo y descripción")
        print()
        print("2. 💡 Instrucciones para obtener coordenadas")
        print("   - Guía paso a paso para Google Maps")
        print("   - Formatos aceptados por el sistema")
        print("   - Alternativas móviles y de escritorio")
        print()
        print("3. 📊 Ver resumen de coordenadas")
        print("4. 🚪 Salir del programa")
        print("=" * 50)
        
        choice = input("Elige una opción (1/2/3/4): ").strip()
        
        if choice == "1":
            interactive_collector()
            input("\nPresiona Enter para regresar al menú principal...")
        elif choice == "2":
            show_instructions()
        elif choice == "3":
            collector = CoordinateCollector()
            collector.show_summary()
            input("\nPresiona Enter para regresar al menú principal...")
        elif choice == "4":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")
