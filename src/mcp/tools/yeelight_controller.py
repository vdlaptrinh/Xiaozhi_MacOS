#!/usr/bin/env python3
"""
Yeelight Desk Lamp Controller
Dieu kien den Yeelight qua WiFi
"""

from yeelight import Bulb, discover_bulbs
from yeelight import LightType
import sys


def discover_device():
    """Phat hien den Yeelight tren mang local"""
    print("Dang quet den Yeelight...")
    bulbs = discover_bulbs()
    if not bulbs:
        print("Khong tim thay den nao!")
        return None
    
    for i, bulb_info in enumerate(bulbs):
        print(f"[{i}] IP: {bulb_info['ip']} | Model: {bulb_info['capabilities']['model']} | Trang thai: {bulb_info['capabilities']['power']}")
    
    if len(bulbs) == 1:
        return bulbs[0]['ip']
    
    choice = int(input("Chon den (so): "))
    return bulbs[choice]['ip']


def print_menu():
    """Hien thi menu dieu khien"""
    print("\n===== YEELIGHT DESK LAMP CONTROLLER =====")
    print("1. Bat den")
    print("2. Tat den")
    print("3. Chuyen doi trang thai (Toggle)")
    print("4. Chinh do sang (0-100)")
    print("5. Chinh nhiet do mau (1700-6500K)")
    print("6. Chon che do mau co dinh")
    print("7. Hien thi trang thai")
    print("8. Luu cau hinh mac dinh")
    print("9. Hen gio tat (phut)")
    print("0. Thoat")
    print("==========================================")


def main():
    # Buoc 1: Tim IP den
    ip = input("Nhap IP cua den (de trong de tu dong quet): ").strip()
    if not ip:
        ip = discover_device()
        if not ip:
            sys.exit(1)
    
    # Buoc 2: Ket noi den
    # auto_on=True: tu dong bat den khi gui lenh
    # effect="smooth", duration=300: chuyen doi mem mai trong 300ms
    bulb = Bulb(ip, auto_on=True, effect="smooth", duration=300)
    
    try:
        # Kiem tra ket noi
        props = bulb.get_properties()
        print(f"Da ket noi: {ip}")
        print(f"Trang thai: {'BAT' if props['power'] == 'on' else 'TAT'} | Do sang: {props['bright']}% | Nhiet do mau: {props['ct']}K")
    except Exception as e:
        print(f"Loi ket noi: {e}")
        print("Hay kiem tra:")
        print("  1. Den va may tinh cung mang WiFi")
        print("  2. Da bat 'LAN Control' trong ung dung Yeelight")
        sys.exit(1)
    
    # Buoc 3: Menu dieu khien
    while True:
        print_menu()
        choice = input("Chon chuc nang: ").strip()
        
        try:
            if choice == "1":
                bulb.turn_on()
                print(">> Da BAT den")
                
            elif choice == "2":
                bulb.turn_off()
                print(">> Da TAT den")
                
            elif choice == "3":
                bulb.toggle()
                print(">> Da chuyen doi trang thai")
                
            elif choice == "4":
                brightness = int(input("  Nhap do sang (0-100): "))
                if 0 <= brightness <= 100:
                    bulb.set_brightness(brightness)
                    print(f">> Da chinh do sang: {brightness}%")
                else:
                    print("  Gia tri khong hop le!")
                    
            elif choice == "5":
                temp = int(input("  Nhap nhiet do mau (1700-6500K): "))
                if 1700 <= temp <= 6500:
                    bulb.set_color_temp(temp)
                    print(f">> Da chinh nhiet do mau: {temp}K")
                    if temp < 3300:
                        print("   (Anh sang am - vang)")
                    elif temp < 5000:
                        print("   (Anh sang trung tinh)")
                    else:
                        print("   (Anh sang lanh - trang)")
                else:
                    print("  Gia tri khong hop le!")
                    
            elif choice == "6":
                print("  1. Anh sang hoc tap (5000K, 100%)")
                print("  2. Anh sang doc sach (4000K, 70%)")
                print("  3. Anh sang thu gian (2700K, 50%)")
                print("  4. Anh sang tap trung (6000K, 90%)")
                mode = input("  Chon che do: ")
                
                presets = {
                    "1": (5000, 100, "Hoc tap"),
                    "2": (4000, 70, "Doc sach"),
                    "3": (2700, 50, "Thu gian"),
                    "4": (6000, 90, "Tap trung"),
                }
                
                if mode in presets:
                    temp, bright, name = presets[mode]
                    bulb.set_color_temp(temp)
                    bulb.set_brightness(bright)
                    print(f">> Da chon che do: {name}")
                else:
                    print("  Lua chon khong hop le!")
                    
            elif choice == "7":
                props = bulb.get_properties()
                print("\n--- Trang thai den ---")
                print(f"  Power: {props['power']}")
                print(f"  Do sang: {props['bright']}%")
                print(f"  Nhiet do mau: {props['ct']}K")
                print(f"  Che do: {props['color_mode']}")
                print(f"  Ten: {props.get('name', 'N/A')}")
                
            elif choice == "8":
                bulb.set_default()
                print(">> Da luu cau hinh mac dinh")
                
            elif choice == "9":
                minutes = int(input("  So phut hen gio: "))
                if minutes > 0:
                    bulb.turn_off(minutes * 60)
                    print(f">> Hen gio tat sau {minutes} phut")
                else:
                    print("  Gia tri khong hop le!")
                    
            elif choice == "0":
                print("Tam biet!")
                break
                
            else:
                print("Lua chon khong hop le!")
                
        except Exception as e:
            print(f"Loi: {e}")


if __name__ == "__main__":
    main()
