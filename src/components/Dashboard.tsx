import React, { useState } from 'react';
import { Users, Camera, BarChart3, Clock, Upload, UserPlus } from 'lucide-react';
import AttendanceStats from './AttendanceStats';
import StudentRegistration from './StudentRegistration';
import FaceRecognition from './FaceRecognition';
import StudentList from './StudentList';
import AttendanceHistory from './AttendanceHistory';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('stats');

  const tabs = [
    { id: 'stats', label: 'Dashboard', icon: BarChart3 },
    { id: 'recognize', label: 'Recognition', icon: Camera },
    { id: 'register', label: 'Register', icon: UserPlus },
    { id: 'students', label: 'Students', icon: Users },
    { id: 'history', label: 'History', icon: Clock },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-indigo-600 p-2 rounded-lg">
                <Camera className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Upashthiti</h1>
                <p className="text-sm text-gray-600">Face Recognition Attendance System</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 px-3 py-1 rounded-full">
                <span className="text-green-800 text-sm font-medium">API Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'stats' && <AttendanceStats />}
        {activeTab === 'recognize' && <FaceRecognition />}
        {activeTab === 'register' && <StudentRegistration />}
        {activeTab === 'students' && <StudentList />}
        {activeTab === 'history' && <AttendanceHistory />}
      </main>
    </div>
  );
};

export default Dashboard;