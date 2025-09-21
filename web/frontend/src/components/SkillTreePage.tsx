import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { CheckCircle, Circle, Lock, Star, Target, Plus, TrendingUp, Award, Briefcase } from 'lucide-react';

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

interface CareerPosition {
  id: string;
  title: string;
  company: string;
  period: string;
  status: 'past' | 'current' | 'future';
  description: string;
  xpGained: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  type: 'project' | 'achievement' | 'certification';
  xpReward: number;
  date: string;
  category: string;
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

// Данные карьерного пути
const careerPath: CareerPosition[] = [
  {
    id: '1',
    title: 'Junior Frontend Developer',
    company: 'Яндекс',
    period: '2020-2022',
    status: 'past',
    description: 'Разработка клиентской части веб-приложений',
    xpGained: 500
  },
  {
    id: '2',
    title: 'Middle Frontend Developer',
    company: 'T1',
    period: '2022-настоящее время',
    status: 'current',
    description: 'Разработка сложных веб-систем и архитектуры',
    xpGained: 800
  },
  {
    id: '3',
    title: 'Senior Frontend Developer',
    company: 'T1',
    period: 'Планируется',
    status: 'future',
    description: 'Техническое лидерство и менторство',
    xpGained: 0
  },
  {
    id: '4',
    title: 'Lead Frontend Developer',
    company: 'T1',
    period: 'Будущее',
    status: 'future',
    description: 'Управление командой и архитектурные решения',
    xpGained: 0
  }
];

// Достижения пользователя
const userAchievements: Achievement[] = [
  {
    id: '1',
    title: 'Завершение проекта iModule 5+1',
    description: 'Успешная разработка и внедрение нового модуля',
    type: 'project',
    xpReward: 300,
    date: '2023-12-15',
    category: 'Разработка'
  },
  {
    id: '2',
    title: 'Сертификация React Developer',
    description: 'Получение официального сертификата React',
    type: 'certification',
    xpReward: 200,
    date: '2023-10-20',
    category: 'Обучение'
  },
  {
    id: '3',
    title: 'Менторство Junior разработчика',
    description: 'Помощь в развитии нового сотрудника',
    type: 'achievement',
    xpReward: 150,
    date: '2023-11-05',
    category: 'Лидерство'
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
  const [achievements, setAchievements] = useState<Achievement[]>(userAchievements);
  const [showAddAchievement, setShowAddAchievement] = useState(false);
  const [newAchievement, setNewAchievement] = useState({
    title: '',
    description: '',
    type: 'project' as 'project' | 'achievement' | 'certification',
    category: ''
  });
  
  const categories = Array.from(new Set(skillTree.map(s => s.category)));
  
  // Расчет XP и уровня
  const totalXP = achievements.reduce((sum, achievement) => sum + achievement.xpReward, 0);
  const currentLevel = Math.floor(totalXP / 1000) + 1;
  const xpInCurrentLevel = totalXP % 1000;
  const xpToNextLevel = 1000 - xpInCurrentLevel;
  const levelProgress = (xpInCurrentLevel / 1000) * 100;
  
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

  const handleAddAchievement = () => {
    if (newAchievement.title && newAchievement.description && newAchievement.category) {
      const randomXP = Math.floor(Math.random() * 500) + 100; // 100-600 XP
      const achievement: Achievement = {
        id: Date.now().toString(),
        title: newAchievement.title,
        description: newAchievement.description,
        type: newAchievement.type,
        xpReward: randomXP,
        date: new Date().toISOString().split('T')[0],
        category: newAchievement.category
      };
      
      setAchievements([...achievements, achievement]);
      setNewAchievement({ title: '', description: '', type: 'project', category: '' });
      setShowAddAchievement(false);
    }
  };

  const getCareerStatusIcon = (status: string) => {
    switch (status) {
      case 'past':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'current':
        return <Target className="w-5 h-5 text-blue-500" />;
      case 'future':
        return <Lock className="w-5 h-5 text-gray-400" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getCareerStatusColor = (status: string) => {
    switch (status) {
      case 'past': return 'border-green-500 bg-green-50';
      case 'current': return 'border-blue-500 bg-blue-50';
      case 'future': return 'border-gray-300 bg-gray-50';
      default: return 'border-gray-300 bg-white';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Заголовок и статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              XP
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalXP}</div>
            <div className="text-sm text-muted-foreground">опыта накоплено</div>
            <Progress value={levelProgress} className="mt-2" />
            <div className="text-xs text-muted-foreground mt-1">
              {xpInCurrentLevel}/1000 до следующего уровня
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              Уровень
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentLevel}</div>
            <div className="text-sm text-muted-foreground">
              При повышении уровня - увеличивается шанс получения повышения или обновления грейда (зарплаты)
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5 text-purple-500" />
              Достижения
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{achievements.length}</div>
            <div className="text-sm text-muted-foreground">достижений получено</div>
            <Dialog open={showAddAchievement} onOpenChange={setShowAddAchievement}>
              <DialogTrigger asChild>
                <Button size="sm" className="mt-2 w-full">
                  <Plus className="w-4 h-4 mr-2" />
                  Добавить достижение
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Добавить новое достижение</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="title">Название</Label>
                    <Input
                      id="title"
                      value={newAchievement.title}
                      onChange={(e) => setNewAchievement({...newAchievement, title: e.target.value})}
                      placeholder="Название проекта или достижения"
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Описание</Label>
                    <Textarea
                      id="description"
                      value={newAchievement.description}
                      onChange={(e) => setNewAchievement({...newAchievement, description: e.target.value})}
                      placeholder="Подробное описание достижения"
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label htmlFor="category">Категория</Label>
                    <Input
                      id="category"
                      value={newAchievement.category}
                      onChange={(e) => setNewAchievement({...newAchievement, category: e.target.value})}
                      placeholder="Например: Разработка, Обучение, Лидерство"
                    />
                  </div>
                  <div>
                    <Label htmlFor="type">Тип</Label>
                    <select
                      id="type"
                      value={newAchievement.type}
                      onChange={(e) => setNewAchievement({...newAchievement, type: e.target.value as 'project' | 'achievement' | 'certification'})}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="project">Проект</option>
                      <option value="achievement">Достижение</option>
                      <option value="certification">Сертификация</option>
                    </select>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setShowAddAchievement(false)}>
                      Отмена
                    </Button>
                    <Button onClick={handleAddAchievement}>
                      Добавить
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>
      </div>

      {/* Карьерный путь */}
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Briefcase className="w-6 h-6" />
            Карьерный путь
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {careerPath.map((position, index) => (
              <Card
                key={position.id}
                className={`cursor-pointer transition-all ${getCareerStatusColor(position.status)} ${
                  index > 0 ? 'relative' : ''
                }`}
              >
                {index > 0 && (
                  <div className="absolute -left-2 top-1/2 transform -translate-y-1/2 w-4 h-0.5 bg-gray-300"></div>
                )}
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getCareerStatusIcon(position.status)}
                      <h4 className="text-sm font-medium">{position.title}</h4>
                    </div>
                    {position.xpGained > 0 && (
                      <Badge variant="outline" className="text-xs">
                        +{position.xpGained} XP
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">{position.company}</p>
                  <p className="text-xs text-muted-foreground mb-2">{position.period}</p>
                  <p className="text-xs text-muted-foreground">{position.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Достижения */}
        <div>
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Award className="w-6 h-6" />
            Последние достижения
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.slice(-6).reverse().map(achievement => (
              <Card key={achievement.id} className="border-purple-200 bg-purple-50">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Award className="w-4 h-4 text-purple-500" />
                      <h4 className="text-sm font-medium">{achievement.title}</h4>
                    </div>
                    <Badge className="text-xs bg-purple-100 text-purple-800">
                      +{achievement.xpReward} XP
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">{achievement.description}</p>
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs">{achievement.category}</Badge>
                    <span className="text-xs text-muted-foreground">{achievement.date}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Прогресс навыков */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-bold mb-4">Прогресс</h2>
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