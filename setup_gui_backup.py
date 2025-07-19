# # setup_gui.py - 프로필 별명 기능 추가 완전 버전
# import tkinter as tk
# from tkinter import messagebox, filedialog, ttk
# import os
# import json
# from env_generate import EnvGenerator

# class GitHubAutoUploadSetup:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.env_generator = EnvGenerator()
#         self.upload_mode = tk.StringVar(value="hybrid")
#         self.repeat_option = tk.StringVar(value="daily")
        
#         # 시간 설정용 StringVar 추가
#         self.hour_var = tk.StringVar(value="14")
#         self.minute_var = tk.StringVar(value="30")
        
#         # 파일 형식 설정용 변수 추가
#         self.file_extensions = tk.StringVar(value="py,txt,md,json,js,html,css")
        
#         # 🔧 새로 추가: 프로필 별명 변수
#         self.profile_name = tk.StringVar(value="")
        
#         self.setup_ui()
#         self.load_existing_profiles()  # 🔧 기존 프로필 목록 로드
    
#     def setup_ui(self):
#         self.root.title("🚀 GitHub 자동 업로드 설정")
#         self.root.geometry("700x1100")  # 높이 더 증가
#         self.root.resizable(True, True)
        
#         # 스크롤 가능한 콘텐츠 영역 생성
#         self.canvas = tk.Canvas(self.root)
#         self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
#         self.scrollable_frame = tk.Frame(self.canvas)
        
#         self.scrollable_frame.bind(
#             "<Configure>",
#             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
#         )
        
#         self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
#         self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
#         # 레이아웃 배치
#         self.canvas.pack(side="left", fill="both", expand=True)
#         self.scrollbar.pack(side="right", fill="y")
        
#         # 메인 프레임
#         main_frame = tk.Frame(self.scrollable_frame, padx=30, pady=30)
#         main_frame.pack(fill='both', expand=True)
        
#         # 제목
#         title_label = tk.Label(main_frame, text="🚀 GitHub 자동 업로드 설정", 
#                               font=("Arial", 18, "bold"))
#         title_label.pack(pady=(0, 30))
        
#         # 🔧 새로 추가: 프로필 설정
#         self.create_profile_section(main_frame)
        
#         # 기본 설정
#         self.create_basic_settings(main_frame)
        
#         # 업로드 모드
#         self.create_upload_mode_section(main_frame)
        
#         # 시간 설정
#         self.create_time_section(main_frame)
        
#         # 파일 형식 설정
#         self.create_file_extension_section(main_frame)
        
#         # 상태 표시
#         self.status_label = tk.Label(main_frame, text="설정을 입력해주세요.", fg="blue", font=("Arial", 11))
#         self.status_label.pack(pady=20)
        
#         # 버튼
#         self.create_button_section(main_frame)
        
#         # 마우스 휠 스크롤 바인딩
#         self.bind_mousewheel()
    
#     # 🔧 새로 추가: 프로필 설정 섹션
#     def create_profile_section(self, parent):
#         profile_frame = tk.LabelFrame(parent, text="🏷️ 프로필 설정", 
#                                      font=("Arial", 12, "bold"), padx=15, pady=15)
#         profile_frame.pack(fill='x', pady=(0, 25))
        
#         # 별명 입력
#         tk.Label(profile_frame, text="프로필 별명 (필수):", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        
#         profile_input_frame = tk.Frame(profile_frame)
#         profile_input_frame.pack(fill='x', pady=5)
        
#         self.profile_entry = tk.Entry(profile_input_frame, textvariable=self.profile_name, 
#                                      font=("Arial", 11), width=30)
#         self.profile_entry.pack(side='left', padx=(0, 10))
        
#         # 기존 프로필 선택 버튼
#         select_btn = tk.Button(profile_input_frame, text="📋 기존 프로필 선택", 
#                               command=self.show_existing_profiles,
#                               bg="lightcyan", font=("Arial", 9))
#         select_btn.pack(side='left')
        
