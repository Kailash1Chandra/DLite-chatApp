import { io } from 'socket.io-client'
import { API_BASE_URL, CHAT_SOCKET_URL } from './appClient'
import { getCurrentAuthSnapshot } from './authClient'

let socketInstance = null

function getSocket({ userId } = {}) {
  if (socketInstance) return socketInstance
  socketInstance = io(CHAT_SOCKET_URL, {
    autoConnect: true,
    transports: ['websocket'],
    auth: userId ? { userId } : undefined,
  })
  return socketInstance
}

function safeUserProfile(userId) {
  const id = String(userId || '').trim()
  return { id, uid: id, username: id || 'User', email: '', photoURL: '' }
}

export function initializeMyPresence() {
  return () => undefined
}

export async function getUserProfileById(userId) {
  return safeUserProfile(userId)
}

export async function searchUsersByUsername(_term, _excludeUserId) {
  const term = String(_term || '').trim()
  if (!term) return []
  const snapshot = await getCurrentAuthSnapshot()
  if (!snapshot?.token) return []
  const url = new URL(`${API_BASE_URL}/chat/users/search`)
  url.searchParams.set('username', term)
  if (_excludeUserId) url.searchParams.set('exclude', String(_excludeUserId))
  const res = await fetch(url.toString(), { headers: { Authorization: `Bearer ${snapshot.token}` } })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || json?.success === false) return []
  return json?.users || []
}

export async function listDirectMessages() {
  return []
}

export function subscribeDirectMessages(_userId, chatId, callback) {
  const s = getSocket({})
  s.emit('join_chat', { chatId })
  const handler = (message) => callback(message, 'added')
  s.on('receive_message', handler)
  return () => s.off('receive_message', handler)
}

export async function sendDirectMessage({ chatId, senderId, content }) {
  const s = getSocket({ userId: senderId })
  s.emit('send_message', { chatId, senderId, content, type: 'text' })
}

export async function sendDirectMedia() {
  const error = new Error('Media messages are disabled.')
  error.code = 'feature/disabled'
  throw error
}

export async function editDirectMessage() {
  const error = new Error('Editing messages is disabled.')
  error.code = 'feature/disabled'
  throw error
}

export async function deleteDirectMessage() {
  const error = new Error('Deleting messages is disabled.')
  error.code = 'feature/disabled'
  throw error
}

export async function hideDirectMessageForMe() {
  return
}

export async function markDirectThreadRead() {
  return
}

export async function exportDirectChatHistory() {
  const error = new Error('Export is disabled.')
  error.code = 'feature/disabled'
  throw error
}

export async function importDirectChatHistory() {
  const error = new Error('Import is disabled.')
  error.code = 'feature/disabled'
  throw error
}

export async function getMessagesByChatId({ chatId, token }) {
  const res = await fetch(`${API_BASE_URL}/chat/messages/${encodeURIComponent(chatId)}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || json?.success === false) throw new Error(json?.message || 'Failed to fetch messages')
  return json?.messages || []
}

export async function setUserProfilePhoto() {
  const error = new Error('Profile photo upload is disabled.')
  error.code = 'feature/disabled'
  throw error
}

export async function clearUserProfilePhoto() {
  return
}

// ===== Stubs for legacy UI (non-breaking) =====
export async function sendGroupMessage() {
  const error = new Error('Group chat is disabled.')
  error.code = 'feature/disabled'
  throw error
}
export async function listGroupMessages() {
  return []
}
export function subscribeGroupMessages() {
  return () => undefined
}
export async function listUserGroups() {
  const snapshot = await getCurrentAuthSnapshot()
  if (!snapshot?.token) return []
  const res = await fetch(`${API_BASE_URL}/chat/groups/my`, { headers: { Authorization: `Bearer ${snapshot.token}` } })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || json?.success === false) throw new Error(json?.message || 'Could not load groups')
  return json?.groups || []
}
export async function ensureGroupMembership() {
  const snapshot = await getCurrentAuthSnapshot()
  if (!snapshot?.token) throw new Error('Not authenticated')
  const groupKey = String(arguments?.[0]?.groupId || arguments?.[0]?.groupKey || '').trim()
  if (!groupKey) throw new Error('groupId is required')
  const res = await fetch(`${API_BASE_URL}/chat/groups/ensure`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${snapshot.token}` },
    body: JSON.stringify({ groupKey }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || json?.success === false) throw new Error(json?.message || 'Could not open group')
  return json?.group
}
export async function addGroupMemberByUsername() {
  const snapshot = await getCurrentAuthSnapshot()
  if (!snapshot?.token) throw new Error('Not authenticated')
  const groupId = String(arguments?.[0]?.groupId || '').trim()
  const username = String(arguments?.[0]?.username || '').trim()
  if (!groupId || !username) throw new Error('groupId and username are required')
  const res = await fetch(`${API_BASE_URL}/chat/groups/${encodeURIComponent(groupId)}/members/add-by-username`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${snapshot.token}` },
    body: JSON.stringify({ username }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || json?.success === false) throw new Error(json?.message || 'Could not add member')
  return json?.member
}
export async function listGroupMembers() {
  const snapshot = await getCurrentAuthSnapshot()
  if (!snapshot?.token) return []
  const groupId = String(arguments?.[0] || '').trim()
  if (!groupId) return []
  const res = await fetch(`${API_BASE_URL}/chat/groups/${encodeURIComponent(groupId)}/members`, {
    headers: { Authorization: `Bearer ${snapshot.token}` },
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok || json?.success === false) throw new Error(json?.message || 'Could not load members')
  return json?.members || []
}
export async function leaveGroupMembership() {
  return
}
export async function removeGroupMember() {
  return
}
export async function setGroupPhoto() {
  const error = new Error('Group chat is disabled.')
  error.code = 'feature/disabled'
  throw error
}
export async function exportGroupChatHistory() {
  const error = new Error('Export is disabled.')
  error.code = 'feature/disabled'
  throw error
}
export async function importGroupChatHistory() {
  const error = new Error('Import is disabled.')
  error.code = 'feature/disabled'
  throw error
}
export async function markGroupThreadRead() {
  return
}
export async function toggleGroupReaction() {
  return
}
export async function setGroupMemberRole() {
  return
}
export async function setGroupMuted() {
  return
}
export async function setGroupTyping() {
  return
}
export function subscribeGroupTyping() {
  return () => undefined
}
export async function pinGroupMessage() {
  return
}
export async function unpinGroupMessage() {
  return
}
export function subscribePinnedGroupMessages() {
  return () => undefined
}
export async function deleteGroupMessage() {
  return
}
export async function toggleDmReaction() {
  return
}
export async function setDmTyping() {
  return
}
export function subscribeDmTyping() {
  return () => undefined
}
export async function pinDmMessage() {
  return
}
export async function unpinDmMessage() {
  return
}
export function subscribePinnedDmMessages() {
  return () => undefined
}
export function subscribeRecentDirectChats(_userId, callback) {
  callback([])
  return () => undefined
}
export function subscribeUserPresence(_userId, callback) {
  callback({ online: false, lastSeen: null })
  return () => undefined
}
export async function markRecentDirectChatRead() {
  return
}
export async function deleteRecentDirectChat() {
  return
}
export async function setRecentDirectChatArchived() {
  return
}
export async function setRecentDirectChatLocked() {
  return
}
export async function setMyPresence() {
  return
}

