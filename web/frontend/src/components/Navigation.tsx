import { Button } from './ui/button';
import { MessageCircle, BookOpen, GitBranch, User } from 'lucide-react';

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

export function Navigation({ currentPage, onPageChange }: NavigationProps) {
  const navItems = [
    { id: 'profile', label: 'Профиль', icon: User },
    { id: 'chat', label: 'Чат с ИИ', icon: MessageCircle },
    { id: 'materials', label: 'Материалы обучения', icon: BookOpen },
    { id: 'skill-tree', label: 'Дерево навыков', icon: GitBranch }
  ];

  return (
    <nav className="border-b bg-white shadow-sm">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <Button
                  key={item.id}
                  variant={isActive ? 'default' : 'ghost'}
                  onClick={() => onPageChange(item.id)}
                  className="flex items-center gap-2 px-4 py-2"
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}