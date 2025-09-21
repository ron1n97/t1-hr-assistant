import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Calendar, Clock, Video, MapPin, Plus, ChevronLeft, ChevronRight } from 'lucide-react';

interface InterviewEvent {
  id: string;
  candidateName: string;
  position: string;
  type: 'technical' | 'hr' | 'final';
  format: 'online' | 'offline' | 'phone';
  date: Date;
  duration: number; // minutes
  status: 'scheduled' | 'completed' | 'cancelled';
  interviewer: string;
  location?: string;
  meetingLink?: string;
}

const mockInterviews: InterviewEvent[] = [
  {
    id: '1',
    candidateName: 'Матвеев Георг Петрович',
    position: 'Senior Front-end Developer',
    type: 'technical',
    format: 'online',
    date: new Date(2025, 0, 21, 10, 0), // Jan 21, 2025, 10:00
    duration: 60,
    status: 'scheduled',
    interviewer: 'Алексей Петров',
    meetingLink: 'https://meet.google.com/abc-def-ghi'
  },
  {
    id: '2',
    candidateName: 'Носов Роман Борисович',
    position: 'Backend Developer',
    type: 'hr',
    format: 'offline',
    date: new Date(2025, 0, 21, 14, 30), // Jan 21, 2025, 14:30
    duration: 45,
    status: 'scheduled',
    interviewer: 'Мария Иванова',
    location: 'Офис, переговорная 2'
  },
  {
    id: '3',
    candidateName: 'Строкова Елена Алексеевна',
    position: 'Product Manager',
    type: 'final',
    format: 'online',
    date: new Date(2025, 0, 22, 11, 0), // Jan 22, 2025, 11:00
    duration: 90,
    status: 'scheduled',
    interviewer: 'Сергей Козлов',
    meetingLink: 'https://zoom.us/j/123456789'
  },
  {
    id: '4',
    candidateName: 'Обухов Павел Петрович',
    position: 'DevOps Engineer',
    type: 'technical',
    format: 'phone',
    date: new Date(2025, 0, 20, 16, 0), // Jan 20, 2025, 16:00
    duration: 30,
    status: 'completed',
    interviewer: 'Алексей Петров'
  }
];

const interviewTypeLabels = {
  technical: 'Техническое',
  hr: 'HR интервью',
  final: 'Финальное'
};

const interviewTypeColors = {
  technical: 'bg-blue-100 text-blue-800',
  hr: 'bg-green-100 text-green-800',
  final: 'bg-purple-100 text-purple-800'
};

const statusLabels = {
  scheduled: 'Запланировано',
  completed: 'Завершено',
  cancelled: 'Отменено'
};

const statusColors = {
  scheduled: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800'
};

export function CalendarPage() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'day' | 'week' | 'month'>('day');

  const todayInterviews = mockInterviews.filter(interview => {
    const today = new Date();
    return interview.date.toDateString() === today.toDateString() && 
           interview.status === 'scheduled';
  });

  const upcomingInterviews = mockInterviews.filter(interview => {
    const today = new Date();
    return interview.date > today && interview.status === 'scheduled';
  }).sort((a, b) => a.date.getTime() - b.date.getTime());

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('ru-RU', { 
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1>Календарь собеседований</h1>
          <p className="text-muted-foreground">Планирование и управление интервью</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Новое собеседование
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar Widget */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Январь 2025</CardTitle>
              <div className="flex gap-1">
                <Button variant="ghost" size="sm">
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm">
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-7 gap-1 text-center text-sm">
              {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map(day => (
                <div key={day} className="p-2 font-medium text-muted-foreground">
                  {day}
                </div>
              ))}
              {Array.from({ length: 31 }, (_, i) => i + 1).map(date => (
                <Button
                  key={date}
                  variant={date === 21 ? 'default' : 'ghost'}
                  size="sm"
                  className="h-8 w-8 p-0 text-sm"
                >
                  {date}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Today's Interviews */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Сегодняшние собеседования
            </CardTitle>
          </CardHeader>
          <CardContent>
            {todayInterviews.length > 0 ? (
              <div className="space-y-4">
                {todayInterviews.map(interview => (
                  <div key={interview.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <Avatar className="w-10 h-10">
                          <AvatarFallback>
                            {interview.candidateName.split(' ').map(n => n[0]).join('').slice(0, 2)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <h4 className="font-medium">{interview.candidateName}</h4>
                          <p className="text-sm text-muted-foreground">{interview.position}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-1 text-sm mb-1">
                          <Clock className="w-4 h-4" />
                          {formatTime(interview.date)} ({interview.duration} мин)
                        </div>
                        <Badge className={interviewTypeColors[interview.type]}>
                          {interviewTypeLabels[interview.type]}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>Интервьюер: {interview.interviewer}</span>
                        <div className="flex items-center gap-1">
                          {interview.format === 'online' && <Video className="w-4 h-4" />}
                          {interview.format === 'offline' && <MapPin className="w-4 h-4" />}
                          <span>
                            {interview.format === 'online' ? 'Онлайн' : 
                             interview.format === 'offline' ? interview.location :
                             'Телефон'}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          Изменить
                        </Button>
                        <Button size="sm">
                          Начать
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Calendar className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p>Сегодня собеседований не запланировано</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Interviews */}
      <Card>
        <CardHeader>
          <CardTitle>Предстоящие собеседования</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {upcomingInterviews.map(interview => (
              <div key={interview.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center gap-4">
                  <Avatar className="w-12 h-12">
                    <AvatarFallback>
                      {interview.candidateName.split(' ').map(n => n[0]).join('').slice(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h4 className="font-medium">{interview.candidateName}</h4>
                    <p className="text-sm text-muted-foreground">{interview.position}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={interviewTypeColors[interview.type]} variant="secondary">
                        {interviewTypeLabels[interview.type]}
                      </Badge>
                      <Badge className={statusColors[interview.status]} variant="secondary">
                        {statusLabels[interview.status]}
                      </Badge>
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="font-medium">{formatDate(interview.date)}</div>
                  <div className="text-sm text-muted-foreground">
                    {formatTime(interview.date)} ({interview.duration} мин)
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {interview.interviewer}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-blue-600">12</div>
            <p className="text-sm text-muted-foreground">Собеседований на неделе</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-green-600">8</div>
            <p className="text-sm text-muted-foreground">Завершено</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-yellow-600">4</div>
            <p className="text-sm text-muted-foreground">Запланировано</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-purple-600">67%</div>
            <p className="text-sm text-muted-foreground">Успешность прохождения</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}