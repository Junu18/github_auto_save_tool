# main_upload.py - 실시간 파일 삭제 감지 포함 완전 버전
import time
import requests
import base64
import os
import json
import schedule
import threading
import glob
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 전역 변수들
GITHUB_TOKEN = None
GITHUB_USERNAME = None
REPO_NAME = None
WATCH_FOLDER_PATH = None
UPLOAD_MODE = None
SCHEDULE_HOUR = None
SCHEDULE_MINUTE = None
REPEAT_OPTION = None
BRANCH = None
FILE_EXTENSIONS = None

def check_env_config():
    """환경 설정 확인"""
    if not GITHUB_TOKEN:
        print("❌ .env 파일에 GITHUB_TOKEN이 설정되지 않았습니다!")
        print("💡 setup_gui.py를 먼저 실행해서 설정을 완료해주세요.")
        return False
    
    required_vars = [GITHUB_USERNAME, REPO_NAME, WATCH_FOLDER_PATH]
    if not all(required_vars):
        print("❌ .env 파일의 설정이 불완전합니다!")
        print("💡 setup_gui.py를 다시 실행해서 설정을 완료해주세요.")
        return False
    
    if not os.path.exists(WATCH_FOLDER_PATH):
        print(f"❌ 감시할 폴더가 존재하지 않습니다: {WATCH_FOLDER_PATH}")
        return False
    
    return True

