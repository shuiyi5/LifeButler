/**
 * 根据时间段返回管家问候语
 */
export function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour >= 6 && hour < 11) return '早上好~今天也要元气满满哦！'
  if (hour >= 11 && hour < 14) return '午安~记得好好吃午饭呀'
  if (hour >= 14 && hour < 18) return '下午好~今天辛苦了'
  if (hour >= 18 && hour < 22) return '晚上好~今天过得怎么样？'
  return '夜深了，早点休息哦~'
}

/**
 * 格式化日期
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  })
}

/**
 * 格式化时间
 */
export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
