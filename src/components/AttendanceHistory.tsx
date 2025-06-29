import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock, Users, Calendar, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import { fetchAttendanceHistory, fetchTodayAttendance } from '../services/api';

const AttendanceHistory: React.FC = () => {
  const { data: history, isLoading } = useQuery({
    queryKey: ['attendance-history', 14],
    queryFn: () => fetchAttendanceHistory(14),
    refetchInterval: 60000,
  });

  const { data: todayData } = useQuery({
    queryKey: ['today-attendance'],
    queryFn: fetchTodayAttendance,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const chartData = history?.history?.map(day => ({
    date: format(new Date(day.date), 'MMM dd'),
    attendance: day.count,
    fullDate: day.date
  })).reverse() || [];

  const totalDays = history?.history?.length || 0;
  const averageAttendance = totalDays > 0 
    ? Math.round(history.history.reduce((sum, day) => sum + day.count, 0) / totalDays)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Today's Attendance</p>
              <p className="text-3xl font-bold text-indigo-600">{todayData?.unique_students || 0}</p>
            </div>
            <div className="bg-indigo-100 p-3 rounded-lg">
              <Users className="h-6 w-6 text-indigo-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Entries Today</p>
              <p className="text-3xl font-bold text-green-600">{todayData?.total_entries || 0}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <Clock className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">14-Day Average</p>
              <p className="text-3xl font-bold text-purple-600">{averageAttendance}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Days Tracked</p>
              <p className="text-3xl font-bold text-orange-600">{totalDays}</p>
            </div>
            <div className="bg-orange-100 p-3 rounded-lg">
              <Calendar className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Attendance Trend Chart */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">14-Day Attendance Trend</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip 
                labelFormatter={(label) => {
                  const item = chartData.find(d => d.date === label);
                  return item ? format(new Date(item.fullDate), 'EEEE, MMMM dd, yyyy') : label;
                }}
              />
              <Line 
                type="monotone" 
                dataKey="attendance" 
                stroke="#4f46e5" 
                strokeWidth={3}
                dot={{ fill: '#4f46e5', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Days */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Days</h3>
          <div className="space-y-3">
            {history?.history?.slice(0, 7).map((day, index) => (
              <div key={day.date} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <div>
                  <p className="font-medium text-gray-900">
                    {format(new Date(day.date), 'EEEE, MMM dd')}
                  </p>
                  <p className="text-sm text-gray-500">
                    {day.attendees.length > 0 ? day.attendees.join(', ') : 'No attendance'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-indigo-600">{day.count}</p>
                  <p className="text-xs text-gray-500">students</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Today's Details */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Today's Activity</h3>
          <div className="space-y-3">
            {todayData?.records?.slice(0, 10).map((record, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <div className="flex items-center space-x-3">
                  <div className="bg-green-100 p-2 rounded-full">
                    <Users className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{record.name}</p>
                    <p className="text-sm text-gray-500">
                      Confidence: {(record.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    {format(new Date(record.timestamp), 'HH:mm:ss')}
                  </p>
                </div>
              </div>
            ))}
            {(!todayData?.records || todayData.records.length === 0) && (
              <p className="text-gray-500 text-center py-4">No activity today</p>
            )}
          </div>
        </div>
      </div>

      {/* API Usage */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">API Endpoints</h3>
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">Get attendance history:</p>
            <code className="block bg-gray-800 text-green-400 p-3 rounded text-sm">
              GET /api/attendance/history?days=7
            </code>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">Get today's attendance:</p>
            <code className="block bg-gray-800 text-green-400 p-3 rounded text-sm">
              GET /api/attendance/today
            </code>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttendanceHistory;