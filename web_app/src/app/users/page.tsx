"use client"

import { useEffect, useState } from 'react'

export default function UsersPage() {
  const [users, setUsers] = useState([])
  const [groups, setGroups] = useState([])

  // Fetch Users
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await fetch('/api-django/users/', {
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
        const res = await fetch('/api-django/groups/', {
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
        {users.map((user: any) => (
          <li key={user.url} className="border p-4 rounded shadow">
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
          </li>
        ))}
      </ul>

      <h1 className="text-2xl font-bold my-6">Groups</h1>
      <ul className="space-y-2">
        {groups.map((group: any) => (
          <li key={group.url} className="border p-4 rounded shadow">
            <p><strong>Group:</strong> {group.name}</p>
          </li>
        ))}
      </ul>
    </main>
  )
}
