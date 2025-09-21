import { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Search, Plus, Phone, Mail, Calendar, MapPin, User, ExternalLink } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';

interface Candidate {
  id: string;
  name: string;
  position: string;
  salary: string;
  age: number;
  location: string;
  phone: string;
  email: string;
  telegram: string;
  avatar?: string;
  skills: string[];
  experience: {
    company: string;
    position: string;
    period: string;
    description: string;
    current: boolean;
  }[];
  createdAt: string;
  status: 'new' | 'in-progress' | 'interview' | 'offer' | 'hired' | 'rejected';
}

const mockCandidates: Candidate[] = [
  {
    id: '1',
    name: 'Матвеев Георг Петрович',
    position: 'Senior Front-end developer',
    salary: '200 000 ₽',
    age: 29,
    location: 'Москва',
    phone: '+7 (962) 123-22-45',
    email: 'georgentrevkh@gmail.ru',
    telegram: '@georgentrevkh',
    skills: ['Front-end', 'Angular', 'JavaScript', 'TypeScript', 'React'],
    experience: [
      {
        company: 'Яндекс',
        position: 'Senior Front-end developer',
        period: 'Февраль 2017 — по настоящее время',
        description: 'Управление разработкой клиентской части iModule 5+1 и мобильного приложения (React Native)',
        current: true
      }
    ],
    createdAt: '22 февраля 2021',
    status: 'interview'
  },
  {
    id: '2',
    name: 'Носов Роман Борисович',
    position: 'Backend Developer',
    salary: '180 000 ₽',
    age: 32,
    location: 'Москва',
    phone: '+7 (905) 456-78-90',
    email: 'r.nosov@example.com',
    telegram: '@rnosov',
    skills: ['Python', 'Django', 'PostgreSQL', 'Redis'],
    experience: [
      {
        company: 'VK',
        position: 'Backend Developer',
        period: 'Январь 2019 — по настоящее время',
        description: 'Разработка высоконагруженных сервисов',
        current: true
      }
    ],
    createdAt: '15 февраля 2021',
    status: 'new'
  },
  {
    id: '3',
    name: 'Обухов Павел Петрович',
    position: 'DevOps Engineer',
    salary: '220 000 ₽',
    age: 28,
    location: 'Санкт-Петербург',
    phone: '+7 (812) 234-56-78',
    email: 'p.obukhov@example.com',
    telegram: '@pobukhov',
    skills: ['Docker', 'Kubernetes', 'AWS', 'Terraform'],
    experience: [
      {
        company: 'Сбер',
        position: 'DevOps Engineer',
        period: 'Март 2020 — по настоящее время',
        description: 'Автоматизация процессов разработки и развертывания',
        current: true
      }
    ],
    createdAt: '10 февраля 2021',
    status: 'in-progress'
  },
  {
    id: '4',
    name: 'Строкова Елена Алексеевна',
    position: 'Product Manager',
    salary: '250 000 ₽',
    age: 31,
    location: 'Москва',
    phone: '+7 (926) 789-01-23',
    email: 'e.strokova@example.com',
    telegram: '@estrokova',
    skills: ['Product Management', 'Analytics', 'Agile', 'Figma'],
    experience: [
      {
        company: 'Тинькофф',
        position: 'Senior Product Manager',
        period: 'Июнь 2019 — по настоящее время',
        description: 'Управление продуктовой линейкой мобильных приложений',
        current: true
      }
    ],
    createdAt: '5 февраля 2021',
    status: 'offer'
  }
];

const statusLabels = {
  'new': 'Новый',
  'in-progress': 'В процессе',
  'interview': 'Собеседование',
  'offer': 'Оффер',
  'hired': 'Нанят',
  'rejected': 'Отклонен'
};

const statusColors = {
  'new': 'bg-blue-100 text-blue-800',
  'in-progress': 'bg-yellow-100 text-yellow-800',
  'interview': 'bg-purple-100 text-purple-800',
  'offer': 'bg-green-100 text-green-800',
  'hired': 'bg-emerald-100 text-emerald-800',
  'rejected': 'bg-red-100 text-red-800'
};

