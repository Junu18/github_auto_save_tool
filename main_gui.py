# main_gui.py - 수정된 최종 버전
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
from dotenv import load_dotenv

class GitHubAutoUploadMain:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()
        self.update_status()  # 🔧 시작할 때 즉시 상태 체크
        
    def setup_ui(self):
        self.root.title("🚀 GitHub 자동 업로드")
        self.root.geometry("500x630")
        self.root.resizable(False, False)
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, padx=30, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # 제목
        title_label = tk.Label(main_frame, text="🚀 GitHub Auto Upload", 
                              font=("Arial", 20, "bold"), fg="navy")
        title_label.pack(pady=(0, 30))
        
        # 상태 표시 프레임
        self.create_status_frame(main_frame)
        
        # 기능 버튼들
        self.create_function_buttons(main_frame)
        
        # 종료 버튼
        self.create_exit_button(main_frame)
    
    def create_status_frame(self, parent):
        status_frame = tk.LabelFrame(parent, text="📊 현재 상태", 
                                    font=("Arial", 12, "bold"), 
                                    padx=20, pady=15)
        status_frame.pack(fill='x', pady=(0, 30))
        
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
    
    def create_function_buttons(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=20)
        
        # 첫 번째 줄
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
        
        # 두 번째 줄
        second_row = tk.Frame(button_frame)
        second_row.pack(pady=10)
        
        self.upload_btn = tk.Button(second_row, text="🚀\n업로드\n시작", 
                                   width=12, height=4,
                                   font=("Arial", 11, "bold"),
                                   bg="orange", fg="white",
                                   command=self.start_upload)
        self.upload_btn.pack(side='left', padx=20)
        
        history_btn = tk.Button(second_row, text="📊\n업로드\n기록", 
                               width=12, height=4,
                               font=("Arial", 11, "bold"),
                               bg="lightgray", fg="black",
                               command=self.show_history)
        history_btn.pack(side='left', padx=20)
        
        # 🔧 상태 새로고침 버튼 추가
        refresh_btn = tk.Button(button_frame, text="🔄 상태 새로고침", 
                               width=20, height=1,
                               font=("Arial", 10),
                               bg="lightcyan", fg="darkblue",
                               command=self.update_status)
        refresh_btn.pack(pady=10)
    
    def create_exit_button(self, parent):
        exit_btn = tk.Button(parent, text="종료", width=10, height=2,
                            font=("Arial", 11),
                            command=self.root.quit)
        exit_btn.pack(pady=30)
    
    def update_status(self):
        """현재 설정 상태 확인"""
        try:
            print("🔄 상태 업데이트 중...")  # 디버그용
            
            if os.path.exists('.env'):
                load_dotenv(override=True)  # 🔧 강제 재로드
                
                token = os.getenv('GITHUB_TOKEN')
                username = os.getenv('GITHUB_USERNAME')
                repo = os.getenv('GITHUB_REPO')        # 🔧 수정: REPO_NAME → GITHUB_REPO
                folder = os.getenv('WATCH_FOLDER')     # 🔧 수정: WATCH_FOLDER_PATH → WATCH_FOLDER
                mode = os.getenv('UPLOAD_MODE', 'realtime')
                
                print(f"📋 환경변수 체크:")  # 디버그용
                print(f"   토큰: {'있음' if token else '없음'}")
                print(f"   사용자명: {username}")
                print(f"   저장소: {repo}")
                print(f"   폴더: {folder}")
                print(f"   모드: {mode}")
                
                if all([token, username, repo, folder]):
                    self.status_label.config(text="✅ 설정 완료 - 업로드 준비됨", fg="green")
                    self.folder_label.config(text=f"📁 감시 폴더: {folder}", fg="black")
                    self.repo_label.config(text=f"📂 저장소: {username}/{repo}", fg="black")
                    
                    mode_text = {
                        "realtime": "실시간 감시",
                        "schedule": "시간 예약", 
                        "hybrid": "실시간 + 예약"
                    }
                    self.mode_label.config(text=f"🔧 업로드 모드: {mode_text.get(mode, mode)}", fg="black")
                    self.upload_btn.config(state='normal', bg="orange")
                    print("✅ 업로드 버튼 활성화!")
                else:
                    self.status_label.config(text="⚠️ 설정 불완전 - 환경설정 필요", fg="orange")
                    self.upload_btn.config(state='disabled', bg="gray")
                    print("⚠️ 설정 불완전")
            else:
                self.status_label.config(text="❌ 설정 없음 - 환경설정 필요", fg="red")
                self.folder_label.config(text="📁 감시 폴더: 설정되지 않음", fg="gray")
                self.repo_label.config(text="📂 저장소: 설정되지 않음", fg="gray")
                self.mode_label.config(text="🔧 업로드 모드: 설정되지 않음", fg="gray")
                self.upload_btn.config(state='disabled', bg="gray")
                print("❌ .env 파일 없음")
                
        except Exception as e:
            self.status_label.config(text="❌ 설정 오류 발생", fg="red")
            self.upload_btn.config(state='disabled', bg="gray")
            print(f"❌ 에러: {e}")
    
    def open_baekjoon(self):
        """백준 문제 풀기 창 열기"""
        try:
            subprocess.Popen([sys.executable, 'baekjoon_gui.py'])
        except FileNotFoundError:
            messagebox.showerror("오류", "baekjoon_gui.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"백준 문제 창을 열 수 없습니다: {e}")
    
    def open_setup(self):
        """환경설정 창 열기"""
        try:
            # 🔧 환경설정 프로세스를 기다리도록 수정
            process = subprocess.Popen([sys.executable, 'setup_gui.py'])
            
            # 🔧 별도 스레드에서 프로세스 종료 대기
            import threading
            def wait_and_update():
                process.wait()  # 환경설정 창이 닫힐 때까지 대기
                self.root.after(100, self.update_status)  # 메인 스레드에서 업데이트
            
            threading.Thread(target=wait_and_update, daemon=True).start()
            
        except FileNotFoundError:
            messagebox.showerror("오류", "setup_gui.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"환경설정 창을 열 수 없습니다: {e}")
    
    def start_upload(self):
        """업로드 프로그램 시작"""
        try:
            subprocess.Popen([sys.executable, 'main_upload.py'])
            messagebox.showinfo("시작", "GitHub 자동 업로드 프로그램이 시작되었습니다!\n\n콘솔 창에서 업로드 상태를 확인할 수 있습니다.")
        except FileNotFoundError:
            messagebox.showerror("오류", "main_upload.py 파일을 찾을 수 없습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"업로드 프로그램을 시작할 수 없습니다: {e}")
    
    def show_history(self):
        messagebox.showinfo("개발 중", "업로드 기록 기능은 개발 중입니다!")

if __name__ == "__main__":
    print("🚀 GitHub 자동 업로드 메인 GUI 시작...")
    app = GitHubAutoUploadMain()
    app.root.mainloop()
    print("👋 메인 GUI 종료")