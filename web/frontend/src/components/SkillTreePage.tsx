import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { CheckCircle, Circle, Lock, Star, Target } from 'lucide-react';

interface SkillNode {
  id: string;
  title: string;
  description: string;
  category: string;
  level: number;
  maxLevel: number;
  status: 'locked' | 'available' | 'in-progress' | 'completed';
  prerequisites?: string[];
  children?: string[];
  points: number;
}

const skillTree: SkillNode[] = [
  // Основы
  {
    id: 'basic-analysis',
    title: 'Основы анализа',
    description: 'Базовые принципы системного и бизнес-анализа',
    category: 'Основы',
    level: 3,
    maxLevel: 3,
    status: 'completed',
    children: ['requirements-gathering', 'stakeholder-management'],
    points: 300
  },
  {
    id: 'documentation',
    title: 'Документирование',
    description: 'Создание и поддержка технической документации',
    category: 'Основы',
    level: 2,
    maxLevel: 3,
    status: 'in-progress',
    children: ['uml-modeling', 'technical-writing'],
    points: 200
  },
  
  // Требования
  {
    id: 'requirements-gathering',
    title: 'Сбор требований',
    description: 'Методы выявления и формализации требований',
    category: 'Требования',
    level: 2,
    maxLevel: 4,
    status: 'in-progress',
    prerequisites: ['basic-analysis'],
    children: ['requirements-analysis', 'stakeholder-interviews'],
    points: 200
  },
  {
    id: 'requirements-analysis',
    title: 'Анализ требований',
    description: 'Декомпозиция и приоритизация требований',
    category: 'Требования',
    level: 0,
    maxLevel: 4,
    status: 'available',
    prerequisites: ['requirements-gathering'],
    children: ['solution-design'],
    points: 0
  },
  
  // Моделирование
  {
    id: 'uml-modeling',
    title: 'UML моделирование',
    description: 'Создание диаграмм и схем систем',
    category: 'Моделирование',
    level: 1,
    maxLevel: 3,
    status: 'available',
    prerequisites: ['documentation'],
    children: ['process-modeling'],
    points: 100
  },
  {
    id: 'process-modeling',
    title: 'Моделирование процессов',
    description: 'BPMN и описание бизнес-процессов',
    category: 'Моделирование',
    level: 0,
    maxLevel: 3,
    status: 'locked',
    prerequisites: ['uml-modeling'],
    points: 0
  },
  
  // Коммуникации
  {
    id: 'stakeholder-management',
    title: 'Работа с заказчиками',
    description: 'Управление коммуникациями с заинтересованными сторонами',
    category: 'Коммуникации',
    level: 2,
    maxLevel: 3,
    status: 'in-progress',
    prerequisites: ['basic-analysis'],
    children: ['stakeholder-interviews'],
    points: 200
  },
  {
    id: 'stakeholder-interviews',
    title: 'Интервьюирование',
    description: 'Техники проведения интервью и встреч',
    category: 'Коммуникации',
    level: 0,
    maxLevel: 3,
    status: 'available',
    prerequisites: ['stakeholder-management', 'requirements-gathering'],
    points: 0
  },
  
  // Продвинутые навыки
  {
    id: 'solution-design',
    title: 'Проектирование решений',
    description: 'Архитектурное мышление и проектирование',
    category: 'Продвинутые',
    level: 0,
    maxLevel: 4,
    status: 'locked',
    prerequisites: ['requirements-analysis'],
    children: ['system-architecture'],
    points: 0
  },
  {
    id: 'system-architecture',
    title: 'Системная архитектура',
    description: 'Принципы построения ИТ-систем',
    category: 'Продвинутые',
    level: 0,
    maxLevel: 4,
    status: 'locked',
    prerequisites: ['solution-design'],
    points: 0
  },
  
  // Техническое письмо
  {
    id: 'technical-writing',
    title: 'Техническое письмо',
    description: 'Создание качественной документации',
    category: 'Документация',
    level: 0,
    maxLevel: 3,
    status: 'available',
    prerequisites: ['documentation'],
    points: 0
  }
];

const getStatusIcon = (status: string, level: number, maxLevel: number) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'in-progress':
      return <Target className="w-5 h-5 text-blue-500" />;
    case 'available':
      return <Circle className="w-5 h-5 text-gray-400" />;
    case 'locked':
      return <Lock className="w-5 h-5 text-gray-300" />;
    default:
      return <Circle className="w-5 h-5 text-gray-400" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return 'border-green-500 bg-green-50';
    case 'in-progress': return 'border-blue-500 bg-blue-50';
    case 'available': return 'border-gray-300 bg-white hover:border-primary';
    case 'locked': return 'border-gray-200 bg-gray-50';
    default: return 'border-gray-300 bg-white';
  }
};

