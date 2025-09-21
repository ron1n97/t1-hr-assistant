"""
API endpoints для работы с профилем пользователя
"""
import json
import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

from .profile_schema import UserProfile, Material, LEARNING_MATERIALS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user/profile", tags=["user-profile"])

# Путь к файлу профиля пользователя
PROFILE_FILE_PATH = "user_profile.json"


class ProfileResponse(BaseModel):
    profile: Optional[UserProfile] = None
    is_complete: bool = False
    completion_percentage: float = 0.0


class ProfileUpdateRequest(BaseModel):
    profile: UserProfile


class MaterialSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    level: Optional[str] = None
    material_type: Optional[str] = None


class MaterialSearchResponse(BaseModel):
    materials: list[Material]
    total_count: int


def get_profile_file_path() -> str:
    """Получает путь к файлу профиля"""
    return PROFILE_FILE_PATH


def load_user_profile() -> Optional[UserProfile]:
    """Загружает профиль пользователя из файла"""
    try:
        profile_path = get_profile_file_path()
        if not os.path.exists(profile_path):
            logger.info("Файл профиля не найден, создаем новый профиль")
            return None
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
            profile = UserProfile(**profile_data)
            logger.info(f"Профиль загружен: {profile.get_completion_percentage():.1f}% заполнен")
            return profile
    except Exception as e:
        logger.error(f"Ошибка при загрузке профиля: {e}")
        return None


def save_user_profile(profile: UserProfile) -> bool:
    """Сохраняет профиль пользователя в файл"""
    try:
        profile_path = get_profile_file_path()
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile.dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Профиль сохранен: {profile.get_completion_percentage():.1f}% заполнен")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении профиля: {e}")
        return False


def create_empty_profile() -> UserProfile:
    """Создает пустой профиль пользователя"""
    from .profile_schema import BasicInfo, CurrentRole, Education
    
    return UserProfile(
        basicInfo=BasicInfo(
            department="",
            position="",
            grade="",
            itExperience=""
        ),
        currentRole=CurrentRole(
            specialization="",
            functionalRole="",
            responsibilities=[]
        ),
        education=Education(
            institution="",
            degree="bachelor",
            specialization="",
            graduationYear=""
        )
    )


@router.get("/", response_model=ProfileResponse)
async def get_profile():
    """Получает профиль пользователя"""
    try:
        profile = load_user_profile()
        
        if profile is None:
            return ProfileResponse(
                profile=None,
                is_complete=False,
                completion_percentage=0.0
            )
        
        return ProfileResponse(
            profile=profile,
            is_complete=profile.is_complete(),
            completion_percentage=profile.get_completion_percentage()
        )
    except Exception as e:
        logger.error(f"Ошибка при получении профиля: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении профиля: {str(e)}")


@router.post("/", response_model=ProfileResponse)
async def create_or_update_profile(request: ProfileUpdateRequest):
    """Создает или обновляет профиль пользователя"""
    try:
        profile = request.profile
        
        if not save_user_profile(profile):
            raise HTTPException(status_code=500, detail="Ошибка при сохранении профиля")
        
        return ProfileResponse(
            profile=profile,
            is_complete=profile.is_complete(),
            completion_percentage=profile.get_completion_percentage()
        )
    except Exception as e:
        logger.error(f"Ошибка при создании/обновлении профиля: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при создании/обновлении профиля: {str(e)}")


@router.delete("/")
async def delete_profile():
    """Удаляет профиль пользователя"""
    try:
        profile_path = get_profile_file_path()
        if os.path.exists(profile_path):
            os.remove(profile_path)
            logger.info("Профиль пользователя удален")
            return {"message": "Профиль успешно удален"}
        else:
            return {"message": "Профиль не найден"}
    except Exception as e:
        logger.error(f"Ошибка при удалении профиля: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении профиля: {str(e)}")


@router.post("/materials/search", response_model=MaterialSearchResponse)
async def search_materials(request: MaterialSearchRequest):
    """Поиск учебных материалов"""
    try:
        query = request.query.lower()
        materials = LEARNING_MATERIALS.copy()
        
        # Фильтрация по запросу
        if query:
            materials = [
                m for m in materials 
                if (query in m.title.lower() or 
                    query in m.description.lower() or 
                    query in m.category.lower())
            ]
        
        # Фильтрация по категории
        if request.category:
            materials = [
                m for m in materials 
                if m.category.lower() == request.category.lower()
            ]
        
        # Фильтрация по уровню
        if request.level:
            materials = [
                m for m in materials 
                if m.level.value == request.level
            ]
        
        # Фильтрация по типу материала
        if request.material_type:
            materials = [
                m for m in materials 
                if m.type.value == request.material_type
            ]
        
        logger.info(f"Найдено {len(materials)} материалов по запросу: {request.query}")
        
        return MaterialSearchResponse(
            materials=materials,
            total_count=len(materials)
        )
    except Exception as e:
        logger.error(f"Ошибка при поиске материалов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске материалов: {str(e)}")


@router.get("/materials", response_model=MaterialSearchResponse)
async def get_all_materials():
    """Получает все доступные учебные материалы"""
    try:
        return MaterialSearchResponse(
            materials=LEARNING_MATERIALS,
            total_count=len(LEARNING_MATERIALS)
        )
    except Exception as e:
        logger.error(f"Ошибка при получении материалов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении материалов: {str(e)}")


@router.get("/materials/{material_id}")
async def get_material(material_id: str):
    """Получает конкретный учебный материал по ID"""
    try:
        material = next((m for m in LEARNING_MATERIALS if m.id == material_id), None)
        if not material:
            raise HTTPException(status_code=404, detail="Материал не найден")
        return material
    except Exception as e:
        logger.error(f"Ошибка при получении материала {material_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении материала: {str(e)}")


@router.get("/completion-status")
async def get_completion_status():
    """Получает статус заполнения профиля"""
    try:
        profile = load_user_profile()
        
        if profile is None:
            return {
                "is_complete": False,
                "completion_percentage": 0.0,
                "missing_fields": [
                    "department", "position", "grade", "itExperience",
                    "specialization", "functionalRole", "institution", 
                    "specialization", "graduationYear"
                ]
            }
        
        missing_fields = []
        if not profile.basicInfo.department.strip():
            missing_fields.append("department")
        if not profile.basicInfo.position.strip():
            missing_fields.append("position")
        if not profile.basicInfo.grade.strip():
            missing_fields.append("grade")
        if not profile.basicInfo.itExperience.strip():
            missing_fields.append("itExperience")
        if not profile.currentRole.specialization.strip():
            missing_fields.append("specialization")
        if not profile.currentRole.functionalRole.strip():
            missing_fields.append("functionalRole")
        if not profile.education.institution.strip():
            missing_fields.append("institution")
        if not profile.education.specialization.strip():
            missing_fields.append("education_specialization")
        if not profile.education.graduationYear.strip():
            missing_fields.append("graduationYear")
        
        return {
            "is_complete": profile.is_complete(),
            "completion_percentage": profile.get_completion_percentage(),
            "missing_fields": missing_fields
        }
    except Exception as e:
        logger.error(f"Ошибка при получении статуса заполнения: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении статуса заполнения: {str(e)}")
