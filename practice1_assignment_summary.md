# 실습 1 환경 구성 및 설치 과정 정리

이 문서는 PDF 내용을 그대로 옮긴 요약이 아니라, 이번 과제를 준비하면서 실제로 수행한 설치 과정과 발생한 오류를 기준으로 정리한 기록이다.

대상 프로젝트:

- `C:\Project\인공지능소프트웨어개발및운영파이프라인`
- 과제 폴더: `C:\Project\인공지능소프트웨어개발및운영파이프라인\2week\1_inital SpamCheck`

## 1. 목표

실습 1을 진행할 수 있도록 다음 개발 환경을 만드는 것이 목표였다.

1. 기존 `.venv` 제거
2. 아나콘다 기반 가상환경으로 재구성
3. 프로젝트 내부에 conda 환경 생성
4. `requirements.txt`에 있는 FastAPI 관련 패키지 설치
5. 이후 과제 진행 시 재사용 가능한 실행 환경 확보

## 2. 처음 상태 확인

처음 확인한 결과는 다음과 같았다.

- 프로젝트 루트에 `.venv`가 존재함
- `pyvenv.cfg`가 있어서 일반 Python `venv` 환경이었음
- `conda` 명령은 현재 셸에서 인식되지 않았음
- 프로젝트 안에 `environment.yml`, `conda.yaml`, `.condarc` 같은 conda 설정 파일은 없었음

즉, 처음 상태는 "아나콘다 환경이 구성된 프로젝트"가 아니라 "기존 `.venv` 기반 프로젝트"였다.

## 3. 기존 가상환경 정리

사용자 요청에 따라 기존 `.venv`를 삭제하려고 했는데 바로 삭제되지 않았다.

발생한 문제:

- `.venv\Scripts\python.exe`
- `.venv\Scripts\uvicorn.exe`

위 실행 파일이 다른 프로세스에서 사용 중이어서 삭제가 거부되었다.

원인:

- 이전에 실행했던 Python / uvicorn 프로세스가 살아 있었기 때문

처리 방법:

1. `.venv`를 점유 중인 `python`, `uvicorn` 프로세스를 확인
2. 해당 프로세스를 종료
3. 다시 `.venv` 삭제

결과:

- 기존 `.venv` 삭제 완료

## 4. 아나콘다 설치 과정

처음에는 `conda`가 PATH에 없어서 바로 환경 생성이 불가능했다.

설치 방식:

- `winget`으로 `Anaconda.Anaconda3` 설치

실제 진행 흐름:

1. `winget search anaconda`로 패키지 확인
2. `winget install -e --id Anaconda.Anaconda3 --silent` 실행
3. Anaconda 설치 완료

설치 후 확인:

- `C:\Users\logan\anaconda3` 경로에 설치됨
- `conda.bat`는 `C:\Users\logan\anaconda3\condabin\conda.bat`에 존재

## 5. 설치 중 만난 실제 오류들

### 5-1. `conda` 명령 미인식

증상:

- 처음에는 `conda not found`

원인:

- Anaconda가 설치되지 않았거나, 현재 셸 PATH에 반영되지 않은 상태

대응:

- Anaconda를 먼저 설치
- 이후 `conda.bat`의 절대경로를 사용해 실행

### 5-2. 샌드박스에서 `conda.bat` 실행 시 Access is denied

증상:

- `Access is denied.`

원인:

- 현재 작업 환경의 샌드박스 권한으로는 직접 실행이 제한됨

대응:

- 권한 상승 방식으로 `conda.bat` 실행

### 5-3. Anaconda 채널 ToS 미승인 오류

증상:

- `CondaToSNonInteractiveError`

메시지 핵심:

- `https://repo.anaconda.com/pkgs/main`
- `https://repo.anaconda.com/pkgs/r`
- `https://repo.anaconda.com/pkgs/msys2`

위 채널의 Terms of Service를 먼저 승인하라는 오류가 발생했다.

원인:

- 새로 설치한 Anaconda에서 기본 채널 사용 전 약관 승인이 필요했기 때문

대응:

- `conda tos accept --override-channels --channel ...` 명령으로 각 채널 약관 승인

### 5-4. `environment.yml`로 env 생성 시 named env가 만들어진 문제

처음에는 `environment.yml`에 `name`과 `prefix`를 함께 둔 상태에서 `conda env create -f environment.yml`을 사용했다.

결과:

- 프로젝트 내부 `.conda-env`가 아니라
- `C:\Users\logan\anaconda3\envs\ai-pipeline-spamcheck`

같은 named env가 먼저 생성되었다.

원인:

- conda가 `prefix`보다 `name` 기반으로 처리한 것으로 보임

대응:

1. 생성된 named env 제거
2. 프로젝트 내부 경로 기준으로 다시 생성 시도

### 5-5. 한글 경로 문제로 conda가 환경 파일을 읽지 못함

가장 큰 문제는 프로젝트 경로에 한글이 포함되어 있다는 점이었다.

프로젝트 경로:

- `C:\Project\인공지능소프트웨어개발및운영파이프라인`

증상 1:

- `EnvironmentLocationNotFound`

증상 2:

- `cp949` 인코딩 관련 오류

예:

- `UnicodeEncodeError`
- `cp949 codec can't decode ...`

원인:

- conda가 환경 생성 과정에서 한글 경로를 안정적으로 처리하지 못함
- 특히 `environment.yml` 읽기와 PowerShell 초기화 단계에서 인코딩 문제가 발생함

### 5-6. `conda init powershell` 중 Unicode 오류

증상:

- `UnicodeEncodeError: 'cp949' codec can't encode ...`

