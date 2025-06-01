from dublib.Methods.Filesystem import ReadTextFile
from dublib.WebRequestor import Protocols
from dublib.Polyglot import HTML

from typing import Any
import random
import signal
import types
import enum
import time
import os
import re

from g4f.client import Client

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class TimeoutException(Exception): pass

class Errors(enum.Enum):
	"""Перечисление ошибок генерации."""

	MaxLengthExceeded = "max_length_exceeded"
	EmptyResponse = "empty_response"
	IncorrectResponseLanguage = "incorrect_response_language"
	RequestBlocked = "request_blocked"
	TimeoutReached = "timeout_reached"

class Languages(enum.Enum):
	"""Перечисление поддерживаемых языков."""

	Russian = "ru"
	English = "en"

	Undefined = None

class Options:
	"""Опции генерации."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def force_proxy(self) -> bool:
		"""Состояние: нужно ли использовать для всех запросов случайный прокси."""

		return self.__ForceProxy

	@property
	def language(self) -> Languages | None:
		"""Код языка ответа по стандарту ISO 639-1."""

		return self.__Language

	@property
	def max_length(self) -> int | None:
		"""Максимальная длина ответа."""

		return self.__MaxLength

	@property
	def model(self) -> str:
		"""Используемая модель нейросети."""

		return self.__Model

	@property
	def only_plaint_text(self) -> bool:
		"""Состояние: требуется ли вернуть только чистый текст без HTML тегов."""

		return True
	
	@property
	def timeout(self) -> int:
		"""Время ожидания ответа."""

		return self.__Timeout

	@property
	def tries(self) -> int:
		"""Количество попыток получения валидного ответа."""

		return self.__Tries

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Опции генерации."""

		self.__Language: Languages | None = None
		self.__MaxLength: int | None = None
		self.__Timeout: int = 30
		self.__Tries = 3
		self.__Model = "gpt-4o"
		self.__ForceProxy = False

	def set_force_proxy(self, status: bool | None):
		"""
		Переключает использование прокси для всех запросов.

		:param status: Статус использования прокси. По умолчанию `False`, что соответствует использованию прокси только в случае блокировки запроса.
		:type status: bool | None
		"""

		self.__ForceProxy = bool(status)

	def set_language(self, language: Languages | str | None):
		"""
		Зазадёт код языка ответа по стандарту ISO 639-1.

		:param language: Двухсимвольный код языка ответа по стандарту ISO 639-1 или `None` для пропуска валидации языка.
		:type language: str | None
		"""

		if type(language) == str:
			if len(language) != 2: raise ValueError("ISO 639-1 requires two characters.")
			language = Languages(language)

		self.__Language = language

	def set_max_length(self, length: int | None):
		"""
		Зазадёт максимальную длину ответа.

		:param length: Длина ответа в символах Unicode.
		:type length: int | None
		"""

		self.__MaxLength = length

	def set_model(self, model: str | None):
		"""
		Зазадёт используемую модель.

		:param model: Название модели. Полный список [здесь](https://github.com/gpt4free/gpt4free.github.io/blob/main/docs%2Fproviders-and-models.md). По умолчанию `gpt-4o`.
		:type model: str | None
		"""

		self.__Model = model or "gpt-4o"

	def set_timeout(self, timeout: int | None):
		"""
		Задаёт тайм-аут генерации ответа.

		:param timeout: Тайм-аут в секундах. При указании `None` используется значение по умолчанию: 30.
		:type timeout: int | None
		"""

		if not timeout: timeout = 30
		self.__Timeout = timeout

	def set_tries(self, tries: int | None):
		"""
		Задаёт количество попыток получения валидного ответа.

		:param tries: Количество попыток. При указании `None` используется значение по умолчанию: 3.
		:type tries: int | None
		"""

		if not tries: tries = 3
		self.__Tries = tries