def upload_file_to_github(local_file_path):
    """GitHub에 파일 업로드 (이모티콘 커밋 메시지 포함)"""
    print(" " * 50, end='\r')
    print(f"\n📄 감지된 파일: {os.path.basename(local_file_path)}")
    
    repo_file_path = os.path.basename(local_file_path)
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{repo_file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        with open(local_file_path, "rb") as file:
            content_encoded = base64.b64encode(file.read()).decode('utf-8')
    except (FileNotFoundError, PermissionError) as e:
        print(f"  ❌ 파일 읽기 실패: {e}")
        return False
    
    # 기존 파일 확인 및 커밋 메시지 결정
    sha = None
    is_update = False
    try:
        response_get = requests.get(url, headers=headers)
        if response_get.status_code == 200:
            sha = response_get.json().get('sha')
            is_update = True
    except requests.exceptions.RequestException:
        pass
    
    # 이모티콘 커밋 메시지 설정
    if is_update:
        commit_message = f"🔄 Update {repo_file_path}"
        action_emoji = "🔄"
        action_text = "업데이트"
    else:
        commit_message = f"➕ Add {repo_file_path}"
        action_emoji = "➕"
        action_text = "추가"
    
    # 업로드 데이터 준비
    data = {
        "message": commit_message,
        "content": content_encoded
    }
    if sha:
        data["sha"] = sha
    
    print(f"  🚀 {action_text} 업로드를 시도합니다...")
    try:
        response_put = requests.put(url, headers=headers, data=json.dumps(data))
        if response_put.status_code in [200, 201]:
            print(f"  ✅ {action_emoji} {repo_file_path} {action_text} 성공!")
            return True
        else:
            print(f"  ❌ {repo_file_path} 업로드 실패! (상태 코드: {response_put.status_code})")
            error_msg = response_put.json().get('message', 'Unknown error')
            print(f"     오류 내용: {error_msg}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ {repo_file_path} 네트워크 오류: {e}")
        return False

def get_github_files():
    """GitHub 저장소의 파일 목록 가져오기"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            files_data = response.json()
            # 파일만 필터링 (폴더 제외)
            github_files = {}
            for item in files_data:
                if item['type'] == 'file':
                    github_files[item['name']] = item['sha']
            return github_files
        else:
            print(f"⚠️ GitHub 파일 목록 가져오기 실패: {response.status_code}")
            return {}
    except Exception as e:
        print(f"⚠️ GitHub 파일 목록 가져오기 오류: {e}")
        return {}

def get_local_files():
    """로컬 폴더의 파일 목록 가져오기"""
    try:
        # 환경변수에서 파일 형식 읽어오기
        file_extensions_str = os.getenv('FILE_EXTENSIONS', 'py,txt,md,json,js,html,css')
        file_extensions_list = [ext.strip() for ext in file_extensions_str.split(',')]
        file_patterns = [f'*.{ext}' for ext in file_extensions_list]
        
        local_files = set()
        for pattern in file_patterns:
            files = glob.glob(os.path.join(WATCH_FOLDER_PATH, pattern))
            for file_path in files:
                if os.path.isfile(file_path):
                    local_files.add(os.path.basename(file_path))
        
        return local_files
    except Exception as e:
        print(f"⚠️ 로컬 파일 목록 가져오기 오류: {e}")
        return set()

def delete_file_from_github(filename, sha):
    """GitHub에서 파일 삭제"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{filename}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        # 삭제 데이터 준비
        data = {
            "message": f"🗑️ Delete {filename}",
            "sha": sha
        }
        
        print(f"  🗑️ {filename} 삭제를 시도합니다...")
        response = requests.delete(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print(f"  ✅ 🗑️ {filename} 삭제 성공!")
            return True
        else:
            print(f"  ❌ {filename} 삭제 실패! (상태 코드: {response.status_code})")
            error_msg = response.json().get('message', 'Unknown error')
            print(f"     오류 내용: {error_msg}")
            return False
    except Exception as e:
        print(f"  ❌ {filename} 삭제 오류: {e}")
        return False

def sync_deleted_files():
    """삭제된 파일들을 GitHub에서도 제거"""
    print(f"\n🔍 삭제된 파일 동기화 확인 중...")
    
    # GitHub와 로컬 파일 목록 가져오기
    github_files = get_github_files()  # {filename: sha}
    local_files = get_local_files()    # {filename}
    
    if not github_files:
        print("📂 GitHub 저장소가 비어있거나 파일 목록을 가져올 수 없습니다.")
        return
    
    # GitHub에만 있고 로컬에 없는 파일들 찾기
    files_to_delete = []
    for github_file, sha in github_files.items():
        if github_file not in local_files:
            files_to_delete.append((github_file, sha))
    
    if not files_to_delete:
        print("🔄 삭제할 파일이 없습니다. 모든 파일이 동기화되어 있습니다.")
        return
    
    print(f"🗑️ {len(files_to_delete)}개의 삭제된 파일을 발견했습니다.")
    for filename, _ in files_to_delete:
        print(f"   📄 {filename} (로컬에서 삭제됨)")
    
    # 삭제 실행
    deleted = 0
    failed = 0
    for filename, sha in files_to_delete:
        success = delete_file_from_github(filename, sha)
        if success:
            deleted += 1
        else:
            failed += 1
        time.sleep(0.5)  # API 제한 방지
    
    # 결과 출력
    if failed == 0:
        print(f"\n🎉 파일 삭제 동기화 완료! 🗑️ {deleted}개 파일 모두 삭제됨")
    else:
        print(f"\n🎉 파일 삭제 동기화 완료! 🗑️ {deleted}개 삭제 성공, ❌ {failed}개 실패")
    
    print("=" * 60)

def upload_existing_files():
    """프로그램 시작 시 기존 파일들을 자동으로 업로드하고 삭제된 파일 동기화"""
    print(f"\n📂 기존 파일 확인 중...")
    
    # 환경변수에서 파일 형식 읽어오기
    file_extensions_str = os.getenv('FILE_EXTENSIONS', 'py,txt,md,json,js,html,css')
    file_extensions_list = [ext.strip() for ext in file_extensions_str.split(',')]
    file_patterns = [f'*.{ext}' for ext in file_extensions_list]
    
    print(f"📋 지원 파일 형식: {', '.join(file_extensions_list)}")
    
    files = []
    for pattern in file_patterns:
        files.extend(glob.glob(os.path.join(WATCH_FOLDER_PATH, pattern)))
    
    if not files:
        print("📁 기존 파일이 없습니다.")
    else:
        print(f"🔍 {len(files)}개의 기존 파일을 발견했습니다.")
        print("📤 자동으로 기존 파일들을 업로드합니다...")
        
        uploaded = 0
        failed = 0
        for file_path in files:
            if os.path.isfile(file_path):
                print(f"\n📄 기존 파일 처리: {os.path.basename(file_path)}")
                success = upload_file_to_github(file_path)
                if success:
                    uploaded += 1
                else:
                    failed += 1
                time.sleep(1)  # API 제한 방지
        
        # 업로드 결과
        if failed == 0:
            print(f"\n🎉 기존 파일 업로드 완료! ✅ {uploaded}개 파일 모두 성공")
        else:
            print(f"\n🎉 기존 파일 업로드 완료! ✅ {uploaded}개 성공, ❌ {failed}개 실패")
    
    # 삭제된 파일 동기화 추가
    sync_deleted_files()

def scheduled_upload():
    """예약된 시간에 실행되는 업로드 함수 (삭제 동기화 포함)"""
    print(f"\n⏰ 예약 업로드 시작: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 환경변수에서 파일 형식 읽어오기
    file_extensions_str = os.getenv('FILE_EXTENSIONS', 'py,txt,md,json,js,html,css')
    file_extensions_list = [ext.strip() for ext in file_extensions_str.split(',')]
    file_patterns = [f'*.{ext}' for ext in file_extensions_list]
    
    print(f"📋 지원 파일 형식: {', '.join(file_extensions_list)}")
    
    files = []
    for pattern in file_patterns:
        files.extend(glob.glob(os.path.join(WATCH_FOLDER_PATH, pattern)))
    
    if not files:
        print("📂 업로드할 파일이 없습니다.")
    else:
        print(f"📁 {len(files)}개 파일을 업로드합니다.")
        uploaded = 0
        failed = 0
        
        for file_path in files:
            if os.path.isfile(file_path):
                success = upload_file_to_github(file_path)
                if success:
                    uploaded += 1
                else:
                    failed += 1
                time.sleep(1)  # API 제한 방지
        
        # 업로드 결과
        if failed == 0:
            print(f"\n🎉 예약 업로드 완료! ✅ {uploaded}개 파일 모두 성공")
        else:
            print(f"\n🎉 예약 업로드 완료! ✅ {uploaded}개 성공, ❌ {failed}개 실패")
    
    # 삭제된 파일 동기화 추가
    sync_deleted_files()

def setup_scheduler():
    """스케줄러 설정"""
    schedule_time = f"{SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}"
    
    if REPEAT_OPTION == "daily":
        schedule.every().day.at(schedule_time).do(scheduled_upload)
        print(f"📅 매일 {schedule_time}에 업로드 예약됨")
    elif REPEAT_OPTION == "weekdays":
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            getattr(schedule.every(), day).at(schedule_time).do(scheduled_upload)
        print(f"📅 평일 {schedule_time}에 업로드 예약됨")
    elif REPEAT_OPTION == "weekends":
        schedule.every().saturday.at(schedule_time).do(scheduled_upload)
        schedule.every().sunday.at(schedule_time).do(scheduled_upload)
        print(f"📅 주말 {schedule_time}에 업로드 예약됨")

def run_scheduler():
    """스케줄러 실행 (별도 쓰레드)"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

# 🔧 실시간 파일 삭제 감지 포함 이벤트 핸들러
class FileEventHandler(FileSystemEventHandler):
    """파일 시스템 이벤트 핸들러 (삭제 감지 포함)"""
    def on_created(self, event):
        if not event.is_directory:
            # 파일 형식 체크
            file_ext = os.path.splitext(event.src_path)[1][1:]  # 확장자 추출 (점 제거)
            if self.is_supported_file(file_ext):
                print(f"\n➕ 새 파일 감지: {os.path.basename(event.src_path)}")
                upload_file_to_github(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            # 파일 형식 체크
            file_ext = os.path.splitext(event.src_path)[1][1:]  # 확장자 추출 (점 제거)
            if self.is_supported_file(file_ext):
                print(f"\n🔄 파일 수정 감지: {os.path.basename(event.src_path)}")
                time.sleep(1)  # 파일 쓰기 완료 대기
                upload_file_to_github(event.src_path)
    
    # 🔧 새로 추가: 파일 삭제 실시간 감지
    def on_deleted(self, event):
        if not event.is_directory:
            # 파일 형식 체크
            file_ext = os.path.splitext(event.src_path)[1][1:]  # 확장자 추출 (점 제거)
            if self.is_supported_file(file_ext):
                filename = os.path.basename(event.src_path)
                print(f"\n🗑️ 파일 삭제 감지: {filename}")
                self.handle_file_deletion(filename)
    
    def handle_file_deletion(self, filename):
        """삭제된 파일을 GitHub에서도 제거"""
        try:
            # GitHub에서 파일 정보 가져오기 (sha 필요)
            url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{filename}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                file_data = response.json()
                sha = file_data.get('sha')
                
                if sha:
                    success = delete_file_from_github(filename, sha)
                    if success:
                        print(f"  ✅ 실시간 삭제 완료: {filename}")
                    else:
                        print(f"  ❌ 실시간 삭제 실패: {filename}")
                else:
                    print(f"  ⚠️ {filename}의 SHA를 가져올 수 없습니다.")
            elif response.status_code == 404:
                print(f"  ℹ️ {filename}는 이미 GitHub에 없습니다.")
            else:
                print(f"  ⚠️ {filename} 정보 조회 실패: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {filename} 삭제 처리 중 오류: {e}")
    
    def is_supported_file(self, file_ext):
        """지원되는 파일 형식인지 확인"""
        file_extensions_str = os.getenv('FILE_EXTENSIONS', 'py,txt,md,json,js,html,css')
        supported_extensions = [ext.strip() for ext in file_extensions_str.split(',')]
        return file_ext.lower() in supported_extensions

def run_upload_system():
    """메인 업로드 시스템 실행 함수 (GUI에서 호출용)"""
    global GITHUB_TOKEN, GITHUB_USERNAME, REPO_NAME, WATCH_FOLDER_PATH
    global UPLOAD_MODE, SCHEDULE_HOUR, SCHEDULE_MINUTE, REPEAT_OPTION, BRANCH, FILE_EXTENSIONS
    
    print("🚀 GitHub 자동 업로드 시스템 시작!")
    print("=" * 60)
    
    # .env 파일 로드
    load_dotenv()
    
    # 설정 값 로드
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    REPO_NAME = os.getenv('GITHUB_REPO')
    WATCH_FOLDER_PATH = os.getenv('WATCH_FOLDER')
    UPLOAD_MODE = os.getenv('UPLOAD_MODE', 'realtime')
    SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 14))
    SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', 30))
    REPEAT_OPTION = os.getenv('REPEAT_OPTION', 'daily')
    BRANCH = os.getenv('BRANCH', 'main')
    FILE_EXTENSIONS = os.getenv('FILE_EXTENSIONS', 'py,txt,md,json,js,html,css')
    
    # 환경 설정 확인
    if not check_env_config():
        print("❌ 설정이 올바르지 않습니다!")
        return False
    
    print(f"✅ 설정 로드 완료!")
    print(f"📍 사용자: {GITHUB_USERNAME}")
    print(f"📂 저장소: {REPO_NAME}")
    print(f"👀 감시 폴더: {WATCH_FOLDER_PATH}")
    print(f"🔧 업로드 모드: {UPLOAD_MODE}")
    print(f"📄 지원 파일 형식: {FILE_EXTENSIONS}")
    
    # 기존 파일 자동 업로드 + 삭제 동기화
    upload_existing_files()
    
    # 실시간 감시 시작
    observer = None
    if UPLOAD_MODE in ["realtime", "hybrid"]:
        if not os.path.exists(WATCH_FOLDER_PATH):
            os.makedirs(WATCH_FOLDER_PATH)
            print(f"📁 감시 폴더를 생성했습니다: {WATCH_FOLDER_PATH}")
        
        event_handler = FileEventHandler()
        observer = Observer()
        observer.schedule(event_handler, WATCH_FOLDER_PATH, recursive=False)
        observer.start()
        print("🔄 실시간 파일 감시 시작! (추가/수정/삭제 모두 감지)")  # 🔧 메시지 업데이트
    
    # 스케줄러 시작
    if UPLOAD_MODE in ["schedule", "hybrid"]:
        setup_scheduler()
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    print("=" * 60)
    print("📂 GitHub 자동 업로드 시스템이 실행 중입니다...")
    print("💡 감시 폴더에서 파일을 추가/수정/삭제하면 자동으로 GitHub에 반영됩니다.")  # 🔧 메시지 업데이트
    
    return True

if __name__ == "__main__":
    # .env 파일 로드
    load_dotenv()
    
    # 설정 값 로드
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    REPO_NAME = os.getenv('GITHUB_REPO')
    WATCH_FOLDER_PATH = os.getenv('WATCH_FOLDER')
    UPLOAD_MODE = os.getenv('UPLOAD_MODE', 'realtime')
    SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 14))
    SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', 30))
    REPEAT_OPTION = os.getenv('REPEAT_OPTION', 'daily')
    BRANCH = os.getenv('BRANCH', 'main')
    FILE_EXTENSIONS = os.getenv('FILE_EXTENSIONS', 'py,txt,md,json,js,html,css')
    
    # 환경 설정 확인
    if not check_env_config():
        input("⏸️ 아무 키나 눌러서 종료...")
        exit(1)
    
    print(f"✅ 설정 로드 완료!")
    print(f"📍 사용자: {GITHUB_USERNAME}")
    print(f"📂 저장소: {REPO_NAME}")
    print(f"👀 감시 폴더: {WATCH_FOLDER_PATH}")
    print(f"🔧 업로드 모드: {UPLOAD_MODE}")
    print(f"📄 지원 파일 형식: {FILE_EXTENSIONS}")
    
    # 기존 파일 자동 업로드 + 삭제 동기화
    upload_existing_files()
    
    # 실시간 감시 시작
    observer = None
    if UPLOAD_MODE in ["realtime", "hybrid"]:
        if not os.path.exists(WATCH_FOLDER_PATH):
            os.makedirs(WATCH_FOLDER_PATH)
            print(f"📁 감시 폴더를 생성했습니다: {WATCH_FOLDER_PATH}")
        
        event_handler = FileEventHandler()
        observer = Observer()
        observer.schedule(event_handler, WATCH_FOLDER_PATH, recursive=False)
        observer.start()
        print("🔄 실시간 파일 감시 시작! (추가/수정/삭제 모두 감지)")
    
    # 스케줄러 시작
    if UPLOAD_MODE in ["schedule", "hybrid"]:
        setup_scheduler()
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    print("=" * 60)
    print("📂 GitHub 자동 업로드 시스템이 실행 중입니다...")
    print("💡 감시 폴더에서 파일을 추가/수정/삭제하면 자동으로 GitHub에 반영됩니다.")
    print("(Ctrl+C를 눌러서 종료)")
    
    # 상태 표시
    spinner = ['|', '/', '-', '\\']
    i = 0
    
    try:
        while True:
            mode_text = {
                "realtime": "실시간 감시 (추가/수정/삭제)",
                "schedule": f"예약 업로드 ({SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d})",
                "hybrid": f"실시간 + 예약 ({SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d})"
            }
            
            print(f"  👀 {mode_text.get(UPLOAD_MODE, '감시')} 중... {spinner[i % len(spinner)]}", 
                  end='\r', flush=True)
            i += 1
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        if observer:
            observer.stop()
        print("\n🛑 시스템을 종료합니다...")
        
    if observer:
        observer.join()
    
    print("👋 GitHub 자동 업로드 시스템이 종료되었습니다.")