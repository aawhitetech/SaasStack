"use client"

import { useEffect, useState } from 'react'

interface User {
  url: string
  username: string
  email: string
  groups: string[]
}

interface Group {
  url: string
  name: string
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [groups, setGroups] = useState<Group[]>([])

  // Fetch Users
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await fetch('/api/users/', {
          credentials: 'include',
        })
        const data = await res.json()
        setUsers(data.results || data)
      } catch (err) {
        console.error('Failed to fetch users:', err)
      }
    }

    fetchUsers()
  }, [])

  // Fetch Groups
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const res = await fetch('/api/groups/', {
          credentials: 'include',
        })
        const data = await res.json()
        setGroups(data.results || data)
      } catch (err) {
        console.error('Failed to fetch groups:', err)
      }
    }

    fetchGroups()
  }, [])

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Users</h1>
      <ul className="space-y-2">
        {users.map((user) => (
          <li key={user.url} className="border p-4 rounded shadow">
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
          </li>
        ))}
      </ul>

      <h1 className="text-2xl font-bold my-6">Groups</h1>
      <ul className="space-y-2">
        {groups.map((group) => (
          <li key={group.url} className="border p-4 rounded shadow">
            <p><strong>Group:</strong> {group.name}</p>
          </li>
        ))}
      </ul>
    </main>
  )
}
