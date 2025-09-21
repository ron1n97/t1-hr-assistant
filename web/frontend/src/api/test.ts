// Простой тест для проверки API
import { apiClient } from './client';

export async function testAPI() {
  try {
    console.log('Тестирование API...');
    
    // Проверяем health endpoint
    const health = await apiClient.getHealth();
    console.log('Health check:', health);
    
    // Проверяем agents endpoint
    const agents = await apiClient.getAgents();
    console.log('Agents info:', agents);
    
    // Тестируем user chat
    const userResponse = await apiClient.sendUserMessage('Привет! Как дела?');
    console.log('User chat response:', userResponse);
    
    // Тестируем HR chat
    const hrResponse = await apiClient.sendHRMessage('Найди кандидатов на позицию разработчика');
    console.log('HR chat response:', hrResponse);
    
    console.log('Все тесты прошли успешно!');
  } catch (error) {
    console.error('Ошибка при тестировании API:', error);
  }
}

// Экспортируем для использования в консоли браузера
(window as any).testAPI = testAPI;
