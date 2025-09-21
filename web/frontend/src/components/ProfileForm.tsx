import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { Plus, Trash2, Download } from 'lucide-react';

interface WorkExperience {
  position: string;
  company: string;
  location: string;
  startDate: string;
  endDate: string;
  duration: string;
  responsibilities: string[];
}

interface Education {
  institution: string;
  degree: string;
  specialization: string;
  graduationYear: string;
}

interface LanguageSkill {
  language: string;
  level: string;
}

interface TechnicalSkill {
  skill: string;
  level: string;
}

interface ProfileData {
  basicInfo: {
    department: string;
    position: string;
    grade: string;
    itExperience: string;
  };
  currentRole: {
    specialization: string;
    functionalRole: string;
    responsibilities: string[];
  };
  additionalRole?: {
    specialization: string;
    role: string;
    responsibilities: string[];
  };
  workExperience: WorkExperience[];
  education: Education;
  skills: string[];
  competencies: string[];
  foreignLanguages: LanguageSkill[];
  otherCompetencies: TechnicalSkill[];
  programmingLanguages: TechnicalSkill[];
}

const technicalSpecialties = [
  'Системный аналитик',
  'Бизнес-аналитик', 
  'Аналитик данных',
  'Продуктовый аналитик',
  'Функциональный аналитик',
  'Аналитик информационных систем',
  'Архитектор систем',
  'Проектировщик ИС',
  'Разработчик требований',
  'Специалист по тестированию',
  'DevOps инженер',
  'Frontend разработчик',
  'Backend разработчик',
  'Fullstack разработчик',
  'Мобильный разработчик',
  'UI/UX дизайнер',
  'Scrum Master',
  'Product Manager',
  'Technical Writer',
  'QA инженер'
];

const skillsAndCompetencies = [
  'Участвует в проектировании ИС/ПС',
  'Взаимодействует с бизнес-аналитиками/заказчиками',
  'Участвует в создании и оценке бизнес-требований к ИС/ПС',
  'Разрабатывает и поддерживает в актуальном состоянии функциональные и нефункциональные требования',
  'Осуществляет декомпозицию требований для разработки',
  'Обеспечивает бесконфликтность и полноту требований в части разрабатываемых Артефактов',
  'Пишет технические задания на разработку автоматизированных систем',
  'Взаимодействует с командой разработки',
  'Анализирует пользовательские интерфейсы',
  'Проводит систематическую проверку тест-кейсов',
  'Передает Артефакты в Архив программы',
  'Осуществляет анализ системы по специфическим запросам',
  'Сопровождает накопленную документацию',
  'Организует и проводит демонстрации прототипов',
  'Принимает участие во внедрении ИС/ПС',
  'Анализ бизнес-инициативы',
  'Анализ предметной области',
  'Интервьирование бизнес-заказчика',
  'Выявление рисков и неопределенностей',
  'Анализ возможных решений',
  'Разработка критериев приемки решения',
  'Подготовка бизнес-требований с учетом возможностей ИТ',
  'Анализ бизнес-данных и документов',
  'Визуализация данных',
  'Разработка глоссария для формализации предметной области',
  'Описание артефактов (Функциональность ИС, Требования к ИС)',
  'Участие в проектировании систем',
  'Моделирование бизнес процессов as-is и проектирование процессов to-be',
  'Документирование',
  'Содействие формированию и управление бэклогом',
  'Моделирование состояний и сценариев использования системы'
];

const proficiencyLevels = [
  'Начальный',
  'Базовый', 
  'Уверенный',
  'Продвинутый',
  'Экспертный'
];

const languages = [
  'Английский',
  'Немецкий',
  'Французский',
  'Испанский',
  'Итальянский',
  'Китайский',
  'Японский',
  'Корейский',
  'Арабский'
];

