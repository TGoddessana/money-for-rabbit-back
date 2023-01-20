# SUCCESS
WELCOME_NEWBIE = "{} 님, 회원가입을 환영합니다!"

# FAIL
NOT_FOUND = "{}를 찾을 수 없습니다."
INTERNAL_SERVER_ERROR = "서버 에러로 요청을 처리하지 못했습니다. 관리자에게 문의하세요."
EMAIL_NOT_CONFIRMED = "이메일 인증이 되지 않은 계정입니다."
ACCOUNT_INFORMATION_NOT_MATCH = "이메일과 비밀번호를 확인하세요."
EMAIL_DUPLICATED = "중복된 이메일입니다."
REFRESH_TOKEN_ERROR = "refresh token 은 2회 이상 사용될 수 없습니다."
FORBIDDEN = "권한이 없습니다."


def get_response(status: bool, message: str, status_code: int) -> tuple:
    """응답 성공 여부와 메시지를 받아 적절한 Response 튜플을 반환합니다.

    Args:
        status (bool): 요청의 성공 여부 (true, false)
        message (str): 메시지
        status_code (int): 상태 코드

    Returns:
        tuple: JSON 응답
    """
    if status:
        return {"success": message}, status_code
    else:
        return {"error": message}, status_code
