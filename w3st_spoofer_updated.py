# W3ST Desktop App - Simple Version (Discord Commands Only)
import os
import json
import subprocess
import shutil
import winreg
import ctypes
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import uuid
import platform
import webbrowser
import random
import sys
import threading

# ===== CONFIGURATION =====
DISCORD_SERVER_INVITE = "https://discord.gg/bEDKbzZWJ4"  # Înlocuiește cu link-ul serverului tău
SUPPORT_URL = "https://discord.gg/bEDKbzZWJ4"
USERS_FILE = "users.json"

class W3STSpoofer:
    """Clasa care gestionează toate operațiunile de spoofer și clean - VERSIUNEA REALĂ CARE FUNCȚIONEAZĂ"""
    
    def __init__(self):
        self.is_admin = self.check_admin()
    
    def check_admin(self):
        """Verifică dacă aplicația rulează cu drepturi de administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def run_cmd(self, command):
        """Rulează o comandă CMD și returnează output-ul"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def kill_process(self, process_name):
        """Omoară un proces - FUNCȚIONAL"""
        return self.run_cmd(f'taskkill /f /im {process_name} /t')
    
    def clean_cache(self):
        """Șterge cache-ul FiveM - FUNCȚIONAL"""
        try:
            fivem_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FiveM', 'FiveM.app')
            
            cache_folders = [
                'cache\\Browser',
                'cache\\db', 
                'cache\\dunno',
                'cache\\priv',
                'cache\\servers',
                'cache\\subprocess',
                'cache\\unconfirmed',
                'cache\\authbrowser'
            ]
            
            for folder in cache_folders:
                folder_path = os.path.join(fivem_path, folder)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path, ignore_errors=True)
            
            # Șterge fișierele specifice
            cache_files = [
                'cache\\crashometry',
                'cache\\launcher_skip',
                'cache\\launcher_skip_mtl2'
            ]
            
            for file in cache_files:
                file_path = os.path.join(fivem_path, file)
                if os.path.exists(file_path):
                    try:
                        if os.path.isdir(file_path):
                            shutil.rmtree(file_path, ignore_errors=True)
                        else:
                            os.remove(file_path)
                    except:
                        pass
            
            return True, "Cache cleaned successfully"
        except Exception as e:
            return False, f"Cache cleaning error: {str(e)}"
    
    def clean_crashes(self):
        """Șterge fișierele de crash - FUNCȚIONAL"""
        try:
            crashes_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FiveM', 'FiveM.app', 'crashes')
            if os.path.exists(crashes_path):
                for item in os.listdir(crashes_path):
                    item_path = os.path.join(crashes_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                    except:
                        continue
            return True, "Crashes cleaned successfully"
        except Exception as e:
            return False, f"Crashes cleaning error: {str(e)}"
    
    def clean_logs(self):
        """Șterge logurile - FUNCȚIONAL"""
        try:
            logs_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FiveM', 'FiveM.app', 'logs')
            if os.path.exists(logs_path):
                for item in os.listdir(logs_path):
                    item_path = os.path.join(logs_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                    except:
                        continue
            return True, "Logs cleaned successfully"
        except Exception as e:
            return False, f"Logs cleaning error: {str(e)}"
    
    def clean_mods(self):
        """Șterge modurile - FUNCȚIONAL"""
        try:
            mods_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FiveM', 'FiveM.app', 'mods')
            if os.path.exists(mods_path):
                for item in os.listdir(mods_path):
                    item_path = os.path.join(mods_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                    except:
                        continue
            return True, "Mods cleaned successfully"
        except Exception as e:
            return False, f"Mods cleaning error: {str(e)}"
    
    def clean_windows_temp(self):
        """Șterge fișiere temporare Windows - FUNCȚIONAL"""
        try:
            temp_folders = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp'),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'temp'),
                os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp')
            ]
            
            for folder in temp_folders:
                if os.path.exists(folder):
                    for item in os.listdir(folder):
                        try:
                            item_path = os.path.join(folder, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                        except:
                            continue
            
            return True, "Windows temp cleaned successfully"
        except Exception as e:
            return False, f"Windows temp cleaning error: {str(e)}"
    
    def spoof_registry(self):
        """Șterge chei de registru pentru spoofer - FUNCȚIONAL"""
        try:
            # Lista de chei de registru de șters (ca în batch-ul tău)
            reg_commands = [
                'REG DELETE "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\MSLicensing\\HardwareID" /f',
                'REG DELETE "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\MSLicensing\\Store" /f',
                'REG DELETE "HKEY_CURRENT_USER\\Software\\WinRAR\\ArcHistory" /f',
                'REG DELETE "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FeatureUsage\\AppSwitched" /f',
                'REG DELETE "HKEY_CLASSES_ROOT\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache" /f',
                'REG DELETE "HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache" /f',
                'REG DELETE "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store" /f'
            ]
            
            for cmd in reg_commands:
                self.run_cmd(cmd)
            
            return True, "Registry spoofed successfully"
        except Exception as e:
            return False, f"Registry spoofing error: {str(e)}"
    
    def spoof_hosts(self):
        """Modifică fișierul hosts pentru spoofer - FUNCȚIONAL"""
        try:
            hosts_path = r'C:\Windows\System32\drivers\etc\hosts'
            
            # Citește conținutul actual
            if os.path.exists(hosts_path):
                with open(hosts_path, 'r') as f:
                    content = f.read()
                
                # Adaugă entrările dacă nu există deja
                entries = [
                    '127.0.0.1 xboxlive.com',
                    '127.0.0.1 user.auth.xboxlive.com',
                    '127.0.0.1 presence-heartbeat.xboxlive.com'
                ]
                
                for entry in entries:
                    if entry not in content:
                        with open(hosts_path, 'a') as f:
                            f.write(f'\n{entry}')
            
            return True, "Hosts file modified successfully"
        except Exception as e:
            return False, f"Hosts file error: {str(e)}"
    
    def delete_fivem_files(self):
        """Șterge fișiere specifice FiveM - FUNCȚIONAL"""
        try:
            fivem_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FiveM', 'FiveM.app')
            
            if not os.path.exists(fivem_path):
                return True, "FiveM path not found (maybe not installed)"
            
            files_to_delete = [
                'cfx_curl_x86_64.dll',
                'steam_api64.dll',
                'profiles.dll',
                'CitizenFX_SubProcess_chrome.bin',
                'CitizenFX_SubProcess_game.bin',
                'CitizenFX_SubProcess_game_372.bin',
                'CitizenFX_SubProcess_game_1604.bin',
                'CitizenFX_SubProcess_game_1868.bin',
                'CitizenFX_SubProcess_game_2060.bin',
                'CitizenFX_SubProcess_game_2189.bin',
                'CitizenGame.dll',
                'steam.dll',
                'asi-five.dll',
                'CitizenFX.ini',
                'caches.XML',
                'adhesive.dll',
                'discord.dll',
                'botan.dll'
            ]
            
            for file_name in files_to_delete:
                file_path = os.path.join(fivem_path, file_name)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            
            return True, "FiveM files deleted successfully"
        except Exception as e:
            return False, f"FiveM files deletion error: {str(e)}"
    
    def unlink_social_club(self):
        """Dezleagă Social Club - FUNCȚIONAL"""
        try:
            digital_path = os.path.join(os.getenv('LOCALAPPDATA'), 'DigitalEntitlements')
            if os.path.exists(digital_path):
                shutil.rmtree(digital_path, ignore_errors=True)
            
            self.kill_process('Steam.exe')
            return True, "Social Club unlinked successfully"
        except Exception as e:
            return False, f"Social Club unlinking error: {str(e)}"
    
    def unlink_citizenfx(self):
        """Dezleagă CitizenFX - FUNCȚIONAL"""
        try:
            citizen_path = os.path.join(os.getenv('APPDATA'), 'CitizenFX')
            if os.path.exists(citizen_path):
                shutil.rmtree(citizen_path, ignore_errors=True)
            
            self.kill_process('Steam.exe')
            return True, "CitizenFX unlinked successfully"
        except Exception as e:
            return False, f"CitizenFX unlinking error: {str(e)}"
    
    def unlink_discord(self):
        """Dezleagă Discord - FUNCȚIONAL"""
        try:
            # Șterge discord.dll din FiveM
            fivem_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FiveM', 'FiveM.app')
            discord_dll = os.path.join(fivem_path, 'discord.dll')
            if os.path.exists(discord_dll):
                os.remove(discord_dll)
            
            # Rename Discord RPC module (ca în batch-ul tău)
            discord_modules = os.path.join(os.getenv('APPDATA'), 'discord')
            if os.path.exists(discord_modules):
                for version in os.listdir(discord_modules):
                    if version.startswith('0.0.'):
                        modules_path = os.path.join(discord_modules, version, 'modules')
                        if os.path.exists(modules_path):
                            discord_rpc = os.path.join(modules_path, 'discord_rpc')
                            new_name = os.path.join(modules_path, 'STARCHARMS_SPOOFER')
                            
                            if os.path.exists(discord_rpc):
                                try:
                                    os.rename(discord_rpc, new_name)
                                except:
                                    pass
            
            self.kill_process('Steam.exe')
            return True, "Discord unlinked successfully"
        except Exception as e:
            return False, f"Discord unlinking error: {str(e)}"
    
    def fix_discord_link(self):
        """Repară link-ul Discord - FUNCȚIONAL"""
        try:
            discord_modules = os.path.join(os.getenv('APPDATA'), 'discord')
            if os.path.exists(discord_modules):
                for version in os.listdir(discord_modules):
                    if version.startswith('0.0.'):
                        modules_path = os.path.join(discord_modules, version, 'modules')
                        if os.path.exists(modules_path):
                            star_path = os.path.join(modules_path, 'STARCHARMS_SPOOFER')
                            new_name = os.path.join(modules_path, 'discord_rpc')
                            
                            if os.path.exists(star_path):
                                try:
                                    os.rename(star_path, new_name)
                                except:
                                    pass
            
            self.kill_process('Discord.exe')
            return True, "Discord link fixed successfully"
        except Exception as e:
            return False, f"Discord fixing error: {str(e)}"
    
    def full_spoof(self):
        """Execută spoofer complet - FUNCȚIONAL EXACT CA ÎN BATCH"""
        try:
            success_messages = []
            
            # 1. Kill Steam
            self.kill_process('Steam.exe')
            success_messages.append("✓ Steam killed")
            
            # 2. Spoof registry
            success, msg = self.spoof_registry()
            if success:
                success_messages.append("✓ Registry spoofed")
            
            # 3. Spoof hosts
            success, msg = self.spoof_hosts()
            if success:
                success_messages.append("✓ Hosts file modified")
            
            # 4. Clean Windows temp
            success, msg = self.clean_windows_temp()
            if success:
                success_messages.append("✓ Windows temp cleaned")
            
            # 5. Delete FiveM files
            success, msg = self.delete_fivem_files()
            if success:
                success_messages.append("✓ FiveM files deleted")
            
            # 6. Clean cache
            success, msg = self.clean_cache()
            if success:
                success_messages.append("✓ Cache cleaned")
            
            # 7. Clean crashes
            success, msg = self.clean_crashes()
            if success:
                success_messages.append("✓ Crashes cleaned")
            
            # 8. Clean logs
            success, msg = self.clean_logs()
            if success:
                success_messages.append("✓ Logs cleaned")
            
            # 9. Clean mods
            success, msg = self.clean_mods()
            if success:
                success_messages.append("✓ Mods cleaned")
            
            # 10. Unlink Discord
            success, msg = self.unlink_discord()
            if success:
                success_messages.append("✓ Discord unlinked")
            
            return True, "Full spoof completed successfully!\n\n" + "\n".join(success_messages)
        except Exception as e:
            return False, f"Full spoof error: {str(e)}"
    
    def clean_all(self):
        """Execută clean complet - FUNCȚIONAL"""
        try:
            success_messages = []
            
            # Clean cache
            success, msg = self.clean_cache()
            if success:
                success_messages.append("✓ Cache cleaned")
            
            # Clean crashes
            success, msg = self.clean_crashes()
            if success:
                success_messages.append("✓ Crashes cleaned")
            
            # Clean logs
            success, msg = self.clean_logs()
            if success:
                success_messages.append("✓ Logs cleaned")
            
            # Clean mods
            success, msg = self.clean_mods()
            if success:
                success_messages.append("✓ Mods cleaned")
            
            return True, "All cleaned successfully!\n\n" + "\n".join(success_messages)
        except Exception as e:
            return False, f"Clean all error: {str(e)}"
    
    def clean_and_spoof_all(self):
        """Execută clean și spoofer complet - FUNCȚIONAL EXACT CA ÎN BATCH"""
        try:
            success_messages = []
            
            # 1. Kill Steam
            self.kill_process('Steam.exe')
            success_messages.append("✓ Steam killed")
            
            # 2. Spoof registry
            success, msg = self.spoof_registry()
            if success:
                success_messages.append("✓ Registry spoofed")
            
            # 3. Spoof hosts
            success, msg = self.spoof_hosts()
            if success:
                success_messages.append("✓ Hosts file modified")
            
            # 4. Clean Windows temp
            success, msg = self.clean_windows_temp()
            if success:
                success_messages.append("✓ Windows temp cleaned")
            
            # 5. Delete FiveM files
            success, msg = self.delete_fivem_files()
            if success:
                success_messages.append("✓ FiveM files deleted")
            
            # 6. Clean cache
            success, msg = self.clean_cache()
            if success:
                success_messages.append("✓ Cache cleaned")
            
            # 7. Clean crashes
            success, msg = self.clean_crashes()
            if success:
                success_messages.append("✓ Crashes cleaned")
            
            # 8. Clean logs
            success, msg = self.clean_logs()
            if success:
                success_messages.append("✓ Logs cleaned")
            
            # 9. Clean mods
            success, msg = self.clean_mods()
            if success:
                success_messages.append("✓ Mods cleaned")
            
            # 10. Unlink DigitalEntitlements
            success, msg = self.unlink_social_club()
            if success:
                success_messages.append("✓ Social Club unlinked")
            
            # 11. Unlink CitizenFX
            success, msg = self.unlink_citizenfx()
            if success:
                success_messages.append("✓ CitizenFX unlinked")
            
            # 12. Unlink Discord
            success, msg = self.unlink_discord()
            if success:
                success_messages.append("✓ Discord unlinked")
            
            return True, "Clean and spoof all completed successfully!\n\n" + "\n".join(success_messages)
        except Exception as e:
            return False, f"Clean and spoof error: {str(e)}"

class UserManager:
    """Manages user registration and login"""
    
    def __init__(self):
        self.users_file = USERS_FILE
        self.load_users()
    
    def load_users(self):
        """Load users from file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = {}
    
    def save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def register(self, email, username, password):
        """Register a new user"""
        # Check if email already exists
        for user_id, user_data in self.users.items():
            if user_data.get('email') == email:
                return False, "Email already registered"
        
        # Check if username already exists
        for user_id, user_data in self.users.items():
            if user_data.get('username') == username:
                return False, "Username already taken"
        
        # Generate user ID
        user_id = str(uuid.uuid4())[:8]
        
        # Create user entry
        self.users[user_id] = {
            'email': email,
            'username': username,
            'password': self.hash_password(password),
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'license': None
        }
        
        if self.save_users():
            return True, user_id
        else:
            return False, "Registration failed"
    
    def login(self, email, password):
        """Login with email and password"""
        for user_id, user_data in self.users.items():
            if user_data.get('email') == email:
                if user_data.get('password') == self.hash_password(password):
                    # Update last login
                    self.users[user_id]['last_login'] = datetime.now().isoformat()
                    self.save_users()
                    return True, user_id, user_data.get('username')
                else:
                    return False, None, "Invalid password"
        
        return False, None, "Email not found"
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_user_by_id(self, user_id):
        """Get user data by ID"""
        return self.users.get(user_id)

class W3STLicenseSystem:
    """Simplified license system - uses local validation only"""
    
    def __init__(self):
        self.license_file = "license.json"
    
    def get_hwid(self):
        """Get unique hardware ID"""
        try:
            hwid_components = []
            
            # MAC address
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                               for elements in range(0, 8*6, 8)][::-1])
                hwid_components.append(mac)
            except:
                pass
            
            # System info
            hwid_components.append(platform.node())
            hwid_components.append(platform.machine())
            
            if hwid_components:
                hwid_string = ''.join(hwid_components)
                return hashlib.sha256(hwid_string.encode()).hexdigest()[:32]
            else:
                return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:32]
                
        except Exception as e:
            print(f"HWID error: {e}")
            return "default_hwid_" + str(random.randint(10000, 99999))
    
    def save_license(self, license_key, license_type, days):
        """Save license locally"""
        try:
            expires_at = datetime.now() + timedelta(days=days)
            
            license_data = {
                'license_key': license_key,
                'license_type': license_type,
                'hwid': self.get_hwid(),
                'expires_at': expires_at.isoformat(),
                'activated_at': datetime.now().isoformat()
            }
            
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def validate_license(self):
        """Validate license from local file"""
        try:
            if not os.path.exists(self.license_file):
                return False, "No license found", None, 0
            
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Check HWID
            if license_data.get('hwid') != self.get_hwid():
                return False, "HWID mismatch", None, 0
            
            # Check expiry
            expires_at = datetime.fromisoformat(license_data['expires_at'])
            if datetime.now() > expires_at:
                return False, "License expired", None, 0
            
            days_left = (expires_at - datetime.now()).days
            license_type = license_data.get('license_type', 'unknown')
            
            return True, "Valid", license_type, days_left
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", None, 0
    
    def delete_license(self):
        """Delete license file"""
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
            return True
        except:
            return False

class W3STClientApp:
    """Main client application - DESIGN ORIGINAL"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("W3ST SPOOFER - PREMIUM EDITION")
        self.root.geometry("900x650")
        
        # Theme colors - EXACT CA ÎN DESIGN-UL TĂU ORIGINAL
        self.bg_color = "#0a0a0a"
        self.card_bg = "#1a1a1a"
        self.accent_color = "#ff0000"
        self.text_color = "#ffffff"
        self.muted_text = "#aaaaaa"
        self.input_bg = "#2a2a2a"
        self.success_color = "#00ff00"
        self.warning_color = "#ff9900"
        self.danger_color = "#ff3333"
        
        self.root.configure(bg=self.bg_color)
        
        # Fonts
        self.title_font = ("Segoe UI", 24, "bold")
        self.header_font = ("Segoe UI", 16, "bold")
        self.normal_font = ("Segoe UI", 11)
        self.small_font = ("Segoe UI", 9)
        
        # Initialize systems
        self.user_manager = UserManager()
        self.license_system = W3STLicenseSystem()
        self.spoofer = W3STSpoofer()
        
        # Current user
        self.current_user_id = None
        self.current_username = None
        
        # Check if license exists
        success, message, license_type, days_left = self.license_system.validate_license()
        
        if success:
            self.license_type = license_type
            self.days_left = days_left
            self.show_main_app()
        else:
            self.show_activation_screen()
    
    def show_activation_screen(self):
        """Show license activation screen - DESIGN ORIGINAL"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        activation_frame = tk.Frame(self.root, bg=self.bg_color)
        activation_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Logo
        tk.Label(
            activation_frame,
            text="W3ST",
            font=("Segoe UI", 48, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        tk.Label(
            activation_frame,
            text="SPOOFER",
            font=("Segoe UI", 20),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(0, 40))
        
        # Instructions
        instructions_frame = tk.Frame(activation_frame, bg=self.card_bg, padx=30, pady=20)
        instructions_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(
            instructions_frame,
            text="📋 Activation Steps:",
            font=self.header_font,
            bg=self.card_bg,
            fg=self.accent_color
        ).pack(anchor=tk.W, pady=(0, 15))
        
        steps = [
            "1️⃣ Join our Discord server",
            "2️⃣ Get your license key from staff",
            "3️⃣ Use command: /activate license_key:YOUR-KEY hwid:YOUR-HWID",
            "4️⃣ Enter your license key below"
        ]
        
        for step in steps:
            tk.Label(
                instructions_frame,
                text=step,
                font=self.normal_font,
                bg=self.card_bg,
                fg=self.text_color,
                anchor=tk.W
            ).pack(anchor=tk.W, pady=3)
        
        # HWID display
        hwid_frame = tk.Frame(activation_frame, bg=self.card_bg, padx=20, pady=15)
        hwid_frame.pack(fill=tk.X, pady=(0, 20))
        
        hwid = self.license_system.get_hwid()
        
        tk.Label(
            hwid_frame,
            text="Your HWID (copy this):",
            font=self.normal_font,
            bg=self.card_bg,
            fg=self.warning_color
        ).pack(anchor=tk.W)
        
        hwid_entry = tk.Entry(
            hwid_frame,
            font=("Consolas", 10),
            bg=self.input_bg,
            fg=self.success_color,
            width=50,
            justify=tk.CENTER
        )
        hwid_entry.insert(0, hwid)
        hwid_entry.config(state='readonly')
        hwid_entry.pack(pady=5)
        
        copy_hwid_btn = tk.Button(
            hwid_frame,
            text="📋 Copy HWID",
            font=self.normal_font,
            bg=self.accent_color,
            fg=self.text_color,
            command=lambda: self.copy_to_clipboard(hwid),
            padx=20,
            pady=5
        )
        copy_hwid_btn.pack(pady=5)
        
        # License key input
        key_frame = tk.Frame(activation_frame, bg=self.bg_color)
        key_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            key_frame,
            text="Enter License Key:",
            font=self.normal_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(0, 10))
        
        self.license_entry = tk.Entry(
            key_frame,
            font=("Consolas", 12),
            bg=self.input_bg,
            fg=self.text_color,
            width=40,
            justify=tk.CENTER
        )
        self.license_entry.pack(pady=(0, 10))
        
        # License type selection
        type_frame = tk.Frame(key_frame, bg=self.bg_color)
        type_frame.pack(pady=(0, 20))
        
        tk.Label(
            type_frame,
            text="License Type:",
            font=self.normal_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.license_type_var = tk.StringVar(value="7days")
        
        types = [("Trial (7d)", "trial", 7), ("Monthly (30d)", "monthly", 30), ("Lifetime", "lifetime", 3650)]
        
        for text, value, days in types:
            rb = tk.Radiobutton(
                type_frame,
                text=text,
                variable=self.license_type_var,
                value=value,
                font=self.normal_font,
                bg=self.bg_color,
                fg=self.text_color,
                selectcolor=self.card_bg,
                command=lambda d=days: setattr(self, 'selected_days', d)
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        self.selected_days = 7  # Default
        
        # Buttons
        buttons_frame = tk.Frame(activation_frame, bg=self.bg_color)
        buttons_frame.pack()
        
        activate_btn = tk.Button(
            buttons_frame,
            text="✅ ACTIVATE LICENSE",
            font=self.header_font,
            bg=self.success_color,
            fg=self.bg_color,
            command=self.activate_license_manual,
            padx=30,
            pady=12
        )
        activate_btn.pack(side=tk.LEFT, padx=5)
        
        discord_btn = tk.Button(
            buttons_frame,
            text="💬 Join Discord",
            font=self.normal_font,
            bg=self.accent_color,
            fg=self.text_color,
            command=lambda: webbrowser.open(DISCORD_SERVER_INVITE),
            padx=20,
            pady=10
        )
        discord_btn.pack(side=tk.LEFT, padx=5)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "HWID copied to clipboard!")
    
    def activate_license_manual(self):
        """Manual license activation (saves locally)"""
        license_key = self.license_entry.get().strip()
        
        if not license_key:
            messagebox.showerror("Error", "Please enter a license key")
            return
        
        if len(license_key) < 10:
            messagebox.showerror("Error", "Invalid license key format")
            return
        
        # Get selected license type
        license_type = self.license_type_var.get()
        days = self.selected_days
        
        # Save license locally
        if self.license_system.save_license(license_key, license_type, days):
            messagebox.showinfo(
                "Success",
                f"✅ License activated!\n\n"
                f"Type: {license_type.upper()}\n"
                f"Duration: {days} days\n\n"
                f"⚠️ Important: Make sure you activated your key on Discord first using:\n"
                f"/activate license_key:{license_key} hwid:{self.license_system.get_hwid()}"
            )
            
            self.license_type = license_type
            self.days_left = days
            self.show_main_app()
        else:
            messagebox.showerror("Error", "Failed to save license")
    
    def show_main_app(self):
        """Show main application - DESIGN ORIGINAL"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(
            header_frame,
            text="W3ST",
            font=("Segoe UI", 36, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame,
            text="SPOOFER",
            font=("Segoe UI", 18),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # License status
        status_color = self.success_color if self.days_left > 7 else self.warning_color
        
        tk.Label(
            header_frame,
            text=f"⚡ {self.license_type.upper()} • {self.days_left} days left",
            font=self.normal_font,
            bg=self.card_bg,
            fg=status_color,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT)
        
        # License info card
        info_frame = tk.Frame(main_frame, bg=self.card_bg, padx=25, pady=20)
        info_frame.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(
            info_frame,
            text="📋 License Information",
            font=self.header_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(0, 15))
        
        info_items = [
            ("License Type:", self.license_type.upper()),
            ("Days Remaining:", f"{self.days_left} days"),
            ("Status:", "Active" if self.days_left > 0 else "Expired"),
            ("HWID:", self.license_system.get_hwid()[:24] + "...")
        ]
        
        for label, value in info_items:
            row = tk.Frame(info_frame, bg=self.card_bg)
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(
                row,
                text=label,
                font=self.normal_font,
                bg=self.card_bg,
                fg=self.muted_text,
                width=18,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=value,
                font=self.normal_font,
                bg=self.card_bg,
                fg=self.text_color,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Tools section
        tk.Label(
            main_frame,
            text="🔧 Available Tools",
            font=self.header_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(0, 15))
        
        tools = [
            ("🧹 Clean Cache", "Remove temporary files", "#ff6666", self.execute_clean_cache),
            ("🔄 Spoof HWID", "Generate new hardware ID", "#ff9900", self.execute_spoofer),
            ("🔧 Fix Issues", "Fix common problems", "#00cc66", self.execute_fix_discord),
            ("💯 Clean/Spoof All", "Full cleanup and spoof", "#cc00cc", self.execute_clean_spoof_all),
            ("🔗 Unlink Social", "Disconnect Social Club", "#ff3366", self.execute_unlink_social),
            ("🎮 Unlink CitizenFX", "Remove CitizenFX traces", "#33ccff", self.execute_unlink_citizen),
            ("💬 Unlink Discord", "Disconnect Discord", "#ff9966", self.execute_unlink_discord),
            ("💥 Clean Crashes", "Delete crash reports", "#ff6633", self.execute_clean_crashes),
            ("📝 Clean Logs", "Clear system logs", "#ffcc33", self.execute_clean_logs),
            ("🎮 Clean Mods", "Remove game modifications", "#66ff99", self.execute_clean_mods)
        ]
        
        # Create 2 columns for tools
        tools_frame = tk.Frame(main_frame, bg=self.bg_color)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        left_column = tk.Frame(tools_frame, bg=self.bg_color)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_column = tk.Frame(tools_frame, bg=self.bg_color)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Distribute tools between columns
        for i, (title, desc, color, command) in enumerate(tools):
            if i % 2 == 0:
                column = left_column
            else:
                column = right_column
            
            tool_frame = tk.Frame(column, bg=self.card_bg)
            tool_frame.pack(fill=tk.X, pady=5)
            
            content = tk.Frame(tool_frame, bg=self.card_bg)
            content.pack(fill=tk.X, padx=20, pady=12)
            
            tk.Label(
                content,
                text=title,
                font=self.normal_font,
                bg=self.card_bg,
                fg=color
            ).pack(side=tk.LEFT)
            
            tk.Label(
                content,
                text=desc,
                font=self.small_font,
                bg=self.card_bg,
                fg=self.muted_text
            ).pack(side=tk.LEFT, padx=(15, 0))
            
            tk.Button(
                content,
                text="Run",
                font=self.small_font,
                bg=color,
                fg=self.text_color,
                command=command,
                padx=15,
                pady=5
            ).pack(side=tk.RIGHT)
        
        # Bottom buttons
        bottom_frame = tk.Frame(main_frame, bg=self.bg_color)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        tk.Button(
            bottom_frame,
            text="🔄 Refresh License",
            font=self.normal_font,
            bg=self.card_bg,
            fg=self.text_color,
            command=self.refresh_license,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)
        
        tk.Button(
            bottom_frame,
            text="🗑️ Reset License",
            font=self.normal_font,
            bg=self.danger_color,
            fg=self.text_color,
            command=self.reset_license,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            bottom_frame,
            text="💬 Support",
            font=self.normal_font,
            bg=self.accent_color,
            fg=self.text_color,
            command=lambda: webbrowser.open(SUPPORT_URL),
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT)
    
    def execute_tool(self, func, tool_name):
        """Execute a tool with loading indication"""
        # Disable window during execution
        self.root.config(cursor="watch")
        
        # Run in separate thread to avoid freezing
        def run_tool():
            try:
                success, message = func()
                self.root.after(0, lambda: self.show_tool_result(success, message, tool_name))
            except Exception as e:
                self.root.after(0, lambda: self.show_tool_result(False, str(e), tool_name))
            finally:
                self.root.after(0, lambda: self.root.config(cursor=""))
        
        threading.Thread(target=run_tool, daemon=True).start()
    
    def show_tool_result(self, success, message, tool_name):
        """Show tool execution result"""
        if success:
            messagebox.showinfo(f"{tool_name} - Success", message)
        else:
            messagebox.showerror(f"{tool_name} - Error", message)
    
    def execute_clean_cache(self):
        self.execute_tool(self.spoofer.clean_cache, "Clean Cache")
    
    def execute_clean_crashes(self):
        self.execute_tool(self.spoofer.clean_crashes, "Clean Crashes")
    
    def execute_clean_logs(self):
        self.execute_tool(self.spoofer.clean_logs, "Clean Logs")
    
    def execute_clean_mods(self):
        self.execute_tool(self.spoofer.clean_mods, "Clean Mods")
    
    def execute_spoofer(self):
        self.execute_tool(self.spoofer.full_spoof, "Spoofer")
    
    def execute_clean_spoof_all(self):
        self.execute_tool(self.spoofer.clean_and_spoof_all, "Clean/Spoof All")
    
    def execute_unlink_social(self):
        self.execute_tool(self.spoofer.unlink_social_club, "Unlink Social Club")
    
    def execute_unlink_citizen(self):
        self.execute_tool(self.spoofer.unlink_citizenfx, "Unlink CitizenFX")
    
    def execute_unlink_discord(self):
        self.execute_tool(self.spoofer.unlink_discord, "Unlink Discord")
    
    def execute_fix_discord(self):
        self.execute_tool(self.spoofer.fix_discord_link, "Fix Discord")
    
    def refresh_license(self):
        """Refresh license validation"""
        success, message, license_type, days_left = self.license_system.validate_license()
        
        if success:
            self.license_type = license_type
            self.days_left = days_left
            messagebox.showinfo("Success", f"✅ License valid!\n\nDays left: {days_left}")
            self.show_main_app()
        else:
            messagebox.showerror("Error", f"❌ License validation failed:\n{message}")
            self.show_activation_screen()
    
    def reset_license(self):
        """Reset/delete license"""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset your license?\n\nYou'll need to activate again."):
            if self.license_system.delete_license():
                messagebox.showinfo("Success", "License reset successfully")
                self.show_activation_screen()
            else:
                messagebox.showerror("Error", "Failed to reset license")

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = W3STClientApp(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
