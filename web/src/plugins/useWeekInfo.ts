// useWeekInfo.ts
import dayjs from 'dayjs'
import isoWeek from 'dayjs/plugin/isoWeek'

dayjs.extend(isoWeek)

/**
 * 从 ISO 周字符串 (如 "2025-W02") 获取该周的年份、月份、日期范围
 */
export function useWeekInfo(weekString: string) {
  const match = weekString.match(/^(\d{4})-W(\d{2})$/)
  if (!match) throw new Error('Invalid week string format, expected YYYY-Www')

  const [, yearStr, weekStr] = match
  const year = Number(yearStr)
  const week = Number(weekStr)

  // 根据 ISO 周规则计算该周的起始日（周一）
  // ISO 周定义：第1周包含该年1月4日
  const startOfFirstWeek = dayjs(`${year}-01-04`).startOf('week') // 周一
  const start = startOfFirstWeek.add(week - 1, 'week')
  const end = start.add(6, 'day')

  const years = new Set<number>()
  const months = new Set<string>()

  for (let i = 0; i < 7; i++) {
    const d = start.add(i, 'day')
    years.add(d.year())
    // 格式化为 "YYYY-MM"，月份补零
    const monthStr = `${d.year()}-${String(d.month() + 1).padStart(2, '0')}`
    months.add(monthStr)
  }

  return {
    range: [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')],
    years: [...years],
    months: [...months],
  }
}