#         # 안내 텍스트
#         help_text = "💡 예시: 개인프로젝트, 회사업무, 학교과제 등 (한글/영문/숫자 가능)"
#         help_label = tk.Label(profile_frame, text=help_text, 
#                              font=("Arial", 9), fg="gray", wraplength=600)
#         help_label.pack(anchor='w', pady=(5, 0))
        
#         # 기존 프로필 목록 표시
#         self.existing_profiles_label = tk.Label(profile_frame, text="", 
#                                                font=("Arial", 10), fg="darkgreen", wraplength=600)
#         self.existing_profiles_label.pack(anchor='w', pady=(10, 0))
    
#     def show_existing_profiles(self):
#         """기존 프로필 선택 다이얼로그"""
#         profiles = self.get_existing_profiles()
#         if not profiles:
#             messagebox.showinfo("프로필 없음", "저장된 프로필이 없습니다.\n새로운 프로필 별명을 입력해주세요.")
#             return
        
#         # 프로필 선택 창
#         profile_window = tk.Toplevel(self.root)
#         profile_window.title("📋 기존 프로필 선택")
#         profile_window.geometry("400x300")
#         profile_window.resizable(False, False)
        
#         tk.Label(profile_window, text="기존 프로필 선택:", font=("Arial", 12, "bold")).pack(pady=10)
        
#         # 리스트박스
#         listbox_frame = tk.Frame(profile_window)
#         listbox_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
#         listbox = tk.Listbox(listbox_frame, font=("Arial", 11))
#         scrollbar = tk.Scrollbar(listbox_frame)
        
#         listbox.config(yscrollcommand=scrollbar.set)
#         scrollbar.config(command=listbox.yview)
        
#         for profile in profiles:
#             listbox.insert(tk.END, profile)
        
#         listbox.pack(side='left', fill='both', expand=True)
#         scrollbar.pack(side='right', fill='y')
        
#         # 버튼
#         button_frame = tk.Frame(profile_window)
#         button_frame.pack(pady=10)
        
#         def select_profile():
#             selection = listbox.curselection()
#             if selection:
#                 selected_profile = listbox.get(selection[0])
#                 self.profile_name.set(selected_profile)
#                 self.load_profile_config(selected_profile)
#                 profile_window.destroy()
#             else:
#                 messagebox.showwarning("선택 없음", "프로필을 선택해주세요.")
        
#         tk.Button(button_frame, text="✅ 선택", command=select_profile).pack(side='left', padx=10)
#         tk.Button(button_frame, text="❌ 취소", command=profile_window.destroy).pack(side='left', padx=10)
    
#     def get_existing_profiles(self):
#         """기존 프로필 목록 가져오기"""
#         try:
#             if os.path.exists('profiles.json'):
#                 with open('profiles.json', 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     return data.get('profiles', [])
#             return []
#         except Exception as e:
#             print(f"프로필 목록 로드 실패: {e}")
#             return []
    
#     def load_existing_profiles(self):
#         """기존 프로필 목록을 화면에 표시"""
#         profiles = self.get_existing_profiles()
#         if profiles:
#             profile_text = f"기존 프로필: {', '.join(profiles)}"
#             self.existing_profiles_label.config(text=profile_text)
#         else:
#             self.existing_profiles_label.config(text="저장된 프로필이 없습니다.")
    
#     def load_profile_config(self, profile_name):
#         """선택된 프로필의 설정 불러오기"""
#         try:
#             env_file = f'.env_{profile_name}'
#             if os.path.exists(env_file):
#                 from dotenv import load_dotenv
#                 load_dotenv(env_file)
                
#                 # 기본 설정 불러오기
#                 token = os.getenv('GITHUB_TOKEN', '')
#                 username = os.getenv('GITHUB_USERNAME', '')
#                 repo = os.getenv('GITHUB_REPO', '')
#                 folder = os.getenv('WATCH_FOLDER', '')
#                 mode = os.getenv('UPLOAD_MODE', 'hybrid')
#                 repeat = os.getenv('REPEAT_OPTION', 'daily')
                
