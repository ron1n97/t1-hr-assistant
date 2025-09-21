import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Send, Bot, User, Loader2, Mic } from 'lucide-react';
import { apiClient } from '../api/client';
import { AudioRecorder } from './AudioRecorder';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Привет! Я ваш ИИ-помощник по развитию карьеры. Я могу помочь вам с анализом вашего профиля, рекомендациями по развитию навыков и планированием карьерного роста. О чем бы вы хотели поговорить?',
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [conversationId] = useState(() => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');

    const newUserMessage: Message = {
      id: Date.now().toString(),
      content: userMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await apiClient.sendUserMessage(userMessage, conversationId);
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Ошибка при отправке сообщения:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.',
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };


  const handleAudioRecording = async (audioBlob: Blob) => {
    setIsTranscribing(true);
    
    try {
      // Создаем файл из blob
      const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
      
      // Отправляем на транскрипцию
      const response = await apiClient.transcribeAudio(audioFile, 'user', conversationId);
      
      // Добавляем транскрибированный текст как сообщение пользователя
      const userMessage: Message = {
        id: Date.now().toString(),
        content: response.text,
        sender: 'user',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Если есть ответ от агента, добавляем его
      if (response.chat_response) {
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: response.chat_response.response,
          sender: 'ai',
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, aiResponse]);
      }
      
    } catch (error) {
      console.error('Ошибка при транскрипции аудио:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Извините, произошла ошибка при обработке голосового сообщения. Попробуйте еще раз.',
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 h-[calc(100vh-5rem)]">
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            Чат с ИИ-помощником по карьере
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col gap-4">
          <ScrollArea className="flex-1 pr-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    {message.sender === 'user' ? (
                      <User className="w-4 h-4 text-primary-foreground" />
                    ) : (
                      <Bot className="w-4 h-4 text-primary-foreground" />
                    )}
                  </div>
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      message.sender === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="leading-relaxed">{message.content}</p>
                    <p className="text-xs mt-2 opacity-70">
                      {message.timestamp.toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          <div className="space-y-2">
            <div className="flex gap-2">
              <Input
                placeholder="Напишите ваш вопрос..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
                disabled={isTranscribing}
              />
              <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isLoading || isTranscribing}>
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            
            <div className="flex items-center gap-2">
              <Mic className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Или используйте голосовой ввод:</span>
              <AudioRecorder 
                onRecordingComplete={handleAudioRecording}
                onError={(error) => console.error('Ошибка записи:', error)}
                disabled={isLoading || isTranscribing}
              />
              {isTranscribing && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Обработка аудио...
                </div>
              )}
            </div>
          </div>

          <div className="text-sm text-muted-foreground">
            <p>💡 <strong>Подсказки для вопросов:</strong></p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>"Какие навыки мне стоит развивать дальше?"</li>
              <li>"Как улучшить мой профиль для карьерного роста?"</li>
              <li>"Какие курсы или сертификации вы рекомендуете?"</li>
              <li>"Как подготовиться к собеседованию на позицию senior аналитика?"</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}