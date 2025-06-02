#!/usr/bin/env python3
import sys
from pathlib import Path
from speech_transcribe_gui import main as gui_main

def main() -> None:
    try:
        # 프로젝트 루트 경로 설정
        project_root = Path(__file__).parent
        sys.path.append(str(project_root))
        
        # GUI 실행
        gui_main()
        
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 