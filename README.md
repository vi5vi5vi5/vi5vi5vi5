<!--
  Профиль vi5vi5vi5. Картинки в assets/ собирает build.py:
  поправь блок НАСТРОЙКИ в нём и запусти `python build.py`.
  Тема (калька/синька) переключается сама под тему GitHub у зрителя.
-->

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/header-light.svg">
    <img alt="Vi5 — backend-разработчик: сетевые сервисы, realtime, self-hosted. Схема: отправитель → релей → N получателей" src="assets/header-light.svg" width="100%">
  </picture>
</p>

Делаю сетевые сервисы на C++ и Python: релеи, видеосвязь, свои протоколы поверх WebSocket. Довожу их до продакшена сам: Docker, nginx, сертификаты, собственный VPS. Сейчас учу Go и иду в бэкенд.

<p align="center">
  <a href="https://github.com/vi5vi5vi5/Ferry"><picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/card-ferry-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/card-ferry-light.svg">
    <img alt="Ferry — релей больших файлов без хранения, E2E-шифрование, раздача N получателям при одной отдаче" src="assets/card-ferry-light.svg" width="49%">
  </picture></a>
  <a href="https://github.com/vi5vi5vi5/MeetUp"><picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/card-meetup-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/card-meetup-light.svg">
    <img alt="MeetUp — видеозвонки на своём сервере, E2E-шифрование, демо на meetup.fferry.ru" src="assets/card-meetup-light.svg" width="49%">
  </picture></a>
</p>

**[Ferry](https://github.com/vi5vi5vi5/Ferry)** — релей файлов и папок любого размера. Сервер ничего не пишет на диск и видит только шифротекст, а отправитель отдаёт том один раз, сколько бы ни было получателей.

**[MeetUp](https://github.com/vi5vi5vi5/MeetUp)** — видеозвонки, которые живут на вашем сервере. Сервер-ретранслятор на C++20/Qt6, веб-клиент на WebCodecs и нативный клиент для Windows. Попробовать: **[meetup.fferry.ru](https://meetup.fferry.ru)**.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/spec-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/spec-light.svg">
    <img alt="Спецификация стека: C++20, Python, C#, Go (изучаю); WebSocket, HTTP API, TLS, nginx, AES-256-GCM, BLAKE3; Docker, Linux, CMake, SQLite" src="assets/spec-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <a href="https://t.me/vi5vi5vi5">Telegram @vi5vi5vi5</a> · <a href="https://meetup.fferry.ru">демо MeetUp</a>
</p>