#                 # 시간 설정 불러오기
#                 upload_time = os.getenv('UPLOAD_TIME', '14:30')
#                 try:
#                     hour, minute = upload_time.split(':')
#                     self.hour_var.set(f"{int(hour):02d}")
#                     self.minute_var.set(f"{int(minute):02d}")
#                 except:
#                     pass
                
#                 # 파일 형식 설정 불러오기
#                 file_extensions = os.getenv('FILE_EXTENSIONS', 'py,txt,md,json,js,html,css')
#                 self.file_extensions.set(file_extensions)
                
#                 # Entry 필드 초기화 후 값 설정
#                 self.token_entry.delete(0, tk.END)
#                 self.username_entry.delete(0, tk.END)
#                 self.repo_entry.delete(0, tk.END)
#                 self.folder_entry.delete(0, tk.END)
                
#                 if token:
#                     self.token_entry.insert(0, token)
#                 if username:
#                     self.username_entry.insert(0, username)
#                 if repo:
#                     self.repo_entry.insert(0, repo)
#                 if folder:
#                     self.folder_entry.insert(0, folder)
                
#                 # 모드 및 반복 설정
#                 self.upload_mode.set(mode)
#                 self.repeat_option.set(repeat)
                
#                 # 파일 형식 표시 업데이트
#                 ext_list = [ext.strip() for ext in file_extensions.split(',')]
#                 display_text = ', '.join(ext_list)
#                 if hasattr(self, 'current_extensions_label'):
#                     self.current_extensions_label.config(text=display_text, fg="darkgreen")
                
#                 # 모드에 따른 시간 설정 활성화/비활성화
#                 self.on_mode_change()
                
#                 self.status_label.config(text=f"'{profile_name}' 프로필 설정을 불러왔습니다.", fg="green")
                
#             else:
#                 messagebox.showwarning("프로필 없음", f"'{profile_name}' 프로필 파일을 찾을 수 없습니다.")
                
#         except Exception as e:
#             print(f"프로필 설정 불러오기 실패: {e}")
#             messagebox.showerror("오류", f"프로필 설정 불러오기에 실패했습니다: {e}")
    
#     def bind_mousewheel(self):
#         """마우스 휠로 스크롤 가능하게 하기"""
#         def _on_mousewheel(event):
#             self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
#         def bind_to_mousewheel(event):
#             self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
#         def unbind_from_mousewheel(event):
#             self.canvas.unbind_all("<MouseWheel>")
        
#         self.canvas.bind('<Enter>', bind_to_mousewheel)
#         self.canvas.bind('<Leave>', unbind_from_mousewheel)
    
#     def create_basic_settings(self, parent):
#         # GitHub 토큰
#         tk.Label(parent, text="🔑 GitHub Personal Access Token:", 
#                 font=("Arial", 11, "bold")).pack(anchor='w', pady=(15, 5))
#         self.token_entry = tk.Entry(parent, width=60, show="*", font=("Arial", 10))
#         self.token_entry.pack(anchor='w', pady=(0, 10))
        
#         # 사용자명
#         tk.Label(parent, text="👤 GitHub 사용자명:", 
#                 font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
#         self.username_entry = tk.Entry(parent, width=30, font=("Arial", 10))
#         self.username_entry.pack(anchor='w', pady=(0, 10))
        
#         # 저장소명
#         tk.Label(parent, text="📂 저장소 이름:", 
#                 font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
#         self.repo_entry = tk.Entry(parent, width=30, font=("Arial", 10))
#         self.repo_entry.pack(anchor='w', pady=(0, 10))
        
#         # 폴더 경로
#         tk.Label(parent, text="📁 감시할 폴더 경로:", 
#                 font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
#         folder_frame = tk.Frame(parent)
#         folder_frame.pack(anchor='w', fill='x', pady=(0, 10))
#         self.folder_entry = tk.Entry(folder_frame, width=50, font=("Arial", 10))
#         self.folder_entry.pack(side='left', padx=(0, 10))
#         tk.Button(folder_frame, text="📁 찾아보기", 
#                  command=self.browse_folder).pack(side='left')
    
