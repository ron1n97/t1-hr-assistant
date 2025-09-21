import { Button } from './ui/button';
import { Calendar, FileText, Users, Handshake, BarChart3, BookOpen, Settings, User, LogOut, MessageSquare } from 'lucide-react';

interface HRNavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  onLogout: () => void;
}

export function HRNavigation({ currentPage, onPageChange, onLogout }: HRNavigationProps) {
  const navItems = [
    { id: 'calendar', label: 'Календарь', icon: Calendar },
    { id: 'materials', label: 'Материалы', icon: FileText },
    { id: 'candidates', label: 'Кандидаты', icon: Users },
    { id: 'chat', label: 'HR Чат', icon: MessageSquare },
    { id: 'agreements', label: 'Соглашения', icon: Handshake },
    { id: 'reports', label: 'Отчёты', icon: BarChart3 },
    { id: 'references', label: 'Справочники', icon: BookOpen },
    { id: 'management', label: 'Управление', icon: Settings }
  ];

  return (
    <div className="w-64 bg-white border-r min-h-screen p-4">
      {/* Logo */}
      <div className="mb-8">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
            <span className="text-white font-bold text-sm">HR</span>
          </div>
          <span className="font-semibold text-lg">RECRUITMENT</span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? 'secondary' : 'ghost'}
              onClick={() => onPageChange(item.id)}
              className="w-full justify-start gap-3 h-12"
            >
              <Icon className="w-5 h-5" />
              {item.label}
            </Button>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="absolute bottom-4 left-4 right-4 space-y-3">
        <Button
          variant="ghost"
          onClick={onLogout}
          className="w-full justify-start gap-3 h-12 text-muted-foreground hover:text-foreground"
        >
          <LogOut className="w-5 h-5" />
          Выйти из системы
        </Button>
        
        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
          <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
            <User className="w-5 h-5" />
          </div>
          <div>
            <div className="font-medium text-sm">Алексей</div>
            <div className="text-xs text-muted-foreground">HR Менеджер</div>
          </div>
        </div>
      </div>
    </div>
  );
}