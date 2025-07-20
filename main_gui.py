# main_gui.py - 스크롤 기능 + 패키지 자동 설치 + 프로필 시스템 완성 버전
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import subprocess
import os
import sys
import psutil
import threading
import time
import importlib
from dotenv import load_dotenv
from env_generate import EnvGenerator

class GitHubAutoUploadMain:
    def __init__(self):
        self.root = tk.Tk()
        self.env_generator = EnvGenerator()
        self.current_profile = tk.StringVar()
        
        # 업로드 프로세스 관리 변수들
        self.upload_process = None
        self.upload_pid_file = "upload_process.pid"
        self.is_upload_running = False
        
        self.setup_ui()
        self.check_required_packages()  # 시작 시 패키지 체크
        self.load_profiles()
        self.update_status()
        self.check_upload_process()
        self.start_process_monitor()
        
    # 🔧 패키지 설치 관련 메서드들
    def check_required_packages(self):
        """필수 패키지 설치 상태 체크"""
        required_packages = [
            'PyGithub', 'python-dotenv', 'watchdog', 'schedule', 
            'requests', 'beautifulsoup4', 'psutil'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                if package == 'PyGithub':
                    importlib.import_module('github')
                elif package == 'python-dotenv':
                    importlib.import_module('dotenv')
                elif package == 'beautifulsoup4':
                    importlib.import_module('bs4')
                else:
                    importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.show_package_install_dialog(missing_packages)
    
    def detect_environment_type(self):
        """현재 Python 환경 타입 감지"""
        python_path = sys.executable
        
        # Conda 환경 체크
        if 'conda' in python_path.lower() or 'miniconda' in python_path.lower() or 'anaconda' in python_path.lower():
            if 'envs' in python_path:
                env_name = python_path.split('envs')[1].split(os.sep)[1] if 'envs' in python_path else 'unknown'
                return f"🐍 Conda 가상환경 ({env_name})"
            else:
                return "🐍 Conda 기본환경"
        
        # 일반 가상환경 체크
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            venv_name = os.path.basename(sys.prefix)
            return f"🔧 가상환경 ({venv_name})"
        
        # 시스템 Python
        return "💻 시스템 Python"
    
    def get_environment_message(self, env_type):
        """환경별 안내 메시지"""
        if "Conda" in env_type:
            return "✅ Conda 환경에서 실행 중입니다. 안전하게 설치됩니다!"
        elif "가상환경" in env_type:
            return "✅ 가상환경에서 실행 중입니다. 안전하게 설치됩니다!"
        else:
            return "⚠️  시스템 Python에서 실행 중입니다. 가상환경 사용을 권장합니다."
    
    def show_package_install_dialog(self, missing_packages):
        """패키지 설치 다이얼로그 표시 (환경 정보 포함)"""
        install_window = tk.Toplevel(self.root)
        install_window.title("📦 패키지 설치 필요")
        install_window.geometry("600x550")
        install_window.resizable(False, False)
        install_window.grab_set()  # 모달 창으로 설정
        
        # 메인 프레임
        main_frame = tk.Frame(install_window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        title_label = tk.Label(main_frame, text="📦 필수 패키지 설치", 
                              font=("Arial", 16, "bold"), fg="navy")
        title_label.pack(pady=(0, 15))
        
        # 🔧 현재 Python 환경 정보 표시
        env_frame = tk.LabelFrame(main_frame, text="🐍 현재 Python 환경", 
                                 font=("Arial", 11, "bold"), padx=15, pady=10)
        env_frame.pack(fill='x', pady=(0, 15))
        
        # Python 경로 및 환경 정보
        python_path = sys.executable
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # 환경 타입 감지
        env_type = self.detect_environment_type()
        
        tk.Label(env_frame, text=f"Python 버전: {python_version}", 
                font=("Arial", 10), anchor='w').pack(fill='x', pady=2)
        tk.Label(env_frame, text=f"환경 타입: {env_type}", 
                font=("Arial", 10, "bold"), anchor='w', fg="blue").pack(fill='x', pady=2)
        tk.Label(env_frame, text=f"설치 경로: {python_path}", 
                font=("Arial", 8), anchor='w', fg="gray", wraplength=550).pack(fill='x', pady=2)
        
        # 환경별 안내 메시지
        env_message = self.get_environment_message(env_type)
        tk.Label(env_frame, text=env_message, 
                font=("Arial", 10), fg="darkgreen", wraplength=550).pack(fill='x', pady=(8, 0))
        
        # 설명
        desc_label = tk.Label(main_frame, 
                             text="프로그램 실행에 필요한 패키지를 현재 환경에 설치합니다.\n아래 버튼을 클릭하여 자동 설치하세요.", 
                             font=("Arial", 11), justify='center')
        desc_label.pack(pady=(0, 15))
        
        # 누락된 패키지 목록
        if missing_packages:
            missing_frame = tk.LabelFrame(main_frame, text="설치할 패키지", 
                                         font=("Arial", 10, "bold"), padx=10, pady=10)
            missing_frame.pack(fill='x', pady=(0, 15))
            
            for package in missing_packages:
                tk.Label(missing_frame, text=f"• {package}", 
                        font=("Arial", 10), fg="red").pack(anchor='w')
        else:
            # 전체 설치 모드
            all_frame = tk.LabelFrame(main_frame, text="전체 패키지 재설치", 
                                     font=("Arial", 10, "bold"), padx=10, pady=10)
            all_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(all_frame, text="requirements.txt의 모든 패키지를 재설치합니다.", 
                    font=("Arial", 10), fg="blue").pack(anchor='w')
        
        # 설치 버튼
        install_btn = tk.Button(main_frame, text="🚀 현재 환경에 설치", 
                               width=25, height=2,
                               font=("Arial", 12, "bold"),
                               bg="green", fg="white",
                               command=lambda: self.install_packages(install_window))
        install_btn.pack(pady=15)
        
        # 수동 설치 안내
        manual_frame = tk.LabelFrame(main_frame, text="수동 설치 방법", 
                                    font=("Arial", 10, "bold"), padx=10, pady=10)
        manual_frame.pack(fill='x', pady=(10, 0))
        
        manual_text = f"터미널에서 직접 실행하려면:\n{python_path} -m pip install -r requirements.txt"
        tk.Label(manual_frame, text=manual_text, 
                font=("Arial", 8), fg="gray", justify='left', wraplength=550).pack(anchor='w')
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        # 닫기 버튼
        close_btn = tk.Button(button_frame, text="❌ 나중에 설치", 
                             command=install_window.destroy,
                             font=("Arial", 10))
        close_btn.pack()
    
    def install_packages(self, parent_window):
        """패키지 자동 설치"""
        # 설치 진행 창 생성
        progress_window = tk.Toplevel(parent_window)
        progress_window.title("📦 패키지 설치 중...")
        progress_window.geometry("700x500")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        # 진행 상황 표시
        progress_frame = tk.Frame(progress_window, padx=20, pady=20)
        progress_frame.pack(fill='both', expand=True)
        
        # 제목과 환경 정보
        title_frame = tk.Frame(progress_frame)
        title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(title_frame, text="📦 패키지 설치 중...", 
                font=("Arial", 14, "bold")).pack()
        
        env_type = self.detect_environment_type()
        tk.Label(title_frame, text=f"설치 환경: {env_type}", 
                font=("Arial", 10), fg="blue").pack(pady=(5, 0))
        
        # 프로그레스 바
        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        progress_bar.pack(fill='x', pady=(0, 15))
        progress_bar.start()
        
        # 로그 출력 영역
        log_frame = tk.LabelFrame(progress_frame, text="설치 진행 상황", font=("Arial", 10, "bold"))
        log_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 9))
        log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 상태 라벨
        status_label = tk.Label(progress_frame, text="설치 준비 중...", 
                               font=("Arial", 11, "bold"), fg="blue")
        status_label.pack()
        
        def update_log(text):
            """로그 텍스트 업데이트"""
            log_text.insert(tk.END, text + '\n')
            log_text.see(tk.END)
            progress_window.update()
        
        def install_thread():
            """별도 스레드에서 패키지 설치"""
            try:
                update_log("=" * 50)
                update_log("🚀 GitHub 자동 업로드 시스템 - 패키지 설치")
                update_log("=" * 50)
                update_log(f"📍 설치 환경: {env_type}")
                update_log(f"🐍 Python 경로: {sys.executable}")
                update_log(f"📁 작업 폴더: {os.getcwd()}")
                update_log("")
                
                status_label.config(text="requirements.txt 설치 중...", fg="orange")
                
                # pip install 명령어 실행
                cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--upgrade']
                update_log(f"🔧 실행 명령어: {' '.join(cmd)}")
                update_log("")
                
                process = subprocess.Popen(cmd, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         text=True, 
                                         universal_newlines=True,
                                         cwd=os.getcwd())
                
                # 실시간 출력 표시
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        update_log(output.strip())
                
                # 프로세스 완료 대기
                return_code = process.wait()
                
                progress_bar.stop()
                
                if return_code == 0:
                    update_log("")
                    update_log("=" * 50)
                    update_log("✅ 모든 패키지 설치가 완료되었습니다!")
                    update_log("🎉 이제 GitHub 자동 업로드 시스템을 사용할 수 있습니다!")
                    update_log("=" * 50)
                    status_label.config(text="✅ 설치 완료! 창을 닫고 프로그램을 사용하세요.", fg="green")
                    
                    # 완료 버튼 추가
                    def close_and_continue():
                        progress_window.destroy()
                        parent_window.destroy()
                        messagebox.showinfo("설치 완료", 
                                          "✅ 패키지 설치가 완료되었습니다!\n\n"
                                          "🚀 이제 모든 기능을 사용할 수 있습니다!\n"
                                          "환경설정에서 GitHub 토큰을 설정하고 시작하세요.")
                    
                    button_frame = tk.Frame(progress_frame)
                    button_frame.pack(pady=10)
                    
                    complete_btn = tk.Button(button_frame, text="✅ 완료", 
                                           command=close_and_continue,
                                           bg="green", fg="white", 
                                           font=("Arial", 12, "bold"),
                                           width=15, height=2)
                    complete_btn.pack()
                    
                else:
                    update_log("")
                    update_log("=" * 50)
                    update_log(f"❌ 설치 중 오류가 발생했습니다. (종료 코드: {return_code})")
                    update_log("💡 위의 오류 메시지를 확인하고 수동 설치를 시도해보세요.")
                    update_log("=" * 50)
                    status_label.config(text="❌ 설치 실패. 로그를 확인하고 수동 설치를 시도하세요.", fg="red")
                    
                    # 재시도/닫기 버튼 추가
                    button_frame = tk.Frame(progress_frame)
                    button_frame.pack(pady=10)
                    
                    retry_btn = tk.Button(button_frame, text="🔄 재시도", 
                                        command=lambda: threading.Thread(target=install_thread, daemon=True).start(),
                                        bg="orange", fg="white", width=10)
                    retry_btn.pack(side='left', padx=10)
                    
                    close_btn = tk.Button(button_frame, text="❌ 닫기", 
                                        command=progress_window.destroy,
                                        bg="gray", fg="white", width=10)
                    close_btn.pack(side='right', padx=10)
                
            except Exception as e:
                progress_bar.stop()
                update_log("")
                update_log("=" * 50)
                update_log(f"❌ 예외 오류 발생: {str(e)}")
                update_log("💡 인터넷 연결을 확인하고 다시 시도해보세요.")
                update_log("=" * 50)
                status_label.config(text="❌ 설치 중 오류 발생", fg="red")
        
        # 설치 스레드 시작
        threading.Thread(target=install_thread, daemon=True).start()
    
    # 🔧 스크롤 기능이 포함된 UI 설정
    def setup_ui(self):
        self.root.title("🚀 GitHub 자동 업로드")
        self.root.geometry("550x700")  # 적당한 크기로 설정
        self.root.resizable(True, True)  # 크기 조정 가능하게
        
        # 🔧 스크롤 가능한 메인 프레임 생성
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 레이아웃 배치
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 메인 프레임 (스크롤 가능한 영역 내에)
        main_frame = tk.Frame(self.scrollable_frame, padx=30, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        title_label = tk.Label(main_frame, text="🚀 GitHub Auto Upload", 
                              font=("Arial", 20, "bold"), fg="navy")
        title_label.pack(pady=(0, 20))
        
        # 프로필 선택 섹션
        self.create_profile_section(main_frame)
        
        # 상태 표시 프레임
        self.create_status_frame(main_frame)
        
        # 기능 버튼들
        self.create_function_buttons(main_frame)
        
        # 🔧 패키지 관리 버튼 추가
        self.create_package_management_section(main_frame)
        
        # 종료 버튼
        self.create_exit_button(main_frame)
        
        # 마우스 휠 스크롤 바인딩
        self.bind_mousewheel()
    
    # 🔧 마우스 휠 스크롤 기능
    def bind_mousewheel(self):
        """마우스 휠로 스크롤 가능하게 하기"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', bind_to_mousewheel)
        self.canvas.bind('<Leave>', unbind_from_mousewheel)
    
    # 🔧 패키지 관리 섹션 추가
    def create_package_management_section(self, parent):
        package_frame = tk.LabelFrame(parent, text="📦 패키지 관리", 
                                     font=("Arial", 11, "bold"), 
                                     padx=15, pady=10)
        package_frame.pack(fill='x', pady=(15, 0))
        
        package_btn_frame = tk.Frame(package_frame)
        package_btn_frame.pack(pady=5)
        
        # 패키지 설치 버튼
        install_btn = tk.Button(package_btn_frame, text="📦 패키지 설치/업데이트", 
                               width=18, height=1,
                               font=("Arial", 10),
                               bg="lightgreen", fg="darkgreen",
                               command=self.manual_package_install)
        install_btn.pack(side='left', padx=5)
        
        # 패키지 상태 확인 버튼
        check_btn = tk.Button(package_btn_frame, text="🔍 패키지 상태 확인", 
                             width=18, height=1,
                             font=("Arial", 10),
                             bg="lightblue", fg="darkblue",
                             command=self.check_package_status)
        check_btn.pack(side='left', padx=5)
    
    def manual_package_install(self):
        """수동 패키지 설치 다이얼로그"""
        self.show_package_install_dialog([])  # 빈 리스트로 호출하여 전체 설치
    
    def check_package_status(self):
        """패키지 설치 상태 확인"""
        status_window = tk.Toplevel(self.root)
        status_window.title("📦 패키지 상태")
        status_window.geometry("500x600")
        status_window.resizable(False, False)
        
        main_frame = tk.Frame(status_window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        tk.Label(main_frame, text="📦 패키지 설치 상태", 
                font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # 환경 정보
        env_type = self.detect_environment_type()
        tk.Label(main_frame, text=f"현재 환경: {env_type}", 
                font=("Arial", 11), fg="blue").pack(pady=(0, 20))
        
        # 패키지 상태 표시
        status_text = scrolledtext.ScrolledText(main_frame, height=20, font=("Consolas", 10))
        status_text.pack(fill='both', expand=True, pady=(0, 20))
        
        required_packages = [
            ('PyGithub', 'github'),
            ('python-dotenv', 'dotenv'),
            ('watchdog', 'watchdog'),
            ('schedule', 'schedule'),
            ('requests', 'requests'),
            ('beautifulsoup4', 'bs4'),
            ('psutil', 'psutil')
        ]
        
        status_text.insert(tk.END, "📦 필수 패키지 설치 상태\n")
        status_text.insert(tk.END, "=" * 40 + "\n\n")
        
        all_installed = True
        for package_name, import_name in required_packages:
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'Unknown')
                status_text.insert(tk.END, f"✅ {package_name:<20} 버전: {version}\n")
            except ImportError:
                status_text.insert(tk.END, f"❌ {package_name:<20} 설치되지 않음\n")
                all_installed = False
        
        status_text.insert(tk.END, "\n" + "=" * 40 + "\n")
        if all_installed:
            status_text.insert(tk.END, "🎉 모든 패키지가 정상적으로 설치되어 있습니다!\n")
            status_text.insert(tk.END, "✅ GitHub 자동 업로드 시스템을 사용할 준비가 되었습니다.")
        else:
            status_text.insert(tk.END, "⚠️  일부 패키지가 설치되지 않았습니다.\n")
            status_text.insert(tk.END, "💡 '패키지 설치/업데이트' 버튼을 클릭하여 설치하세요.")
        
        # 닫기 버튼
        tk.Button(main_frame, text="닫기", command=status_window.destroy,
                 font=("Arial", 11), width=10).pack()
    
    # 기존 메서드들
    def create_profile_section(self, parent):
        profile_frame = tk.LabelFrame(parent, text="🏷️ 프로필 선택", 
                                     font=("Arial", 12, "bold"), 
                                     padx=20, pady=15)
        profile_frame.pack(fill='x', pady=(0, 20))
        
        selection_frame = tk.Frame(profile_frame)
        selection_frame.pack(fill='x', pady=5)
        
        tk.Label(selection_frame, text="현재 프로필:", 
                font=("Arial", 11, "bold")).pack(side='left')
        
        self.profile_combobox = ttk.Combobox(selection_frame, 
                                           textvariable=self.current_profile,
                                           state="readonly", 
                                           width=20, 
                                           font=("Arial", 11))
        self.profile_combobox.pack(side='left', padx=(10, 10))
        self.profile_combobox.bind('<<ComboboxSelected>>', self.on_profile_change)
        
        refresh_profiles_btn = tk.Button(selection_frame, text="🔄", 
                                       command=self.load_profiles,
                                       font=("Arial", 10), width=3)
        refresh_profiles_btn.pack(side='left', padx=5)
        
        self.profile_info_label = tk.Label(profile_frame, 
                                          text="프로필을 선택하세요", 
                                          font=("Arial", 10), 
                                          fg="gray")
        self.profile_info_label.pack(anchor='w', pady=(10, 0))
    
    def load_profiles(self):
        try:
            profiles = self.env_generator.get_all_profiles()
            
            if profiles:
                self.profile_combobox['values'] = profiles
                current = self.current_profile.get()
                if not current or current not in profiles:
                    self.current_profile.set(profiles[0])
                    self.on_profile_change()
                
                self.profile_info_label.config(
                    text=f"사용 가능한 프로필: {len(profiles)}개", 
                    fg="darkgreen"
                )
            else:
                self.profile_combobox['values'] = []
                self.current_profile.set("")
                self.profile_info_label.config(
                    text="저장된 프로필이 없습니다. 환경설정에서 프로필을 생성하세요.", 
                    fg="orange"
                )
            
            print(f"📋 프로필 목록 로드: {profiles}")
            
        except Exception as e:
            print(f"❌ 프로필 로드 실패: {e}")
            self.profile_info_label.config(text="프로필 로드 실패", fg="red")
    
    def on_profile_change(self, event=None):
        selected_profile = self.current_profile.get()
        if not selected_profile:
            return
        
        try:
            print(f"🔄 프로필 전환: {selected_profile}")
            success, message = self.env_generator.copy_profile_to_current_env(selected_profile)
            
            if success:
                print(f"✅ 프로필 전환 성공: {message}")
                profile_info = self.env_generator.get_profile_info(selected_profile)
                if profile_info:
                    repo = profile_info.get('GITHUB_REPO', 'Unknown')
                    username = profile_info.get('GITHUB_USERNAME', 'Unknown')
                    self.profile_info_label.config(
                        text=f"활성 프로필: {selected_profile} → {username}/{repo}", 
                        fg="darkblue"
                    )
                self.update_status()
            else:
                print(f"❌ 프로필 전환 실패: {message}")
                messagebox.showerror("프로필 전환 실패", message)
                
        except Exception as e:
            print(f"❌ 프로필 변경 중 오류: {e}")
            messagebox.showerror("오류", f"프로필 변경 중 오류가 발생했습니다: {e}")
    
    def create_status_frame(self, parent):
        status_frame = tk.LabelFrame(parent, text="📊 현재 상태", 
                                    font=("Arial", 12, "bold"), 
                                    padx=20, pady=15)
        status_frame.pack(fill='x', pady=(0, 20))
        
        self.status_label = tk.Label(status_frame, text="⚙️ 설정 확인 중...", 
                                    font=("Arial", 11), fg="orange")
        self.status_label.pack(anchor='w', pady=5)
        
        self.folder_label = tk.Label(status_frame, text="📁 감시 폴더: 확인 중...", 
                                    font=("Arial", 10), fg="gray")
        self.folder_label.pack(anchor='w', pady=2)
        
        self.repo_label = tk.Label(status_frame, text="📂 저장소: 확인 중...", 
                                  font=("Arial", 10), fg="gray")
        self.repo_label.pack(anchor='w', pady=2)
        
        self.mode_label = tk.Label(status_frame, text="🔧 업로드 모드: 확인 중...", 
                                  font=("Arial", 10), fg="gray")
        self.mode_label.pack(anchor='w', pady=2)
        
        self.upload_status_label = tk.Label(status_frame, text="🚀 업로드 상태: 중지됨", 
                                           font=("Arial", 10, "bold"), fg="red")
        self.upload_status_label.pack(anchor='w', pady=2)
    
    def create_function_buttons(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=20)
        
        first_row = tk.Frame(button_frame)
        first_row.pack(pady=10)
        
        baekjoon_btn = tk.Button(first_row, text="📚\n백준 문제\n풀기", 
                                width=12, height=4,
                                font=("Arial", 11, "bold"),
                                bg="lightblue", fg="navy",
                                command=self.open_baekjoon)
        baekjoon_btn.pack(side='left', padx=20)
        
        setup_btn = tk.Button(first_row, text="⚙️\n환경설정", 
                             width=12, height=4,
                             font=("Arial", 11, "bold"),
                             bg="lightgreen", fg="darkgreen",
                             command=self.open_setup)
        setup_btn.pack(side='left', padx=20)
        
        second_row = tk.Frame(button_frame)
        second_row.pack(pady=10)
        
        self.upload_btn = tk.Button(second_row, text="🚀\n업로드\n시작", 
                                   width=12, height=4,
                                   font=("Arial", 11, "bold"),
                                   bg="orange", fg="white",
                                   command=self.toggle_upload)
        self.upload_btn.pack(side='left', padx=20)
        
        history_btn = tk.Button(second_row, text="📊\n업로드\n기록", 
                               width=12, height=4,
                               font=("Arial", 11, "bold"),
                               bg="lightgray", fg="black",
                               command=self.show_history)
        history_btn.pack(side='left', padx=20)
        
        refresh_btn = tk.Button(button_frame, text="🔄 상태 새로고침", 
                               width=20, height=1,
                               font=("Arial", 10),
                               bg="lightcyan", fg="darkblue",
                               command=self.update_status)
        refresh_btn.pack(pady=10)
    
    def create_exit_button(self, parent):
        exit_btn = tk.Button(parent, text="종료", width=10, height=2,
                            font=("Arial", 11),
                            command=self.on_exit)
        exit_btn.pack(pady=20)
    
    # 업로드 관련 메서드들
    def toggle_upload(self):
        if self.is_upload_running:
            self.stop_upload()
        else:
            self.start_upload()
    
    def start_upload(self):
        try:
            if self.is_upload_running:
                messagebox.showwarning("경고", "업로드가 이미 실행 중입니다!")
                return
            
            self.upload_process = subprocess.Popen([sys.executable, 'main_upload.py'])
            
            with open(self.upload_pid_file, 'w') as f:
                f.write(str(self.upload_process.pid))
            
            self.is_upload_running = True
            self.update_upload_button()
            
            current_profile = self.current_profile.get()
            if current_profile:
                message_text = f"GitHub 자동 업로드가 시작되었습니다!\n\n현재 프로필: {current_profile}\n콘솔 창에서 업로드 상태를 확인할 수 있습니다."
            else:
                message_text = "GitHub 자동 업로드가 시작되었습니다!\n\n콘솔 창에서 업로드 상태를 확인할 수 있습니다."
            
            messagebox.showinfo("시작", message_text)
            print(f"✅ 업로드 프로세스 시작됨 (PID: {self.upload_process.pid})")
            
        except FileNotFoundError:
            messagebox.showerror("오류", "main_upload.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"업로드 프로그램을 시작할 수 없습니다: {e}")
            self.is_upload_running = False
            self.update_upload_button()
    
    def stop_upload(self):
        try:
            if self.upload_process and self.upload_process.poll() is None:
                try:
                    parent = psutil.Process(self.upload_process.pid)
                    children = parent.children(recursive=True)
                    
                    for child in children:
                        try:
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                    
                    parent.terminate()
                    
                    gone, still_alive = psutil.wait_procs([parent] + children, timeout=3)
                    for p in still_alive:
                        try:
                            p.kill()
                        except psutil.NoSuchProcess:
                            pass
                    
                    print(f"✅ 업로드 프로세스 종료됨 (PID: {self.upload_process.pid})")
                    
                except psutil.NoSuchProcess:
                    print("ℹ️  프로세스가 이미 종료되었습니다")
                except Exception as e:
                    print(f"⚠️  프로세스 종료 중 오류: {e}")
                    self.upload_process.terminate()
            
            if os.path.exists(self.upload_pid_file):
                os.remove(self.upload_pid_file)
            
            self.upload_process = None
            self.is_upload_running = False
            self.update_upload_button()
            
            messagebox.showinfo("중지", "GitHub 자동 업로드가 중지되었습니다!")
            
        except Exception as e:
            messagebox.showerror("오류", f"업로드 프로그램을 중지할 수 없습니다: {e}")
            print(f"❌ 업로드 중지 실패: {e}")
    
    def update_upload_button(self):
        if self.is_upload_running:
            self.upload_btn.config(
                text="⏹️\n업로드\n중지",
                bg="red",
                fg="white"
            )
            self.upload_status_label.config(
                text="🚀 업로드 상태: 실행 중",
                fg="green"
            )
        else:
            self.upload_btn.config(
                text="🚀\n업로드\n시작",
                bg="orange",
                fg="white"
            )
            self.upload_status_label.config(
                text="🚀 업로드 상태: 중지됨",
                fg="red"
            )
    
    def check_upload_process(self):
        try:
            if os.path.exists(self.upload_pid_file):
                with open(self.upload_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    try:
                        process = psutil.Process(pid)
                        if 'python' in process.name().lower():
                            self.is_upload_running = True
                            self.upload_process = subprocess.Popen([], shell=False)
                            self.upload_process.pid = pid
                            print(f"ℹ️  기존 업로드 프로세스 발견 (PID: {pid})")
                        else:
                            os.remove(self.upload_pid_file)
                    except psutil.NoSuchProcess:
                        os.remove(self.upload_pid_file)
                else:
                    os.remove(self.upload_pid_file)
            
            self.update_upload_button()
            
        except Exception as e:
            print(f"⚠️  프로세스 상태 체크 실패: {e}")
            self.is_upload_running = False
            self.update_upload_button()
    
    def start_process_monitor(self):
        def monitor():
            while True:
                try:
                    if self.is_upload_running and self.upload_process:
                        if self.upload_process.poll() is not None:
                            self.is_upload_running = False
                            self.upload_process = None
                            
                            if os.path.exists(self.upload_pid_file):
                                os.remove(self.upload_pid_file)
                            
                            self.root.after(0, self.update_upload_button)
                            print("ℹ️  업로드 프로세스가 종료되어 버튼 상태를 업데이트했습니다")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"⚠️  프로세스 모니터링 오류: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def update_status(self):
        try:
            print("🔄 상태 업데이트 중...")
            
            if os.path.exists('.env'):
                load_dotenv(override=True)
                
                token = os.getenv('GITHUB_TOKEN')
                username = os.getenv('GITHUB_USERNAME')
                repo = os.getenv('GITHUB_REPO')
                folder = os.getenv('WATCH_FOLDER')
                mode = os.getenv('UPLOAD_MODE', 'realtime')
                
                if all([token, username, repo, folder]):
                    current_profile = self.current_profile.get()
                    if current_profile:
                        self.status_label.config(
                            text=f"✅ 설정 완료 - 업로드 준비됨 (프로필: {current_profile})", 
                            fg="green"
                        )
                    else:
                        self.status_label.config(text="✅ 설정 완료 - 업로드 준비됨", fg="green")
                    
                    self.folder_label.config(text=f"📁 감시 폴더: {folder}", fg="black")
                    self.repo_label.config(text=f"📂 저장소: {username}/{repo}", fg="black")
                    
                    mode_text = {
                        "realtime": "실시간 감시",
                        "schedule": "시간 예약", 
                        "hybrid": "실시간 + 예약"
                    }
                    self.mode_label.config(text=f"🔧 업로드 모드: {mode_text.get(mode, mode)}", fg="black")
                    
                    if not self.is_upload_running:
                        self.upload_btn.config(state='normal')
                    
                    print("✅ 설정 완료!")
                else:
                    self.status_label.config(text="⚠️ 설정 불완전 - 환경설정 필요", fg="orange")
                    if not self.is_upload_running:
                        self.upload_btn.config(state='disabled', bg="gray")
                    print("⚠️ 설정 불완전")
            else:
                self.status_label.config(text="❌ 설정 없음 - 환경설정 필요", fg="red")
                self.folder_label.config(text="📁 감시 폴더: 설정되지 않음", fg="gray")
                self.repo_label.config(text="📂 저장소: 설정되지 않음", fg="gray")
                self.mode_label.config(text="🔧 업로드 모드: 설정되지 않음", fg="gray")
                if not self.is_upload_running:
                    self.upload_btn.config(state='disabled', bg="gray")
                print("❌ .env 파일 없음")
                
        except Exception as e:
            self.status_label.config(text="❌ 설정 오류 발생", fg="red")
            if not self.is_upload_running:
                self.upload_btn.config(state='disabled', bg="gray")
            print(f"❌ 에러: {e}")
    
    def open_baekjoon(self):
        try:
            subprocess.Popen([sys.executable, 'baekjoon_gui.py'])
        except FileNotFoundError:
            messagebox.showerror("오류", "baekjoon_gui.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"백준 문제 창을 열 수 없습니다: {e}")
    
    def open_setup(self):
        try:
            process = subprocess.Popen([sys.executable, 'setup_gui.py'])
            
            def wait_and_update():
                process.wait()
                self.root.after(100, self.load_profiles)
                self.root.after(200, self.update_status)
            
            threading.Thread(target=wait_and_update, daemon=True).start()
            
        except FileNotFoundError:
            messagebox.showerror("오류", "setup_gui.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"환경설정 창을 열 수 없습니다: {e}")
    
    def show_history(self):
        messagebox.showinfo("개발 중", "업로드 기록 기능은 개발 중입니다!")
    
    def on_exit(self):
        if self.is_upload_running:
            result = messagebox.askyesno(
                "종료 확인", 
                "업로드가 실행 중입니다.\n업로드를 중지하고 종료하시겠습니까?"
            )
            if result:
                self.stop_upload()
                self.root.quit()
        else:
            self.root.quit()

if __name__ == "__main__":
    print("🚀 GitHub 자동 업로드 메인 GUI 시작...")
    app = GitHubAutoUploadMain()
    app.root.mainloop()
    print("👋 메인 GUI 종료")