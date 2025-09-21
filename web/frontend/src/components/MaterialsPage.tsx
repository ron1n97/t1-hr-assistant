import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { BookOpen, ExternalLink, Clock, Star, Play } from 'lucide-react';

interface Material {
  id: string;
  title: string;
  description: string;
  type: 'course' | 'book' | 'video' | 'article';
  duration: string;
  rating: number;
  level: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  url?: string;
}

const materials: Material[] = [
  {
    id: '1',
    title: 'Основы системного анализа',
    description: 'Полный курс по методам и практикам системного анализа для начинающих специалистов.',
    type: 'course',
    duration: '12 часов',
    rating: 4.8,
    level: 'beginner',
    category: 'Системный анализ'
  },
  {
    id: '2',
    title: 'UML моделирование на практике',
    description: 'Практическое руководство по созданию UML диаграмм для проектирования систем.',
    type: 'video',
    duration: '3 часа',
    rating: 4.6,
    level: 'intermediate',
    category: 'Моделирование'
  },
  {
    id: '3',
    title: 'Бизнес-анализ: от требований к решениям',
    description: 'Комплексное изучение процесса бизнес-анализа и работы с заказчиками.',
    type: 'book',
    duration: '400 страниц',
    rating: 4.9,
    level: 'intermediate',
    category: 'Бизнес-анализ'
  },
  {
    id: '4',
    title: 'Agile и Scrum для аналитиков',
    description: 'Особенности работы аналитика в гибких методологиях разработки.',
    type: 'course',
    duration: '8 часов',
    rating: 4.7,
    level: 'intermediate',
    category: 'Методологии'
  },
  {
    id: '5',
    title: 'SQL для анализа данных',
    description: 'Основы SQL с фокусом на задачи анализа и отчетности.',
    type: 'course',
    duration: '15 часов',
    rating: 4.5,
    level: 'beginner',
    category: 'Технические навыки'
  },
  {
    id: '6',
    title: 'Современные инструменты аналитика',
    description: 'Обзор и практика работы с JIRA, Confluence, Figma и другими инструментами.',
    type: 'article',
    duration: '45 мин',
    rating: 4.4,
    level: 'beginner',
    category: 'Инструменты'
  }
];

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'course': return BookOpen;
    case 'video': return Play;
    case 'book': return BookOpen;
    case 'article': return BookOpen;
    default: return BookOpen;
  }
};

const getTypeLabel = (type: string) => {
  switch (type) {
    case 'course': return 'Курс';
    case 'video': return 'Видео';
    case 'book': return 'Книга';
    case 'article': return 'Статья';
    default: return 'Материал';
  }
};

const getLevelLabel = (level: string) => {
  switch (level) {
    case 'beginner': return 'Начальный';
    case 'intermediate': return 'Средний';
    case 'advanced': return 'Продвинутый';
    default: return level;
  }
};

const getLevelColor = (level: string) => {
  switch (level) {
    case 'beginner': return 'bg-green-100 text-green-800';
    case 'intermediate': return 'bg-yellow-100 text-yellow-800';
    case 'advanced': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export function MaterialsPage() {
  const categories = Array.from(new Set(materials.map(m => m.category)));

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Материалы для обучения</h1>
          <p className="text-muted-foreground mt-2">
            Курсы, книги и статьи для развития профессиональных навыков
          </p>
        </div>
      </div>

      {/* Категории */}
      <div className="flex flex-wrap gap-2">
        <Button variant="default" size="sm">
          Все категории
        </Button>
        {categories.map(category => (
          <Button key={category} variant="outline" size="sm">
            {category}
          </Button>
        ))}
      </div>

      {/* Материалы */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {materials.map((material) => {
          const TypeIcon = getTypeIcon(material.type);
          
          return (
            <Card key={material.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <TypeIcon className="w-5 h-5 text-primary" />
                    <Badge variant="secondary" className="text-xs">
                      {getTypeLabel(material.type)}
                    </Badge>
                    <Badge className={`text-xs ${getLevelColor(material.level)}`}>
                      {getLevelLabel(material.level)}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm">{material.rating}</span>
                  </div>
                </div>
                <CardTitle className="text-lg leading-tight">
                  {material.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground text-sm">
                  {material.description}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {material.duration}
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {material.category}
                    </Badge>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button className="flex-1">
                    Начать изучение
                  </Button>
                  <Button variant="outline" size="sm">
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Рекомендации */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900">💡 Персональные рекомендации</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-blue-800">
          <p>На основе вашего профиля рекомендуем:</p>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>Изучить углубленно системный анализ для расширения экспертизы</li>
            <li>Освоить работу с API для технических компетенций</li>
            <li>Пройти курс по Agile для современных методологий</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}