#     def create_upload_mode_section(self, parent):
#         mode_frame = tk.LabelFrame(parent, text="⏰ 업로드 모드 설정", 
#                                   font=("Arial", 11, "bold"), padx=15, pady=15)
#         mode_frame.pack(fill='x', pady=25)
        
#         tk.Radiobutton(mode_frame, text="🔄 실시간 감시 (파일 넣으면 즉시 업로드)", 
#                       variable=self.upload_mode, value="realtime", font=("Arial", 10),
#                       command=self.on_mode_change).pack(anchor='w', pady=8)
        
#         tk.Radiobutton(mode_frame, text="⏰ 시간 예약 (지정 시간에만 업로드)", 
#                       variable=self.upload_mode, value="schedule", font=("Arial", 10),
#                       command=self.on_mode_change).pack(anchor='w', pady=8)
        
#         tk.Radiobutton(mode_frame, text="🔄⏰ 혼합 모드 (실시간 + 예약)", 
#                       variable=self.upload_mode, value="hybrid", font=("Arial", 10),
#                       command=self.on_mode_change).pack(anchor='w', pady=8)
    
#     def create_time_section(self, parent):
#         self.time_frame = tk.LabelFrame(parent, text="🕐 업로드 시간 설정", 
#                                        font=("Arial", 11, "bold"), padx=15, pady=15)
#         self.time_frame.pack(fill='x', pady=15)
        
#         # 시간 입력
#         time_input_frame = tk.Frame(self.time_frame)
#         time_input_frame.pack(anchor='w', pady=15)
        
#         tk.Label(time_input_frame, text="시간:", font=("Arial", 11)).pack(side='left')
        
#         self.hour_spinbox = tk.Spinbox(time_input_frame, from_=0, to=23, width=5, 
#                                       format="%02.0f", font=("Arial", 12),
#                                       textvariable=self.hour_var)
#         self.hour_spinbox.pack(side='left', padx=8)
        
#         tk.Label(time_input_frame, text=":", font=("Arial", 14, "bold")).pack(side='left')
        
#         self.minute_spinbox = tk.Spinbox(time_input_frame, from_=0, to=59, width=5, 
#                                         format="%02.0f", font=("Arial", 12),
#                                         textvariable=self.minute_var)
#         self.minute_spinbox.pack(side='left', padx=8)
        
#         # 반복 설정
#         repeat_frame = tk.Frame(self.time_frame)
#         repeat_frame.pack(anchor='w', pady=15)
        
#         tk.Label(repeat_frame, text="반복 설정:", font=("Arial", 11)).pack(side='left')
#         repeat_combo = ttk.Combobox(repeat_frame, textvariable=self.repeat_option, 
#                                    values=["daily", "weekdays", "weekends"], 
#                                    state="readonly", width=15, font=("Arial", 10))
#         repeat_combo.pack(side='left', padx=15)
    
#     def create_file_extension_section(self, parent):
#         file_ext_frame = tk.LabelFrame(parent, text="📄 업로드 파일 형식 설정", 
#                                       font=("Arial", 11, "bold"), padx=15, pady=15)
#         file_ext_frame.pack(fill='x', pady=15)
        
#         # 현재 지원 형식 표시
#         current_label = tk.Label(file_ext_frame, text="현재 지원 형식:", font=("Arial", 10, "bold"))
#         current_label.pack(anchor='w', pady=(0, 5))
        
#         self.current_extensions_label = tk.Label(file_ext_frame, 
#                                                 text="py, txt, md, json, js, html, css", 
#                                                 font=("Arial", 10), fg="darkgreen",
#                                                 wraplength=600)
#         self.current_extensions_label.pack(anchor='w', pady=(0, 15))
        
#         # 파일 형식 수정 영역
#         edit_frame = tk.Frame(file_ext_frame)
#         edit_frame.pack(fill='x', pady=10)
        
