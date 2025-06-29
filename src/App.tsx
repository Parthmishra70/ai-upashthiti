import React, { useState, useRef } from 'react';
import { Camera, Upload, Users, CheckCircle, AlertCircle, UserPlus } from 'lucide-react';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-13b09.up.railway.app';

interface RecognizedFace {
  name: string;
  confidence: number;
  student_id?: string;
  bbox: number[];
}

interface RecognitionResult {
  message: string;
  recognized_faces: RecognizedFace[];
  total_faces_detected: number;
  model_used?: string;
}

function App() {
  const [activeTab, setActiveTab] = useState<'recognize' | 'register'>('recognize');
  
  // Recognition state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<RecognitionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Registration state
  const [formData, setFormData] = useState({
    name: '',
    studentId: '',
  });
  const [regFile, setRegFile] = useState<File | null>(null);
  const [regPreview, setRegPreview] = useState<string | null>(null);
  const [regLoading, setRegLoading] = useState(false);
  const [regSuccess, setRegSuccess] = useState<string | null>(null);
  const [regError, setRegError] = useState<string | null>(null);
  const regFileInputRef = useRef<HTMLInputElement>(null);

  // Recognition functions
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResults(null);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRecognize = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_BASE_URL}/api/recognize`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setResults(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Recognition failed');
    } finally {
      setIsLoading(false);
    }
  };

  const resetRecognition = () => {
    setSelectedFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Registration functions
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleRegFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setRegFile(file);
      setRegError(null);
      setRegSuccess(null);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setRegPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setRegError('Student name is required');
      return;
    }
    
    if (!regFile) {
      setRegError('Please select an image');
      return;
    }

    setRegLoading(true);
    setRegError(null);
    setRegSuccess(null);

    try {
      const submitData = new FormData();
      submitData.append('name', formData.name.trim());
      submitData.append('file', regFile);
      if (formData.studentId.trim()) {
        submitData.append('student_id', formData.studentId.trim());
      }

      const response = await fetch(`${API_BASE_URL}/api/register`, {
        method: 'POST',
        body: submitData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setRegSuccess(`${result.message}. Detected ${result.faces_detected} face(s) in the image.`);
      
      // Reset form
      setFormData({ name: '', studentId: '' });
      setRegFile(null);
      setRegPreview(null);
      if (regFileInputRef.current) {
        regFileInputRef.current.value = '';
      }
    } catch (err) {
      setRegError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setRegLoading(false);
    }
  };

  const resetRegistration = () => {
    setFormData({ name: '', studentId: '' });
    setRegFile(null);
    setRegPreview(null);
    setRegError(null);
    setRegSuccess(null);
    if (regFileInputRef.current) {
      regFileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-indigo-600 p-2 rounded-lg">
                <Camera className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Upashthiti</h1>
                <p className="text-sm text-gray-600">Face Recognition System</p>
              </div>
            </div>
            <div className="bg-green-100 px-3 py-1 rounded-full">
              <span className="text-green-800 text-sm font-medium">API Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('recognize')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'recognize'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Camera className="h-5 w-5" />
              <span>Recognize Faces</span>
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'register'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <UserPlus className="h-5 w-5" />
              <span>Register Student</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'recognize' && (
          <div className="space-y-6">
            {/* Face Recognition */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-indigo-100 p-2 rounded-lg">
                  <Camera className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Face Recognition</h2>
                  <p className="text-gray-600">Upload an image to recognize registered students</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Upload className="h-5 w-5" />
                    <span>Select Image</span>
                  </button>
                  
                  {selectedFile && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{selectedFile.name}</span>
                      <button
                        onClick={resetRecognition}
                        className="text-red-600 hover:text-red-700 text-sm"
                      >
                        Clear
                      </button>
                    </div>
                  )}
                </div>

                {selectedFile && (
                  <button
                    onClick={handleRecognize}
                    disabled={isLoading}
                    className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Users className="h-5 w-5" />
                    <span>{isLoading ? 'Recognizing...' : 'Recognize Faces'}</span>
                  </button>
                )}
              </div>
            </div>

            {/* Results */}
            {(preview || results || error) && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Image Preview */}
                {preview && (
                  <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Image Preview</h3>
                    <div className="relative">
                      <img
                        src={preview}
                        alt="Preview"
                        className="w-full h-auto rounded-lg border border-gray-200"
                      />
                      {isLoading && (
                        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                          <div className="bg-white p-4 rounded-lg">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
                            <p className="text-sm text-gray-600 mt-2">Processing...</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Results */}
                {(results || error) && (
                  <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Recognition Results</h3>
                    
                    {error && (
                      <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <AlertCircle className="h-5 w-5 text-red-600" />
                        <span className="text-red-700">{error}</span>
                      </div>
                    )}

                    {results && (
                      <div className="space-y-4">
                        <div className="flex items-center space-x-2 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                          <CheckCircle className="h-5 w-5 text-blue-600" />
                          <span className="text-blue-700">{results.message}</span>
                        </div>

                        {results.recognized_faces.length > 0 ? (
                          <div className="space-y-3">
                            <h4 className="font-medium text-gray-900">Recognized Students:</h4>
                            {results.recognized_faces.map((face, index) => (
                              <div key={index} className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
                                <div>
                                  <p className="font-medium text-green-900">{face.name}</p>
                                  {face.student_id && (
                                    <p className="text-sm text-green-700">ID: {face.student_id}</p>
                                  )}
                                </div>
                                <div className="text-right">
                                  <p className="text-sm font-medium text-green-800">
                                    {(face.confidence * 100).toFixed(1)}%
                                  </p>
                                  <p className="text-xs text-green-600">Confidence</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-yellow-700">
                              {results.total_faces_detected > 0 
                                ? 'Faces detected but no matches found with registered students'
                                : 'No faces detected in the image'
                              }
                            </p>
                          </div>
                        )}

                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-gray-900">{results.total_faces_detected}</p>
                            <p className="text-sm text-gray-600">Faces Detected</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-green-600">{results.recognized_faces.length}</p>
                            <p className="text-sm text-gray-600">Recognized</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'register' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center space-x-3 mb-6">
                <div className="bg-green-100 p-2 rounded-lg">
                  <UserPlus className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Register New Student</h2>
                  <p className="text-gray-600">Add a new student to the face recognition system</p>
                </div>
              </div>

              {/* Success/Error Messages */}
              {regSuccess && (
                <div className="mb-6 flex items-center space-x-2 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-green-700">{regSuccess}</span>
                </div>
              )}

              {regError && (
                <div className="mb-6 flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <AlertCircle className="h-5 w-5 text-red-600" />
                  <span className="text-red-700">{regError}</span>
                </div>
              )}

              <form onSubmit={handleRegister} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                      Student Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Enter student name"
                    />
                  </div>

                  <div>
                    <label htmlFor="studentId" className="block text-sm font-medium text-gray-700 mb-2">
                      Student ID (Optional)
                    </label>
                    <input
                      type="text"
                      id="studentId"
                      name="studentId"
                      value={formData.studentId}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Enter student ID"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Student Photo *
                  </label>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4">
                      <input
                        ref={regFileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleRegFileSelect}
                        className="hidden"
                      />
                      <button
                        type="button"
                        onClick={() => regFileInputRef.current?.click()}
                        className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        <Upload className="h-5 w-5" />
                        <span>Select Photo</span>
                      </button>
                      
                      {regFile && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">{regFile.name}</span>
                          <button
                            type="button"
                            onClick={() => {
                              setRegFile(null);
                              setRegPreview(null);
                              if (regFileInputRef.current) regFileInputRef.current.value = '';
                            }}
                            className="text-red-600 hover:text-red-700 text-sm"
                          >
                            Remove
                          </button>
                        </div>
                      )}
                    </div>

                    {regPreview && (
                      <div className="mt-4">
                        <img
                          src={regPreview}
                          alt="Preview"
                          className="w-32 h-32 object-cover rounded-lg border border-gray-200"
                        />
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-4 pt-4">
                  <button
                    type="submit"
                    disabled={regLoading}
                    className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <UserPlus className="h-5 w-5" />
                    <span>{regLoading ? 'Registering...' : 'Register Student'}</span>
                  </button>

                  <button
                    type="button"
                    onClick={resetRegistration}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Clear Form
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;