const otherTechnicalSkills = [
  'API',
  'REST',
  'GraphQL',
  'SOAP',
  'Kafka',
  'RabbitMQ',
  'PostgreSQL',
  'MySQL',
  'MongoDB',
  'Redis',
  'Docker',
  'Kubernetes',
  'AWS',
  'Azure',
  'GCP',
  'Git',
  'Jenkins',
  'JIRA',
  'Confluence',
  'Postman',
  'Swagger',
  'Linux',
  'Windows Server',
  'Nginx',
  'Apache'
];

const programmingLanguages = [
  'Python',
  'Java',
  'JavaScript',
  'TypeScript', 
  'C#',
  'C++',
  'PHP',
  'Ruby',
  'Go',
  'Rust',
  'Swift',
  'Kotlin',
  'Scala',
  'R',
  'MATLAB',
  'SQL',
  'HTML/CSS',
  'Shell/Bash'
];

export function ProfileForm() {
  const [profileData, setProfileData] = useState<ProfileData>({
    basicInfo: {
      department: '',
      position: '',
      grade: '',
      itExperience: ''
    },
    currentRole: {
      specialization: '',
      functionalRole: '',
      responsibilities: []
    },
    workExperience: [],
    education: {
      institution: '',
      degree: '',
      specialization: '',
      graduationYear: ''
    },
    skills: [],
    competencies: [],
    foreignLanguages: [],
    otherCompetencies: [],
    programmingLanguages: []
  });

  const addWorkExperience = () => {
    setProfileData(prev => ({
      ...prev,
      workExperience: [...prev.workExperience, {
        position: '',
        company: '',
        location: '',
        startDate: '',
        endDate: '',
        duration: '',
        responsibilities: []
      }]
    }));
  };

  const removeWorkExperience = (index: number) => {
    setProfileData(prev => ({
      ...prev,
      workExperience: prev.workExperience.filter((_, i) => i !== index)
    }));
  };

  const updateWorkExperience = (index: number, field: keyof WorkExperience, value: any) => {
    setProfileData(prev => ({
      ...prev,
      workExperience: prev.workExperience.map((exp, i) => 
        i === index ? { ...exp, [field]: value } : exp
      )
    }));
  };

  const toggleSkill = (skill: string) => {
    setProfileData(prev => ({
      ...prev,
      skills: prev.skills.includes(skill) 
        ? prev.skills.filter(s => s !== skill)
        : [...prev.skills, skill]
    }));
  };

  const toggleCompetency = (competency: string) => {
    setProfileData(prev => ({
      ...prev,
      competencies: prev.competencies.includes(competency)
        ? prev.competencies.filter(c => c !== competency)
        : [...prev.competencies, competency]
    }));
  };

  const addForeignLanguage = () => {
    setProfileData(prev => ({
      ...prev,
      foreignLanguages: [...prev.foreignLanguages, { language: '', level: '' }]
    }));
  };

  const removeForeignLanguage = (index: number) => {
    setProfileData(prev => ({
      ...prev,
      foreignLanguages: prev.foreignLanguages.filter((_, i) => i !== index)
    }));
  };

  const updateForeignLanguage = (index: number, field: keyof LanguageSkill, value: string) => {
    setProfileData(prev => ({
      ...prev,
      foreignLanguages: prev.foreignLanguages.map((lang, i) => 
        i === index ? { ...lang, [field]: value } : lang
      )
    }));
  };

  const addOtherCompetency = () => {
    setProfileData(prev => ({
      ...prev,
      otherCompetencies: [...prev.otherCompetencies, { skill: '', level: '' }]
    }));
  };

  const removeOtherCompetency = (index: number) => {
    setProfileData(prev => ({
      ...prev,
      otherCompetencies: prev.otherCompetencies.filter((_, i) => i !== index)
    }));
  };

  const updateOtherCompetency = (index: number, field: keyof TechnicalSkill, value: string) => {
    setProfileData(prev => ({
      ...prev,
      otherCompetencies: prev.otherCompetencies.map((skill, i) => 
        i === index ? { ...skill, [field]: value } : skill
      )
    }));
  };

  const addProgrammingLanguage = () => {
    setProfileData(prev => ({
      ...prev,
      programmingLanguages: [...prev.programmingLanguages, { skill: '', level: '' }]
    }));
  };

  const removeProgrammingLanguage = (index: number) => {
    setProfileData(prev => ({
      ...prev,
      programmingLanguages: prev.programmingLanguages.filter((_, i) => i !== index)
    }));
  };

  const updateProgrammingLanguage = (index: number, field: keyof TechnicalSkill, value: string) => {
    setProfileData(prev => ({
      ...prev,
      programmingLanguages: prev.programmingLanguages.map((lang, i) => 
        i === index ? { ...lang, [field]: value } : lang
      )
    }));
  };

  const exportToJSON = () => {
    const dataStr = JSON.stringify(profileData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'profile-data.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1>АНКЕТА 3 - Профиль сотрудника</h1>
        <Button onClick={exportToJSON} className="flex items-center gap-2">
          <Download className="w-4 h-4" />
          Экспорт JSON
        </Button>
      </div>

      {/* Основная информация */}
      <Card>
        <CardHeader>
          <CardTitle>Основная информация</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="department">Подразделение:</Label>
              <Input
                id="department"
                value={profileData.basicInfo.department}
                onChange={(e) => setProfileData(prev => ({
                  ...prev,
                  basicInfo: { ...prev.basicInfo, department: e.target.value }
                }))}
              />
            </div>
            <div>
              <Label htmlFor="position">Должность:</Label>
              <Input
                id="position"
                value={profileData.basicInfo.position}
                onChange={(e) => setProfileData(prev => ({
                  ...prev,
                  basicInfo: { ...prev.basicInfo, position: e.target.value }
                }))}
              />
            </div>
            <div>
              <Label htmlFor="grade">Грейд:</Label>
              <Input
                id="grade"
                value={profileData.basicInfo.grade}
                onChange={(e) => setProfileData(prev => ({
                  ...prev,
                  basicInfo: { ...prev.basicInfo, grade: e.target.value }
                }))}
              />
            </div>
            <div>
              <Label htmlFor="itExperience">Опыт работы в ТТ:</Label>
              <Input
                id="itExperience"
                value={profileData.basicInfo.itExperience}
                onChange={(e) => setProfileData(prev => ({
                  ...prev,
                  basicInfo: { ...prev.basicInfo, itExperience: e.target.value }
                }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Текущие роли */}
      <Card>
        <CardHeader>
          <CardTitle>Текущие роли</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="specialization">Специализация:</Label>
            <Select
              value={profileData.currentRole.specialization}
              onValueChange={(value) => setProfileData(prev => ({
                ...prev,
                currentRole: { ...prev.currentRole, specialization: value }
              }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Выберите спец��ализацию" />
              </SelectTrigger>
              <SelectContent>
                {technicalSpecialties.map(specialty => (
                  <SelectItem key={specialty} value={specialty}>
                    {specialty}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label htmlFor="functionalRole">Функциональная роль:</Label>
            <Input
              id="functionalRole"
              value={profileData.currentRole.functionalRole}
              onChange={(e) => setProfileData(prev => ({
                ...prev,
                currentRole: { ...prev.currentRole, functionalRole: e.target.value }
              }))}
            />
          </div>

          <div>
            <Label>Обязанности:</Label>
            <Textarea
              placeholder="Опишите основные обязанности..."
              value={profileData.currentRole.responsibilities.join('\n')}
              onChange={(e) => setProfileData(prev => ({
                ...prev,
                currentRole: { 
                  ...prev.currentRole, 
                  responsibilities: e.target.value.split('\n').filter(r => r.trim()) 
                }
              }))}
              rows={6}
            />
          </div>
        </CardContent>
      </Card>

      {/* Предыдущий опыт работы */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Предыдущий опыт работы
            <Button onClick={addWorkExperience} variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Добавить опыт
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {profileData.workExperience.map((exp, index) => (
            <div key={index} className="p-4 border rounded-lg space-y-4">
              <div className="flex items-center justify-between">
                <h4>Опыт работы #{index + 1}</h4>
                <Button
                  onClick={() => removeWorkExperience(index)}
                  variant="outline"
                  size="sm"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Роль/Должность:</Label>
                  <Input
                    value={exp.position}
                    onChange={(e) => updateWorkExperience(index, 'position', e.target.value)}
                  />
                </div>
                <div>
                  <Label>Компания:</Label>
                  <Input
                    value={exp.company}
                    onChange={(e) => updateWorkExperience(index, 'company', e.target.value)}
                  />
                </div>
                <div>
                  <Label>Период работы (начало):</Label>
                  <Input
                    type="month"
                    value={exp.startDate}
                    onChange={(e) => updateWorkExperience(index, 'startDate', e.target.value)}
                  />
                </div>
                <div>
                  <Label>Период работы (конец):</Label>
                  <Input
                    type="month"
                    value={exp.endDate}
                    onChange={(e) => updateWorkExperience(index, 'endDate', e.target.value)}
                  />
                </div>
                <div>
                  <Label>Место работы:</Label>
                  <Input
                    value={exp.location}
                    onChange={(e) => updateWorkExperience(index, 'location', e.target.value)}
                  />
                </div>
                <div>
                  <Label>Длительность:</Label>
                  <Input
                    value={exp.duration}
                    onChange={(e) => updateWorkExperience(index, 'duration', e.target.value)}
                    placeholder="напр. 1 год 5 месяцев"
                  />
                </div>
              </div>
              
              <div>
                <Label>Обязанности:</Label>
                <Textarea
                  value={exp.responsibilities.join('\n')}
                  onChange={(e) => updateWorkExperience(index, 'responsibilities', 
                    e.target.value.split('\n').filter(r => r.trim()))}
                  rows={4}
                  placeholder="Опишите основные обязанности и достижения..."
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Образование */}
      <Card>
        <CardHeader>
          <CardTitle>Образование</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="institution">Название учебного заведения:</Label>
            <Input
              id="institution"
              value={profileData.education.institution}
              onChange={(e) => setProfileData(prev => ({
                ...prev,
                education: { ...prev.education, institution: e.target.value }
              }))}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="degree">Уровень образования:</Label>
              <Select
                value={profileData.education.degree}
                onValueChange={(value) => setProfileData(prev => ({
                  ...prev,
                  education: { ...prev.education, degree: value }
                }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите уровень" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bachelor">Бакалавриат</SelectItem>
                  <SelectItem value="specialist">Специалитет</SelectItem>
                  <SelectItem value="master">Магистратура</SelectItem>
                  <SelectItem value="phd">Аспирантура</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="graduationYear">Год окончания:</Label>
              <Input
                id="graduationYear"
                type="number"
                value={profileData.education.graduationYear}
                onChange={(e) => setProfileData(prev => ({
                  ...prev,
                  education: { ...prev.education, graduationYear: e.target.value }
                }))}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="educationSpecialization">Специальность:</Label>
            <Input
              id="educationSpecialization"
              value={profileData.education.specialization}
              onChange={(e) => setProfileData(prev => ({
                ...prev,
                education: { ...prev.education, specialization: e.target.value }
              }))}
            />
          </div>
        </CardContent>
      </Card>

      {/* Знания и навыки */}
      <Card>
        <CardHeader>
          <CardTitle>Знания и навыки</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h4>Выберите ваши компетенции и навыки:</h4>
            <div className="grid grid-cols-1 gap-3 mt-4 max-h-96 overflow-y-auto">
              {skillsAndCompetencies.map(skill => (
                <div key={skill} className="flex items-start space-x-2">
                  <Checkbox
                    id={skill}
                    checked={profileData.competencies.includes(skill)}
                    onCheckedChange={() => toggleCompetency(skill)}
                  />
                  <Label htmlFor={skill} className="cursor-pointer leading-tight">
                    {skill}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          <div>
            <h4>Выбранные компетенции:</h4>
            <div className="flex flex-wrap gap-2 mt-2">
              {profileData.competencies.map(competency => (
                <Badge key={competency} variant="secondary" className="cursor-pointer"
                       onClick={() => toggleCompetency(competency)}>
                  {competency} ×
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Иностранные языки */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Иностранные языки
            <Button onClick={addForeignLanguage} variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Добавить язык
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {profileData.foreignLanguages.map((lang, index) => (
            <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
              <div className="flex-1">
                <Label>Язык:</Label>
                <Select
                  value={lang.language}
                  onValueChange={(value) => updateForeignLanguage(index, 'language', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите язык" />
                  </SelectTrigger>
                  <SelectContent>
                    {languages.map(language => (
                      <SelectItem key={language} value={language}>
                        {language}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex-1">
                <Label>Уровень:</Label>
                <Select
                  value={lang.level}
                  onValueChange={(value) => updateForeignLanguage(index, 'level', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите уровень" />
                  </SelectTrigger>
                  <SelectContent>
                    {proficiencyLevels.map(level => (
                      <SelectItem key={level} value={level}>
                        {level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => removeForeignLanguage(index)}
                variant="outline"
                size="sm"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
          {profileData.foreignLanguages.length === 0 && (
            <div className="text-center py-6 text-muted-foreground">
              Нажмите "Добавить язык" чтобы указать знание иностранных языков
            </div>
          )}
        </CardContent>
      </Card>

      {/* Прочие компетенции */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Прочие компетенции
            <Button onClick={addOtherCompetency} variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Добавить компетенцию
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {profileData.otherCompetencies.map((skill, index) => (
            <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
              <div className="flex-1">
                <Label>Компетенция:</Label>
                <Select
                  value={skill.skill}
                  onValueChange={(value) => updateOtherCompetency(index, 'skill', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите компетенцию" />
                  </SelectTrigger>
                  <SelectContent>
                    {otherTechnicalSkills.map(techSkill => (
                      <SelectItem key={techSkill} value={techSkill}>
                        {techSkill}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex-1">
                <Label>Уровень:</Label>
                <Select
                  value={skill.level}
                  onValueChange={(value) => updateOtherCompetency(index, 'level', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите уровень" />
                  </SelectTrigger>
                  <SelectContent>
                    {proficiencyLevels.map(level => (
                      <SelectItem key={level} value={level}>
                        {level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => removeOtherCompetency(index)}
                variant="outline"
                size="sm"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
          {profileData.otherCompetencies.length === 0 && (
            <div className="text-center py-6 text-muted-foreground">
              Нажмите "Добавить компетенцию" чтобы указать дополнительные технические навыки
            </div>
          )}
        </CardContent>
      </Card>

      {/* Языки программирования */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Языки программирования
            <Button onClick={addProgrammingLanguage} variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Добавить язык
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {profileData.programmingLanguages.map((lang, index) => (
            <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
              <div className="flex-1">
                <Label>Язык программирования:</Label>
                <Select
                  value={lang.skill}
                  onValueChange={(value) => updateProgrammingLanguage(index, 'skill', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите язык" />
                  </SelectTrigger>
                  <SelectContent>
                    {programmingLanguages.map(progLang => (
                      <SelectItem key={progLang} value={progLang}>
                        {progLang}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex-1">
                <Label>Уровень:</Label>
                <Select
                  value={lang.level}
                  onValueChange={(value) => updateProgrammingLanguage(index, 'level', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите уровень" />
                  </SelectTrigger>
                  <SelectContent>
                    {proficiencyLevels.map(level => (
                      <SelectItem key={level} value={level}>
                        {level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => removeProgrammingLanguage(index)}
                variant="outline"
                size="sm"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
          {profileData.programmingLanguages.length === 0 && (
            <div className="text-center py-6 text-muted-foreground">
              Нажмите "Добавить язык" чтобы указать знание языков программирования
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}