class Proxy:
	"""Данные прокси-сервера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def protocol(self) -> Protocols | None:
		"""Тип протокола подключения."""

		return self.__Protocol
	
	@property
	def host(self) -> str | None:
		"""IP адрес или домен хоста."""

		return self.__Host
	
	@property
	def port(self) -> int | None:
		"""Номер порта."""

		return self.__Port
	
	@property
	def login(self) -> str | None:
		"""Логин."""

		return self.__Login
	
	@property
	def password(self) -> str | None:
		"""Пароль."""

		return self.__Password

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, protocol: Protocols | None = None, host: str | None = None, port: int | str | None = None, login: str | None = None, password: str | None = None):
		"""
		Данные прокси-сервера.

		:param protocol: Тип протокола подключения.
		:type protocol: Protocols | None, optional
		:param host: IP адрес или домен хоста.
		:type host: str | None, optional
		:param port: Номер порта.
		:type port: int | str | None, optional
		:param login: Логин.
		:type login: str | None, optional
		:param password: Пароль.
		:type password: str | None, optional
		"""

		self.__Protocol = protocol
		self.__Host = host
		self.__Port = port
		self.__Login = login
		self.__Password = password

	def parse(self, proxy: str) -> "Proxy":
		"""
		Парсит данные прокси из строки вида `protocol://username:password@host:port`.

		:param proxy: Строка с данными прокси.
		:type proxy: str
		:return: Текущий объект данных прокси-сервера.
		:rtype: Proxy
		"""

		ProtocolPart, ProxyPart = proxy.split("://")
		LoginPart, HostPart = (None, None)

		if "@" in ProxyPart: LoginPart, HostPart = ProxyPart.split("@")
		else: HostPart = ProxyPart

		Host, Port = HostPart.split(":")
		Login, Password = (None, None)

		if LoginPart: Login, Password = LoginPart.split(":")

		self.__Protocol = Protocols(ProtocolPart.lower())
		self.__Host = Host
		self.__Port = int(Port)
		self.__Login = Login
		self.__Password = Password

		return self

	def to_dict(self, force_http: bool = True) -> dict[str, str]:
		"""
		Строит словарь для подключения прокси к **requests**-подобным библиотекам.

		:param force_http: Большинство прокси неверно работают при использовании протокола HTTPS. 
		При включённом состоянии для HTTPS-соединения **requests** будет использоваться `http://{proxy}` соединение.
		:type force_http: bool, optional
		:return: Словарь данных прокси для подключения к **requests**-подобным библиотекам.
		:rtype: dict[str, str]
		"""

		Authorization = f"{self.__Login}:{self.__Password}@" if self.__Login and self.__Password else ""
		ProxyString = f"{self.__Protocol.value}://{Authorization}{self.__Host}:{self.__Port}"

		ProxyDict = dict()

		if self.__Protocol.value.startswith("http"):
			ProxyDict["http"] = ProxyString.replace("https", "http")
			if self.__Protocol == Protocols.HTTPS: ProxyDict["https"] = ProxyString.replace("https", "http") if force_http else ProxyString

		else: ProxyDict = {self.__Protocol.value: ProxyString}

		return ProxyDict

class Response:
	"""Контейнер ответа нейросети."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def text(self) -> str | None:
		"""Текст ответа нейросети."""

		return self.__Text
	
	@property
	def current_try(self) -> int:
		"""Номер текущей попытки генерации."""

		return self.__CurrentTry

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""
		Контейнер ответа нейросети.

		:param text: Текст ответа. По умолчанию 'None'.
		:type text: str | None, optional
		"""

		self.__Text = None
		self.__Time = None
		self.__CurrentTry = 1
		self.__ErrorsCounter = dict()
		self.__Messages = list()

		self.__StartTime = time.perf_counter()

	def __str__(self) -> str:
		"""Возвращает строковое представление ответа нейросети."""

		return str(self.to_dict())

	def get_error_count(self, error: Errors) -> int:
		"""
		Возвращает количество ошибок определённого типа.

		:param error: Тип ошибки.
		:type error: Errors
		:return: Количество ошибок данного типа.
		:rtype: int
		"""

		Count = 0

		try: Count = self.__ErrorsCounter[error.value]
		except KeyError: pass

		return Count

	def increment_try(self):
		"""Инкрементирует номер попытки генерации."""

		self.__CurrentTry += 1

	def push_error(self, error: Errors):
		"""
		Добавляет ошибку в счётчик.

		:param error: Тип ошибки.
		:type error: Errors
		"""

		if error.value not in self.__ErrorsCounter.keys(): self.__ErrorsCounter[error.value] = 1
		else: self.__ErrorsCounter[error.value] = self.__ErrorsCounter[error.value] + 1

	def push_message(self, message: str):
		"""
		Добавляет сообщение в сведения отладки.

		:param message: Текст сообщения.
		:type message: str
		"""

		self.__Messages.append(message)
		self.__Messages = list(set(self.__Messages))

	def set_text(self, text: str):
		"""
		Задаёт текст ответа.

		:param text: Текст ответа.
		:type text: str
		"""

		self.__Text = text

	def set_try(self, current_try: int):
		"""
		Инкрементирует номер попытки.

		:param current_try: Номер текущей попытки. генерации
		:type current_try: int
		"""

		self.__CurrentTry = current_try

	def stop_timer(self):
		"""Останавливает таймер выполнения и сохраняет значение."""

		self.__Time = round(time.perf_counter() - self.__StartTime, 2)

	def to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление ответа.

		:return: Словарное представление ответа.
		:rtype: dict
		"""

		return {
			"text": self.__Text,
			"debug": {
				"time": self.__Time,
				"tries": self.__CurrentTry,
				"errors": self.__ErrorsCounter,
				"messages": self.__Messages
			}
		}

