import { useState } from 'react';
import { HRNavigation } from './HRNavigation';
import { CandidatesPage } from './CandidatesPage';
import { CalendarPage } from './CalendarPage';
import { HRChatPage } from './HRChatPage';
import { Card, CardContent } from './ui/card';
import { Users, Calendar, FileText, TrendingUp } from 'lucide-react';

function MaterialsPage() {
  return (
    <div className="p-6">
      <h1>Материалы</h1>
      <p className="text-muted-foreground">Документы, шаблоны и материалы для HR процессов</p>
    </div>
  );
}

function AgreementsPage() {
  return (
    <div className="p-6">
      <h1>Соглашения</h1>
      <p className="text-muted-foreground">Контракты и соглашения с кандидатами</p>
    </div>
  );
}

function ReportsPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1>Отчёты и аналитика</h1>
        <p className="text-muted-foreground">Статистика по найму и эффективности процессов</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">127</div>
                <p className="text-sm text-muted-foreground">Активные кандидаты</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">24</div>
                <p className="text-sm text-muted-foreground">Собеседований в месяц</p>
              </div>
              <Calendar className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">12</div>
                <p className="text-sm text-muted-foreground">Нанято в месяц</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">18</div>
                <p className="text-sm text-muted-foreground">Дней средний цикл найма</p>
              </div>
              <FileText className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function ReferencesPage() {
  return (
    <div className="p-6">
      <h1>Справочники</h1>
      <p className="text-muted-foreground">Справочная информация, должности, навыки</p>
    </div>
  );
}

function ManagementPage() {
  return (
    <div className="p-6">
      <h1>Управление</h1>
      <p className="text-muted-foreground">Настройки системы и управление пользователями</p>
    </div>
  );
}

interface HRAppProps {
  onLogout: () => void;
}

export function HRApp({ onLogout }: HRAppProps) {
  const [currentPage, setCurrentPage] = useState('candidates');

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'calendar':
        return <CalendarPage />;
      case 'materials':
        return <MaterialsPage />;
      case 'candidates':
        return <CandidatesPage />;
      case 'chat':
        return <HRChatPage />;
      case 'agreements':
        return <AgreementsPage />;
      case 'reports':
        return <ReportsPage />;
      case 'references':
        return <ReferencesPage />;
      case 'management':
        return <ManagementPage />;
      default:
        return <CandidatesPage />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <HRNavigation currentPage={currentPage} onPageChange={setCurrentPage} onLogout={onLogout} />
      <div className="flex-1">
        {renderCurrentPage()}
      </div>
    </div>
  );
}