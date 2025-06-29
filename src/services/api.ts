import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-13b09.up.railway.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('🔄 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

export interface Student {
  name: string;
  student_id?: string;
  registered_at?: string;
}

export interface AttendanceRecord {
  name: string;
  timestamp: string;
  confidence: number;
}

export interface AttendanceStats {
  total_students: number;
  present_today: number;
  attendance_rate: number;
  recent_entries: AttendanceRecord[];
}

export interface RecognitionResult {
  message: string;
  recognized_faces: {
    name: string;
    confidence: number;
    student_id?: string;
    bbox: number[];
  }[];
  total_faces_detected: number;
  model_used: string;
}

export const registerStudent = async (
  name: string,
  file: File,
  studentId?: string
): Promise<{ message: string; student_id?: string; faces_detected: number; model_used: string }> => {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('file', file);
  if (studentId) {
    formData.append('student_id', studentId);
  }

  const response = await api.post('/api/register', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const recognizeFace = async (file: File): Promise<RecognitionResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/recognize', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const fetchStudents = async (): Promise<{ students: Student[]; total: number }> => {
  const response = await api.get('/api/students');
  return response.data;
};

export const deleteStudent = async (studentName: string): Promise<{ message: string }> => {
  const response = await api.delete(`/api/students/${encodeURIComponent(studentName)}`);
  return response.data;
};

export const fetchAttendanceStats = async (): Promise<AttendanceStats> => {
  const response = await api.get('/api/attendance/stats');
  return response.data;
};

export const fetchTodayAttendance = async (): Promise<{
  date: string;
  total_entries: number;
  unique_students: number;
  records: AttendanceRecord[];
  attendees: string[];
}> => {
  const response = await api.get('/api/attendance/today');
  return response.data;
};

export const fetchAttendanceHistory = async (days: number = 7): Promise<{
  history: {
    date: string;
    count: number;
    attendees: string[];
  }[];
}> => {
  const response = await api.get(`/api/attendance/history?days=${days}`);
  return response.data;
};