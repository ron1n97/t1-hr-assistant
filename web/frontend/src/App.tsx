import { useState } from 'react';
import { Navigation } from './components/Navigation';
import { ProfileForm } from './components/ProfileForm';
import { ChatPage } from './components/ChatPage';
import { MaterialsPage } from './components/MaterialsPage';
import { SkillTreePage } from './components/SkillTreePage';
import { HRApp } from './components/HRApp';
import { Button } from './components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card';
import { Users, UserCheck } from 'lucide-react';

export default function App() {
  const [appMode, setAppMode] = useState<'employee' | 'hr' | 'selector'>('selector');
  const [currentPage, setCurrentPage] = useState('profile');

  if (appMode === 'selector') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="max-w-2xl w-full space-y-6">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4">HR Система Управления Талантами</h1>
            <p className="text-muted-foreground">
              Выберите режим работы с системой
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow" 
                  onClick={() => setAppMode('employee')}>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <Users className="w-8 h-8 text-blue-600" />
                  Профиль сотрудника
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Заполните анкету профиля, управляйте навыками, получайте рекомендации по развитию карьеры
                </p>
                <ul className="text-sm space-y-1">
                  <li>• Создание профиля сотрудника</li>
                  <li>• Чат с ИИ-помощником</li>
                  <li>• Материалы для обучения</li>
                  <li>• Дерево навыков и компетенций</li>
                </ul>
                <Button className="w-full mt-4">
                  Войти как сотрудник
                </Button>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-lg transition-shadow" 
                  onClick={() => setAppMode('hr')}>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <UserCheck className="w-8 h-8 text-green-600" />
                  HR Личный кабинет
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Управляйте кандидатами, планируйте собеседования, ведите аналитику процессов найма
                </p>
                <ul className="text-sm space-y-1">
                  <li>• Поиск и управление кандидатами</li>
                  <li>• Планирование собеседований</li>
                  <li>• Календарь мероприятий</li>
                  <li>• Отчеты и аналитика</li>
                </ul>
                <Button className="w-full mt-4">
                  Войти как HR
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (appMode === 'hr') {
    return <HRApp onLogout={() => setAppMode('selector')} />;
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'profile':
        return <ProfileForm />;
      case 'chat':
        return <ChatPage />;
      case 'materials':
        return <MaterialsPage />;
      case 'skill-tree':
        return <SkillTreePage />;
      default:
        return <ProfileForm />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="border-b bg-white px-6 py-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Режим: Профиль сотрудника</span>
          <Button variant="ghost" size="sm" onClick={() => setAppMode('selector')}>
            Сменить режим
          </Button>
        </div>
      </div>
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      <div className="py-8">
        {renderCurrentPage()}
      </div>
    </div>
  );
}