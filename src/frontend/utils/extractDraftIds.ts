/**
 * 草稿 ID 格式：13位毫秒时间戳 + UUID v4（小写十六进制）
 * 例：1774814277612-08262a35-ea9b-4082-9289-f7846809a148
 */
const DRAFT_ID_RE = /\d{10,15}-[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}/gi

/**
 * 从任意文本中智能提取草稿 ID，支持三种格式：
 * 1. JSON 对象：`{ "draft_id": "..." }`
 * 2. JSON 对象：`{ "draft_ids": ["...", ...] }`
 * 3. 任意分隔符（逗号、换行、空格、顿号等）分隔的纯 ID 列表
 *
 * 返回去重后的小写 ID 数组，若未识别到则返回空数组。
 */
export function extractDraftIds(text: string): string[] {
  const trimmed = text.trim()
  if (!trimmed) return []

  // 路径1：尝试 JSON 解析
  try {
    const json = JSON.parse(trimmed) as Record<string, unknown>
    if (typeof json.draft_id === 'string') return [json.draft_id]
    if (Array.isArray(json.draft_ids)) {
      const ids = json.draft_ids.filter((x): x is string => typeof x === 'string')
      if (ids.length > 0) return ids
    }
  } catch {
    // fall through to regex extraction
  }

  // 路径2：正则提取任意位置的 ID（去重、统一小写）
  const matches = trimmed.match(DRAFT_ID_RE)
  if (!matches) return []
  return [...new Set(matches.map((s) => s.toLowerCase()))]
}
