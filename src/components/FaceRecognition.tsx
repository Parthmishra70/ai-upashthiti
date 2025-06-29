import React, { useState, useRef } from 'react';
import { Camera, Upload, Users, CheckCircle, AlertCircle } from 'lucide-react';
import { recognizeFace } from '../services/api';

interface RecognizedFace {
  name: string;
  confidence: number;
  student_id?: string;
  bbox: number[];
}

const FaceRecognition: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<{
    recognized_faces: RecognizedFace[];
    total_faces_detected: number;
    message: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResults(null);
      
      // Create preview
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
      const result = await recognizeFace(selectedFile);
      setResults(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Recognition failed');
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
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

        {/* File Upload */}
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
                  onClick={resetForm}
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

      {/* Preview and Results */}
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
                  {/* Summary */}
                  <div className="flex items-center space-x-2 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-blue-600" />
                    <span className="text-blue-700">{results.message}</span>
                  </div>

                  {/* Recognized Faces */}
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

                  {/* Stats */}
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

      {/* API Usage Example */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">API Usage</h3>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-2">Use this endpoint to integrate face recognition into your application:</p>
          <code className="block bg-gray-800 text-green-400 p-3 rounded text-sm overflow-x-auto">
            POST /api/recognize
            <br />
            Content-Type: multipart/form-data
            <br />
            Body: file (image file)
          </code>
        </div>
      </div>
    </div>
  );
};

export default FaceRecognition;