export function SkillTreePage() {
  const [selectedSkill, setSelectedSkill] = useState<SkillNode | null>(null);
  const categories = Array.from(new Set(skillTree.map(s => s.category)));
  
  const totalPoints = skillTree.reduce((sum, skill) => sum + skill.points, 0);
  const maxPossiblePoints = skillTree.reduce((sum, skill) => sum + (skill.maxLevel * 100), 0);
  const completionPercentage = Math.round((totalPoints / maxPossiblePoints) * 100);
  
  const completedSkills = skillTree.filter(s => s.status === 'completed').length;
  const totalSkills = skillTree.length;

  const handleSkillClick = (skill: SkillNode) => {
    if (skill.status !== 'locked') {
      setSelectedSkill(skill);
    }
  };

  const handleLevelUp = (skillId: string) => {
    // В реальном приложении здесь была бы логика увеличения уровня навыка
    console.log(`Повысить уровень навыка: ${skillId}`);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Заголовок и статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              Очки навыков
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalPoints}</div>
            <div className="text-sm text-muted-foreground">из {maxPossiblePoints} возможных</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Прогресс</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completionPercentage}%</div>
            <Progress value={completionPercentage} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Завершенные навыки</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedSkills}/{totalSkills}</div>
            <div className="text-sm text-muted-foreground">навыков изучено</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Дерево навыков */}
        <div className="lg:col-span-2 space-y-6">
          {categories.map(category => (
            <div key={category}>
              <h3 className="mb-4">{category}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {skillTree
                  .filter(skill => skill.category === category)
                  .map(skill => (
                    <Card
                      key={skill.id}
                      className={`cursor-pointer transition-all ${getStatusColor(skill.status)} ${
                        selectedSkill?.id === skill.id ? 'ring-2 ring-primary' : ''
                      }`}
                      onClick={() => handleSkillClick(skill)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(skill.status, skill.level, skill.maxLevel)}
                            <h4 className="text-sm font-medium">{skill.title}</h4>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {skill.level}/{skill.maxLevel}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mb-2">
                          {skill.description}
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1">
                            <Star className="w-3 h-3 text-yellow-500" />
                            <span className="text-xs">{skill.points}</span>
                          </div>
                          {skill.level < skill.maxLevel && skill.status !== 'locked' && (
                            <Progress 
                              value={(skill.level / skill.maxLevel) * 100} 
                              className="w-16 h-2" 
                            />
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </div>
            </div>
          ))}
        </div>

        {/* Детали навыка */}
        <div>
          {selectedSkill ? (
            <Card className="sticky top-6">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    {getStatusIcon(selectedSkill.status, selectedSkill.level, selectedSkill.maxLevel)}
                    {selectedSkill.title}
                  </CardTitle>
                  <Badge variant="outline">
                    {selectedSkill.level}/{selectedSkill.maxLevel}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm">{selectedSkill.description}</p>
                
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Прогресс</span>
                    <span className="text-sm text-muted-foreground">
                      {selectedSkill.level}/{selectedSkill.maxLevel}
                    </span>
                  </div>
                  <Progress value={(selectedSkill.level / selectedSkill.maxLevel) * 100} />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm">Очки: {selectedSkill.points}</span>
                  </div>
                  <Badge className="text-xs">{selectedSkill.category}</Badge>
                </div>

                {selectedSkill.prerequisites && selectedSkill.prerequisites.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium mb-2">Требования:</h5>
                    <div className="space-y-1">
                      {selectedSkill.prerequisites.map(prereq => {
                        const prereqSkill = skillTree.find(s => s.id === prereq);
                        return (
                          <div key={prereq} className="text-xs text-muted-foreground">
                            • {prereqSkill?.title}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {selectedSkill.status === 'available' && selectedSkill.level < selectedSkill.maxLevel && (
                  <Button 
                    className="w-full"
                    onClick={() => handleLevelUp(selectedSkill.id)}
                  >
                    Повысить уровень
                  </Button>
                )}

                {selectedSkill.status === 'in-progress' && (
                  <Button variant="outline" className="w-full">
                    Продолжить изучение
                  </Button>
                )}

                {selectedSkill.status === 'completed' && (
                  <Button variant="outline" className="w-full" disabled>
                    Навык освоен
                  </Button>
                )}

                {selectedSkill.status === 'locked' && (
                  <Button variant="outline" className="w-full" disabled>
                    Заблокировано
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-6 text-center">
                <Target className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h4>Выберите навык</h4>
                <p className="text-sm text-muted-foreground">
                  Нажмите на любой навык слева, чтобы увидеть подробную информацию и возможности развития.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}