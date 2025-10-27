import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Shield, Users, Package, Calendar, Ban, Check, X, Trash2, Search, AlertTriangle } from 'lucide-react'

const AdminDashboard = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [equipment, setEquipment] = useState([])
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [selectedEquipment, setSelectedEquipment] = useState(null)
  const [showBanDialog, setShowBanDialog] = useState(false)
  const [showRejectDialog, setShowRejectDialog] = useState(false)
  const [banReason, setBanReason] = useState('')
  const [rejectReason, setRejectReason] = useState('')
  const [filterStatus, setFilterStatus] = useState('pending')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('token')
      
      // Load stats
      const statsRes = await fetch('/api/admin/dashboard/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const statsData = await statsRes.json()
      if (statsData.success) {
        setStats(statsData.stats)
      }
      
      setLoading(false)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      setLoading(false)
    }
  }

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/users?search=${searchQuery}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        setUsers(data.users)
      }
    } catch (error) {
      console.error('Error loading users:', error)
    }
  }

  const loadEquipment = async () => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/equipment?status=${filterStatus}&search=${searchQuery}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        setEquipment(data.equipment)
      }
    } catch (error) {
      console.error('Error loading equipment:', error)
    }
  }

  const loadBookings = async () => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/admin/bookings', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        setBookings(data.bookings)
      }
    } catch (error) {
      console.error('Error loading bookings:', error)
    }
  }

  useEffect(() => {
    if (activeTab === 'users') loadUsers()
    if (activeTab === 'equipment') loadEquipment()
    if (activeTab === 'bookings') loadBookings()
  }, [activeTab, searchQuery, filterStatus])

  const handleBanUser = async (userId) => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/users/${userId}/ban`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: banReason })
      })
      const data = await res.json()
      if (data.success) {
        alert('User banned successfully')
        setShowBanDialog(false)
        setBanReason('')
        loadUsers()
      }
    } catch (error) {
      console.error('Error banning user:', error)
    }
  }

  const handleUnbanUser = async (userId) => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/users/${userId}/unban`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        alert('User unbanned successfully')
        loadUsers()
      }
    } catch (error) {
      console.error('Error unbanning user:', error)
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user? This cannot be undone.')) return
    
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        alert('User deleted successfully')
        loadUsers()
      }
    } catch (error) {
      console.error('Error deleting user:', error)
    }
  }

  const handleApproveEquipment = async (equipmentId) => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/equipment/${equipmentId}/approve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        alert('Equipment approved successfully')
        loadEquipment()
      }
    } catch (error) {
      console.error('Error approving equipment:', error)
    }
  }

  const handleRejectEquipment = async (equipmentId) => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/equipment/${equipmentId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: rejectReason })
      })
      const data = await res.json()
      if (data.success) {
        alert('Equipment rejected successfully')
        setShowRejectDialog(false)
        setRejectReason('')
        loadEquipment()
      }
    } catch (error) {
      console.error('Error rejecting equipment:', error)
    }
  }

  const handleDeleteEquipment = async (equipmentId) => {
    if (!confirm('Are you sure you want to delete this equipment? This cannot be undone.')) return
    
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/admin/equipment/${equipmentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        alert('Equipment deleted successfully')
        loadEquipment()
      }
    } catch (error) {
      console.error('Error deleting equipment:', error)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <Button variant="outline" onClick={onLogout}>Logout</Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-8">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="equipment">Equipment</TabsTrigger>
            <TabsTrigger value="bookings">Bookings</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-gray-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
                  <p className="text-xs text-red-600 mt-1">{stats?.banned_users || 0} banned</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Equipment Listings</CardTitle>
                  <Package className="h-4 w-4 text-gray-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_equipment || 0}</div>
                  <p className="text-xs text-yellow-600 mt-1">{stats?.pending_equipment || 0} pending approval</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
                  <Calendar className="h-4 w-4 text-gray-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_bookings || 0}</div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Pending Approvals</CardTitle>
                <CardDescription>Equipment listings waiting for approval</CardDescription>
              </CardHeader>
              <CardContent>
                {stats?.pending_equipment > 0 ? (
                  <Button onClick={() => setActiveTab('equipment')}>
                    Review {stats.pending_equipment} Pending Listings
                  </Button>
                ) : (
                  <p className="text-gray-600">No pending approvals</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>User Management</CardTitle>
                    <CardDescription>Manage all users on the platform</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Search users..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-64"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((u) => (
                      <TableRow key={u.id}>
                        <TableCell>{u.first_name} {u.last_name}</TableCell>
                        <TableCell>{u.email}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{u.user_type}</Badge>
                        </TableCell>
                        <TableCell>
                          {u.is_banned ? (
                            <Badge variant="destructive">Banned</Badge>
                          ) : (
                            <Badge variant="success">Active</Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            {u.is_banned ? (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleUnbanUser(u.id)}
                              >
                                Unban
                              </Button>
                            ) : (
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => {
                                  setSelectedUser(u)
                                  setShowBanDialog(true)
                                }}
                              >
                                <Ban className="h-4 w-4" />
                              </Button>
                            )}
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDeleteUser(u.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Equipment Tab */}
          <TabsContent value="equipment">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Equipment Moderation</CardTitle>
                    <CardDescription>Approve or reject equipment listings</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="border rounded px-3 py-2"
                    >
                      <option value="pending">Pending</option>
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                    </select>
                    <Input
                      placeholder="Search equipment..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-64"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Owner</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {equipment.map((eq) => (
                      <TableRow key={eq.id}>
                        <TableCell>{eq.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{eq.category}</Badge>
                        </TableCell>
                        <TableCell>${eq.daily_price}/day</TableCell>
                        <TableCell>{eq.owner?.email}</TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              eq.approval_status === 'approved' ? 'success' :
                              eq.approval_status === 'rejected' ? 'destructive' :
                              'warning'
                            }
                          >
                            {eq.approval_status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            {eq.approval_status === 'pending' && (
                              <>
                                <Button
                                  size="sm"
                                  variant="default"
                                  onClick={() => handleApproveEquipment(eq.id)}
                                >
                                  <Check className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => {
                                    setSelectedEquipment(eq)
                                    setShowRejectDialog(true)
                                  }}
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              </>
                            )}
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDeleteEquipment(eq.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Bookings Tab */}
          <TabsContent value="bookings">
            <Card>
              <CardHeader>
                <CardTitle>All Bookings</CardTitle>
                <CardDescription>View all platform bookings</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Equipment</TableHead>
                      <TableHead>Renter</TableHead>
                      <TableHead>Dates</TableHead>
                      <TableHead>Total</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {bookings.map((booking) => (
                      <TableRow key={booking.id}>
                        <TableCell>{booking.equipment?.name}</TableCell>
                        <TableCell>{booking.renter?.email}</TableCell>
                        <TableCell>
                          {new Date(booking.start_date).toLocaleDateString()} - 
                          {new Date(booking.end_date).toLocaleDateString()}
                        </TableCell>
                        <TableCell>${booking.total_price}</TableCell>
                        <TableCell>
                          <Badge>{booking.status}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Ban User Dialog */}
      <Dialog open={showBanDialog} onOpenChange={setShowBanDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ban User</DialogTitle>
            <DialogDescription>
              Are you sure you want to ban {selectedUser?.email}?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Reason for ban</label>
              <Textarea
                value={banReason}
                onChange={(e) => setBanReason(e.target.value)}
                placeholder="Enter reason..."
              />
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowBanDialog(false)}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleBanUser(selectedUser?.id)}
              >
                Ban User
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Reject Equipment Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Equipment</DialogTitle>
            <DialogDescription>
              Are you sure you want to reject "{selectedEquipment?.name}"?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Reason for rejection</label>
              <Textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Enter reason..."
              />
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowRejectDialog(false)}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleRejectEquipment(selectedEquipment?.id)}
              >
                Reject
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default AdminDashboard