class Generator:
	"""Обработчик запросов к нейросетям."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __RaiseTimeoutException(self, signum: int, frame: types.FrameType):
		"""
		Выбрасывает `TimeoutException`.

		:param signum: Номер сигнала, передаваемый обработчику.
		:param frame: Текущий стек вызовов в момент прерывания.
		:raises TimeoutException: Выбрасывается как результат выполнения метода.
		"""

		raise TimeoutException()

	def __ReadProxy(self):
		"""Считывает данные прокси из файла `Proxies.txt`."""

		Proxies = list()

		if os.path.exists("Proxies.txt"):
			Data = ReadTextFile("Proxies.txt", split = "\n")
			for Line in Data: Proxies.append(Proxy().parse(Line))

		self.__Proxies = tuple(Proxies)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ ВАЛИДАЦИИ <<<<< #
	#==========================================================================================#

	def __IsRussian(self, text: str) -> bool:
		"""
		Проверяет валидность текста на основе регулярного выражения, исключающего латиницу и иные не кирилические символы.
		  text – проверяемый текст.
		"""

		return bool(re.match(r"^[А-Яа-яЁё\s.,:;!?()\-\–«»\"\'\[\]{}]+$", text, re.IGNORECASE))
	
	def __ValidateText(self, text: str | None) -> str | Errors:
		"""
		Обрабатывает текст согласно параметрам и проводит его отбраковку.

		:param text: Обрабатываемый текст.
		:type text: str
		:return: Обработанный текст или тип ошибки.
		:rtype: str | Errors
		"""

		if not text: return Errors.EmptyResponse

		if self.__Options.only_plaint_text: text = HTML(text).plain_text

		if self.__Options.max_length and len(text) > self.__Options.max_length: return Errors.MaxLengthExceeded
		if self.__Options.language and self.__Options.language == Languages.Russian and not self.__IsRussian(text): return Errors.IncorrectResponseLanguage

		if text in (
			"You have reached your request limit for the hour.",
		): return Errors.RequestBlocked

		return text

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ <<<<< #
	#==========================================================================================#

	def __init__(self, options: Options):
		"""
		Обработчик запросов к нейросетям.

		:param options: Опции генерации.
		:type options: Options
		"""

		self.__Options = options

		self.__Proxies: tuple[Proxy] = tuple()

		self.__ReadProxy()

	def generate(self, request: str) -> Response:
		"""
		Генерирует ответ нейросети.

		:param request: Текст запроса.
		:type request: str
		:return: Контейнер ответа нейросети.
		:rtype: Response
		"""

		ClientObject = Client()
		ResponseObject = Response()

		while ResponseObject.current_try <= self.__Options.tries and not ResponseObject.text:
			
			if self.__Proxies: 
				if ResponseObject.get_error_count(Errors.RequestBlocked) or self.__Options.force_proxy:
					ClientObject = Client(proxies = random.choice(self.__Proxies).to_dict())

			try:
				ResponseData = ClientObject.chat.completions.create(model = self.__Options.model, messages = [{"role": "user", "content": request}])
				ValidatedData = self.__ValidateText(ResponseData.choices[0].message.content.strip())

				if type(ValidatedData) == str:
					ResponseObject.set_text(ValidatedData)
					break

				else: ResponseObject.push_error(ValidatedData)

			except TimeoutException:
				ResponseObject.push_error(Errors.TimeoutReached)
				break

			except KeyboardInterrupt: break
			except Exception as ExceptionData: ResponseObject.push_message(str(ExceptionData))

			ResponseObject.increment_try()

		if ResponseObject.current_try > self.__Options.tries: ResponseObject.set_try(self.__Options.tries)
		ResponseObject.stop_timer()

		return ResponseObject
	
	def generate_with_timeout(self, request: str) -> Response:
		"""
		Генерирует ответ нейросети и обрабатывает таймаут генерации. Может использоваться только из главного потока процесса.

		:param request: Текст запроса.
		:type request: str
		:return: Контейнер ответа нейросети.
		:rtype: Response
		"""

		signal.signal(signal.SIGALRM, self.__RaiseTimeoutException)
		signal.alarm(self.__Options.timeout)
		Response = self.generate(request)
		signal.alarm(0)

		return Response