export function CandidatesPage() {
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(mockCandidates[0]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [locationFilter, setLocationFilter] = useState('all');
  const [salaryRangeFilter, setSalaryRangeFilter] = useState('all');
  const [ageRangeFilter, setAgeRangeFilter] = useState('all');
  const [experienceFilter, setExperienceFilter] = useState('all');
  const [skillFilter, setSkillFilter] = useState('all');
  const [companyFilter, setCompanyFilter] = useState('all');
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);

  // Получаем уникальные значения для фильтров
  const allLocations = [...new Set(mockCandidates.map(c => c.location))];
  const allSkills = [...new Set(mockCandidates.flatMap(c => c.skills))];
  const allCompanies = [...new Set(mockCandidates.flatMap(c => c.experience.map(e => e.company)))];

  const filteredCandidates = mockCandidates.filter(candidate => {
    // Поиск по всем текстовым полям
    const searchLower = searchQuery.toLowerCase();
    const matchesSearch = searchQuery === '' || (
      candidate.name.toLowerCase().includes(searchLower) ||
      candidate.position.toLowerCase().includes(searchLower) ||
      candidate.email.toLowerCase().includes(searchLower) ||
      candidate.phone.includes(searchQuery) ||
      candidate.telegram.toLowerCase().includes(searchLower) ||
      candidate.skills.some(skill => skill.toLowerCase().includes(searchLower)) ||
      candidate.experience.some(exp => 
        exp.company.toLowerCase().includes(searchLower) ||
        exp.position.toLowerCase().includes(searchLower) ||
        exp.description.toLowerCase().includes(searchLower)
      )
    );

    // Фильтр по статусу
    const matchesStatus = statusFilter === 'all' || candidate.status === statusFilter;
    
    // Фильтр по локации
    const matchesLocation = locationFilter === 'all' || candidate.location === locationFilter;
    
    // Фильтр по зарплате
    const matchesSalary = (() => {
      if (salaryRangeFilter === 'all') return true;
      const salary = parseInt(candidate.salary.replace(/\D/g, ''));
      switch (salaryRangeFilter) {
        case '0-150': return salary < 150000;
        case '150-200': return salary >= 150000 && salary < 200000;
        case '200-250': return salary >= 200000 && salary < 250000;
        case '250+': return salary >= 250000;
        default: return true;
      }
    })();
    
    // Фильтр по возрасту
    const matchesAge = (() => {
      if (ageRangeFilter === 'all') return true;
      switch (ageRangeFilter) {
        case '20-25': return candidate.age >= 20 && candidate.age <= 25;
        case '26-30': return candidate.age >= 26 && candidate.age <= 30;
        case '31-35': return candidate.age >= 31 && candidate.age <= 35;
        case '35+': return candidate.age > 35;
        default: return true;
      }
    })();
    
    // Фильтр по опыту работы (количество лет)
    const matchesExperience = (() => {
      if (experienceFilter === 'all') return true;
      const totalExperience = candidate.experience.reduce((total, exp) => {
        const years = exp.period.includes('—') ? 
          parseInt(exp.period.split('—')[0].trim().split(' ')[1]) - 
          parseInt(exp.period.split('—')[1].trim().split(' ')[1]) : 1;
        return total + Math.abs(years);
      }, 0);
      
      switch (experienceFilter) {
        case '0-1': return totalExperience <= 1;
        case '2-3': return totalExperience >= 2 && totalExperience <= 3;
        case '4-5': return totalExperience >= 4 && totalExperience <= 5;
        case '5+': return totalExperience > 5;
        default: return true;
      }
    })();
    
    // Фильтр по навыкам
    const matchesSkill = skillFilter === 'all' || candidate.skills.includes(skillFilter);
    
    // Фильтр по компании
    const matchesCompany = companyFilter === 'all' || 
      candidate.experience.some(exp => exp.company === companyFilter);

    return matchesSearch && matchesStatus && matchesLocation && 
           matchesSalary && matchesAge && matchesExperience && 
           matchesSkill && matchesCompany;
  });

  const handleScheduleInterview = () => {
    // В реальном приложении здесь была бы логика планирования собеседования
    setShowScheduleDialog(false);
    console.log('Собеседование запланировано');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Candidates List */}
      <div className="w-1/3 bg-white border-r">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between mb-4">
            <h1>Кандидаты</h1>
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Новый кандидат
            </Button>
          </div>
          
          {/* Search and Filters */}
          <div className="space-y-3">
            {/* Основной поиск */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Поиск по имени, должности, навыкам, опыту..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Фильтры - первый ряд */}
            <div className="grid grid-cols-2 gap-2">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Статус" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все статусы</SelectItem>
                  <SelectItem value="new">Новые</SelectItem>
                  <SelectItem value="in-progress">В процессе</SelectItem>
                  <SelectItem value="interview">Собеседование</SelectItem>
                  <SelectItem value="offer">Оффер</SelectItem>
                  <SelectItem value="hired">Нанят</SelectItem>
                  <SelectItem value="rejected">Отклонен</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={locationFilter} onValueChange={setLocationFilter}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Локация" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все локации</SelectItem>
                  {allLocations.map(location => (
                    <SelectItem key={location} value={location}>{location}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Фильтры - второй ряд */}
            <div className="grid grid-cols-2 gap-2">
              <Select value={salaryRangeFilter} onValueChange={setSalaryRangeFilter}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Зарплата" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Любая зарплата</SelectItem>
                  <SelectItem value="0-150">До 150 000 ₽</SelectItem>
                  <SelectItem value="150-200">150 000 - 200 000 ₽</SelectItem>
                  <SelectItem value="200-250">200 000 - 250 000 ₽</SelectItem>
                  <SelectItem value="250+">От 250 000 ₽</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={ageRangeFilter} onValueChange={setAgeRangeFilter}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Возраст" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Любой возраст</SelectItem>
                  <SelectItem value="20-25">20-25 лет</SelectItem>
                  <SelectItem value="26-30">26-30 лет</SelectItem>
                  <SelectItem value="31-35">31-35 лет</SelectItem>
                  <SelectItem value="35+">35+ лет</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Фильтры - третий ряд */}
            <div className="grid grid-cols-2 gap-2">
              <Select value={experienceFilter} onValueChange={setExperienceFilter}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Опыт работы" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Любой опыт</SelectItem>
                  <SelectItem value="0-1">0-1 год</SelectItem>
                  <SelectItem value="2-3">2-3 года</SelectItem>
                  <SelectItem value="4-5">4-5 лет</SelectItem>
                  <SelectItem value="5+">5+ лет</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={skillFilter} onValueChange={setSkillFilter}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Навыки" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все навыки</SelectItem>
                  {allSkills.map(skill => (
                    <SelectItem key={skill} value={skill}>{skill}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Фильтр по компании */}
            <div>
              <Select value={companyFilter} onValueChange={setCompanyFilter}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Компания" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все компании</SelectItem>
                  {allCompanies.map(company => (
                    <SelectItem key={company} value={company}>{company}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Счетчик результатов и сброс фильтров */}
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Найдено: {filteredCandidates.length} из {mockCandidates.length} кандидатов
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setSearchQuery('');
                  setStatusFilter('all');
                  setLocationFilter('all');
                  setSalaryRangeFilter('all');
                  setAgeRangeFilter('all');
                  setExperienceFilter('all');
                  setSkillFilter('all');
                  setCompanyFilter('all');
                }}
                className="text-xs"
              >
                Сбросить фильтры
              </Button>
            </div>
          </div>
        </div>

        {/* Candidates List */}
        <div className="overflow-auto">
          {filteredCandidates.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Кандидаты не найдены</p>
              <p className="text-sm">Попробуйте изменить параметры поиска</p>
            </div>
          ) : (
            filteredCandidates.map((candidate) => (
              <div
                key={candidate.id}
                className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
                  selectedCandidate?.id === candidate.id ? 'bg-blue-50 border-blue-200' : ''
                }`}
                onClick={() => setSelectedCandidate(candidate)}
              >
                <div className="flex items-start gap-3">
                  <Avatar className="w-12 h-12">
                    <AvatarImage src={candidate.avatar} />
                    <AvatarFallback>
                      {candidate.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-sm">{candidate.name}</h4>
                        <p className="text-sm text-muted-foreground mb-1">{candidate.position}</p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                          <span>{candidate.age} лет</span>
                          <span>•</span>
                          <span>{candidate.location}</span>
                          <span>•</span>
                          <span className="font-medium text-green-600">{candidate.salary}</span>
                        </div>
                        <div className="flex flex-wrap gap-1 mb-2">
                          {candidate.skills.slice(0, 3).map(skill => (
                            <Badge key={skill} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                          {candidate.skills.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{candidate.skills.length - 3}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center justify-between">
                          <p className="text-xs text-muted-foreground">{candidate.createdAt}</p>
                          <Badge className={`text-xs ${statusColors[candidate.status]}`}>
                            {statusLabels[candidate.status]}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Candidate Details */}
      <div className="flex-1 overflow-auto">
        {selectedCandidate ? (
          <div className="p-6">
            {/* Header */}
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-start gap-6">
                <Avatar className="w-24 h-24">
                  <AvatarImage src={selectedCandidate.avatar} />
                  <AvatarFallback className="text-2xl">
                    {selectedCandidate.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h1 className="text-2xl font-semibold mb-2">{selectedCandidate.name}</h1>
                  <div className="flex items-center gap-6 text-sm text-muted-foreground mb-4">
                    <div className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      {selectedCandidate.age} лет
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {selectedCandidate.location}
                    </div>
                    <div>{selectedCandidate.position}</div>
                  </div>
                  <div className="flex gap-2 mb-4">
                    {selectedCandidate.skills.map(skill => (
                      <Badge key={skill} variant="secondary">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold mb-2">{selectedCandidate.salary}</div>
                <Button 
                  onClick={() => setShowScheduleDialog(true)}
                  className="mb-2"
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  Назначить собеседование
                </Button>
                <div>
                  <Button variant="outline" size="sm">
                    Редактировать
                  </Button>
                </div>
              </div>
            </div>

            {/* Contact Info */}
            <Card className="mb-6">
              <CardContent className="p-6">
                <h3 className="font-semibold mb-4">Контактная информация</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Phone className="w-4 h-4 text-muted-foreground" />
                    <span>{selectedCandidate.phone}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail className="w-4 h-4 text-muted-foreground" />
                    <span>{selectedCandidate.email}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="w-4 h-4 text-muted-foreground text-xs font-bold">TG</span>
                    <span>{selectedCandidate.telegram}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Experience */}
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold mb-4">Опыт работы</h3>
                <div className="space-y-4">
                  {selectedCandidate.experience.map((exp, index) => (
                    <div key={index} className="border-l-2 border-blue-200 pl-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium">{exp.position}</h4>
                          <p className="text-sm text-muted-foreground">{exp.company}</p>
                          <p className="text-xs text-muted-foreground">{exp.period}</p>
                        </div>
                        {exp.current && (
                          <Badge className="bg-green-100 text-green-800">
                            Текущая
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm mt-2">{exp.description}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <User className="w-16 h-16 mx-auto mb-4 opacity-20" />
              <p>Выберите кандидата для просмотра деталей</p>
            </div>
          </div>
        )}
      </div>

      {/* Schedule Interview Dialog */}
      <Dialog open={showScheduleDialog} onOpenChange={setShowScheduleDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Назначить собеседование</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="interview-type">Тип собеседования</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите тип" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technical">Техническое</SelectItem>
                  <SelectItem value="hr">HR интервью</SelectItem>
                  <SelectItem value="final">Финальное</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="interview-date">Дата и время</Label>
              <Input type="datetime-local" />
            </div>

            <div>
              <Label htmlFor="interview-format">Формат</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите формат" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="online">Онлайн</SelectItem>
                  <SelectItem value="offline">Оффлайн</SelectItem>
                  <SelectItem value="phone">Телефон</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="interview-notes">Комментарии</Label>
              <Textarea 
                placeholder="Дополнительная информация..."
                rows={3}
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowScheduleDialog(false)}>
                Отмена
              </Button>
              <Button onClick={handleScheduleInterview}>
                Назначить
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}