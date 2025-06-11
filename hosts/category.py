from enum import Enum
import httpx


# 1. 카테고리 Enum 정의
class Category(Enum):
    MT1 = "대형마트"
    CS2 = "편의점"
    PS3 = "어린이집, 유치원"
    SC4 = "학교"
    AC5 = "학원"
    PK6 = "주차장"
    OL7 = "주유소, 충전소"
    SW8 = "지하철역"
    BK9 = "은행"
    CT1 = "문화시설"
    AG2 = "중개업소"
    PO3 = "공공기관"
    AT4 = "관광명소"
    AD5 = "숙박"
    FD6 = "음식점"
    CE7 = "카페"
    HP8 = "병원"
    PM9 = "약국"

    @classmethod
    def get_category_code(cls, category_name: str) -> str:
        """한글 카테고리명으로 매핑되는 코드 값을 반환"""
        for category in cls:
            if category.value == category_name:
                return category.name
        return category_name