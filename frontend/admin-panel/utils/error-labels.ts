const messages: Record<string, string> = {
  'Incorrect email or password': 'Неверный email или пароль',
  'Email already registered': 'Этот email уже зарегистрирован',
  'User not found': 'Пользователь не найден',
  'Inactive user': 'Учётная запись отключена',
  'Token has expired': 'Сессия истекла. Войдите снова',
  'Not enough permissions': 'Недостаточно прав доступа',
  'Insufficient permissions': 'Недостаточно прав доступа',
  'Device not found': 'Устройство не найдено',
  'Integration not found': 'Подключение не найдено',
  'Device is disabled': 'Устройство отключено',
  'Signal not found for this device': 'Показатель устройства не найден',
  'This signal is read-only': 'Этот показатель доступен только для просмотра',
  'Emulator synchronization unavailable':
    'Не удалось подключить демонстрационные устройства. Проверьте, что эмуляторы запущены.',
  'Fleet already belongs to another object': 'Устройства уже подключены к другому объекту',
}
export const errorLabel = (message: string): string => messages[message] || message
