"""
Middleware для обработки редиректов.
"""
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from .models import Redirect
import logging

logger = logging.getLogger(__name__)


class RedirectMiddleware(MiddlewareMixin):
    """
    Middleware для обработки редиректов старых OJS URL.
    Проверяет полный URL запроса и выполняет редирект если найден в Redirect.
    """
    
    def process_request(self, request):
        """Обрабатывает запрос и проверяет необходимость редиректа."""
        # Получаем полный URL запроса
        full_url = request.build_absolute_uri()
        
        # Ищем редирект
        try:
            redirect_obj = Redirect.objects.filter(
                old_url=full_url,
                is_active=True
            ).first()
            
            if redirect_obj:
                # Логируем событие редиректа
                from .models_extended import Event
                Event.objects.create(
                    object_type='redirect',
                    object_id=redirect_obj.pk,
                    kind='redirect',
                    ip=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    referer=request.META.get('HTTP_REFERER', '')[:500],
                )
                
                # Выполняем редирект
                if redirect_obj.http_status == 301:
                    return HttpResponsePermanentRedirect(redirect_obj.new_path)
                else:
                    return HttpResponseRedirect(redirect_obj.new_path)
        
        except Exception as e:
            logger.error(f"Ошибка в RedirectMiddleware: {e}")
        
        # Продолжаем обработку запроса
        return None

