import os
import pandas as pd
from datetime import datetime
from typing import Optional, List
from app import db, cache
from app.config import Config
from app.models.fire import Fire
from app.utils.logger import log_error

class ExportService:
    ALLOWED_FORMATS = ['csv', 'xlsx']
    
    def __init__(self):
        self._ensure_export_directory()
    
    def _ensure_export_directory(self) -> None:
        """Создание директории для экспорта если не существует"""
        if not os.path.exists(Config.EXPORT_FOLDER):
            os.makedirs(Config.EXPORT_FOLDER)
    
    @cache.memoize(timeout=300)
    def get_fires_data(self, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> List[Fire]:
        """Получение данных о пожарах с кэшированием"""
        query = Fire.query
        
        if start_date:
            query = query.filter(Fire.date >= start_date)
        if end_date:
            query = query.filter(Fire.date <= end_date)
            
        return query.all()
    
    def export_fires(self, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, 
                    format: str = 'csv') -> str:
        """
        Экспорт данных о пожарах
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            format: Формат файла (csv или xlsx)
        Returns:
            str: Путь к экспортированному файлу
        """
        try:
            if format not in self.ALLOWED_FORMATS:
                raise ValueError(f"Неподдерживаемый формат: {format}")
            
            fires = self.get_fires_data(start_date, end_date)
            
            df = pd.DataFrame([{
                'Дата пожара': fire.date,
                'Регион': fire.region,
                'КГУ/ООПТ': fire.kgu_oopt,
                'Филиал': fire.branch,
                'Площадь пожара': fire.area,
                'Площадь лесная': fire.forest_area,
                'Ущерб': fire.damage,
                'Затраты': fire.costs
            } for fire in fires])
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'fires_export_{timestamp}.{format}'
            filepath = os.path.join(Config.EXPORT_FOLDER, filename)
            
            if format == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            else:
                df.to_excel(filepath, index=False)
            
            return filepath
            
        except Exception as e:
            log_error(f"Ошибка при экспорте: {str(e)}")
            raise