#         tk.Label(edit_frame, text="파일 형식 (쉼표로 구분):", font=("Arial", 10, "bold")).pack(anchor='w', pady=(0, 5))
        
#         # 입력 필드와 버튼을 같은 줄에 배치
#         input_button_frame = tk.Frame(edit_frame)
#         input_button_frame.pack(fill='x', pady=5)
        
#         self.extensions_entry = tk.Entry(input_button_frame, textvariable=self.file_extensions, 
#                                         font=("Arial", 10), width=50)
#         self.extensions_entry.pack(side='left', padx=(0, 10))
        
#         update_btn = tk.Button(input_button_frame, text="✅ 적용", 
#                               command=self.update_file_extensions,
#                               bg="lightgreen", font=("Arial", 9, "bold"))
#         update_btn.pack(side='left')
        
#         # 도움말 텍스트
#         help_text = "💡 예시: py,txt,md,json,js,html,css,java,cpp,c (확장자만 입력, *. 제외)"
#         help_label = tk.Label(file_ext_frame, text=help_text, 
#                              font=("Arial", 9), fg="gray", wraplength=600)
#         help_label.pack(anchor='w', pady=(5, 0))
        
#         # 자주 사용하는 형식 버튼들
#         quick_frame = tk.LabelFrame(file_ext_frame, text="빠른 추가", font=("Arial", 9))
#         quick_frame.pack(fill='x', pady=(15, 0))
        
#         quick_buttons_frame = tk.Frame(quick_frame)
#         quick_buttons_frame.pack(pady=10)
        
#         quick_extensions = [
#             ("Java", "java"),
#             ("C/C++", "c,cpp,h"),
#             ("웹", "html,css,js,php"),
#             ("데이터", "csv,xml,yaml"),
#             ("이미지", "jpg,png,gif,svg"),
#             ("문서", "pdf,docx,xlsx")
#         ]
        
#         for i, (name, ext) in enumerate(quick_extensions):
#             btn = tk.Button(quick_buttons_frame, text=name, 
#                            command=lambda e=ext: self.add_quick_extensions(e),
#                            font=("Arial", 8), width=8)
#             btn.grid(row=i//3, column=i%3, padx=5, pady=2)
    
#     def update_file_extensions(self):
#         """파일 형식 업데이트 및 표시"""
#         extensions = self.file_extensions.get().strip()
#         if extensions:
#             # 쉼표로 분리해서 정리
#             ext_list = [ext.strip().replace('*.', '').replace('*', '') for ext in extensions.split(',')]
#             ext_list = [ext for ext in ext_list if ext]  # 빈 문자열 제거
            
#             # 다시 합치기
#             clean_extensions = ','.join(ext_list)
#             self.file_extensions.set(clean_extensions)
            
#             # 표시 업데이트
#             display_text = ', '.join(ext_list)
#             self.current_extensions_label.config(text=display_text, fg="darkgreen")
            
#             messagebox.showinfo("적용 완료", f"파일 형식이 업데이트되었습니다!\n\n지원 형식: {display_text}")
#         else:
#             messagebox.showwarning("입력 오류", "파일 형식을 입력해주세요.")
    
#     def add_quick_extensions(self, new_extensions):
#         """빠른 추가 버튼으로 형식 추가"""
#         current = self.file_extensions.get()
#         if current:
#             # 기존 형식과 중복 제거
#             current_list = [ext.strip() for ext in current.split(',')]
#             new_list = [ext.strip() for ext in new_extensions.split(',')]
            
#             # 합치고 중복 제거
#             combined = list(set(current_list + new_list))
#             combined.sort()  # 정렬
            
#             self.file_extensions.set(','.join(combined))
#         else:
#             self.file_extensions.set(new_extensions)
        
#         self.update_file_extensions()
    
#     def on_mode_change(self):
#         if self.upload_mode.get() == "realtime":
#             self.disable_time_settings()
#         else:
#             self.enable_time_settings()
    