원인:

- PowerShell 초기화 메시지 출력 과정에서 한글 경로가 포함되며 인코딩 문제가 발생한 것으로 보임

영향:

- `conda init powershell`이 완전히 깔끔하게 끝나지 않음

대응:

- `conda-hook.ps1`를 직접 호출하는 방식으로 우회

## 6. 한글 경로 문제를 해결한 실제 방법

한글 경로 문제를 피하기 위해 프로젝트를 가리키는 ASCII 경로 조인트를 만들었다.

생성한 조인트:

- `C:\Project\aipipeline_ascii`

이 조인트는 실제로 아래 프로젝트를 가리킨다.

- `C:\Project\인공지능소프트웨어개발및운영파이프라인`

이 방법을 쓴 이유:

- 실제 프로젝트 위치는 유지
- conda는 ASCII 경로를 통해 접근
- 결과적으로 생성된 `.conda-env`는 원래 프로젝트 내부에 보이도록 유지 가능

## 7. 최종적으로 성공한 conda 환경 구성 방법

`environment.yml`만으로는 한글 경로 문제 때문에 안정적으로 생성되지 않았다.

그래서 최종적으로 성공한 방식은 다음과 같다.

1. ASCII 조인트 경로 사용
2. `conda create -p` 방식으로 직접 환경 생성

실제 성공한 개념은 다음과 같다.

```powershell
conda create -p C:\Project\aipipeline_ascii\.conda-env python=3.10 pip git -y
```

이 방식으로 프로젝트 내부에 로컬 conda 환경이 생성되었다.

최종 생성 위치:

- `C:\Project\인공지능소프트웨어개발및운영파이프라인\.conda-env`

확인된 항목:

- Python 3.10.20
- `.conda-env` 내부에 `git.exe` 존재

## 8. requirements 설치 과정

과제 폴더의 요구 패키지는 아래 파일에 정리해 두었다.

- `2week\1_inital SpamCheck\requirements.txt`

내용:

- `fastapi`
- `uvicorn[standard]`
- `python-multipart`

주의:

- `git`은 pip 패키지로 설치하는 항목이 아니라 conda 환경 의존성으로 넣었다.

설치 시에도 한글 경로 문제를 피하기 위해 ASCII 경로를 사용했다.

실제 성공한 흐름:

```powershell
conda run -p C:\Project\aipipeline_ascii\.conda-env python -m pip install -r "C:\Project\aipipeline_ascii\2week\1_inital SpamCheck\requirements.txt"
```

설치 후 import 검증 결과:

- `fastapi 0.135.1`
- `uvicorn 0.41.0`
- `python-multipart 0.0.22`

## 9. 현재 실습 1 실행 방법

현재 가장 안정적인 실행 방법은 아래와 같다.

```powershell
cd "C:\Project\인공지능소프트웨어개발및운영파이프라인"
& "C:\Users\logan\anaconda3\shell\condabin\conda-hook.ps1"
conda activate C:\Project\aipipeline_ascii\.conda-env
cd "C:\Project\인공지능소프트웨어개발및운영파이프라인\2week\1_inital SpamCheck"
uvicorn app.main:app --reload
```

접속 주소:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## 10. 이번 설치 과정에서 중요하게 배운 점

### 10-1. 한글 경로는 conda에서 실제 문제를 만들 수 있다

이번 과정에서 가장 큰 장애 요인은 한국어 폴더명이 포함된 프로젝트 경로였다.

겉보기에는 경로가 정상이어도, 실제로는 아래 문제가 발생했다.

- 환경 생성 실패
- `environment.yml` 읽기 실패
- PowerShell 초기화 중 인코딩 오류

### 10-2. `environment.yml`만 믿으면 안 되는 경우가 있다

일반적으로는 `conda env create -f environment.yml`이면 충분하지만, 이번처럼 경로/인코딩 문제가 있으면 오히려 직접 `conda create -p`가 더 안정적이었다.

### 10-3. 설치 오류는 단계별로 끊어서 원인을 봐야 한다

이번 설치에서는 다음 문제들이 순서대로 분리되어 있었다.

1. conda 없음
2. 설치 후 PATH 미반영
3. 채널 ToS 미승인
4. 한글 경로 문제
5. `environment.yml` 처리 실패
6. `conda-hook.ps1` 우회 사용

즉, 한 번에 해결된 것이 아니라 문제를 하나씩 분리해서 처리해야 했다.

## 11. 현재 남아 있는 주의사항

환경 설치는 끝났지만, 과제 코드 자체에는 별도 문제점이 남아 있다.

- 빈 문자열 입력 시 `check_spam()` 반환 형식이 깨질 수 있음
- `static` 경로를 상대경로로 처리해서 실행 위치에 의존함
- 코드 일부 한글이 깨져 있음

이 부분은 "환경 설치 문제"와 "애플리케이션 코드 문제"를 구분해서 봐야 한다.

## 12. 최종 정리

이번 실습 1 준비 과정에서 가장 큰 문제는 "아나콘다 자체 설치"보다 "프로젝트 경로에 포함된 한글"이었다.

최종적으로는 다음 방식으로 해결했다.

1. 기존 `.venv` 삭제
2. Anaconda 설치
3. 채널 ToS 승인
4. ASCII 조인트 경로 생성
5. `conda create -p`로 프로젝트 내부 `.conda-env` 생성
6. 해당 환경에 `requirements.txt` 설치
7. FastAPI 서버 실행 확인

즉, 이번 과제 환경 구성은 단순 설치가 아니라 "경로 인코딩 문제를 우회하면서 로컬 conda 환경을 만드는 과정"이었다.
