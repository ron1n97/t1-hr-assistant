"""
Данные кандидатов для HR системы
"""

from models import Candidate, Experience

# Моковые данные кандидатов
MOCK_CANDIDATES = [
    Candidate(
        id='1',
        name='Матвеев Георг Петрович',
        position='Senior Front-end developer',
        salary='200 000 ₽',
        age=29,
        location='Москва',
        phone='+7 (962) 123-22-45',
        email='georgentrevkh@gmail.ru',
        telegram='@georgentrevkh',
        skills=['Front-end', 'Angular', 'JavaScript', 'TypeScript', 'React'],
        experience=[
            Experience(
                company='Яндекс',
                position='Senior Front-end developer',
                period='Февраль 2017 — по настоящее время',
                description='Управление разработкой клиентской части iModule 5+1 и мобильного приложения (React Native)',
                current=True
            )
        ],
        createdAt='22 февраля 2021',
        status='interview'
    ),
    Candidate(
        id='2',
        name='Носов Роман Борисович',
        position='Backend Developer',
        salary='180 000 ₽',
        age=32,
        location='Москва',
        phone='+7 (905) 456-78-90',
        email='r.nosov@example.com',
        telegram='@rnosov',
        skills=['Python', 'Django', 'PostgreSQL', 'Redis'],
        experience=[
            Experience(
                company='VK',
                position='Backend Developer',
                period='Январь 2019 — по настоящее время',
                description='Разработка высоконагруженных сервисов',
                current=True
            )
        ],
        createdAt='15 февраля 2021',
        status='new'
    ),
    Candidate(
        id='3',
        name='Обухов Павел Петрович',
        position='DevOps Engineer',
        salary='220 000 ₽',
        age=28,
        location='Санкт-Петербург',
        phone='+7 (812) 234-56-78',
        email='p.obukhov@example.com',
        telegram='@pobukhov',
        skills=['Docker', 'Kubernetes', 'AWS', 'Terraform'],
        experience=[
            Experience(
                company='Сбер',
                position='DevOps Engineer',
                period='Март 2020 — по настоящее время',
                description='Автоматизация процессов разработки и развертывания',
                current=True
            )
        ],
        createdAt='10 февраля 2021',
        status='in-progress'
    ),
    Candidate(
        id='4',
        name='Строкова Елена Алексеевна',
        position='Product Manager',
        salary='250 000 ₽',
        age=31,
        location='Москва',
        phone='+7 (926) 789-01-23',
        email='e.strokova@example.com',
        telegram='@estrokova',
        skills=['Product Management', 'Analytics', 'Agile', 'Figma'],
        experience=[
            Experience(
                company='Тинькофф',
                position='Senior Product Manager',
                period='Июнь 2019 — по настоящее время',
                description='Управление продуктовой линейкой мобильных приложений',
                current=True
            )
        ],
        createdAt='5 февраля 2021',
        status='offer'
    )
]