#     def enable_time_settings(self):
#         for widget in self.time_frame.winfo_children():
#             self.enable_widget_recursive(widget)
    
#     def disable_time_settings(self):
#         for widget in self.time_frame.winfo_children():
#             self.disable_widget_recursive(widget)
    
#     def enable_widget_recursive(self, widget):
#         try:
#             widget.configure(state='normal')
#         except:
#             pass
#         for child in widget.winfo_children():
#             self.enable_widget_recursive(child)
    
#     def disable_widget_recursive(self, widget):
#         try:
#             widget.configure(state='disabled')
#         except:
#             pass
#         for child in widget.winfo_children():
#             self.disable_widget_recursive(child)
    
#     def browse_folder(self):
#         folder_path = filedialog.askdirectory(title="감시할 폴더를 선택하세요")
#         if folder_path:
#             self.folder_entry.delete(0, tk.END)
#             self.folder_entry.insert(0, folder_path)
    
#     def create_button_section(self, parent):
#         # 구분선 추가
#         separator = tk.Frame(parent, height=3, bg="lightgray")
#         separator.pack(fill='x', pady=30)
        
#         # 안내 텍스트
#         guide_label = tk.Label(parent, text="📋 프로필 별명과 모든 설정을 완료한 후 '완료' 버튼을 눌러주세요!", 
#                               font=("Arial", 13, "bold"), fg="darkblue")
#         guide_label.pack(pady=20)
        
#         button_frame = tk.Frame(parent)
#         button_frame.pack(pady=30)
        
#         # 버튼들
#         tk.Button(button_frame, text="❌ 취소", width=14, height=3,
#                  font=("Arial", 11), bg="lightcoral",
#                  command=self.cancel_setup).pack(side='left', padx=20)
        
#         tk.Button(button_frame, text="🔍 연결 테스트", width=14, height=3,
#                  font=("Arial", 11), bg="lightblue",
#                  command=self.test_connection).pack(side='left', padx=20)
        
#         # 완료 버튼
#         complete_btn = tk.Button(button_frame, text="✅ 완료", width=14, height=3,
#                                 bg="#4CAF50", fg="white", 
#                                 font=("Arial", 14, "bold"),
#                                 command=self.create_env)
#         complete_btn.pack(side='left', padx=20)
        
#         # 완료 버튼 설명
#         complete_info = tk.Label(parent, text="완료 버튼 클릭 → 프로필별 .env 파일 생성 → main_upload.py 실행 가능", 
#                                 font=("Arial", 10), fg="darkgreen")
#         complete_info.pack(pady=15)
        
#         # 추가 여백 공간 (스크롤을 위해)
#         tk.Label(parent, text="", height=3).pack()
    
#     def cancel_setup(self):
#         result = messagebox.askyesno("설정 취소", "설정을 취소하고 창을 닫으시겠습니까?")
#         if result:
#             self.root.quit()
    
#     def test_connection(self):
#         token = self.token_entry.get().strip()
#         username = self.username_entry.get().strip()
#         repo_name = self.repo_entry.get().strip()
        
#         if not all([token, username, repo_name]):
#             messagebox.showwarning("입력 오류", "토큰, 사용자명, 저장소명을 모두 입력해주세요.")
#             return
        
#         self.status_label.config(text="🔍 연결 테스트 중...", fg="orange")
#         self.root.update()
        
#         # 토큰 검증
#         token_valid, token_msg = self.env_generator.validate_token(token)
#         if not token_valid:
#             self.status_label.config(text="❌ 토큰 오류", fg="red")
#             messagebox.showerror("토큰 오류", token_msg)
#             return
        
#         # 저장소 검증
#         repo_valid, repo_msg = self.env_generator.validate_repository(token, username, repo_name)
#         if not repo_valid:
#             self.status_label.config(text="❌ 저장소 오류", fg="red")
#             messagebox.showerror("저장소 오류", repo_msg)
#             return
        
#         self.status_label.config(text="✅ 연결 테스트 성공!", fg="green")
#         messagebox.showinfo("테스트 성공", "GitHub 연결이 정상적으로 확인되었습니다!")
    
