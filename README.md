**Менеджер Сети** — это настольное приложение для Windows, предназначенное для быстрого управления DNS и базовыми сетевыми настройками через удобный графический интерфейс.
* **Network Manager** is a desktop application for Windows designed to quickly manage DNS and basic network settings through an easy-to-use graphical interface.

## Скриншоты
<p align="center">
  <img src="https://github.com/user-attachments/assets/fc234dee-77a6-40f7-9268-13ccc0bbba37" width="32%">
  <img src="https://github.com/user-attachments/assets/c8543bbd-02f4-44d0-9ad8-4c5cc8e2d4e6" width="32%">
  <img src="https://github.com/user-attachments/assets/9a258b2e-da77-4997-8eaa-edceef65086a" width="32%">
</p>

## Функционал

### DNS Менеджер

* Применение DNS-серверов вручную (Primary / Secondary)
* Встроенные пресеты:

  * Google DNS
  * Cloudflare DNS
  * Comss DNS (dns.comss.one)
  * Xbox DNS (xbox-dns.ru)
* Создание и удаление пользовательских пресетов
* Автоматическое определение активного сетевого адаптера
* Сброс DNS к автоматическим настройкам (DHCP)
* Очистка DNS-кэша (`ipconfig /flushdns`)
* Логирование всех операций

### Сброс сети

* Очистка DNS-кэша
* Освобождение IP (`ipconfig /release`)
* Обновление IP (`ipconfig /renew`)
* Сброс Winsock (`netsh winsock reset`)
* Сброс TCP/IP (`netsh int ip reset`)
* Отображение результатов выполнения команд

### Интерфейс

* GUI на базе `tkinter`
* Вкладочная структура (DNS / Сброс / Справка)
* Всплывающие подсказки с описанием команд
* Простое управление без необходимости использовать командную строку

## Особенности

* Все операции выполняются локально
* Отсутствует передача данных на внешние серверы
* Минимальные системные требования
* Быстрый доступ к основным сетевым функциям Windows

## Требования

* Windows 10 / 11
* Python 3.10+ (для запуска из исходников)
* Права администратора (обязательно для изменения сетевых настроек)

## Сборка в EXE

```bash
pyinstaller --noconsole --onefile Network_Manager_1_1.py
```

## Предупреждение VirusTotal

Некоторые антивирусные программы могут помечать исполняемый файл как подозрительный.

Это ложные срабатывания, вызванные:
- упаковкой через PyInstaller
- использованием системных сетевых команд (netsh, ipconfig)
- необходимостью запуска с правами администратора

Исходный код полностью открыт и доступен для проверки.

При желании вы можете самостоятельно собрать программу из исходников:
```bash
pyinstaller --noconsole --onefile Network_Manager_1.1.py
```
После сборки результат будет аналогично определяться антивирусами, что подтверждает отсутствие вредоносного кода.

## Автор

Solar Svarga
GitHub: [https://github.com/solarsvarga](https://github.com/solarsvarga)