#     def create_env(self):
#         print("\n🚀 환경설정 완료 버튼 클릭됨!")
        
#         # 🔧 프로필 별명 검증 추가
#         profile_name = self.profile_name.get().strip()
#         if not profile_name:
#             messagebox.showwarning("입력 오류", "프로필 별명을 입력해주세요.")
#             self.profile_entry.focus()
#             return
        
#         # 입력값 가져오기
#         token = self.token_entry.get().strip()
#         username = self.username_entry.get().strip()
#         repo_name = self.repo_entry.get().strip()
#         folder_path = self.folder_entry.get().strip()
        
#         upload_mode = self.upload_mode.get()
#         schedule_hour = None
#         schedule_minute = None
#         repeat_option = self.repeat_option.get()
        
#         # 파일 형식 가져오기
#         file_extensions = self.file_extensions.get().strip()
        
#         print(f"📋 수집된 정보:")
#         print(f"   프로필 별명: {profile_name}")  # 🔧 추가
#         print(f"   토큰: {'있음' if token else '없음'}")
#         print(f"   사용자명: {username}")
#         print(f"   저장소: {repo_name}")
#         print(f"   폴더: {folder_path}")
#         print(f"   모드: {upload_mode}")
#         print(f"   파일 형식: {file_extensions}")
        
#         if upload_mode in ["schedule", "hybrid"]:
#             try:
#                 schedule_hour = int(self.hour_var.get())
#                 schedule_minute = int(self.minute_var.get())
#                 print(f"   시간: {schedule_hour:02d}:{schedule_minute:02d}")
#             except ValueError:
#                 messagebox.showerror("오류", "시간과 분은 숫자여야 합니다.")
#                 return
        
#         # 입력값 검증
#         if not token:
#             messagebox.showwarning("입력 오류", "GitHub 토큰을 입력해주세요.")
#             self.token_entry.focus()
#             return
#         if not username:
#             messagebox.showwarning("입력 오류", "GitHub 사용자명을 입력해주세요.")
#             self.username_entry.focus()
#             return
#         if not repo_name:
#             messagebox.showwarning("입력 오류", "저장소 이름을 입력해주세요.")
#             self.repo_entry.focus()
#             return
#         if not folder_path:
#             messagebox.showwarning("입력 오류", "감시할 폴더 경로를 선택해주세요.")
#             self.folder_entry.focus()
#             return
#         if not file_extensions:
#             messagebox.showwarning("입력 오류", "파일 형식을 입력해주세요.")
#             self.extensions_entry.focus()
#             return
        
#         self.status_label.config(text="🔄 프로필 생성 중...", fg="orange")
#         self.root.update()
        
#         # 🔧 .env 파일 생성 (프로필별로)
#         success, message = self.env_generator.create_profile_env_file(
#             profile_name, token, username, repo_name, folder_path, upload_mode, 
#             schedule_hour, schedule_minute, repeat_option, file_extensions
#         )
        
#         if success:
#             self.status_label.config(text="✅ 프로필 생성 완료!", fg="green")
#             result = messagebox.showinfo("🎉 프로필 생성 완료!", 
#                                         f"{message}\n\n"
#                                         f"✅ '{profile_name}' 프로필이 생성되었습니다!\n"
#                                         f"🚀 이제 main_gui.py에서 프로필을 선택하여 업로드하세요!")
#             print("✅ 프로필 생성 완료!")
            
#             # 🔧 프로필 목록 업데이트
#             self.load_existing_profiles()
            
#             self.root.quit()
#         else:
#             self.status_label.config(text="❌ 프로필 생성 실패", fg="red")
#             messagebox.showerror("오류", message)
#             print(f"❌ 오류: {message}")

# if __name__ == "__main__":
#     print("🚀 GitHub 자동 업로드 설정 GUI 시작...")
#     app = GitHubAutoUploadSetup()
#     app.root.mainloop()
#     print("👋 설정 GUI 종료")